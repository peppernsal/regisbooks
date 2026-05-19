import sys
import httpx
import constants

resp = httpx.post(f"{constants.SERVER_URL}/api/external/normalize-badges", json={ "key": constants.ADMIN_KEY })

print(resp)