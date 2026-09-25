from authentication.sso import SSO
from config.settings import EMAIL, LOGIN_URL, PASSWORD
from navigation.menu import Menu
from navigation.skills.grammar import Grammar
from quiz.quiz_data import QuizData
from quiz.quiz_runner import QuizRunner
from selenium import webdriver


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

        input("\nPress Enter to close...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
