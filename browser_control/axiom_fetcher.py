from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

from browser_utilities.await_loading import wait_for_loading
from browser_utilities.general_utils import generate_urls
from browser_utilities.navigate_verifier import perform_login
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

    def goto_record_manager(self):
        self.driver.get(self.manager_url)
        # make the advanced options visible
        input_status = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "react-select-3-input")))
        while not input_status.is_displayed():
            button_options = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ToggleAdvancedOptions")))
            button_options.click()
            time.sleep(.1)

        # set the status options
        for status in self.options:
            input_status.send_keys(f"{status}\n")

        # click the search button
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "SearchButton"))).click()

    def main_loop(self):
        """
        Main logic loop
        :return: None
        """
        while True:
            wait_for_loading(self.driver)
            page_urls = []
            rows = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "rdt_TableRow")))
            for row in rows:
                cols = row.find_elements(By.CLASS_NAME, "rdt_TableCell")
                page_urls.append(f"{self.verifier_url}{cols[2].text}")
            self.database.bulk_add_urls(page_urls)

            nav_box = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "rdt_Pagination")))
            button_next = nav_box.find_element(By.ID, "pagination-next-page")
            span_stats = nav_box.find_element(By.XPATH, ".//span[1]").text
            self.actions.move_to_element(button_next).perform()
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "pagination-next-page")))
            # print(span_stats)
            button_next.click()
