from selenium import webdriver

from authentication.sso import SSO
from config.settings import EMAIL, LOGIN_URL, PASSWORD
from navigation.menu import Menu
from navigation.skills.grammar import Grammar


def main():
    print("=== 7Speaking Automation ===")
    print()

    print("Starting Firefox...")

    driver = webdriver.Firefox()

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

        input("Press Enter to close...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
