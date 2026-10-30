from config.settings import HOME_URL
from quiz import selectors as S
from utils.clicks import safe_click
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

GENERAL_SKILLS = (By.XPATH, "//p[normalize-space()='General skills']")
GRAMMAR_WORKSHOP = (By.XPATH, "//span[normalize-space()='Grammar workshop']")

PROFESSIONAL = (
    By.XPATH,
    "//li[contains(@class, 'navigation__item')]"
    "[.//p[normalize-space()='Professional competencies']]",
)
BUSINESS_SKILLS = (
    By.CSS_SELECTOR,
    'a[href="/workshop/professionnal-content/business-skills"]',
)

MIN_VIEWPORT_HEIGHT = 400


class Menu:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ------------------------------------------------------------------
    def ensure_window(self):
        """Restore the browser window if it was minimised or collapsed.

        A collapsed window makes every element 'not displayed', so all
        clicks fail with 'could not be scrolled into view'.
        """
        try:
            height = self.driver.execute_script("return window.innerHeight;")
            if height is not None and height < MIN_VIEWPORT_HEIGHT:
                print("Browser window is too small, restoring it...")
                self.driver.set_window_rect(0, 0, 1400, 900)
                self.driver.maximize_window()
        except Exception:
            pass

    def go_home(self):
        """Hard reset: reload the home page. Used to recover from any odd state."""
        self.driver.get(HOME_URL)
        self.ensure_window()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, S.HOME_MARKER))
        )

    # ------------------------------------------------------------------
    def _is_visible(self, locator):
        try:
            return any(e.is_displayed() for e in self.driver.find_elements(*locator))
        except Exception:
            return False

    def _expand(self, parent, child):
        """Open a collapsible menu entry, only if its child is not already visible.

        The entries are toggles: clicking an already open one would close it.
        """
        self.ensure_window()
        if self._is_visible(child):
            return

        for _ in range(3):
            safe_click(self.driver, self.wait.until(EC.element_to_be_clickable(parent)))
            try:
                WebDriverWait(self.driver, 4).until(lambda d: self._is_visible(child))
                return
            except TimeoutException:
                continue  # it may have been open and just closed, click again

        raise TimeoutException(f"Menu entry {child} never became visible.")

    def _click(self, locator):
        safe_click(self.driver, self.wait.until(EC.element_to_be_clickable(locator)))

    # ------------------------------------------------------------------
    def open_general_skills(self):
        self._expand(GENERAL_SKILLS, GRAMMAR_WORKSHOP)

    def open_grammar(self):
        self.open_general_skills()  # harmless when already open
        self._click(GRAMMAR_WORKSHOP)

    def open_professional_competencies(self):
        self._expand(PROFESSIONAL, BUSINESS_SKILLS)

    def open_business_skills(self):
        self.open_professional_competencies()  # harmless when already open
        self._click(BUSINESS_SKILLS)
