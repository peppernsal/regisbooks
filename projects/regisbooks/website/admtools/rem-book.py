import sys
import httpx
import admkey

SERVER_URL = "https://regisbooks.onrender.com"

book = sys.argv[1]

resp = httpx.post(f"{SERVER_URL}/api/external/rem-book", json={ "bookID": book, "key": admkey.ADMIN_KEY })

print(resp)