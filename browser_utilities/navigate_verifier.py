from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver


def identify_page(driver: webdriver) -> str:
    """
    Identify the current page
    :param driver: webdriver
    :return: string identifying the page
    """
    match_dialogue = driver.find_element(By.CLASS_NAME, "bs-matchstatus-modal")
    if match_dialogue.get_attribute("aria-hidden") == "false":
        return "match dialogue"
    else:
        error_icon_xpath = ("//i[contains(@class, 'sourcefield-error') "
                            "and not(contains(@class, 'hidden'))]")
        error_icons = driver.find_elements(By.XPATH, error_icon_xpath)
        if error_icons:
            error_row = error_icons[0].find_element(By.XPATH, "../../../div[1]")
            # error_row_input = error_row.find_element(By.XPATH, "./../div[2]/input[1]")
            return f"error - {error_row.text}"
        else:
            return "normal"
