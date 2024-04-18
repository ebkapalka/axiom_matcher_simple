from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
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


class AxiomDriver:
    """
    Class to control the Axiom driver
    """

    def __init__(self, database: DatabaseManager, environ="test", source=601, status="Verify"):
        """
        Initialize the Axiom driver
        :param database: DatabaseManager instance
        :param environ: "prod" or "test"
        :param status: "Verify" or "Error"
        :param source: numeric key for the source
        """
        if environ not in ["test", "prod"]:
            print("Invalid run env")
            sys.exit()
        if status not in ["Verify", "Error"]:
            print("Invalid status")
            sys.exit()

        self.base_url = f"https://axiom-elite-{environ}.msu.montana.edu"
        self.verifier_url = (f"{self.base_url}/Verification/Verification.aspx"
                             f"?SourceID={source}&Status={status}")
        self.driver = webdriver.Chrome()
        self.database = database
        self.await_login()
        self.main_loop()

    def await_login(self):
        """
        Wait for user to log into Axiom
        :return: None
        """
        print("Please log into Axiom")
        self.driver.get(self.base_url)
        WebDriverWait(self.driver, 300).until(
            EC.title_is("Axiom Elite - Dashboard"))
        print("Axiom Login Successful")

    def main_loop(self):
        """
        Main logic loop
        :return: None
        """
        self.driver.get(self.verifier_url)
        while True:
            wait_for_loading(self.driver)
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "VerifyRecordViewPort")))
            page = identify_page(self.driver)
            if page == "finished":
                return
            elif page in HANDLERS:
                result = HANDLERS[page](self.driver)
                if page.startswith("error"):
                    self.database.add_event(page)
                if result:
                    self.database.add_event(result)
            else:
                print(f"Unknown page: {page}")
                input("Press Enter to continue")
