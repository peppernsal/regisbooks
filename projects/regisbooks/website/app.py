import re

from sqlalchemy import text
import genid
import httpx
import isbnlib
import secret_keys
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import TypeVar
from flask import Response, jsonify, render_template, request
from propelauth_flask import current_user, init_auth
from propelauth_flask.user import LoggedInUser
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.attributes import flag_modified
from webpy import App

current_user: LoggedInUser
T = TypeVar('T')

app = App(__name__, template_folder="html")

BAD_REQUEST = Response(status=400)
RESP_OK = Response(status=200)
FORBIDDEN = Response(status=403)
LISTINGS_PER_PAGE = 10

def webpy_setup(app: App):
	global auth, db

	auth = init_auth(secret_keys.AUTH_URL, secret_keys.AUTH_API_KEY)

	db = app.sqlalchemy.init(secret_keys.DB_URI)

	init_db_api()
	register_internal_api_routes()
	register_external_api_routes()
	reigster_404_handler()

def register_external_api_routes(): # TODO, also have an efficient system to manage verification of API keys (research) |||| extract & reuse logic from register_internal_api_routes
	@app.route("/api/external/rem-book", methods=["POST"])
	def rembook_external():
		admin_key = request.json.get("key")

		if admin_key != secret_keys.ADMIN_KEY: return FORBIDDEN

		book_id = request.json.get("bookID")

		if type(book_id) is not str: return BAD_REQUEST

		Book.query.filter(Book.id == book_id).delete()

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/rem-listing", methods=["POST"])
	def remlisting_external():
		admin_key = request.json.get("key")

		if admin_key != secret_keys.ADMIN_KEY: return FORBIDDEN

		listing_id = request.json.get("listingID")

		if type(listing_id) is not str: return BAD_REQUEST

		listing_query = Listing.query.filter(Listing.id == listing_id)

		listing: Listing = listing_query.first()

		if listing is None: return BAD_REQUEST

		listing.author.stats.listings_made -= 1

		flag_modified(listing.author, "stats") # ensure stats is updated in db

		listing_query.delete()

		db.session.commit()

		return RESP_OK

	@app.route("/api/external/clear-taken-listings", methods=["POST"])
	def cleartakenlistings_external():
		admin_key = request.json.get("key")

		if admin_key != secret_keys.ADMIN_KEY: return FORBIDDEN

		Listing.query.filter(Listing.status == Listing.Status.TAKEN).delete()

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/temp/normalize-book-isbns", methods=["POST"])
	def normalize_book_isbns_external():
		admin_key = request.json.get("key")

		if admin_key != secret_keys.ADMIN_KEY: return FORBIDDEN

		db.session.execute(text("""ALTER TABLE listings
DROP CONSTRAINT listings_book_id_fkey,
ADD CONSTRAINT listings_book_id_fkey
FOREIGN KEY (book_id)
REFERENCES books (id)
ON UPDATE CASCADE;
"""))

		books = Book.get_all()

		for book in books:
			if isbnlib.is_isbn10(book.id):
				new_id = isbnlib.to_isbn13(book.id)

				db.session.execute(
					text("UPDATE books SET id = :new_id WHERE id = :old_id"),
					{ "new_id": new_id, "old_id": book.id }
				)

		db.session.commit()

		return RESP_OK
	
def register_internal_api_routes():
	@app.route("/api/internal/get-user")
	@auth.require_user
	def getuser_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		user = User.by_id(request.args.get("id"))

		if user is None: return BAD_REQUEST
		return jsonify(user.as_dict)

	@app.route("/api/internal/get-users")
	@auth.require_user
	def getusers_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		users = User.query.filter(~User.email.in_(secret_keys.EMAIL_WHITELIST)).all()

		return jsonify([user.id for user in users])

	@app.route("/api/internal/get-listing")
	@auth.require_user
	def getlisting_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		listing = Listing.by_id(request.args.get("id"))

		if listing is None: return BAD_REQUEST
		return jsonify(listing.as_dict)
	
	@app.route("/api/internal/get-book")
	@auth.require_user
	def getbook_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		book = Book.by_id(request.args.get("id"))

		if book is None: return BAD_REQUEST

		return jsonify(book.as_dict)

	@app.route("/api/internal/get-listings", methods=["GET", "POST"])
	@auth.require_user
	def getlistings_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		if request.method == "GET":
			listings = Listing.get_all() # TODO: add pagination

			return jsonify([listing.as_dict for listing in listings])
		
		options: dict[str, str | int | list[str]] = request.json
				
		name_filter: str = options.get("name")
		isbn_filter: str = options.get("isbn")
		location_filters: list[str] = options.get("locations", [])
		status_filter: int = options.get("status")
		usage_filter: int = options.get("usage")
		poster_id: str = options.get("posterID")
		page_num: int = options.get("page", 0)

		if isbnlib.is_isbn10(isbn_filter):
			isbn_filter = isbnlib.to_isbn13(isbn_filter)

		query = Listing.query

		if name_filter is not None:
			query = query.join(Book).filter(Book.title.ilike(f"%{name_filter}%")).reset_joinpoint()

		if isbn_filter is not None:
			query = query.filter(Listing.book_id.ilike(f"%{isbn_filter}%"))

		if status_filter is not None:
			query = query.filter(Listing.status == status_filter)

		if usage_filter is not None:
			query = query.filter(Listing.usage_level == usage_filter)

		if poster_id is not None:
			query = query.filter(Listing.author_id == poster_id)

		def filter_pickup_loc(listing: Listing, targets: list[str]): # NOTE: this is kind of slow, maybe fix sometime before prod?
			for target in targets:
				for location in listing.pickup_locations:
					if re.match(f".*{target.lower()}.*", location.lower()): return True

			return False
		
		if len(location_filters) == 0:
			filtered = query.order_by(Listing.id).offset(page_num*LISTINGS_PER_PAGE).limit(LISTINGS_PER_PAGE).all()
		else:
			filtered: list[Listing] = [listing for listing in query.all() if filter_pickup_loc(listing, location_filters)][page_num*LISTINGS_PER_PAGE:(page_num+1)*LISTINGS_PER_PAGE]

		return jsonify([listing.as_dict for listing in filtered])

	@app.route("/api/internal/get-open-reqs")
	@auth.require_user
	def getopenreqs_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		requests = PreRequest.get_all()

		return jsonify([request.as_dict for request in requests])

	@app.route("/api/internal/get-books")
	@auth.require_user
	def getbooks_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN
		
		books = Book.get_all()
				
		return jsonify([book.as_dict for book in books])
	
	@app.route("/api/internal/add-listing", methods=["POST"])
	@auth.require_user
	def addlisting_internal():
		try: author = ensure_user()
		except PermissionError: return FORBIDDEN
		get = request.json.get

		book_id = get("bookID")
		notes = get("notes")
		pickup_locations = get("pickupLocations")
		usage_level = get("usageLevel")

		if (type(usage_level) is not int) or not (0 <= usage_level <= 2): return BAD_REQUEST
		
		if (type(notes) is not str): return BAD_REQUEST
		
		if (type(pickup_locations) is not list) or any(type(loc) is not str for loc in pickup_locations): return BAD_REQUEST

		if (type(book_id) is not str): return BAD_REQUEST

		if Book.by_id(book_id) is None: return BAD_REQUEST

		new_listing = Listing(
			book_id=book_id,
			notes=notes,
			usage_level=usage_level,
			author_id=author.id,
			pickup_locations=[loc.strip() for loc in pickup_locations]
		)

		author.stats.listings_made += 1

		flag_modified(author, "stats") # ensure stats is updated in db
		
		db_add(new_listing)

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/internal/update-listing", methods=["POST"])
	@auth.require_user
	def updatelisting_internal():
		try: author = ensure_user()
		except PermissionError: return FORBIDDEN
		get = request.json.get

		listing_id = get("listingID")

		if type(listing_id) is not str: return BAD_REQUEST

		listing: Listing = Listing.by_id(listing_id)
		
		if listing is None: return BAD_REQUEST
		if listing.author_id != author.id: return FORBIDDEN
		if listing.status != Listing.Status.AVAILABLE: return BAD_REQUEST

		notes = get("notes", listing.notes)
		pickup_locations = get("pickupLocations", listing.pickup_locations)
		usage_level = get("usageLevel", listing.usage_level)

		if (type(usage_level) is not int) or not (0 <= usage_level <= 2): return BAD_REQUEST
		
		if (type(notes) is not str): return BAD_REQUEST
		
		if (type(pickup_locations) is not list) or any(type(loc) is not str for loc in pickup_locations): return BAD_REQUEST

		# update listing info
		listing.notes = notes
		listing.usage_level = usage_level
		listing.pickup_locations = pickup_locations

		db.session.commit()

		return RESP_OK

	@app.route("/api/internal/add-pre-req", methods=["POST"])
	@auth.require_user
	def addprereq_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		get = request.json.get

		book_id = get("bookID")
		author_id = get("authorID")
		preferred_pickup_locations = get("prefPickupLocations")

		
		if (type(preferred_pickup_locations) is not list) or any(type(loc) is not str for loc in preferred_pickup_locations): return BAD_REQUEST

		if (type(book_id) is not str) or (type(author_id) is not str): return BAD_REQUEST

		Book.ensure_in_db(book_id)
		author = User.by_id(author_id)

		if author is None: return BAD_REQUEST

		req = PreRequest(
			book_id=book_id,
			author_id=author_id
		)

		req.preferred_pickup_locations = preferred_pickup_locations

		db_add(req)
		return RESP_OK

	@app.route("/api/internal/rem-listing")
	@auth.require_user
	def remlisting_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str: return BAD_REQUEST
		
		listing_query: Listing = Listing.query.filter(Listing.id == listing_id)

		listing = listing_query.first()

		if (listing.status != Listing.Status.AVAILABLE): return BAD_REQUEST
		
		if (listing.author_id != user.id): return FORBIDDEN

		user.stats.listings_made -= 1
		
		flag_modified(user, "stats") # ensure stats is updated in db

		listing_query.delete()
		db.session.commit()

		return RESP_OK


	@app.route("/api/internal/rem-pre-req")
	@auth.require_user
	def remprereq_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		req_id = request.args.get("id")

		if type(req_id) is not str: return BAD_REQUEST
		
		req: PreRequest = PreRequest.query.filter(PreRequest.id == req_id)

		if req.creator_id != user.id: return FORBIDDEN
		
		req.delete()
		db.session.commit()

		return RESP_OK

	@app.route("/api/internal/add-book")
	@auth.require_user
	def addbook_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		isbn = request.args.get("isbn")

		if type(isbn) is not str: return BAD_REQUEST
		if not isbn.isdigit(): return BAD_REQUEST
		
		try: return jsonify(Book.ensure_in_db(isbn).as_dict)
		except JSONDecodeError: return BAD_REQUEST
	
	# requesting existing listings
	@app.route("/api/internal/req-listing")
	@auth.require_user
	def reqlisting_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str: return BAD_REQUEST

		listing: Listing = Listing.query.filter(Listing.id == listing_id).first()

		if listing is None: return BAD_REQUEST
		
		if listing.is_requested and listing.requester_id != current_user.user_id: return BAD_REQUEST
		if listing.author_id == current_user.user_id: return BAD_REQUEST

		listing.status = Listing.Status.REQUESTED
		listing.requester_id = current_user.user_id

		db.session.commit()
		return RESP_OK

	@app.route("/api/internal/fulfill-req")
	@auth.require_user
	def fulfilllisting_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str: return BAD_REQUEST

		listing: Listing = Listing.by_id(listing_id)

		if listing is None: return BAD_REQUEST

		if listing.author_id != current_user.user_id: return FORBIDDEN
		if listing.status != Listing.Status.REQUESTED: return BAD_REQUEST

		listing.status = Listing.Status.TAKEN
		listing.author.stats.books_given += 1
		listing.requester.stats.books_recieved += 1

		flag_modified(listing.author, "stats") # ensure stats is updated in db
		flag_modified(listing.requester, "stats")


		db.session.commit()
		return RESP_OK
	
	@app.route("/api/internal/reject-listing-req")
	@auth.require_user
	def rejectlistingreq_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str: return BAD_REQUEST

		listing: Listing = Listing.query.filter(Listing.id == listing_id).first()

		if listing is None: return BAD_REQUEST

		if listing.status != Listing.Status.REQUESTED: return BAD_REQUEST
		if listing.author_id != current_user.user_id and listing.requester_id != current_user.user_id: return FORBIDDEN

		listing.status = Listing.Status.AVAILABLE
		listing.requester_id = None

		db.session.commit()
		return RESP_OK

def init_db_api():	
	global User, Listing, Book, PreRequest, query_by_id, query_all_of, ensure_user, db_add

	def ensure_user() -> "User":		
		user = query_by_id(User, current_user.user_id)

		if user is None:
			if not current_user.user.email.endswith("@regis.org") and (current_user.user.email not in secret_keys.EMAIL_WHITELIST):
				auth.delete_user(current_user.user_id)
				raise PermissionError()

			user = User(
				id=current_user.user_id,
				first_name=current_user.user.first_name,
				last_name=current_user.user.last_name,
				email=current_user.user.email,
				username=current_user.user.username
			)

			db.session.add(user)

			db.session.commit()

		return user
	
		
	def db_add(model):
		db.session.add(model)
		db.session.commit()

	def query_by_id(model_type: type[T], model_id: str) -> T: #I think  this is a beautiful line of code
		return db.session.execute(
			db.select(model_type).where(model_type.id == model_id)
		).scalar()
	
	def query_all_of(model_type: type[T]) -> list[T]:
		return list(
			db.session.execute(
				db.select(model_type)
			).scalars().all()
		)
	
	class User(db.Model):
		@dataclass
		class Stats:
			listings_made: int = field(default=0)
			books_given: int = field(default=0)
			books_recieved: int = field(default=0)

		__tablename__ = "users"
		
		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False)
		first_name: str = db.Column(db.String, nullable=False)
		last_name: str = db.Column(db.String, nullable=False)
		username: str = db.Column(db.String, nullable=False)
		email: str = db.Column(db.String, unique=True, nullable=False)
		listings: Mapped[list["Listing"]] = db.relationship("Listing", backref="author", lazy=True)
		requests: Mapped[list["PreRequest"]] = db.relationship("PreRequest", backref="creator", lazy=True)
		stats: Stats = db.Column(db.PickleType, nullable=False, default=Stats)

		@staticmethod
		def by_id(user_id: str):
			return query_by_id(User, user_id)
		
		@staticmethod
		def get_all():
			return query_all_of(User)
		
		@property
		def as_dict(self) -> dict:
			return {
				"id": self.id,
				"firstName": self.first_name,
				"lastName": self.last_name,
				"username": self.username,
				"email": self.email,
				"stats": {
					"listingsMade": self.stats.listings_made,
					"booksGiven": self.stats.books_given,
					"booksReceived": self.stats.books_recieved,
				}
			}

	class Listing(db.Model):
		class UsageLevel:
			NEW = 0
			LIGHT = 1
			USED = 2
		
		class Status:
			AVAILABLE = 0
			REQUESTED = 1
			TAKEN = 2
		
		class Class:
			FRESHMAN = 0
			SOPHOMORE = 1
			JUNIOR = 2
			SENIOR = 3

		class SubjectArea:
			ART = 0
			MUSIC = 1
			SCIENCE = 2
			MATH = 3
			HISTORY = 4
			ENGLISH = 5
			CS = 6
			THEOLOGY = 7
			FRENCH = 8
			SPANISH = 9
			GERMAN = 10
			LATIN = 11
			CHINESE = 12
			OTHER = 13



		__tablename__ = "listings"

		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False, default=genid.genid)
		book_id: Mapped[str] = db.Column(db.String, db.ForeignKey('books.id', onupdate="CASCADE"))
		usage_level: int = db.Column(db.Integer, nullable=False)
		notes: str = db.Column(db.String, nullable=False)
		status: int = db.Column(db.Integer, nullable=False, default=Status.AVAILABLE)
		pickup_locations: list[str] = db.Column(db.PickleType, nullable=False)
		author_id: Mapped[str] = db.Column(db.String, db.ForeignKey('users.id'))
		requester_id: Mapped[str] = db.Column(db.String, default=None)

		@property
		def as_dict(self) -> dict:
			return {
				"id": self.id,
				"bookID": self.book_id,
				"usageLevel": self.usage_level,
				"notes": self.notes,
				"status": self.status,
				"pickupLocations": self.pickup_locations,
				"authorID": self.author_id,
				"requesterID": self.requester_id
			}
		
		@property
		def creator(self) -> User: return self.author
		
		@property
		def poster(self) -> User: return self.author

		@property
		def is_requested(self) -> bool:
			return self.status != Listing.Status.AVAILABLE

		@property
		def requester(self) -> User:
			if self.requester_id is None: return None
			return User.by_id(self.requester_id)

		@staticmethod
		def by_id(listing_id: str):
			return query_by_id(Listing, listing_id)
		
		@staticmethod
		def get_all():
			return query_all_of(Listing)

	class PreRequest(db.Model):
		class Status:
			OPEN = 0
			ATTACHED = 1
			FULFILLED = 2

		__tablename__ = "prerequests"

		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False, default=genid.genid)
		book_id: Mapped[str] = db.Column(db.String, db.ForeignKey('books.id'))
		preferred_pickup_locations: list[str] = db.Column(db.PickleType, nullable=False, default=[])
		creator_id: Mapped[str] = db.Column(db.String, db.ForeignKey('users.id'))
		status: int = db.Column(db.Integer, nullable=False, default=0)
		attached_listing_id: Mapped[str] = db.Column(db.String, default=None)

		@property
		def requester(self): return self.creator

		@property
		def as_dict(self) -> dict:
			return {
				"id": self.id,
				"bookID": self.book_id,
				"preferredPickupLocations": self.preferred_pickup_locations,
				"creatorID": self.creator_id,
				"status": self.status,
				"attachedListingID": self.attached_listing_id
			}
		
		@property
		def attached_listing(self) -> Listing:
			if self.attached_listing_id is None: return None
			return Listing.by_id(self.attached_listing_id)
		
		@property
		def is_open(self) -> bool:
			return self.status == PreRequest.Status.OPEN

		@staticmethod
		def by_id(listing_id: str):
			return query_by_id(PreRequest, listing_id)
		
		@staticmethod
		def get_all():
			return query_all_of(PreRequest)

	class Book(db.Model):
		__tablename__ = "books"

		# same as ISBN
		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False)
		listings: Mapped[list[Listing]] = db.relationship("Listing", backref="book", lazy=True)
		open_requests: Mapped[list[PreRequest]] = db.relationship("PreRequest", backref="book", lazy=True)
		title: str = db.Column(db.String, nullable=False)
		author: str = db.Column(db.String, nullable=False)
		publisher: str = db.Column(db.String, nullable=False)
		publish_date: str = db.Column(db.String, nullable=False)
		cover_image_url: str = db.Column(db.String, nullable=False)

		@property
		def isbn(self): return self.id

		@property
		def as_dict(self) -> dict:
			return {
				"id": self.id,
				"listings": [listing.id for listing in self.listings],
				"title": self.title,
				"author": self.author,
				"publisher": self.publisher,
				"publishDate": self.publish_date,
				"isbn": self.isbn,
				"coverImageURL": self.cover_image_url
			}
			
		@staticmethod
		def by_id(book_id: str):
			if isbnlib.is_isbn10(book_id):
				book_id = isbnlib.to_isbn13(book_id)

			return query_by_id(Book, book_id)
		
		@staticmethod
		def get_all(): return query_all_of(Book)

		@staticmethod
		def ensure_in_db(isbn: str) -> "Book":
			already = Book.by_id(isbn)

			if already is None:
				book = Book.from_isbn(isbn)
				db_add(book)
				return book
			
			return already

		@staticmethod
		def from_isbn(isbn: str) -> "Book": # TODO: add validation for isbns			
			if isbnlib.is_isbn10(isbn):
				isbn = isbnlib.to_isbn13(isbn)
		
			book_info = httpx.get(f"https://openlibrary.org/isbn/{isbn}.json", follow_redirects=True).json()

			work_path: str = book_info["works"][0]["key"]

			work_info = httpx.get(f"https://openlibrary.org{work_path}.json", follow_redirects=True).json()

			author_path: str = work_info["authors"][0]["author"]["key"]

			author: str = httpx.get(f"https://openlibrary.org{author_path}.json", follow_redirects=True).json()["name"]

			# first try to get cover from google, then openlib, then give up
			google_info = httpx.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}", follow_redirects=True).json()
			
			try: cover_url = google_info["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
			except KeyError:
				cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

				if httpx.get(cover_url, follow_redirects=True).is_error:
					cover_url = "<no-url>"

			return Book(
				id=isbn,
				title=work_info["title"],
				author=author,
				publisher=book_info["publishers"][0],
				publish_date=book_info["publish_date"],
				cover_image_url=cover_url
			)
		
def reigster_404_handler():
	@app.errorhandler(404)
	def not_found(e):
		return render_template("404.html"), 404