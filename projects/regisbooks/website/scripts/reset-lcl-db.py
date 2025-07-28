import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import app, webpy_setup

webpy_setup(app)

with app.app_context():
	app.sqlalchemy.db.drop_all()
	app.sqlalchemy.db.create_all()