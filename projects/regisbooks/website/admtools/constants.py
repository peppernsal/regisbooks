import dotenv
import os

dotenv.load_dotenv()

ADMIN_KEY = os.getenv("ADMIN_KEY")
SERVER_URL = "http://localhost:5000"