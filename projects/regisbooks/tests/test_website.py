import pytest
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import SERVER_URL, TEST_USER_ONE, TEST_USER_ONE_EMAIL, TEST_USER_TWO, page, timeout

@pytest.mark.order(0)
def test_profile_loaded(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	profile_loaded(driver, TEST_USER_ONE)
	profile_loaded(driver_two, TEST_USER_TWO)

def profile_loaded(driver: webdriver.Chrome, username: str):
	driver.get(SERVER_URL)

	if "propelauthtest" in driver.current_url:
		signin_btn = driver.find_element(By.CSS_SELECTOR, "#__next > div > div > main > div.mantine-MediaQuery-media.mantine-zcpb3y > div > div.mantine-b6zkvl.mantine-ScrollArea-viewport > div > div > div > div.mantine-Paper-root.mantine-sowdty > div > button")
		signin_btn.click()

	assert driver.current_url == page(f"view-profile/")

	assert timeout(driver, EC.text_to_be_present_in_element((By.ID, "full-name"), username))

@pytest.mark.order(1)
def test_bookfetch(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	driver.get(page("enter-isbn"))

	isbn_input = driver.find_element(value="isbn-entry")
	isbn_input.send_keys("9780679406419")

	submit_btn = driver.find_element(By.CSS_SELECTOR, "body > div.content.py-5 > div > div > div > div > form > div.d-grid > button")
	submit_btn.click()

	assert driver.current_url == page("add-listing/?book=9780679406419")

	waiting_msg = driver.find_element(value="waiting-message")

	assert timeout(driver, EC.staleness_of(waiting_msg), sec=10)

	title = driver.find_element(value="book-title").text

	assert "Maus" in title

# TODO: add testing for error cases which trigger window.alert

@pytest.mark.order(2)
def test_add_listing(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	# the add-listing page should already be loaded from the previous test

	assert driver.current_url == page("add-listing/?book=9780679406419")

	usage_input = Select(driver.find_element(value="usage-level"))
	usage_input.select_by_visible_text("Lightly Used")

	driver.find_element(value="notes").send_keys("These are test notes")

	driver.find_element(value="english-flag").click()

	add_loc_btn = driver.find_element(value="add-pickup-location")

	add_loc_btn.click()
	add_loc_btn.click()
	add_loc_btn.click()

	driver.find_element(By.CSS_SELECTOR, "#pickup-locations-container > div:nth-child(1) > div.col-5.offset-1 > input").send_keys("Test City, NY")
	driver.find_element(By.CSS_SELECTOR, "#pickup-locations-container > div:nth-child(2) > div.col-5.offset-1 > input").send_keys("New York, NY")

	driver.find_element(By.CSS_SELECTOR, "#pickup-locations-container > div:nth-child(3) > div.col-2 > button").click() # remove the third pickup location

	driver.find_element(By.CSS_SELECTOR, "body > div.content.py-5.centered > div > div > div > div > div > div:nth-child(6) > button").click()

@pytest.mark.order(3)
def test_listing_created(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	# we should be on view-listings from the previous test

	assert timeout(driver, EC.url_contains(page("view-listings/")))

	assert (listing_anchor := timeout(driver, EC.presence_of_element_located((By.CSS_SELECTOR, "#listings-container > div:nth-child(1) > div:nth-child(1) > a"))))
	
	listing_anchor.click()

	# now switch to the other user

	driver_two.get(driver.current_url)

	assert timeout(driver_two, EC.text_to_be_present_in_element((By.ID, "book-title"), "Maus"))
	assert driver_two.find_element(value="listing-author").text == f"Listed by: {TEST_USER_ONE}"
	assert driver_two.find_element(value="listing-usage-level").text == "Condition: Lightly Used"
	assert driver_two.find_element(value="listing-status").text == "Status: Available"
	assert driver_two.find_element(value="listing-notes").text == "These are test notes"
	assert driver_two.find_elements(value="english-alert")

	pickup_loc_text = driver_two.find_element(value="pickup-locations-container").text
	assert pickup_loc_text == "Pickup At: New York, NY\nPickup At: Test City, NY" or pickup_loc_text == "Pickup At: Test City, NY\nPickup At: New York, NY"

@pytest.mark.order(4)
def test_request_listing(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	assert (req_listing_btn := timeout(driver_two, EC.presence_of_element_located((By.ID, "request-listing"))))
	req_listing_btn.click()

	assert timeout(driver_two, EC.text_to_be_present_in_element((By.ID, "email-info"), TEST_USER_ONE_EMAIL))
	driver_two.find_element(value="rem-listing-req").click()

	assert (alert := timeout(driver_two, EC.alert_is_present()))
	alert.accept()

	assert timeout(driver_two, EC.text_to_be_present_in_element((By.ID, "book-title"), "Maus")) # wait for the listing to reload

	assert (req_listing_btn := timeout(driver_two, EC.presence_of_element_located((By.ID, "request-listing"))))
	req_listing_btn.click()

	assert timeout(driver_two, EC.text_to_be_present_in_element((By.ID, "email-info"), TEST_USER_ONE_EMAIL))

@pytest.mark.order(5)
def test_fulfill_request(driver: webdriver.Chrome, driver_two: webdriver.Chrome):
	pass