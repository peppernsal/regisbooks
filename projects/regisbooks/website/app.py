import re
import hashlib
import genid
import httpx
import isbnlib
import secret_keys
import badges
from logsetup import logger
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
AURA_PER_LISTING = 1
AURA_PER_BOOK_GIVEN = 3

def webpy_setup(app: App):
	global auth, db

	if app.debug: # debug/test mode set by webpy
		auth = init_auth(secret_keys.TEST_REGISBOOKS_AUTH_URL, secret_keys.TEST_REGISBOOKS_AUTH_API_KEY)
	else:	
		auth = init_auth(secret_keys.AUTH_URL, secret_keys.AUTH_API_KEY)

	db = app.sqlalchemy.init(secret_keys.DB_URI)

	init_db_api()
	register_internal_api_routes()
	register_external_api_routes()
	reigster_404_handler()


def register_external_api_routes(): # TODO, also have an efficient system to manage verification of API keys (research) |||| extract & reuse logic from register_internal_api_routes
	def check_admin_key(key: str) -> bool:
		key_hash = hashlib.sha512(key.encode()).hexdigest()

		return key_hash == secret_keys.ADMIN_KEY_HASH
	
	@app.route("/api/external/rem-book", methods=["POST"])
	def rembook_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		book_id = request.json.get("bookID")

		if type(book_id) is not str: return BAD_REQUEST

		query = Book.query.filter(Book.id == book_id)

		book: Book = query.first()

		if book is None: return BAD_REQUEST

		for listing in book.listings:
			if listing.book_id == book_id:
				return BAD_REQUEST # cannot delete book with existing listings

		query.delete()

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/rem-listing", methods=["POST"])
	def remlisting_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		listing_id = request.json.get("listingID")

		if type(listing_id) is not str: return BAD_REQUEST

		listing_query = Listing.query.filter(Listing.id == listing_id)

		listing: Listing = listing_query.first()

		if listing is None: return BAD_REQUEST

		listing.author.stats.listings_made -= 1
		listing.author.aura -= AURA_PER_LISTING

		flag_modified(listing.author, "stats") # ensure stats is updated in db

		listing_query.delete()

		db.session.commit()

		return RESP_OK

	@app.route("/api/external/clear-taken-listings", methods=["POST"])
	def cleartakenlistings_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		Listing.query.filter(Listing.status == Listing.Status.TAKEN).delete()

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/get-impact")
	def getimpact_external(): # not sensitive, no authentication needed
		given = Listing.query.filter(Listing.status == Listing.Status.TAKEN).count()
		otw = Listing.query.filter(Listing.status == Listing.Status.REQUESTED).count()
		available = Listing.query.filter(Listing.status == Listing.Status.AVAILABLE).count()

		return jsonify({
			"givenAway": given,
			"requested": otw,
			"available": available
		})

	@app.route("/api/external/reset-stats", methods=["POST"])
	def resetstats_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		user_id = request.json.get("userID")

		if type(user_id) is not str: return BAD_REQUEST

		user = User.by_id(user_id)

		user.stats = User.Stats()
		user.aura = 0
		flag_modified(user, "stats")

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/rem-request", methods=["POST"])
	def remrequest_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		listing_id = request.json.get("listingID")

		if type(listing_id) is not str: return BAD_REQUEST

		listing = Listing.by_id(listing_id)

		if listing is None: return BAD_REQUEST
		if listing.status != Listing.Status.REQUESTED: return BAD_REQUEST

		listing.status = Listing.Status.AVAILABLE
		listing.requester_id = None

		db.session.commit()

		return RESP_OK

	@app.route("/api/external/normalize-aura", methods=["POST"])
	def normalizeaura_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		users = User.get_all()

		for user in users:
			user.aura = AURA_PER_LISTING*user.stats.listings_made + AURA_PER_BOOK_GIVEN*user.stats.books_given

		db.session.commit()

		return RESP_OK
	
	@app.route("/api/external/normalize-badges", methods=["POST"])
	def normalizebadges_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		users = User.get_all()

		for user in users:
			if user.badges is None:
				user.badges = []

		db.session.commit()

		return RESP_OK

	@app.route("/api/external/set-eng-flag", methods=["POST"])
	def setengflag_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		listing_id = request.json.get("listingID")

		if type(listing_id) is not str: return BAD_REQUEST

		listing = Listing.by_id(listing_id)

		if listing is None: return BAD_REQUEST

		listing.is_annotated_english_book = True

		db.session.commit()

		return RESP_OK

	@app.route("/api/external/set-listing-status", methods=["POST"])
	def setlistingstatus_external():
		admin_key = request.json.get("key")

		if not check_admin_key(admin_key): return FORBIDDEN

		listing_id = request.json.get("listingID")
		status = request.json.get("status")

		if type(listing_id) is not str: return BAD_REQUEST
		if type(status) is not int or not (Listing.Status.AVAILABLE <= status <= Listing.Status.TAKEN): return BAD_REQUEST

		listing = Listing.by_id(listing_id)

		if listing is None: return BAD_REQUEST

		listing.status = status

		db.session.commit()

		return RESP_OK		

def register_internal_api_routes():
	@app.route("/api/internal/get-user")
	@auth.require_user
	def getuser_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		user_id = request.args.get("id")
		fallback_id = request.args.get("fallbackID")
		user = User.by_id(user_id, fallback_id)

		if user is None:
			logger.warning(f"Failure: get-user - User not found. user_id={user_id}, fallback_id={fallback_id}")
			return BAD_REQUEST
		logger.info(f"Success: get-user for user_id={user.id}")
		return jsonify(user.as_dict)
	
	# for foreign profile viewing and badge achievement notification
	@app.route("/api/internal/get-updated-achieved-badges")
	@auth.require_user
	def getupdatedbadges_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		user_id = request.args.get("id", "")
		user = User.by_id(user_id)

		if user is None:
			logger.warning(f"Failure: get-updated-achieved-badges - User not found. user_id={user_id}")
			return BAD_REQUEST
		
		achieved_badges = [badge for badge in badges.badges if badge.achieved(user, Listing, Book)]

		logger.info(f"Success: get-updated-achieved-badges for user_id={user_id}, badges_count={len(achieved_badges)}")
		return jsonify([badge.as_dict for badge in achieved_badges])
	
	# supports badge achievement notification, can and should only be called from the current user
	@app.route("/api/internal/update-achieved-badges")
	@auth.require_user
	def updateachievedbadges_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		user.badges = [badge.name for badge in badges.badges if badge.achieved(user, Listing, Book)]
		db.session.commit()

		logger.info(f"Success: update-achieved-badges for user_id={user.id}, badges_count={len(user.badges)}")
		return RESP_OK
	
	@app.route("/api/internal/update-phone-number")
	@auth.require_user
	def updatephonenumber_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		phone_number: str | None = request.args.get("number", "")
		if phone_number == "null":
			user.phone_number = None
			db.session.commit()

			logger.info(f"Success: update-phone-number (removed) for user_id={user.id}")

			return RESP_OK
		
		if (type(phone_number) is not str) or (len(phone_number) != 10) or (not phone_number.isdigit()):
			logger.warning(f"Failure: update-phone-number - Invalid phone number. user_id={user.id}, value={phone_number}")
			return BAD_REQUEST
		
		user.phone_number = phone_number
		db.session.commit()

		logger.info(f"Success: update-phone-number for user_id={user.id}, phone_number={phone_number}")

		return RESP_OK

	@app.route("/api/internal/get-users")
	@auth.require_user
	def getusers_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		users = User.get_all()

		logger.info(f"Success: get-users, count={len(users)}")

		return jsonify([user.id for user in users])
	
	@app.route("/api/internal/get-leaderboard")
	@auth.require_user
	def getleaderboard_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		leaders: list[User] = User.query.order_by(User.aura.desc()).limit(10).all()

		logger.info(f"Success: get-leaderboard, count={len(leaders)}")

		return jsonify([
			leader.as_dict for leader in leaders
		])

	@app.route("/api/internal/get-listing")
	@auth.require_user
	def getlisting_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")
		listing = Listing.by_id(listing_id)

		if listing is None:
			logger.warning(f"Failure: get-listing - Listing not found. listing_id={listing_id}")
			return BAD_REQUEST
		
		logger.info(f"Success: get-listing for listing_id={listing_id}")

		return jsonify(listing.as_dict)
	
	@app.route("/api/internal/get-book")
	@auth.require_user
	def getbook_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		book_id = request.args.get("id")
		book = Book.by_id(book_id)

		if book is None:
			logger.warning(f"Failure: get-book - Book not found. book_id={book_id}")
			return BAD_REQUEST
		
		logger.info(f"Success: get-book for book_id={book_id}")

		return jsonify(book.as_dict)

	@app.route("/api/internal/get-listings", methods=["GET", "POST"])
	@auth.require_user
	def getlistings_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN
		
		options: dict[str, str | int | list[str]] = request.json
				
		name_filter: str = options.get("name")
		isbn_filter: str = options.get("isbn")
		location_filters: list[str] = options.get("locations", [])
		status_filter: int = options.get("status")
		usage_filter: int = options.get("usage")
		poster_id: str = options.get("posterID")
		page_num: int = options.get("page", 0)

		query = Listing.query

		if name_filter is not None:
			query = query.join(Book).filter(Book.title.ilike(f"%{name_filter}%")).reset_joinpoint()

		if isbn_filter is not None:
			if isbnlib.is_isbn10(isbn_filter):
				isbn_filter = isbnlib.to_isbn13(isbn_filter)
			query = query.filter(Listing.book_id.ilike(f"%{isbn_filter}%"))

		if status_filter is not None:
			query = query.filter(Listing.status == status_filter)

		if usage_filter is not None:
			query = query.filter(Listing.usage_level == usage_filter)

		if poster_id is not None: # this necessitates the frontend sending the DB id of the user
			query = query.filter(Listing.author_id == poster_id)

		query = query.filter(Listing.status != Listing.Status.TAKEN) # compliance with decision for #14

		def filter_pickup_loc(listing: Listing, targets: list[str]): # NOTE: this is kind of slow, maybe fix sometime before prod?
			for target in targets:
				for location in listing.pickup_locations:
					if re.match(f".*{target.lower()}.*", location.lower()): return True

			return False
		
		if len(location_filters) == 0:
			total_count = query.count()
			filtered = query.order_by(Listing.id).offset(page_num*LISTINGS_PER_PAGE).limit(LISTINGS_PER_PAGE).all()
		else:
			filtered_all: list[Listing] = [listing for listing in query.all() if filter_pickup_loc(listing, location_filters)]
			total_count = len(filtered_all)
			filtered  = filtered_all[page_num*LISTINGS_PER_PAGE:(page_num+1)*LISTINGS_PER_PAGE]

		logger.info(f"Success: get-listings, returned={len(filtered)}, total={total_count}, name_full={name_filter}, isbn={isbn_filter}, locations={location_filters}, status={status_filter}, usage={usage_filter}, poster_id={poster_id}, page={page_num}")

		return jsonify({ "listings": [listing.as_dict for listing in filtered], "totalCount": total_count })

	@app.route("/api/internal/get-open-reqs")
	@auth.require_user
	def getopenreqs_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		requests = PreRequest.get_all()

		logger.info(f"Success: get-open-reqs, count={len(requests)}")

		return jsonify([request.as_dict for request in requests])

	@app.route("/api/internal/get-books")
	@auth.require_user
	def getbooks_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN
		
		books = Book.get_all()
		class_filter = request.args.get("class")

		if class_filter is None:
			logger.info(f"Success: get-books, count={len(books)} (no filter)")

			return jsonify([book.as_dict for book in books])
		if not class_filter.isdigit():
			logger.warning(f"Failure: get-books - Invalid class filter. value={class_filter}")
			return BAD_REQUEST
		
		class_filter = int(class_filter)

		if class_filter == Book.Class.FRESHMAN:
			filtered_books = [book.as_dict for book in books if book.isbn in Book.Class.FRESHMAN_LIST]

			logger.info(f"Success: get-books, count={len(filtered_books)} (freshman)")

			return jsonify(filtered_books)
		elif class_filter == Book.Class.SOPHOMORE:
			filtered_books = [book.as_dict for book in books if book.isbn in Book.Class.SOPHOMORE_LIST]

			logger.info(f"Success: get-books, count={len(filtered_books)} (sophomore)")

			return jsonify(filtered_books)
		elif class_filter == Book.Class.JUNIOR:
			filtered_books = [book.as_dict for book in books if book.isbn in Book.Class.JUNIOR_LIST]

			logger.info(f"Success: get-books, count={len(filtered_books)} (junior)")

			return jsonify(filtered_books)
		elif class_filter == Book.Class.SENIOR:
			filtered_books = [book.as_dict for book in books if book.isbn in Book.Class.SENIOR_LIST]

			logger.info(f"Success: get-books, count={len(filtered_books)} (senior)")

			return jsonify(filtered_books)
		
		logger.warning(f"Failure: get-books - Unknown class filter. value={class_filter}")

		return BAD_REQUEST # unknown class filter
	
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
		english_flag = get("englishFlag")

		if (type(usage_level) is not int) or not (0 <= usage_level <= 2):
			logger.warning(f"Failure: add-listing - Invalid usage_level. author_id={author.id}, value={usage_level}")
			return BAD_REQUEST
		
		if (type(notes) is not str):
			logger.warning(f"Failure: add-listing - Invalid notes. author_id={author.id}, value={notes}")
			return BAD_REQUEST
		
		if (type(pickup_locations) is not list) or any(type(loc) is not str for loc in pickup_locations) or not (0 < len(pickup_locations) <= 5):
			logger.warning(f"Failure: add-listing - Invalid pickup_locations. author_id={author.id}, value={pickup_locations}")
			return BAD_REQUEST
		
		if (type(book_id) is not str):
			logger.warning(f"Failure: add-listing - Invalid book_id. author_id={author.id}, value={book_id}")
			return BAD_REQUEST
		
		if (type(english_flag) is not bool):
			logger.warning(f"Failure: add-listing - Invalid english_flag. author_id={author.id}, value={english_flag}")
			return BAD_REQUEST
		
		if isbnlib.is_isbn10(book_id):
			book_id = isbnlib.to_isbn13(book_id)

		if Book.by_id(book_id) is None:
			logger.warning(f"Failure: add-listing - Book not found. author_id={author.id}, book_id={book_id}")
			return BAD_REQUEST
		
		pickup_locations = [*set(pickup_locations)]
		new_listing = Listing(
			book_id=book_id,
			notes=notes,
			usage_level=usage_level,
			author_id=author.id,
			pickup_locations=[loc.strip() for loc in pickup_locations],
			is_annotated_english_book=english_flag
		)

		author.stats.listings_made += 1
		author.aura += AURA_PER_LISTING

		flag_modified(author, "stats") # ensure stats is updated in db

		db.session.add(new_listing)
		db.session.commit()

		logger.info(f"Success: add-listing for author_id={author.id}, listing_id={new_listing.id}")

		return RESP_OK
	
	@app.route("/api/internal/update-listing", methods=["POST"])
	@auth.require_user
	def updatelisting_internal():
		try: author = ensure_user()
		except PermissionError: return FORBIDDEN
		get = request.json.get

		listing_id = get("listingID")

		if type(listing_id) is not str:
			logger.warning(f"Failure: update-listing - Invalid listing_id. author_id={author.id}, value={listing_id}")
			return BAD_REQUEST
		
		listing: Listing = Listing.by_id(listing_id)

		if listing is None:
			logger.warning(f"Failure: update-listing - Listing not found. author_id={author.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.author_id != author.id:
			logger.warning(f"Failure: update-listing - Forbidden. author_id={author.id}, listing_id={listing_id}")
			return FORBIDDEN
		
		if listing.status != Listing.Status.AVAILABLE:
			logger.warning(f"Failure: update-listing - Listing not available. author_id={author.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		notes = get("notes", listing.notes)
		pickup_locations = get("pickupLocations", listing.pickup_locations)
		usage_level = get("usageLevel", listing.usage_level)
		english_flag = get("englishFlag", listing.is_annotated_english_book)

		if (type(usage_level) is not int) or not (0 <= usage_level <= 2):
			logger.warning(f"Failure: update-listing - Invalid usage_level. author_id={author.id}, listing_id={listing_id}, value={usage_level}")
			return BAD_REQUEST
		
		if (type(notes) is not str):
			logger.warning(f"Failure: update-listing - Invalid notes. author_id={author.id}, listing_id={listing_id}, value={notes}")
			return BAD_REQUEST
		
		if (type(english_flag) is not bool):
			logger.warning(f"Failure: update-listing - Invalid english_flag. author_id={author.id}, listing_id={listing_id}, value={english_flag}")
			return BAD_REQUEST
		
		if (type(pickup_locations) is not list) or any(type(loc) is not str for loc in pickup_locations) or not (0 < len(pickup_locations) <= 5):
			logger.warning(f"Failure: update-listing - Invalid pickup_locations. author_id={author.id}, listing_id={listing_id}, value={pickup_locations}")
			return BAD_REQUEST
		
		pickup_locations = [*set(pickup_locations)]

		# update listing info
		listing.notes = notes
		listing.usage_level = usage_level
		listing.is_annotated_english_book = english_flag
		listing.pickup_locations = pickup_locations

		db.session.commit()

		logger.info(f"Success: update-listing for author_id={author.id}, listing_id={listing_id}")

		return RESP_OK

	@app.route("/api/internal/rem-listing")
	@auth.require_user
	def remlisting_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")
		if type(listing_id) is not str:
			logger.warning(f"Failure: rem-listing - Invalid listing_id. user_id={user.id}, value={listing_id}")
			return BAD_REQUEST
		
		listing_query: Listing = Listing.query.filter(Listing.id == listing_id)
		listing = listing_query.first()

		if listing is None:
			logger.warning(f"Failure: rem-listing - Listing not found. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if (listing.status != Listing.Status.AVAILABLE):
			logger.warning(f"Failure: rem-listing - Listing not available. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if (listing.author_id != user.id):
			logger.warning(f"Failure: rem-listing - Forbidden. user_id={user.id}, listing_id={listing_id}")
			return FORBIDDEN
		
		user.stats.listings_made -= 1
		user.aura -= AURA_PER_LISTING

		flag_modified(user, "stats") # ensure stats is updated in db

		listing_query.delete()
		db.session.commit()

		logger.info(f"Success: rem-listing for user_id={user.id}, listing_id={listing_id}")

		return RESP_OK

	@app.route("/api/internal/add-book")
	@auth.require_user
	def addbook_internal():
		try: ensure_user()
		except PermissionError: return FORBIDDEN

		isbn = request.args.get("isbn")

		if type(isbn) is not str:
			logger.warning(f"Failure: add-book - Invalid isbn. value={isbn}")
			return BAD_REQUEST
		
		if not isbn.isdigit():
			logger.warning(f"Failure: add-book - Non-digit isbn. value={isbn}")
			return BAD_REQUEST
		try:
			book = Book.ensure_in_db(isbn)
			
			logger.info(f"Success: add-book for isbn={isbn}")

			return jsonify(book.as_dict)
		except JSONDecodeError:
			logger.warning(f"Failure: add-book - JSON decode error. isbn={isbn}")
			return BAD_REQUEST
	
	@app.route("/api/internal/req-listing")
	@auth.require_user
	def reqlisting_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str:
			logger.warning(f"Failure: req-listing - Invalid listing_id. user_id={user.id}, value={listing_id}")
			return BAD_REQUEST
		
		listing: Listing = Listing.by_id(listing_id)

		if listing is None:
			logger.warning(f"Failure: req-listing - Listing not found. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.is_requested and listing.requester_id != user.id:
			logger.warning(f"Failure: req-listing - Listing already requested by another user. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.author_id == user.id:
			logger.warning(f"Failure: req-listing - Author cannot request own listing. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		listing.status = Listing.Status.REQUESTED
		listing.requester_id = user.id

		db.session.commit()

		logger.info(f"Success: req-listing for user_id={user.id}, listing_id={listing_id}")

		return RESP_OK

	@app.route("/api/internal/fulfill-req")
	@auth.require_user
	def fulfilllisting_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str:
			logger.warning(f"Failure: fulfill-req - Invalid listing_id. user_id={user.id}, value={listing_id}")
			return BAD_REQUEST
		
		listing: Listing = Listing.by_id(listing_id)

		if listing is None:
			logger.warning(f"Failure: fulfill-req - Listing not found. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.author_id != user.id:
			logger.warning(f"Failure: fulfill-req - Forbidden. user_id={user.id}, listing_id={listing_id}")
			return FORBIDDEN
		
		if listing.status != Listing.Status.REQUESTED:
			logger.warning(f"Failure: fulfill-req - Listing not requested. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		listing.status = Listing.Status.TAKEN
		listing.author.stats.books_given += 1
		listing.author.aura += AURA_PER_BOOK_GIVEN

		requester = listing.requester
		requester.stats.books_received += 1

		flag_modified(listing.author, "stats") # ensure stats is updated in db
		flag_modified(requester, "stats")

		db.session.commit()

		logger.info(f"Success: fulfill-req for user_id={user.id}, listing_id={listing_id}")

		return RESP_OK
	
	@app.route("/api/internal/reject-listing-req")
	@auth.require_user
	def rejectlistingreq_internal():
		try: user = ensure_user()
		except PermissionError: return FORBIDDEN

		listing_id = request.args.get("id")

		if type(listing_id) is not str:
			logger.warning(f"Failure: reject-listing-req - Invalid listing_id. user_id={user.id}, value={listing_id}")
			return BAD_REQUEST
		
		listing: Listing = Listing.by_id(listing_id)

		if listing is None:
			logger.warning(f"Failure: reject-listing-req - Listing not found. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.status != Listing.Status.REQUESTED:
			logger.warning(f"Failure: reject-listing-req - Listing not requested. user_id={user.id}, listing_id={listing_id}")
			return BAD_REQUEST
		
		if listing.author_id != user.id and listing.requester_id != user.id:
			logger.warning(f"Failure: reject-listing-req - Forbidden. user_id={user.id}, listing_id={listing_id}")
			return FORBIDDEN
		
		listing.status = Listing.Status.AVAILABLE
		listing.requester_id = None

		db.session.commit()
		
		logger.info(f"Success: reject-listing-req for user_id={user.id}, listing_id={listing_id}")

		return RESP_OK

def init_db_api():	
	global User, Listing, Book, PreRequest, query_by_id, query_all_of, ensure_user, authoritative_id_of

	def authoritative_id_of(user: LoggedInUser) -> str:
		if user.user.legacy_user_id is not None:
			return user.user.legacy_user_id
		
		return user.user_id

	def ensure_user() -> "User":
		user = User.query.filter(
			User.id == authoritative_id_of(current_user)
		).first()
		
		if user is None:
			if not current_user.user.email.endswith("@regis.org") and (current_user.user.email not in secret_keys.EMAIL_WHITELIST):
				logger.warning(f"Rejected user {current_user.user.email} (invalid email domain)")
				auth.delete_user(current_user.user_id)
				raise PermissionError()

			user = User(
				id=authoritative_id_of(current_user),
				first_name=current_user.user.first_name,
				last_name=current_user.user.last_name,
				email=current_user.user.email,
				username=current_user.user.username,
				badges=[]
			)

			db.session.add(user)

			db.session.commit()

			logger.info(f"Added user {current_user.user.email} to db")

		return user

	def query_by_id(model_type: type[T], model_id: str) -> T: #I think  this is a beautiful line of code
		return model_type.query.filter(model_type.id == model_id).first()
	
	def query_all_of(model_type: type[T]) -> list[T]:
		return model_type.query.all()
	
	class User(db.Model):
		@dataclass
		class Stats:
			listings_made: int = field(default=0)
			books_given: int = field(default=0)
			books_received: int = field(default=0)

		__tablename__ = "users"
		
		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False)
		first_name: str = db.Column(db.String, nullable=False)
		last_name: str = db.Column(db.String, nullable=False)
		username: str = db.Column(db.String, nullable=False)
		email: str = db.Column(db.String, unique=True, nullable=False)
		listings: Mapped[list["Listing"]] = db.relationship("Listing", backref="author", lazy=True)
		requests: Mapped[list["PreRequest"]] = db.relationship("PreRequest", backref="creator", lazy=True)
		stats: Stats = db.Column(db.PickleType, nullable=False, default=Stats)
		aura: int = db.Column(db.Integer, nullable=False, default=0)
		badges: list[str] | None = db.Column(db.PickleType, nullable=True) # needed nullable=True for pre-migration compat
		phone_number: str | None = db.Column(db.String, nullable=True)

		@staticmethod
		def by_id(user_id: str, fallback_id: str = None):			
			"""THIS METHOD REQUIRES A DB ID, a new ID for a legacy user *will not work*. A new ID for a legacy user may be passed as the fallback ID"""

			res = query_by_id(User, user_id)

			if res is None and fallback_id is not None:
				return query_by_id(User, fallback_id)
			
			return res
		
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
					"booksReceived": self.stats.books_received,
				},
				"aura": self.aura,
				"badges": [badges.get(badge_name).as_dict for badge_name in self.badges],
				"phoneNumber": self.phone_number
			}

	class Listing(db.Model):
		class UsageLevel:
			LIKE_NEW = 0
			LIGHT = 1
			USED = 2
		
		class Status:
			AVAILABLE = 0
			REQUESTED = 1
			TAKEN = 2

		__tablename__ = "listings"

		id: str = db.Column(db.String, primary_key=True, unique=True, nullable=False, default=genid.genid)
		book_id: Mapped[str] = db.Column(db.String, db.ForeignKey('books.id', onupdate="CASCADE"))
		usage_level: int = db.Column(db.Integer, nullable=False)
		notes: str = db.Column(db.String, nullable=False)
		status: int = db.Column(db.Integer, nullable=False, default=Status.AVAILABLE)
		pickup_locations: list[str] = db.Column(db.PickleType, nullable=False)
		author_id: Mapped[str] = db.Column(db.String, db.ForeignKey('users.id'))
		requester_id: Mapped[str] = db.Column(db.String, default=None)
		is_annotated_english_book: bool = db.Column(db.Boolean, nullable=False, default=False)

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
				"requesterID": self.requester_id,
				"isAnnotatedEnglishBook": self.is_annotated_english_book
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
		class Class:
			FRESHMAN = 0
			SOPHOMORE = 1
			JUNIOR = 2
			SENIOR = 3

			# Yes, these constants are hardcoded like the badge system. They need to be updated statically once a year and thus have no value being in a database

			FRESHMAN_LIST = {
				"9780670921676",
				"9780205309023",
				"9780140444254",
				"9780061120060",
				"9780367513436",
				"9781319244415",
				"9780199374380",
				"9781622917457",
				"9781622911363",
				"9781622911370",
				"9781259999826",
				"9781264215393",
				"9781585102129",
				"9781585104239",
				"9781264877522"
			}

			SOPHOMORE_LIST = {
				"9780811216029",
				"9780486284996",
				"9780142437278",
				"9780316769174",
				"9781982149482",
				"9780190089528",
				"9780687646234",
				"9781622917495",
				"9781622911431",
				"9781111354183",
				"9781259999826",
				"9780156013987",
				"9781264215393",
				"9781585102327",
				"9781585102129",
				"9781585104239",
				"9781264877522"
			}

			JUNIOR_LIST = {
				"9780345806567",
				"9780743477123",
				"9781538182222",
				"9780190058241",
				"9781622911578",
				"9781622911561",
				"9781111354183",
				"9782070360215",
				"9781260120998",
				"9781585102327",
				"9780806142326",
				"9780060935061"
			}

			SENIOR_LIST = {
				"9780073534664",
				"9780195339222",
				"9780316499071",
				"9781620974551",
				"9781622911516",
				"9781622911523",
				"9782035873880",
				"9782070360024",
				"9782070362363",
				"9780865164215",
				"9783903352513",
				"9781260121001",
				"9788422698456"
			}

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

				db.session.add(book)
				db.session.commit()

				logger.info(f"Added book {isbn} to db")

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
					cover_url = "/static/images/no-cover.png"

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