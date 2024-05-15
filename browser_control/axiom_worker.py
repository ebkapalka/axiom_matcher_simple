from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import random
import time
import sys

from browser_utilities.case_handlers import (handle_normal, handle_bad_ceeb, handle_bad_address,
                                             handle_bad_firstname, handle_bad_lastname,
                                             handle_bad_city, handle_bad_zip, handle_bad_state)
from browser_utilities.general_utils import generate_urls
from matching_utilities.match_handler import handle_match_dialogue
from browser_utilities.navigate_verifier import identify_page, perform_login
from browser_utilities.await_loading import wait_for_loading
from database_sqlite.database import DatabaseManager


HANDLERS = {
    "match dialogue": handle_match_dialogue,
    "normal": handle_normal,
    "error - Address 1": handle_bad_address,
    "error - Address 2": handle_bad_address,
    "error - High School CEEB": handle_bad_ceeb,
    "error - First Name": handle_bad_firstname,
    "error - Last Name": handle_bad_lastname,
    "error - City": handle_bad_city,
    "error - State": handle_bad_state,
    "error - Zip": handle_bad_zip,
    # add other handlers here as needed
}


class AxiomWorker:
    """
    AxiomWorker class
    """
    def __init__(self, database: DatabaseManager, config: dict,
                 credentials: dict, identifier: str, headless=True):
        self.manager_url, self.verifier_url, self.login_url = generate_urls(config)
        self.credentials = credentials
        self.identifier = identifier
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)
        self.driver.minimize_window()
        self.database = database
        perform_login(self.driver,
                      self.login_url,
                      self.credentials)
        print(f"{self.identifier} login successful")
        self.main_loop()

    def main_loop(self):
        """
        Main logic loop
        :return: None
        """
        ...
        while True:
            # check out a URL from the database
            url = self.database.check_out_url()
            while not url:
                time.sleep(random.uniform(1, 2))
                url = self.database.check_out_url()
            # print(f"{self.identifier} processing {url}")

            # navigate to the URL
            self.driver.get(url)
            wait_for_loading(self.driver)
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "ModalOverlayArea")))

            # identify the page and handle it
            page = identify_page(self.driver)
            wait_for_loading(self.driver)
            while page not in ["dashboard", "lock expired"]:
                if page in HANDLERS:
                    result = HANDLERS[page](self.driver)
                    if page.startswith("error"):
                        self.database.add_event(page)
                    if result:
                        self.database.add_event(result)
                else:
                    print(f"Unknown page: {page}")
                    time.sleep(100000000)
                wait_for_loading(self.driver)
                page = identify_page(self.driver)

            self.database.mark_url_as_processed(url)
            # time.sleep(10)