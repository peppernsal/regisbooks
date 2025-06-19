import sys
import httpx
import admkey

SERVER_URL = "https://regisbooks.onrender.com"

user = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/reset-stats", json={ "userID": user, "key": admkey.ADMIN_KEY })

print(resp)