from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import time


def handle_match_dialogue(driver: webdriver) -> str:
    """
    Handle the match dialogue by extracting the first row of data from a table.
    :param driver: Instance of webdriver to interact with the browser.
    :return: Dictionary mapping table column headers to the values of the first row.
    """
    match_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "MatchListTable")))
    records = match_table.find_elements(By.XPATH, "./tbody/tr")
    incoming_prospect = {}
    potential_matches = []
    for record in records[1:]:
        record.click()
        comparison_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MatchComparisonTable")))
        rows = comparison_table.find_elements(By.XPATH, "./tbody/tr")

        # extract the values for the potential match
        potential_match = {}
        for row in rows[1:]:
            potential_match[row.find_element(By.XPATH, "./td[1]").text] = (
                row.find_element(By.XPATH, "./td[3]").text)
        potential_matches.append(potential_match)

        # extract the values for the incoming prospect
        if not incoming_prospect:
            for row in rows[1:]:
                incoming_prospect[row.find_element(By.XPATH, "./td[1]").text] = (
                    row.find_element(By.XPATH, "./td[2]").text)
    print(incoming_prospect)
    for potential_match in potential_matches:
        print(potential_match)
    time.sleep(100000000)
    # TODO: return only "skipped" or "".  Any other return value will
    #  be handled by the normal handler after this dialogue is closed.


def decide_best_match(incoming_prospect: dict, potential_matches: list[dict]) -> str:
    """
    Decide the best match from a list of potential matches.
    :param incoming_prospect: Dictionary mapping column headers to values for the incoming prospect.
    :param potential_matches: List of dictionaries mapping column headers to values for potential matches.
    :return: Student_id of the best match.
    """
    pass
