from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Menu:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open_general_skills(self):
        general_skills = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//p[normalize-space()='General skills']")
            )
        )

        general_skills.click()

    def open_grammar(self):
        grammar = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[normalize-space()='Grammar workshop']")
            )
        )

        grammar.click()
