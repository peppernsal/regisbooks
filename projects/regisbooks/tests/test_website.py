import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By

from server_url import SERVER_URL, TEST_USER


def test_profile_loaded(driver: webdriver.Chrome):
	driver.get(f"{SERVER_URL}/")

	assert driver.current_url == f"{SERVER_URL}/view-profile/"

	name_elem = driver.find_element(By.CSS_SELECTOR, "#full-name")
	
	while name_elem.text == "": pass

	assert name_elem.text == TEST_USER