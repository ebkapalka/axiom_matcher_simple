from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver


def wait_for_loading(driver: webdriver, timeout=300):
    """
    Wait for all loading bars / spinners / icons to disappear
    :param driver: webdriver
    :param timeout: int
    :return: None
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "loader-container")))
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "progress-bar")))
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "knyrie")))
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "fullpage-overlay")))
        WebDriverWait(driver, timeout).until(
            lambda d: _class_no_longer_present(d, (By.CSS_SELECTOR, "input.updating")))
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "Form3")))
    except TimeoutException:
        driver.refresh()
        wait_for_loading(driver, timeout)


def _class_no_longer_present(driver: webdriver, selector: tuple):
    elements = driver.find_elements(*selector)
    return len(elements) == 0
