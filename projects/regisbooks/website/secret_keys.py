import os
from sys import path
import dotenv
from sqlalchemy import exists

ENV_PATH = "instance/.env"

if os.path.exists(ENV_PATH): dotenv.load_dotenv(ENV_PATH)

APP_SECRET_KEY = os.getenv("REGISBOOKS_SECRET_KEY")
AUTH_URL = os.getenv("REGISBOOKS_AUTH_URL")
AUTH_API_KEY = os.getenv("REGISBOOKS_AUTH_API_KEY")