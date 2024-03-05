from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from pprint import pprint
import atexit
import time

from browserutilities.navigate_verifier import identify_page
from browserutilities.await_loading import wait_for_loading


class AxiomDriver:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.actions = ActionChains(self.driver)
        self.stats = {
            "create": 0,
            "skip": 0,
            "match": 0,
            "delete": 0,
            "fix": {
                "bad address": 0,
                "bad ceeb": 0,
            }
        }
        atexit.register(self.print_stats)
        self.await_login()
        self.goto_verifier()
        self.main_loop()

    def await_login(self):
        print("Please log into Axiom")
        self.driver.get("https://axiom-elite-prod.msu.montana.edu/")
        WebDriverWait(self.driver, 300).until(EC.title_is("Axiom Elite - Dashboard"))
        print("Axiom Login Successful")

    def goto_verifier(self):
        """
        Go to the verifier page
        :return: None
        """
        def _button_with_color_darkgray(driver) -> WebElement | bool:
            """
            Find the button with the darkgray color
            :param driver: webdriver
            :return:
            """
            try:
                buttons = driver.find_elements(By.XPATH, '//button[@title="Card View" or @title="Table View"]')
                for button in buttons:
                    if "color: darkgray;" in button.get_attribute("style"):
                        return button
            except Exception as e:
                print(type(e), e)
            return False

        if "https://axiom-elite-prod.msu.montana.edu/Dashboard" not in self.driver.current_url:
            self.driver.get("https://axiom-elite-prod.msu.montana.edu/Dashboard")
        wait_for_loading(self.driver)
        current_tab = WebDriverWait(self.driver, 10).until(
            _button_with_color_darkgray).get_attribute("title")
        if current_tab == "Card View":
            title_elem = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//span[text()='01 Bozeman UG EAB Prospect']")))
            body_elem = title_elem.find_element(By.XPATH, './../../../div[2]')
            verifier = body_elem.find_element(By.XPATH, './div[1]/div[2]')
            verifier_count = verifier.text.strip()
        else:
            title_elem = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//td[text()='01 Bozeman UG EAB Prospect']")))
            verifier = title_elem.find_element(By.XPATH, './../td[2]')
            verifier_count = verifier.text.strip()

        print(f"Records to process: {verifier_count}")
        if int(verifier_count) > 0:
            verifier.click()

    def main_loop(self):
        while True:
            wait_for_loading(self.driver)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "VerifyRecordViewPort")))
            page = identify_page(self.driver)
            match page:
                case "normal":
                    ...
                case "error - Address 1":
                    ...
                case "error - Address 2":
                    ...
                case "error - High School CEEB":
                    ...
                case _:
                    ...
            time.sleep(30)

    def print_stats(self):
        pprint(self.stats)
