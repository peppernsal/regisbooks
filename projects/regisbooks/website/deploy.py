from waitress import serve
from app import app, webpy_setup
from json import load
from webpy.fs_routes import parse_fs_routes

with open("config.json", 'r') as f:
	config = load(f)

webpy_setup(app)
parse_fs_routes(app, "root", {}, {})
print("Setup complete, starting server...")

serve(app, host=config["host"], port=config["port"], threads=8)