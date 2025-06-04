from sqlalchemy import text
from waitress import serve
from app import app, webpy_setup
from json import load
from webpy.fs_routes import parse_fs_routes

with open("config.json", 'r') as f:
	config = load(f)

webpy_setup(app)
parse_fs_routes(app, "root", {}, {})

with app.app_context():
	app.sqlalchemy.db.create_all()

	# with app.sqlalchemy.db.engine.connect() as conn:
	# 	conn.execute(text("ALTER TABLE users DROP CONSTRAINT users_first_name_key;"))
	# 	conn.execute(text("ALTER TABLE users DROP CONSTRAINT users_last_name_key;"))
	# 	conn.execute(text("ALTER TABLE users DROP CONSTRAINT users_username_key;")) 	
	# 	conn.commit()

print("Setup complete, starting server...")

serve(app, host=config["host"], port=config["port"], threads=8)