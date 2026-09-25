from selenium.webdriver.common.by import By


class ChoiceHandler:
    def supports(self, question):
        return question["variant"] == "choice"

    def solve(self, driver, question):
        answer_id = question["answerOptions"]["answer"][0]["id"]

        for index, option in enumerate(question["answerOptions"]["options"]):
            if option["id"] == answer_id:
                driver.find_element(By.CSS_SELECTOR, f'button[value="{index}"]').click()

                print("Answer selected.")
                return
