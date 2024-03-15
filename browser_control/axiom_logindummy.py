from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from getpass import getpass
import sys

# Constants
LOGIN_TIMEOUT = 5
RECORD_TYPES = {
    "prospects": 601,
    "act": 361,
    # add other record types here as needed
}


def validate_config(config: dict) -> None:
    """
    Validate the configuration
    :param config: configuration dictionary
    :return: None
    """
    if config.get("environment mode") not in ["test", "prod"]:
        print("Invalid run mode")
        sys.exit(1)
    if config.get("record type") not in RECORD_TYPES:
        print("Invalid record type")
        sys.exit(1)


def prompt_credentials() -> tuple[str, str]:
    """
    Prompt the user for their Axiom credentials
    :return: tuple of username and password
    """
    username = input("Enter your Axiom username: ").strip()
    password = getpass("Enter your Axiom password: ").strip()
    return username, password


class AxiomDummy:
    def __init__(self, config: dict):
        validate_config(config)
        mode = config['environment mode']
        record_type_id = RECORD_TYPES[config['record type']]
        self.base_url = (f"https://axiom-elite-{mode}.msu.montana.edu/"
                         f"RecordManager.aspx?SourceID={record_type_id}")
        self.login_url = (f"https://axiom-elite-{mode}.msu.montana.edu/"
                          f"Login.aspx")
        self.credentials = {}

    def perform_login(self) -> None:
        """
        Perform the login process
        :return: None
        """
        self.driver.get(self.login_url)
        self.handle_login()
        self.handle_two_factor_authentication()
        print("Axiom Login Successful")

    def handle_login(self, timeout=LOGIN_TIMEOUT) -> None:
        """
        Handle the login process
        :param timeout: time to wait
        :return: None
        """
        while True:
            username, password = prompt_credentials()
            self.enter_login_credentials(username, password, timeout)
            button_close = self.driver.find_elements(
                By.XPATH, "//button[text()='Close']")
            if button_close and button_close[0].is_displayed():
                button_close[0].click()
                print("Invalid credentials. Please try again.")
                continue
            if self.wait_for_title("Two-Factor Authentication", timeout):
                self.credentials.update(username=username, password=password)
                break

    def enter_login_credentials(self, username: str, password: str, timeout: int):
        """
        Enter the login credentials into the form
        :param username: username
        :param password: password
        :param timeout: time to wait
        :return: None
        """
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "Login")))
        input_username = self.driver.find_element(By.ID, "UserName")
        input_username.clear()
        input_username.send_keys(username)
        input_password = self.driver.find_element(By.ID, "Password")
        input_password.clear()
        input_password.send_keys(password)
        self.driver.find_element(By.ID, "Login").click()

    def handle_two_factor_authentication(self, timeout=LOGIN_TIMEOUT) -> None:
        """
        Handle two-factor authentication
        :param timeout: time to wait
        :return: None
        """
        while True:
            verification_code = input("Enter your Axiom verification code: ").strip()
            self.enter_verification_code(verification_code, timeout)
            button_close = self.driver.find_elements(
                By.XPATH, "//button[text()='Close']")
            if button_close and button_close[0].is_displayed():
                button_close[0].click()
                print("Invalid verification code. Please try again.")
                continue
            if self.wait_for_title("Axiom Elite - Dashboard", timeout):
                self.credentials["verification"] = verification_code
                break

    def enter_verification_code(self, code: str, timeout: int) -> None:
        """
        Enter the two-factor authentication code
        :param code: verification code
        :param timeout: time to wait
        :return: None
        """
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "ValidateBtn")))
        self.driver.find_element(By.ID, "SecurityPin").send_keys(code)
        self.driver.find_element(By.ID, "ValidateBtn").click()

    def wait_for_title(self, title: str, timeout: int) -> bool:
        """
        Wait for the title of the page to change
        :param title: title to wait for
        :param timeout: time to wait
        :return: Boolean indicating if the title changed
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.title_is(title))
            return True
        except:
            return False

    def get_credentials(self):
        """
        Get the credentials
        :return:
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.perform_login()
        self.driver.quit()
        return self.credentials
