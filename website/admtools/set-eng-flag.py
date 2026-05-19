import sys
import httpx
import constants

listing = sys.argv[1]

resp = httpx.post(f"{constants.SERVER_URL}/api/external/set-eng-flag", json={ "listingID": listing, "key": constants.ADMIN_KEY })

print(resp)