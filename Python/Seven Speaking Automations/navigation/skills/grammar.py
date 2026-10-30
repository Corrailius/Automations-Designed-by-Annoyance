from utils.clicks import safe_click
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Only the "All grammar rules" list. The page also has a "Based on your frequent
# mistakes" carousel that uses the same button class but sits off-screen.
CARD_LOCATOR = (By.CSS_SELECTOR, ".grammarWorkshop__List .grammar-card")
LESSON_BUTTON = "button.image__actionArea"
COMPLETED_BADGE = ".list__completion"


class Grammar:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def get_cards(self):
        return self.wait.until(EC.presence_of_all_elements_located(CARD_LOCATOR))

    def get_lessons(self):
        return [card.find_element(By.CSS_SELECTOR, LESSON_BUTTON) for card in self.get_cards()]

    def ensure_open(self, recover):
        """Make sure the lesson list is displayed, calling `recover()` if not."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(CARD_LOCATOR)
            )
        except TimeoutException:
            print("Grammar list not displayed, navigating back to it...")
            recover()

    def is_completed(self, index):
        """True when the lesson card shows the green completed check."""
        card = self.get_cards()[index]
        return bool(card.find_elements(By.CSS_SELECTOR, COMPLETED_BADGE))

    def select_lesson(self, index):
        card = self.get_cards()[index]
        lesson = card.find_element(By.CSS_SELECTOR, LESSON_BUTTON)
        safe_click(self.driver, lesson)

    def open_quiz(self):
        print("Opening quiz...")

        locator = (By.CSS_SELECTOR, "button.sheet__quizButton")

        for _ in range(3):
            try:
                self.wait.until(EC.element_to_be_clickable(locator))

                safe_click(self.driver, self.driver.find_element(*locator))

                print("Quiz button clicked.")
                return

            except StaleElementReferenceException:
                continue

        raise RuntimeError("Could not click the quiz button.")
