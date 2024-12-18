import app as server

app = server.app

server.webpy_setup(app)

with app.app_context():
	app.sqlalchemy.db.create_all()

	# Any default initialization can go here