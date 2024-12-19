from dataclasses import dataclass, field
from http.client import BAD_REQUEST
from json import JSONDecodeError
from typing import TypeVar, TypedDict
from flask import jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
import httpx
from sqlalchemy import null
from traitlets import default
from webpy import App
from propelauth_flask import init_auth, current_user
from propelauth_flask.user import LoggedInUser
from sqlalchemy.orm import Mapped

import secret_keys
import genid

current_user: LoggedInUser
T = TypeVar('T')

app = App(__name__, template_folder="html")

BAD_REQUEST = Response(status=400)
RESP_OK = Response(status=200)

def webpy_setup(app: App):
	global auth, db

	app.debug = True

	auth = init_auth(secret_keys.AUTH_URL, secret_keys.AUTH_API_KEY)

	db = app.sqlalchemy.init("sqlite:///database.db")

	init_db_api()
	register_internal_api_routes()

def register_external_api_routes(): pass # TODO, also have an efficient system to manage verification of API keys (research) |||| extract & reuse logic from register_internal_api_routes

def register_internal_api_routes():
	@app.route("/api/internal/get-user")
	@auth.require_user
	def getuser_internal():
		ensure_user()

		user = User.by_id(request.args.get("id"))

		if user is None: return BAD_REQUEST
		return jsonify(user.as_dict)
	
	@app.route("/api/internal/get-listing")
	@auth.require_user
	def getlisting_internal():
		ensure_user()

		listing = Listing.by_id(request.args.get("id"))

		if listing is None: return BAD_REQUEST
		return jsonify(listing.as_dict)
	
	@app.route("/api/internal/get-book")
	@auth.require_user
	def getbook_internal():
		ensure_user()

		book = Book.by_id(request.args.get("id"))

		if book is None: return BAD_REQUEST

		return jsonify(book.as_dict)

	@app.route("/api/internal/get-listings")
	@auth.require_user
	def getlistings_internal():
		ensure_user()

		listings = Listing.get_all()

		return jsonify([listing.as_dict for listing in listings])

	@app.route("/api/internal/get-open-reqs")
	@auth.require_user
	def getopenreqs_internal():
		ensure_user()

		requests = PreRequest.get_all()

		return jsonify([request.as_dict for request in requests])

	@app.route("/api/internal/get-books")
	@auth.require_user
	def getbooks_internal():
		ensure_user()
		
		books = Book.get_all()
				
		return jsonify([book.as_dict for book in books])
	
	@app.route("/api/internal/add-listing", methods=["POST"])
	@auth.require_user
	def addlisting_internal():
		author = ensure_user()
		get = request.json.get

		book_id = get("bookID")
		notes = get("notes")
		pickup_locations = get("pickupLocations")
		usage_level = get("usageLevel")

		if (type(usage_level) is not int) or not (0 <= usage_level <= 2): return BAD_REQUEST
		
		if (type(notes) is not str): return BAD_REQUEST
		
		if (type(pickup_locations) is not list) or any(type(loc) is not str for loc in pickup_locations): return BAD_REQUEST

		if (type(book_id) is not str): return BAD_REQUEST

		Book.ensure_in_db(book_id)

		new_listing = Listing(
			book_id=book_id,
			notes=notes,
			usage_level=usage_level,
			author_id=author.id,
			pickup_locations=pickup_locations
		)

		db_add(new_listing)

		return RESP_OK

	@app.route("/api/internal/add-pre-req", methods=["POST"])
	@auth.require_user
	def addprereq_internal():
		ensure_user()

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
		ensure_user()

		listing_id = request.args.get("id")

		if type(listing_id) is not str: return BAD_REQUEST
		
		Listing.query.filter(Listing.id == listing_id).delete()

		return RESP_OK


	@app.route("/api/internal/rem-pre-req")
	@auth.require_user
	def remprereq_internal():
		ensure_user()

		req_id = request.args.get("id")

		if type(req_id) is not str: return BAD_REQUEST
		
		PreRequest.query.filter(PreRequest.id == req_id).delete()

		return RESP_OK

	@app.route("/api/internal/add-book")
	@auth.require_user
	def addbook_internal():
		ensure_user()

		isbn = request.args.get("isbn")

		if type(isbn) is not str: return BAD_REQUEST
		
		try: return jsonify(Book.ensure_in_db(isbn).as_dict)
		except JSONDecodeError: return BAD_REQUEST

	@app.route("/api/internal/rem-book")
	@auth.require_user
	def rembook_internal():
		ensure_user()

		book_id = request.args.get("id")

		if type(book_id) is not str: return BAD_REQUEST

		Book.query.filter(Book.id == book_id).delete()

		return RESP_OK
	
def init_db_api():
	global User, Listing, Book, PreRequest, query_by_id, query_all_of, ensure_user, db_add

	def ensure_user() -> "User":		
		user = query_by_id(User, current_user.user_id)

		if user is None:
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
		first_name: str = db.Column(db.String, unique=True, nullable=False)
		last_name: str = db.Column(db.String, unique=True, nullable=False)
		username: str = db.Column(db.String, unique=True, nullable=False)
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
				"listings": self.listings,
				"stats": {
					"listingsMade": self.stats.listings_made,
					"booksGiven": self.stats.books_given,
					"booksRecieved": self.stats.books_recieved,
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
		
		class Classes: # TODO: decide if this should be in listing or books
			FRESHMAN = 0
			SOPHOMORE = 1
			JUNIOR = 2
			SENIOR = 3

		__tablename__ = "listings"

		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False, default=genid.genid)
		book_id: Mapped[str] = db.Column(db.String, db.ForeignKey('books.id'))
		usage_level: int = db.Column(db.Integer, nullable=False)
		notes: str = db.Column(db.String, nullable=False)
		status: int = db.Column(db.Integer, nullable=False, default=Status.AVAILABLE)
		pickup_locations: list[str] = db.Column(db.PickleType, nullable=False)
		author_id: Mapped[str] = db.Column(db.String, db.ForeignKey('users.id'))
		
		@property
		def as_dict(self) -> dict:
			return {
				"id": self.id,
				"bookID": self.book_id,
				"usageLevel": self.usage_level,
				"notes": self.notes,
				"status": self.status,
				"pickupLocations": self.pickup_locations,
				"authorID": self.author_id
			}
		
		@property
		def creator(self) -> User: return self.author
		
		@property
		def poster(self) -> User: return self.author

		@staticmethod
		def by_id(listing_id: str):
			return query_by_id(Listing, listing_id)
		
		@staticmethod
		def get_all():
			return query_all_of(Listing)
		
	class PreRequest(db.Model):
		__tablename__ = "prerequests"

		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False, default=genid.genid)
		book_id: Mapped[str] = db.Column(db.String, db.ForeignKey('books.id'))
		preferred_pickup_locations: list[str] = db.Column(db.PickleType, nullable=False, default=[])
		creator_id: Mapped[str] = db.Column(db.String, db.ForeignKey('users.id'))

		@property
		def requester(self): return self.creator

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
		def from_isbn(isbn: str) -> "Book":
			info = httpx.get(f"https://openlibrary.org/isbn/{isbn}.json", follow_redirects=True).json()
			author_path: str = info["authors"][0]["key"]

			author: str = httpx.get(f"https://openlibrary.org{author_path}.json", follow_redirects=True).json()["name"]

			# get cover from google
			google_info = httpx.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}", follow_redirects=True).json()
			

			return Book(
				id=isbn,
				title=info["title"],
				author=author,
				publisher=info["publishers"][0],
				publish_date=info["publish_date"],
				cover_image_url=google_info["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
			)