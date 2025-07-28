from typing import Callable, TypeVar
from selenium.common.exceptions import TimeoutException
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

SERVER_URL = "http://localhost:5000"
TEST_USER_ONE = "Constus V"
TEST_USER_ONE_EMAIL = "constusv@gmail.com"
TEST_USER_TWO = "Constus IV"
TEST_USER_TWO_EMAIL = "constusiv@gmail.com"

def page(path: str) -> str:
	return f"{SERVER_URL}/{path}"

T = TypeVar('T')
TRet = TypeVar("TRet")

def timeout(driver: webdriver.Chrome, condition: Callable[[T], TRet | False], sec: float=2):
	"""
	Waits for a condition to be met on the driver, returning the result of the condition if successful.
	Returns False if the condition is not met within the specified timeout.
	"""
	try:
		return WebDriverWait(driver, sec).until(condition)
	except TimeoutException:
		return False