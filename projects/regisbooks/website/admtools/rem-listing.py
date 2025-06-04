import os
import sys
import httpx

sys.path.append(os.path.abspath(".."))
os.chdir("..")

import secret_keys

SERVER_URL = "https://regisbooks.onrender.com"

listing = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/rem-listing", json={ "listingID": listing, "key": secret_keys.ADMIN_KEY })

print(resp)