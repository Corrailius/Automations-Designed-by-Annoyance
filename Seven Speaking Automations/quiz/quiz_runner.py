from quiz.choice_handler import ChoiceHandler
from quiz.fill_handler import FillHandler
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class QuizRunner:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

        self.handlers = [ChoiceHandler(), FillHandler()]

    def solve(self, questions):
        for index, question in enumerate(questions):
            variant = question["variant"]

            print(f"\nQuestion {index + 1}/{len(questions)}")
            print(f"Solving {variant} question...")

            handler = self.get_handler(question)

            if handler is None:
                print(f"Unsupported question type: {variant}")
                continue

            handler.solve(self.driver, question)

            self.validate()

            if index < len(questions):
                self.next_question()

        self.finish()

    def get_handler(self, question):
        for handler in self.handlers:
            if handler.supports(question):
                return handler

        return None

    def validate(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def next_question(self):
        next_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="submit"]:not([disabled])')
            )
        )

        next_button.click()

        print("Question completed.")

    def finish(self):
        continue_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[normalize-space()='Continue']]")
            )
        )

        continue_button.click()

        print("Quiz completed. Returned to Grammar Workshop.")
