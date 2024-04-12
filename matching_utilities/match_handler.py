from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from rapidfuzz import fuzz
import unicodedata
import time
import re

from browser_utilities.navigate_verifier import skip_record


def handle_match_dialogue(driver: webdriver, thorough=False) -> str:
    """
    Handle the match dialogue by extracting the first row of data from a table.
    :param driver: Instance of webdriver to interact with the browser
    :param thorough: Boolean to indicate whether to use SQL queries to find the best match.
    :return: Dictionary mapping table column headers to the values of the first row.
    """
    # TODO: Implement the thorough status
    match_table = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "MatchListTable")))
    records = match_table.find_elements(By.XPATH, "./tbody/tr")
    incoming_prospect = {}
    potential_matches = []
    for record in records[1:]:
        while 'selected-value' not in record.get_attribute("class"):
            record.click()
            time.sleep(0.1)
        comparison_table = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "MatchComparisonTable")))
        rows = comparison_table.find_elements(By.XPATH, "./tbody/tr")

        # extract the values for the potential match
        potential_match = {}
        for row in rows:
            potential_match[row.find_element(By.XPATH, "./td[1]").text] = (
                row.find_element(By.XPATH, "./td[3]").text)
        potential_match["element"] = record
        potential_matches.append(potential_match)

        # extract the values for the incoming prospect
        if not incoming_prospect:
            for row in rows[1:]:
                incoming_prospect[row.find_element(By.XPATH, "./td[1]").text] = (
                    row.find_element(By.XPATH, "./td[2]").text)

    # decide the best match and act accordingly
    best_match = decide_best_match(incoming_prospect, potential_matches)
    if best_match == "skip":
        skip_record(driver)
        return "skip"
    elif best_match == "new record":
        button_new_record = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "NewRecordButton")))
        button_new_record.click()
        return ''
    elif isinstance(best_match, WebElement):
        select_match_element(driver, best_match)
    else:
        print("Unhandled case")
        print(type(best_match), best_match)


def decide_best_match(incoming_prospect: dict, potential_matches: list[dict], name_thresh=80) -> str | WebElement:
    """
    Decide the best match from a list of potential matches.
    :param incoming_prospect: Dictionary mapping column headers to values for the incoming prospect.
    :param potential_matches: List of dictionaries mapping column headers to values for potential matches.
    :param name_thresh: Threshold for the name similarity score.
    :return: Student_id of the best match.
    """
    # TODO: impliment some sort of system to match on imperfect keys,
    #  such as "Name" vs "Student Name" or "City" vs "Home City".  This
    #  will require a mapping of keys to their alternate keys.
    prospect_name = (process_name(incoming_prospect["First Name"],
                                  incoming_prospect["Last Name"]))
    for potential_match in potential_matches:
        match_name = process_name(potential_match["First Name"],
                                  potential_match["Last Name"])
        name_similarity = fuzz.token_set_ratio(prospect_name, match_name)
        if potential_match["Email"] == incoming_prospect["Email"]:
            if name_similarity <= name_thresh:
                return "skip"
            return potential_match["element"]
        elif potential_match["Address 1"] == incoming_prospect["Address 1"]:
            if name_similarity <= name_thresh:
                return "skip"
            return potential_match["element"]
        elif (potential_match["City"] == incoming_prospect["City"]
              and potential_match["Birth Date"] == incoming_prospect["Birth Date"]
              and name_similarity == 100):
            return potential_match["element"]
        elif (potential_match["City"] == incoming_prospect["City"]
              and potential_match["Birth Date"] == incoming_prospect["Birth Date"]
              and name_similarity >= name_thresh):
            return "skip"
        else:
            return "new record"


def select_match_element(driver: webdriver, elem: WebElement) -> None:
    """
    Select a match by the student_id.
    :param driver: Instance of webdriver to interact with the browser.
    :param elem: WebElement to select.
    :return: None
    """
    while 'selected-value' not in elem.get_attribute("class"):
        elem.click()
        time.sleep(.5)
    button_savematch = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "SaveMatchButton")))
    button_savematch.click()


def process_name(first_name: str, last_name: str) -> str:
    """
    Process the first and last name of a student.
    :param first_name: First name of the student.
    :param last_name: Last name of the student.
    :return: Processed name.
    """
    def _normalize_string(input_string: str) -> str:
        """
        Normalize a string by removing accents and non-alpha characters, and converting to lowercase.
        :param input_string: The string to normalize.
        :return: Normalized string.
        """
        nfkd_form = unicodedata.normalize('NFKD', input_string)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode()
        cleaned_string = re.sub(r'[^a-zA-Z ]', '', only_ascii).lower()
        return cleaned_string

    common_prefixes = {"mr", "mrs", "ms", "miss", "dr"}
    first_name = first_name.lower().strip()
    first_name = _normalize_string(first_name)
    first_name = first_name.split()
    first_name = [s for s in first_name if s not in common_prefixes]

    common_suffixes = {"jr", "sr", "ii", "iii", "iv", "v"}
    last_name = last_name.lower().strip()
    last_name = _normalize_string(last_name)
    last_name = last_name.split()
    last_name = [s for s in last_name if s not in common_suffixes]
    return f"{first_name[0]} {last_name[-1]}"
