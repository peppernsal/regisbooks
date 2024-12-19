import os
import app as server

app = server.app

server.webpy_setup(app)

if (os.path.exists("instance/database.db")): os.remove("instance/database.db")

with app.app_context():
	app.sqlalchemy.db.create_all()

	# Any default initialization can go here

	# TEST DATA

	# wciv = server.Book.ensure_in_db("9781111342135")

	# server.db_add(
	# 	server.Listing(
	# 		book_id=wciv.id,
	# 		usage_level=server.Listing.UsageLevel.NEW,
	# 		status=server.Listing.Status.AVAILABLE,
	# 		pub
	# 		author_id="",
	# 		notes="WCiv Euro Textbook",
	# 		pickup_locations_str="Fairfield, CT$Somerset, NJ"
	# 	)
	# )