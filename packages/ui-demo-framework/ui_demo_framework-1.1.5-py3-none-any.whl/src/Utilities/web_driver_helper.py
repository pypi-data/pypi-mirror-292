from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from Utilities.read_properties import ReadConfig


class WebDriverHelper:
    read_config = ReadConfig()

    def __init__(self, driver, logger):
        self.driver = driver
        self.log = logger

    @staticmethod
    def select_static_dropdown(web_element):
        dropdown = Select(web_element)
        return dropdown

    def wait_load_page_by_tag_name(self, tag_name):
        time_load_page = 10

        try:
            element_present = EC.visibility_of_element_located((By.TAG_NAME, tag_name))
            WebDriverWait(self.driver, time_load_page).until(element_present)
        except TimeoutException:
            self.log.error("Timed out waiting for page to load")

    def wait_web_element(self, by, value):
        delay_web_element = 10

        try:
            element = WebDriverWait(self.driver, delay_web_element).until(
                EC.presence_of_element_located((by, value))
            )
            self.log.info(f"Element with {by}='{value}' found and ready")
            return element
        except TimeoutException:
            self.log.error(f"Timed out waiting for element with {by}='{value}' to be present")
            return None
        except Exception as e:
            self.log.error(f"Error occurred while waiting for element with {by}='{value}': {e}")
            return None

    def wait_web_element_by_id(self, web_element_id):
        delay_web_element = self.read_config.get_delay_web_element()

        try:
            element = WebDriverWait(self.driver, delay_web_element).until(
                EC.presence_of_element_located((By.ID, web_element_id))
            )
            self.log.info(f"Element with ID '{web_element_id}' found and ready")
            return element
        except TimeoutException:
            self.log.error(f"Timed out waiting for element with ID '{web_element_id}' to be present")
            return None
        except Exception as e:
            self.log.error(f"Error occurred while waiting for element with ID '{web_element_id}': {e}")
            return None

    def click_button(self, xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            self.log.info(f"Clicked on button with XPATH: {xpath}")
        except TimeoutException:
            self.log.error(f"Timed out waiting for button with XPATH: {xpath} to be clickable")
        except ElementClickInterceptedException as e:
            self.log.error(f"Element Click Intercepted Exception for button with XPATH: {xpath}: {e}")
        except Exception as e:
            self.log.error(f"Error clicking button: {e}")

    def enter_text(self, xpath, text):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.clear()
            element.send_keys(text)
            self.log.info(f"Entered text in field with XPATH: {xpath}")
        except TimeoutException:
            self.log.error(f"Timed out waiting for field with XPATH: {xpath} to be present")
        except Exception as e:
            self.log.error(f"Error entering text in field: {e}")

    def get_element_text(self, xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = element.text
            self.log.info(f"Text of element with XPATH {xpath}: {text}")
            return text
        except TimeoutException:
            self.log.error(f"Timed out waiting for element with XPATH: {xpath} to be present")
            return None
        except NoSuchElementException:
            self.log.error(f"No such element found with XPATH: {xpath}")
            return None
        except Exception as e:
            self.log.error(f"Error getting text from element: {e}")
            return None
