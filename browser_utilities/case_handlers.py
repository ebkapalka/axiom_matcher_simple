from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver

from browser_utilities.navigate_verifier import delete_record


def handle_normal(driver: webdriver) -> str:
    """
    Handle the normal page
    :param driver: webdriver
    :return: None
    """
    button_done = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "SubmitButton")))
    return_text = button_done.text
    # button_done.click()
    # TODO: uncomment the above line when ready to submit records
    if return_text == "Submit Match":
        return "matched record"
    return "new record"



def handle_bad_address(driver: webdriver) -> str:
    error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                        "and not(contains(@class, 'hidden'))]")
    error_icon = driver.find_elements(By.XPATH, error_icon_xpath)[0]
    address_elem_group = error_icon.find_element(By.XPATH, "../../../..")
    address_data = {
        "Address 1": address_elem_group.find_element(By.XPATH, "./div[1]/div[2]/input[1]").get_attribute("value"),
        "Address 2": address_elem_group.find_element(By.XPATH, "./div[2]/div[2]/input[1]").get_attribute("value"),
        "City": address_elem_group.find_element(By.XPATH, "./div[4]/div[2]/input[1]").get_attribute("value"),
        "State": address_elem_group.find_element(By.XPATH, "./div[5]/div[2]/input[1]").get_attribute("value"),
        "Zip": address_elem_group.find_element(By.XPATH, "./div[6]/div[2]/input[1]").get_attribute("value"),
    }
    print(address_data)
    # error_row = error_icon.find_element(By.XPATH, "../../../div[1]")
    # error_row_input = error_row.find_element(By.XPATH, "./../div[2]/input[1]")
    # This one could result in a deleted record or a new record


def handle_bad_firstname(driver: webdriver) -> str:
    """
    Delete record with bad first name
    :param driver: webdriver
    :return: "deleted record", since this condition always results in a deleted record
    """
    delete_record(driver, "bad name")
    return "deleted record"


def handle_bad_lastname(driver: webdriver) -> str:
    """
    Delete record with bad last name
    :param driver: webdriver
    :return: "deleted record", since this condition always results in a deleted record
    """
    delete_record(driver, "bad name")
    return "deleted record"


def handle_bad_ceeb(driver: webdriver) -> str:
    """
    Handle the bad ceeb page
    :param driver: webdriver
    :return: None
    """
    error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                        "and not(contains(@class, 'hidden'))]")
    error_icons = driver.find_elements(By.XPATH, error_icon_xpath)
    error_row = error_icons[0].find_element(By.XPATH, "../../../div[1]")
    error_row_input = error_row.find_element(By.XPATH, "./../div[2]/input[1]")
    error_row_input.clear()
    return ''  # this doesn't necessarily result in a new or deleted record
