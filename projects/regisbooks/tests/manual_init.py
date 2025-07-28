import asyncio
from server_url import SERVER_URL
import os
import zendriver

USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "profiles")

async def start():
	conf = zendriver.Config(
		user_data_dir=USER_DATA_DIR
	)

	driver = await zendriver.start(conf)

	await driver.get(SERVER_URL)

	while 1: pass

asyncio.run(start())