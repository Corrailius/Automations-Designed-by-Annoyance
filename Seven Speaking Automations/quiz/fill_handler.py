from selenium.webdriver.common.by import By


class FillHandler:
    def supports(self, question):
        return question["variant"] == "fill"

    def solve(self, driver, question):
        answer = question["answerOptions"]["answer"][0]["value"]

        input_field = driver.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Enter your reply"]'
        )

        input_field.send_keys(answer)

        print(f"Filled answer: {answer}")
