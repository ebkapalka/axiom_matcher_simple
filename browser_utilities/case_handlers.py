from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver


def handle_normal(driver: webdriver) -> None:
    """
    Handle the normal page
    :param driver: webdriver
    :return: None
    """
    button_new_record = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "SubmitButton")))
    # button_new_record.click()
    # TODO: uncomment the above line when ready to submit records


def handle_bad_address(driver: webdriver) -> str:
    ...


def handle_bad_firstname(driver: webdriver) -> str:
    ...


def handle_bad_lastname(driver: webdriver) -> str:
    ...


def handle_bad_ceeb(driver: webdriver) -> None:
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
