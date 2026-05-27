import os
import dotenv

ENV_PATH = "instance/.env"

if os.path.isfile(ENV_PATH): dotenv.load_dotenv(ENV_PATH)

APP_SECRET_KEY = os.getenv("REGISBOOKS_SECRET_KEY")
AUTH_URL = os.getenv("REGISBOOKS_AUTH_URL")
AUTH_API_KEY = os.getenv("REGISBOOKS_AUTH_API_KEY")
ADMIN_KEY_HASH = os.getenv("ADMIN_KEY_HASH")
DB_URI = os.getenv("DB_URI")
EMAIL_WHITELIST = os.getenv("EMAIL_WHITELIST", "").split(",") if os.getenv("EMAIL_WHITELIST") else []
TEST_REGISBOOKS_AUTH_URL = os.getenv("TEST_REGISBOOKS_AUTH_URL")
TEST_REGISBOOKS_AUTH_API_KEY = os.getenv("TEST_REGISBOOKS_AUTH_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# This only works for top-level routes, which is fine because we only have top-level HTML routes.
SAFE_STATIC_HTML_ROUTES = [
	f"/{route_name}" for route_name in os.listdir("root") if os.path.isfile(os.path.join("root", route_name, "index.html"))
]