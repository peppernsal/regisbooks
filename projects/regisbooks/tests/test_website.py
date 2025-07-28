import time
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By

from server_url import SERVER_URL, TEST_USER_ONE, TEST_USER_TWO


def test_profile_loaded(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	profile_loaded(driver, TEST_USER_ONE)
	profile_loaded(driver_two, TEST_USER_TWO)

def profile_loaded(driver: webdriver.Chrome, username: str):
	driver.get(f"{SERVER_URL}/")

	if "propelauthtest" in driver.current_url:
		signin_btn = driver.find_element(By.CSS_SELECTOR, "#__next > div > div > main > div.mantine-MediaQuery-media.mantine-zcpb3y > div > div.mantine-b6zkvl.mantine-ScrollArea-viewport > div > div > div > div.mantine-Paper-root.mantine-sowdty > div > button")
		signin_btn.click()

	assert driver.current_url == f"{SERVER_URL}/view-profile/"

	name_elem = driver.find_element(By.CSS_SELECTOR, "#full-name")
	
	while name_elem.text == "": pass

	assert name_elem.text == username