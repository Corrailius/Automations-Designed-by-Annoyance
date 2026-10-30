import random

from quiz import selectors as S
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ChoiceHandler:
    def supports(self, question):
        return question["variant"] == "choice"

    def solve(self, driver, question, correct=True):
        options = question["answerOptions"]["options"]
        answers = question["answerOptions"]["answer"]

        correct_ids = {answer["id"] for answer in answers}
        correct_indexes = [
            i for i, option in enumerate(options) if option["id"] in correct_ids
        ]

        if correct:
            targets = correct_indexes
        else:
            wrong_indexes = [i for i in range(len(options)) if i not in correct_indexes]
            targets = [random.choice(wrong_indexes)] if wrong_indexes else correct_indexes

        if not targets:
            raise RuntimeError("Could not find the answer option for this question.")

        for index in targets:
            button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, S.CHOICE_BUTTON.format(index=index))
                )
            )
            button.click()

        print("Answer selected." if correct else "Wrong answer selected (on purpose).")
