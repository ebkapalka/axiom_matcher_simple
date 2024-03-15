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
from matching_utilities.match_handler import handle_match_dialogue
from browser_utilities.navigate_verifier import identify_page
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
    def __init__(self, database: DatabaseManager, config: dict, credentials: dict):
        run_mode = config["environment mode"]
        if run_mode not in ["test", "prod"]:
            print("Invalid run mode")
            sys.exit()
        self.login_url = (f"https://axiom-elite-{run_mode}"
                          f".msu.montana.edu/Login.aspx")

        self.credentials = credentials
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.database = database
        self.perform_login()
        self.main_loop()

    def perform_login(self, timeout=5):
        """
        Wait for user to log into Axiom
        :return: None
        """
        self.driver.get(self.login_url)
        button_login = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "Login")))
        input_username = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "UserName")))
        input_password = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "Password")))
        input_username.send_keys(self.credentials["username"])
        input_password.send_keys(self.credentials["password"])
        button_login.click()

        # handle entering verification code
        button_validate = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "ValidateBtn")))
        input_verification = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "SecurityPin")))
        input_verification.send_keys(self.credentials["verification"])
        button_validate.click()

        # verify login
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.title_is("Axiom Elite - Dashboard"))
            print("Worker Login Successful")
            return
        except:
            print("Invalid verification code")
            sys.exit()

    def main_loop(self):
        """
        Main logic loop
        :return: None
        """
        ...
        # while True:
        #     # check out a URL from the database
        #     url = self.database.check_out_url()
        #     while not url:
        #         time.sleep(random.uniform(1, 2))
        #         url = self.database.check_out_url()
        #
        #     # navigate to the URL
        #     self.driver.get(url.url)
        #     wait_for_loading(self.driver)
        #     WebDriverWait(self.driver, 30).until(
        #         EC.visibility_of_element_located((By.ID, "VerifyRecordViewPort")))
        #
        #     # handle the page
        #     page = identify_page(self.driver)
        #     if page == "finished":
        #         return
        #     elif page in HANDLERS:
        #         result = HANDLERS[page](self.driver)
        #         if page.startswith("error"):
        #             self.database.add_event(page)
        #         if result:
        #             self.database.add_event(result)
        #     else:
        #         print(f"Unknown page: {page}")
        #         time.sleep(100000000)
