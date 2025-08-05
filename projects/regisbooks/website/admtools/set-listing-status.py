import sys
import httpx
import constants

listing = sys.argv[1]
status = int(sys.argv[2])

resp = httpx.post(f"{constants.SERVER_URL}/api/external/set-listing-status", json={ "listingID": listing, "status": status, "key": constants.ADMIN_KEY })

print(resp)