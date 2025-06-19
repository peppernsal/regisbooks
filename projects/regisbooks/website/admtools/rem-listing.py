import sys
import httpx
import admkey

SERVER_URL = "https://regisbooks.onrender.com"

listing = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/rem-listing", json={ "listingID": listing, "key": admkey.ADMIN_KEY })

print(resp)