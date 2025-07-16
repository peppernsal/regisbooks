import sys
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

# change this to logging once it is set up
print("Setup complete, starting server...", file=sys.stderr)

serve(app, host=config["host"], port=config["port"], threads=8)