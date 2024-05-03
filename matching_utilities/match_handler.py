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

PATTERN = re.compile(r'\D')


def handle_match_dialogue(driver: webdriver, thorough=False) -> str:
    """
    Handle the match dialogue by extracting the first row of data from a table.
    :param driver: Instance of webdriver to interact with the browser
    :param thorough: Boolean to indicate whether to use SQL queries to find the best match.
    :return: Dictionary mapping table column headers to the values of the first row.
    """
    # TODO: Implement the thorough status
    js_script = """
        const waitForElement = async (selector, timeout = 30000) => {
            const startTime = new Date().getTime();
            return new Promise((resolve, reject) => {
                const interval = setInterval(() => {
                    const elapsedTime = new Date().getTime() - startTime;
                    const element = document.querySelector(selector);
                    if (element) {
                        clearInterval(interval);
                        resolve(element);
                    } else if (elapsedTime >= timeout) {
                        clearInterval(interval);
                        reject('Element ' + selector + ' not found within ' + timeout + 'ms');
                    }
                }, 100);
            });
        };

        const extractData = async () => {
            const matchTable = await waitForElement('#MatchListTable');
            const records = matchTable.querySelectorAll('tbody tr');
            const potentialMatches = [];
            let incomingProspect = {};

            for (let i = 1; i < records.length; i++) {
                const record = records[i];
                record.click();  // Simulate the click

                const comparisonTable = await waitForElement('#MatchComparisonTable');
                const rows = comparisonTable.querySelectorAll('tbody tr');
                const potentialMatch = {};

                for (const row of rows) {
                    const key = row.cells[0].innerText;
                    const matchValue = row.cells[2].innerText;
                    potentialMatch[key] = matchValue;
                }
                potentialMatch['elementSelector'] = '#MatchListTable tbody tr:nth-child(' + (i + 1) + ')';
                potentialMatches.push(potentialMatch);

                if (Object.keys(incomingProspect).length === 0) {
                    for (const row of rows) {
                        const key = row.cells[0].innerText;
                        const prospectValue = row.cells[1].innerText;
                        incomingProspect[key] = prospectValue;
                    }
                }
            }
            return { 'potentialMatches': potentialMatches, 'incomingProspect': incomingProspect };
        };

        return extractData();
    """
    incoming_prospect, potential_matches = (
        driver.execute_script(js_script).values())

    # find the elements for the potential matches
    for match in potential_matches:
        selector = match['elementSelector']
        match['element'] = driver.find_element(
            By.CSS_SELECTOR, selector)
        del match['elementSelector']

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

    def _get_with_fallback(d: dict, key: str, fallback_key: str) -> str:
        value = d[key] if key in d else d[fallback_key]
        return str(value).strip().lower()

    prospect_values = {
        "first_name": _get_with_fallback(incoming_prospect,"First Name", "Student First Name"),
        "last_name": _get_with_fallback(incoming_prospect,"Last Name", "Student Last Name"),
        "email": _get_with_fallback(incoming_prospect,"Email", "Student E-mail Address"),
        "addr1": _get_with_fallback(incoming_prospect,"Address 1", "Street Address"),
        "birthday": _get_with_fallback(incoming_prospect,"Birth Date", "Date of Birth (MMDDYYYY)"),
        "city": incoming_prospect.get("City", None),
        "phone": incoming_prospect.get("Phone", None)
    }
    prospect_name = (process_name(prospect_values["first_name"], prospect_values["last_name"]))

    for potential_match in potential_matches:
        match_values = {
            "first_name": _get_with_fallback(potential_match,"First Name", "Student First Name"),
            "last_name": _get_with_fallback(potential_match,"Last Name", "Student Last Name"),
            "email": _get_with_fallback(potential_match,"Email", "Student E-mail Address"),
            "addr1": _get_with_fallback(potential_match,"Address 1", "Street Address"),
            "birthday": _get_with_fallback(potential_match,"Birth Date", "Date of Birth (MMDDYYYY)"),
            "city": potential_match.get("City", None),
            "phone": potential_match.get("Phone", None)
        }
        match_name = (process_name(match_values["first_name"], match_values["last_name"]))
        name_similarity = fuzz.token_set_ratio(prospect_name, match_name)
        if (prospect_values["email"] and match_values["email"]
                and prospect_values["email"] == match_values["email"]):
            if name_similarity <= name_thresh:
                return "skip"
            return potential_match["element"]
        elif (prospect_values["phone"] and match_values["phone"]
              and PATTERN.sub('', str(prospect_values["phone"])) ==
              PATTERN.sub('', str(match_values["phone"]))):
            if name_similarity <= name_thresh:
                return "skip"
            return potential_match["element"]
        elif (prospect_values["addr1"] and match_values["addr1"]
              and prospect_values["addr1"] == match_values["addr1"]):
            if name_similarity <= name_thresh:
                return "skip"
            return potential_match["element"]
        elif (prospect_values["city"] and match_values["city"]
              and prospect_values["city"] == match_values["city"]
              and prospect_values["birthday"] == match_values["birthday"]
              and name_similarity == 100):
            return potential_match["element"]
        elif (prospect_values["city"] and match_values["city"]
              and prospect_values["city"] == match_values["city"]
              and prospect_values["birthday"] == match_values["birthday"]
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
