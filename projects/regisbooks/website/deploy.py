from alembic import op
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

	with op.batch_alter_table('users') as batch_op:
		batch_op.drop_constraint('users_first_name_key', type_='unique')
		batch_op.drop_constraint('users_last_name_key', type_='unique')
		batch_op.drop_constraint('users_username_key', type_='unique')

print("Setup complete, starting server...")

serve(app, host=config["host"], port=config["port"], threads=8)