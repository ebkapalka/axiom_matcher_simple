from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from selenium import webdriver
import sys

from browser_utilities.await_loading import wait_for_loading


def perform_login(driver: webdriver, login_url: str, credentials: dict, timeout=5) -> None:
    """
    Log into Axiom with the given credentials
    :param driver: webdriver
    :param login_url: url to login page
    :param credentials: dictionary of credentials
    :param timeout: time to wait for the elements
    :return: None
    """
    driver.get(login_url)
    button_login = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "Login")))
    input_username = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "UserName")))
    input_password = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "Password")))
    input_username.send_keys(credentials["username"])
    input_password.send_keys(credentials["password"])
    button_login.click()

    # handle entering verification code
    button_validate = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "ValidateBtn")))
    input_verification = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "SecurityPin")))
    input_verification.send_keys(credentials["verification"])
    button_validate.click()

    # verify login
    try:
        WebDriverWait(driver, timeout).until(
            EC.title_is("Axiom Elite - Dashboard"))
        return
    except Exception as e:
        print(type(e), e)
        sys.exit()


def identify_page(driver: webdriver) -> str:
    """
    Identify the current page
    :param driver: webdriver
    :return: string identifying the page
    """

    def element_has_non_null_text(xpath: str, parent_element: WebElement) -> WebElement | bool:
        """
        Check if an element has non-null text
        :param xpath: xpath of the element relative to the parent
        :param parent_element: parent element to start the search
        :return:
        """
        try:
            element = parent_element.find_element(By.XPATH, xpath)
            if element.text != "":
                return element
        except:
            pass
        return False

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
        error_row_xpath = "../../../div[1]"
        error_icon = driver.find_element(By.XPATH, error_icon_xpath)
        error_row = WebDriverWait(driver, 10).until(
            lambda _: element_has_non_null_text(error_row_xpath, error_icon))
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
    print(f"Deleting record: {reason}")

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
    print("Skipping record")
    button_skip = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "NavForwardButton")))
    button_skip.click()
