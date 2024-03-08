from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium import webdriver

from browser_utilities.navigate_verifier import delete_record, skip_record
from matching_utilities.address_picker import select_address


def handle_normal(driver: webdriver) -> str:
    """
    Handle the normal page
    :param driver: webdriver
    :return: None
    """
    button_done = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "SubmitButton")))
    return_text = button_done.text
    button_done.click()
    if return_text == "Submit Match":
        print("Matched record")
        return "matched record"
    print("New record")
    return "new record"


def handle_bad_address(driver: webdriver) -> str:
    """
    Handle a bad address error
    :param driver: webdriver
    :return: "deleted record" or '' depending on the result of the operation
    """
    error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                        "and not(contains(@class, 'hidden'))]")
    error_icon = driver.find_elements(By.XPATH, error_icon_xpath)[0]
    address_elem_group = error_icon.find_element(By.XPATH, "../../../..")
    address1_elem = address_elem_group.find_element(By.XPATH, "./div[1]/div[2]/input[1]")
    address2_elem = address_elem_group.find_element(By.XPATH, "./div[2]/div[2]/input[1]")
    address_data = {
        "Address 1": address1_elem.get_attribute("value"),
        "Address 2": address2_elem.get_attribute("value"),
        "City": address_elem_group.find_element(By.XPATH, "./div[4]/div[2]/input[1]").get_attribute("value"),
        "State": address_elem_group.find_element(By.XPATH, "./div[5]/div[2]/input[1]").get_attribute("value"),
        "Zip": address_elem_group.find_element(By.XPATH, "./div[6]/div[2]/input[1]").get_attribute("value"),
    }
    best_address = select_address(address_data)
    if not best_address:
        delete_record(driver, "bad address")
        return "deleted record"
    elif best_address == "skip":
        skip_record(driver)
        return "skipped record"
    else:
        address1_elem.send_keys(Keys.CONTROL + "a")
        address1_elem.send_keys(best_address)
        address2_elem.clear()


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


def handle_bad_city(driver: webdriver):
    """
    Delete record with bad city
    :param driver: webdriver
    :return: "deleted record", since this condition always results in a deleted record
    """
    delete_record(driver, "bad address")
    return "deleted record"


def handle_bad_zip(driver: webdriver):
    """
    Delete record with bad zipcode
    :param driver: webdriver
    :return: "deleted record", since this condition always results in a deleted record
    """
    delete_record(driver, "bad address")
    return "deleted record"
