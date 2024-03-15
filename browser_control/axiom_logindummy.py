from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from getpass import getpass
import sys
import logging

# Constants
LOGIN_TIMEOUT = 5
RECORD_TYPES = {
    "prospects": 601,
    "act": 361,
    # add other record types here as needed
}


class AxiomDummy:
    def __init__(self, config: dict, credentials: dict):
        self.validate_config(config)
        mode = config['environment mode']
        record_type_id = RECORD_TYPES[config['record type']]
        self.base_url = f"https://axiom-elite-{mode}.msu.montana.edu/RecordManager.aspx?SourceID={record_type_id}"
        self.login_url = f"https://axiom-elite-{mode}.msu.montana.edu/Login.aspx"
        self.credentials = credentials
        self.driver = webdriver.Chrome()
        self.perform_login()

    def validate_config(self, config):
        if config["environment mode"] not in ["test", "prod"]:
            logging.error("Invalid run mode")
            sys.exit(1)
        if config["record type"] not in RECORD_TYPES:
            logging.error("Invalid record type")
            sys.exit(1)

    def perform_login(self):
        self.driver.get(self.login_url)
        self.handle_login()
        self.handle_two_factor_authentication()
        logging.info("Axiom Login Successful")

    def handle_login(self, timeout=LOGIN_TIMEOUT):
        while True:
            username, password = self.prompt_credentials()
            self.enter_login_credentials(username, password, timeout)
            if self.wait_for_title("Two-Factor Authentication", timeout):
                self.credentials.update(username=username, password=password)
                break
            else:
                logging.error("Invalid credentials. Please try again.")

    def prompt_credentials(self):
        username = input("Enter your Axiom username: ").strip()
        password = getpass("Enter your Axiom password: ").strip()
        return username, password

    def enter_login_credentials(self, username, password, timeout):
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.ID, "Login")))
        self.driver.find_element(By.ID, "UserName").send_keys(username)
        self.driver.find_element(By.ID, "Password").send_keys(password)
        self.driver.find_element(By.ID, "Login").click()

    def handle_two_factor_authentication(self, timeout=LOGIN_TIMEOUT):
        while True:
            verification_code = input("Enter your Axiom verification code: ").strip()
            self.enter_verification_code(verification_code, timeout)
            if self.wait_for_title("Axiom Elite - Dashboard", timeout):
                self.credentials["verification"] = verification_code
                break
            else:
                logging.error("Invalid verification code. Please try again.")

    def enter_verification_code(self, code, timeout):
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.ID, "ValidateBtn")))
        self.driver.find_element(By.ID, "SecurityPin").send_keys(code)
        self.driver.find_element(By.ID, "ValidateBtn").click()

    def wait_for_title(self, title, timeout):
        try:
            WebDriverWait(self.driver, timeout).until(EC.title_is(title))
            return True
        except:
            return False
