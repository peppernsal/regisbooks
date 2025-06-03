import os
import dotenv

ENV_PATH = "instance/.env"

if os.path.isfile(ENV_PATH): dotenv.load_dotenv(ENV_PATH)

APP_SECRET_KEY = os.getenv("REGISBOOKS_SECRET_KEY")
AUTH_URL = os.getenv("REGISBOOKS_AUTH_URL")
AUTH_API_KEY = os.getenv("REGISBOOKS_AUTH_API_KEY")
ADMIN_KEY = os.getenv("ADMIN_KEY")
DB_URI = os.getenv("DB_URI")
EMAIL_WHITELIST = os.getenv("EMAIL_WHITELIST", "").split(",") if os.getenv("EMAIL_WHITELIST") else []