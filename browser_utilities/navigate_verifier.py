from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from selenium import webdriver
import time
import sys

from browser_utilities.await_loading import wait_for_loading


def goto_verifier(driver: webdriver, base_url: str):
    """
    Go to the verifier page
    :param driver: webdriver
    :param base_url: base url of the site
    :return: None
    """
    def _button_with_color_darkgray(dr: webdriver) -> WebElement | bool:
        """
        Find the button with the darkgray color
        :param dr: webdriver
        :return:
        """
        try:
            buttons = dr.find_elements(By.XPATH, '//button[@title="Card View" or @title="Table View"]')
            for button in buttons:
                if "color: darkgray;" in button.get_attribute("style"):
                    return button
        except Exception as e:
            print(type(e), e)
        return False

    # ensure that the current page is the dashboard
    url = urljoin(base_url, "/Dashboard")
    if url not in driver.current_url:
        driver.get(url)
    wait_for_loading(driver)

    # determine which dashboard view is currently active
    current_tab = WebDriverWait(driver, 10).until(
        _button_with_color_darkgray).get_attribute("title")
    if current_tab == "Card View":
        title_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[text()='01 Bozeman UG EAB Prospect']")))
        body_elem = title_elem.find_element(By.XPATH, './../../../div[2]')
        verifier = body_elem.find_element(By.XPATH, './div[1]/div[2]')
        verifier_count = verifier.text.strip()
    else:
        title_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//td[text()='01 Bozeman UG EAB Prospect']")))
        verifier = title_elem.find_element(By.XPATH, './../td[2]')
        verifier_count = verifier.text.strip()

    # click the verifier if there are records to process
    print(f"Records to process: {verifier_count}")
    if int(verifier_count) > 0:
        verifier.click()
    else:
        print("No records to process")
        sys.exit()


def identify_page(driver: webdriver) -> str:
    """
    Identify the current page
    :param driver: webdriver
    :return: string identifying the page
    """
    # check for the match dialogue
    try:
        match_dialogue = driver.find_element(By.CLASS_NAME, "bs-matchstatus-modal")
        if match_dialogue.get_attribute("aria-hidden") == "false":
            return "match dialogue"
    except NoSuchElementException:
        pass

    # check for the final record message
    try:
        final_record_message = driver.find_element(By.ID, "FinalRecordMessage")
        if final_record_message.get_attribute("style") == "display: block;":
            return "finished"
    except NoSuchElementException:
        pass

    # check for errors
    try:
        error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                            "and not(contains(@class, 'hidden'))]")
        error_icon = driver.find_element(By.XPATH, error_icon_xpath)
        error_row = error_icon.find_element(By.XPATH, "../../../div[1]")
        return f"error - {error_row.text}"
    # if no errors, return "normal"
    except NoSuchElementException:
        return "normal"


def delete_record(driver: webdriver, reason: str, timeout=10) -> None:
    """
    Delete the current record, entering the reason
    :param driver: webdriver
    :param reason: explanation for deletion
    :param timeout: time to wait for the elements
    :return: None
    """
    # click delete button
    button_delete = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "DeleteButton")))
    button_delete.click()

    # enter text into the delete notes box
    input_box = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "DeleteNotes")))
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "DeleteNotes")))
    input_box.click()
    input_box.send_keys(reason)

    # confirm the deletion
    button_confirm = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "DeleteRecord")))
    button_confirm.click()


def skip_record(driver: webdriver, timeout=10) -> None:
    """
    Skip the current record
    :param driver: webdriver
    :param timeout: time to wait for the element to be clickable
    :return: None
    """
    button_skip = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "NavForwardButton")))
    button_skip.click()
