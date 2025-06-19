import os
import sys
import httpx

sys.path.append(os.path.abspath(".."))
os.chdir("..")

import secret_keys

SERVER_URL = "https://regisbooks.onrender.com"

user = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/reset-stats", json={ "userID": user, "key": secret_keys.ADMIN_KEY })

print(resp)