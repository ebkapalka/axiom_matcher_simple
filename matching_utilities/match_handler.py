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
    for record in records[1:]:
        record.click()
        comparison_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MatchComparisonTable")))
        rows = comparison_table.find_elements(By.XPATH, "./tbody/tr")
        for row in rows:
            # TODO: extract the data from the table
            print(row.text)
        print()
    time.sleep(100000000)
    # TODO: return only "skipped" or "".  Any other return value will
    #  be handled by the normal handler after this dialogue is closed.
