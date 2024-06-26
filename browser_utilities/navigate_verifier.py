from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver


def identify_page(driver: webdriver) -> str:
    """
    Identify the current page
    :param driver: webdriver
    :return: string identifying the page
    """

    # TODO: move all of these special EC functions to their own file
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


def delete_record(driver: webdriver, reason: str, timeout=10, override=False) -> None:
    """
    Delete the current record, entering the reason
    :param driver: webdriver
    :param reason: explanation for deletion
    :param timeout: time to wait for the elements
    :param override: flag to skip the record without deletion
    :return: None
    """
    # check if the record should be skipped
    if override:
        skip_record(driver)
        return

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
