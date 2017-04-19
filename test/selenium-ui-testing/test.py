from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


import Constants as constants


# ccreate new Firefox session
driver = webdriver.Firefox()
driver.maximize_window()

# navigate to CONSIDER Home Page
driver.get("http://localhost:8080")
driver.find_element_by_id(constants.LOGIN_ID).click()
# verify elements

# Login
#driver.get("http://localhost:8080/_ah/login?continue=http%3A//localhost%3A8080/")
driver.find_element_by_id("email").clear()
driver.find_element_by_id("email").send_keys("aang@gmail.com")
driver.find_element_by_id("submit-login").click()

# close browser window
driver.quit()



# 

"""
# Localhost Login
try
	delay = 5
	WebDriverWait(driver, 5).until(EC.presence_of_element_located(driver.find_element_by_id("submit-login")))
except TimeoutException:
	print "Timed out waiting for page to load: localhost login"

driver.find_element_by_id("email").send_keys("aang@gmail.com")
driver.find_element_by_id("submit-login").click()
"""
"""
driver = webdriver.Firefox()
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close
"""

"""run locally

> python ~/Installations/google_appengine/dev_appserver.py --host localhost --datastore_path ./temp/consider.db $PWD
"""