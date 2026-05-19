import sys
import httpx
import constants

user = sys.argv[1]

resp = httpx.post(f"{constants.SERVER_URL}/api/external/reset-stats", json={ "userID": user, "key": constants.ADMIN_KEY })

print(resp)