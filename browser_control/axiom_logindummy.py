from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver

from browser_utilities.general_utils import (generate_urls,
                                             prompt_credentials)


class AxiomDummy:
    def __init__(self, config: dict):
        self.config = config
        self.login_url = generate_urls(config)[2]
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

    def handle_login(self, timeout=5) -> None:
        """
        Handle the login process
        :param timeout: time to wait
        :return: None
        """
        while True:
            env = self.config.get("environment mode", "TEST")
            username, password = prompt_credentials(env)
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

    def handle_two_factor_authentication(self, timeout=5) -> None:
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
