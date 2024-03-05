from selenium.webdriver import ActionChains
from selenium import webdriver
from pprint import pprint
import atexit


class AxiomDriver:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.actions = ActionChains(self.driver)
        self.stats = {
            "new person": 0,
            "skip": 0,
            "match": 0,
        }
        self.await_login()
        atexit.register(self.print_stats)
        self.main_loop()

    def await_login(self):
        ...

    def main_loop(self):
        ...

    def print_stats(self):
        pprint(self.stats)
