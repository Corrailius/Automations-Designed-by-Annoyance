from quiz import selectors as S
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FillHandler:
    def supports(self, question):
        return question["variant"] == "fill"

    def solve(self, driver, question, correct=True):
        answer = str(question["answerOptions"]["answer"][0]["value"])

        if not correct:
            # Same trick as the bot: repeat the last character.
            answer = answer + answer[-1:] if answer else "x"

        input_field = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, S.FILL_INPUT))
        )
        input_field.clear()
        input_field.send_keys(answer)

        print(f"Filled answer: {answer}")
