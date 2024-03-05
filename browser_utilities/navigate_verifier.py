from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import sys

from browser_utilities.await_loading import wait_for_loading


def goto_verifier(driver: webdriver):
    """
    Go to the verifier page
    :param driver: webdriver
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

    if "https://axiom-elite-prod.msu.montana.edu/Dashboard" not in driver.current_url:
        driver.get("https://axiom-elite-prod.msu.montana.edu/Dashboard")
    wait_for_loading(driver)
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
    match_dialogue = driver.find_element(By.CLASS_NAME, "bs-matchstatus-modal")
    final_record_message = driver.find_element(By.ID, "FinalRecordMessage")
    if match_dialogue.get_attribute("aria-hidden") == "false":
        return "match dialogue"
    elif final_record_message.get_attribute("style") == "display: block;":
        return "finished"
    else:
        error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                            "and not(contains(@class, 'hidden'))]")
        error_icons = driver.find_elements(By.XPATH, error_icon_xpath)
        if error_icons:
            error_row = error_icons[0].find_element(By.XPATH, "../../../div[1]")
            return f"error - {error_row.text}"
        else:
            return "normal"


def delete_record(driver: webdriver, reason: str) -> None:
    """
    Delete the current record, entering the reason
    :param driver: webdriver
    :param reason: explanation for deletion
    :return: None
    """
    button_delete = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "DeleteButton")))
    button_delete.click()
    input_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "DeleteForm")))
    input_box.send_keys(reason)
    button_confirm = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "DeleteRecord")))
    button_confirm.click()
