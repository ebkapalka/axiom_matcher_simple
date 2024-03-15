from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import sys

from browser_utilities.navigate_verifier import identify_page
from database_sqlite.database import DatabaseManager

REC_TYPES = {
    "prospects": 601,
    "act": 361,
    # add other record types here as needed
}


class AxiomFetcher:
    def __init__(self, database: DatabaseManager, config: dict, credentials: dict):
        run_mode = config["environment mode"]
        if run_mode not in ["test", "prod"]:
            print("Invalid run mode")
            sys.exit()
        source_id = REC_TYPES[config["record type"]]
        self.base_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                         f"/RecordManager.aspx?SourceID={source_id}")
        self.login_url = (f"https://axiom-elite-{run_mode}.msu.montana.edu"
                          f"/Login.aspx")

        self.credentials = credentials
        self.option = config["issue type"]
        self.driver = webdriver.Chrome()
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
            print("Fetcher Login Successful")
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
