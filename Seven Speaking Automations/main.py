from authentication.sso import SSO
from config.settings import EMAIL, LOGIN_URL, PASSWORD
from navigation.menu import Menu
from navigation.skills.grammar import Grammar
from quiz.quiz_data import QuizData
from quiz.quiz_runner import QuizRunner
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main():

    print("=== 7Speaking Automation ===")
    print()

    print("Starting Firefox...")
    options = webdriver.FirefoxOptions()
    options.enable_bidi = True
    driver = webdriver.Firefox(options=options)

    try:
        print("Opening 7Speaking...")
        driver.get(LOGIN_URL)

        authentication = SSO(driver, EMAIL, PASSWORD)
        authentication.login()

        menu = Menu(driver)

        # ==========================================================
        # GRAMMAR
        # ==========================================================

        print("Opening General skills...")
        menu.open_general_skills()

        print("Opening Grammar Workshop...")
        menu.open_grammar()

        grammar = Grammar(driver)

        lessons = grammar.get_lessons()
        print(f"Found {len(lessons)} grammar lessons.")

        grammar.select_lesson(0)

        quiz_data = QuizData(driver)

        grammar.open_quiz()

        print("Quiz should now be open.")

        questions = quiz_data.get_questions()

        quiz_runner = QuizRunner(driver)
        quiz_runner.solve(questions)

        input("\nPress Enter to continue to Business Skills...")

        print("Opening Professional competencies...")

        professional_competencies = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//li[contains(@class, 'navigation__item')][.//p[normalize-space()='Professional competencies']]"
                )
            )
        )

        professional_competencies.click()

        print("Professional competencies opened.")

        # ==========================================================
        # BUSINESS SKILLS - TEMPORARY TEST
        # ==========================================================

        print("\n=== Business Skills Test ===")

        wait = WebDriverWait(driver, 30)

        print("Opening Business Skills...")

        business_skills = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'a[href="/workshop/professionnal-content/business-skills"]',
                )
            )
        )

        business_skills.click()

        print("Business Skills opened.")

        # ----------------------------------------------------------
        # TEMPORARY: open Sample letter n°1
        # ----------------------------------------------------------

        print("Opening Sample letter n°1...")

        activity = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//h3[normalize-space()='Sample letter n°1']")
            )
        )

        activity.click()

        print("Sample letter n°1 opened.")

        # ----------------------------------------------------------
        # TEMPORARY: open Comprehension test
        # ----------------------------------------------------------

        print("Opening Comprehension test...")

        comprehension_test = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='button'][.//p[normalize-space()='Comprehension test']]",
                )
            )
        )

        # QuizData must listen BEFORE the API request is triggered.
        business_quiz_data = QuizData(driver)

        comprehension_test.click()

        print("Comprehension test opened.")

        # ----------------------------------------------------------
        # Get and solve Business Skills quiz
        # ----------------------------------------------------------

        business_questions = business_quiz_data.get_questions()

        print("Business Skills quiz received.")

        business_quiz_runner = QuizRunner(driver)
        business_quiz_runner.solve(business_questions)

        print("Business Skills quiz completed.")

        input("\nPress Enter to close...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
