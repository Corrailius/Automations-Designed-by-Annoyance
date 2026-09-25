from selenium.common.exceptions import StaleElementReferenceException
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
        lesson = lessons[index]

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", lesson
        )

        self.wait.until(lambda driver: lesson.is_displayed() and lesson.is_enabled())

        lesson.click()


    def open_quiz(self):
        print("Opening quiz...")

        locator = (By.CSS_SELECTOR, "button.sheet__quizButton")

        for _ in range(3):
            try:
                self.wait.until(EC.element_to_be_clickable(locator))

                self.driver.find_element(*locator).click()

                print("Quiz button clicked.")
                return

            except StaleElementReferenceException:
                continue

        raise RuntimeError("Could not click the quiz button.")
