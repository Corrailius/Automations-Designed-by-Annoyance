from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Grammar:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def get_lessons(self):
        return self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "button.image__actionArea")
            )
        )

    def select_lesson(self, index):
        lessons = self.get_lessons()

        lessons[index].click()