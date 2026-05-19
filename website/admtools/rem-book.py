import sys
import httpx
import constants


book = sys.argv[1]

resp = httpx.post(f"{constants.SERVER_URL}/api/external/rem-book", json={ "bookID": book, "key": constants.ADMIN_KEY })

print(resp)