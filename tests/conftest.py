import os
import subprocess
import pytest
import selenium.webdriver as webdriver

USER_DATA_DIR_BASE = os.path.join(os.path.dirname(__file__), "profiles")

@pytest.fixture(scope="session")
def driver():
	os.chdir("../website")

	# Set debug flag for auth.js before tests

	auth_js = open("static/js/auth.js").read()

	auth_js = auth_js.replace("const DEBUG = false;", "const DEBUG = true;")

	open("static/js/auth.js", "w").write(auth_js)

	# Clear test database before running tests

	SITE_INTERPRETER = "venv/Scripts/python"

	subprocess.run([SITE_INTERPRETER, "scripts/reset-lcl-db.py"], check=True)

	# start the server

	srv = subprocess.Popen(
		[SITE_INTERPRETER, "-m", "webpy", "run", "--force-debug"],
		stdout=subprocess.PIPE
	)

	# setup webdriver instance

	options = webdriver.ChromeOptions()
	options.add_argument(f"--user-data-dir={USER_DATA_DIR_BASE}")
	options.add_argument("--profile-directory=Default")
	# options.add_argument("--headless")

	driver = webdriver.Chrome(options=options)

	yield driver

	# close the webdriver instance

	driver.quit()

	# stop the server after tests

	srv.terminate()

	# Remove debug flag after tests

	auth_js = open("static/js/auth.js").read()

	auth_js = auth_js.replace("const DEBUG = true;", "const DEBUG = false;")

	open("static/js/auth.js", "w").write(auth_js)

	os.chdir("../tests")

@pytest.fixture(scope="session")
def driver_two():
	options = webdriver.ChromeOptions()
	options.add_argument(f"--user-data-dir={USER_DATA_DIR_BASE}2")
	options.add_argument("--profile-directory=Default")
	# options.add_argument("--headless")

	driver = webdriver.Chrome(options=options)

	yield driver