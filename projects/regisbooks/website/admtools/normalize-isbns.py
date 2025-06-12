import os
import sys
import httpx

sys.path.append(os.path.abspath(".."))
os.chdir("..")

import secret_keys

SERVER_URL = "https://regisbooks.onrender.com"

book = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/temp/normalize-book-isbns", json={ "key": secret_keys.ADMIN_KEY })

print(resp)