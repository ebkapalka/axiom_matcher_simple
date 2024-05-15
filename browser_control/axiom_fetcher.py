
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
from copy import copy
import time

from browser_utilities.navigate_verifier import perform_login
from browser_utilities.await_loading import wait_for_loading
from browser_utilities.general_utils import generate_urls
from database_sqlite.database import DatabaseManager


class AxiomFetcher:
    def __init__(self, database: DatabaseManager, config: dict, credentials: dict):
        self.manager_url, self.verifier_url, self.login_url = (generate_urls(config))
        self.credentials = credentials
        self.options = config["issue types"]
        self.driver = webdriver.Chrome()
        self.actions = ActionChains(self.driver)
        self.driver.maximize_window()
        self.database = database
        perform_login(self.driver,
                      self.login_url,
                      self.credentials)
        print("Fetcher login successful")
        self.goto_record_manager()
        self.main_loop()

    def goto_record_manager(self, timeout=30):
        """
        Navigate to the record manager page
        :return: None
        """
        self.driver.get(self.manager_url)
        selector_advanced_options = (By.XPATH, "//button[@aria-label='Toggle Advanced Search Options']")
        selector_status_text = (By.XPATH, "//div[text()='Status...']")
        selector_status_input = (By.XPATH, "//input[@aria-label='Select Statuses']")
        selector_search_button = (By.XPATH, "//button[@aria-label='Search Record Manager']")

        # make the advanced options visible
        while True:
            button_options = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(selector_advanced_options))
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(selector_status_text))
                break
            except TimeoutException:
                button_options.click()
                time.sleep(0.5)
                continue
            except Exception as e:
                print("Goto record manager error:", type(e))
                button_options.click()
                time.sleep(0.5)
                continue

        # set the status options
        input_status = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(selector_status_input))
        for status in self.options:
            input_status.send_keys(f"{status}\n")

        # click the search button
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(selector_search_button)).click()

    def main_loop(self):
        """
        Main logic loop
        :return: None
        """
        fetch_script = """
            return Array.from(
                document.querySelectorAll('#record-id')
            ).map(element => element.textContent);
        """
        while True:
            wait_for_loading(self.driver)
            page_urls = []
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "record-id")))
            prospect_ids = self.driver.execute_script(fetch_script)
            for prospect_id in prospect_ids:
                new_url = f"{self.verifier_url}{prospect_id}"
                print(new_url); page_urls.append(new_url)
            self.database.bulk_add_urls(page_urls)

            # navigate to the next page
            selector = (By.XPATH, "//button[@title='Go to the next page']")
            button_next = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(selector))
            if not button_next.is_enabled():
                print("No more pages to fetch")
                return

            self.actions.move_to_element(button_next).perform()
            initial_page = self.driver.find_element(
                By.ID, "currentPageInput").get_attribute("value")
            current_page = copy(initial_page)
            while current_page == initial_page:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)).click()
                    wait_for_loading(self.driver)
                    current_page = (WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "currentPageInput"))).get_attribute("value"))
                except ElementClickInterceptedException:
                    time.sleep(0.5)
                    current_page = (WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "currentPageInput"))).get_attribute("value"))
