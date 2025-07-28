import asyncio
from server_url import SERVER_URL
import os
import zendriver

USER_DATA_DIR_BASE = os.path.join(os.path.dirname(__file__), "profiles")

async def start():
	conf = zendriver.Config(
		user_data_dir=USER_DATA_DIR_BASE
	)

	driver = await zendriver.start(conf)

	await driver.get(SERVER_URL)

	input()

	await driver.stop()

	conf = zendriver.Config(
		user_data_dir=f"{USER_DATA_DIR_BASE}2"
	)

	driver = await zendriver.start(conf)

	await driver.get(SERVER_URL)

	input()

	await driver.stop()

asyncio.run(start())