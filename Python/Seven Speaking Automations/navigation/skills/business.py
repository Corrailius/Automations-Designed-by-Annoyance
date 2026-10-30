from quiz import selectors as S
from utils.clicks import safe_click
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def xpath_literal(text):
    """Quote any string for use inside an XPath expression."""
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    parts = text.split("'")
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"


class NoQuizAvailable(Exception):
    """The activity page has no Comprehension test."""


class BusinessSkills:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ------------------------------------------------------------------
    # Category grid (Letters, Phoning, Meetings, ...)
    # ------------------------------------------------------------------
    def wait_view(self, timeout=20):
        """'grid' (category cards), 'category' (activity cards) or None."""

        def detect(driver):
            if driver.find_elements(By.CSS_SELECTOR, S.BUSINESS_CATEGORY_TITLE):
                return "grid"
            if driver.find_elements(By.CSS_SELECTOR, S.BUSINESS_ACTIVITY_TITLE):
                return "category"
            return False

        try:
            return WebDriverWait(self.driver, timeout).until(detect)
        except TimeoutException:
            return None

    def list_categories(self):
        titles = []
        for element in self.driver.find_elements(
            By.CSS_SELECTOR, S.BUSINESS_CATEGORY_TITLE
        ):
            text = element.text.strip()
            if text and text not in titles:
                titles.append(text)
        return titles

    def open_category(self, name):
        locator = (
            By.XPATH,
            f"//h3[contains(@class, 'previewGris__title')]"
            f"[normalize-space()={xpath_literal(name)}]",
        )
        element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(locator)
        )
        safe_click(self.driver, element)

        # Wait until the category's activity cards are there.
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, S.BUSINESS_ACTIVITY_TITLE)
            )
        )
        print(f"Category opened: {self.driver.current_url}")

    # ------------------------------------------------------------------
    def list_activities(self):
        """Titles of every activity card inside the open category (page order)."""
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, S.BUSINESS_ACTIVITY_TITLE)
                )
            )
        except TimeoutException:
            return []
        titles = []
        for element in self.driver.find_elements(
            By.CSS_SELECTOR, S.BUSINESS_ACTIVITY_TITLE
        ):
            text = element.text.strip()
            if text and text not in titles:
                titles.append(text)
        return titles

    def _reset_windows(self):
        """Back to a single window: lessons may open in a new tab."""
        try:
            handles = self.driver.window_handles
            for extra in handles[1:]:
                self.driver.switch_to.window(extra)
                self.driver.close()
            self.driver.switch_to.window(handles[0])
        except Exception:
            pass

    def _wait_for_lesson(self, handles_before, timeout=15):
        """After clicking a card: follow a new tab, wait for the /document/ page."""

        def ready(driver):
            new = [h for h in driver.window_handles if h not in handles_before]
            if new:
                driver.switch_to.window(new[-1])
                print("Lesson opened in a new tab.")
            return "/document/" in driver.current_url

        try:
            WebDriverWait(self.driver, timeout).until(ready)
        except TimeoutException:
            print(f"Warning: lesson page not detected (url: {self.driver.current_url}).")

    def open_activity(self, title, recover):
        """Click an activity by title. Calls `recover()` and retries once on failure."""
        locator = (
            By.XPATH,
            f"//h3[normalize-space()={xpath_literal(title)}]",
        )
        for attempt in range(2):
            try:
                self._reset_windows()
                element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(locator)
                )
                before = list(self.driver.window_handles)
                safe_click(self.driver, element)
                self._wait_for_lesson(before)
                return
            except TimeoutException:
                if attempt == 1:
                    raise
                print("Business Skills list not displayed, navigating back...")
                recover()

    def _find_comprehension_tab(self, driver):
        """First displayed 'Comprehension test' tab, else False."""
        for by, selector in (
            (By.CSS_SELECTOR, S.COMPREHENSION_TAB_CSS),
            (By.XPATH, S.COMPREHENSION_TAB_XPATH),
        ):
            for element in driver.find_elements(by, selector):
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    continue
        return False

    def open_comprehension_test(self):
        """Click the 'Comprehension test' tab in the lesson page header."""
        print("Opening Comprehension test...")
        try:
            tab = WebDriverWait(self.driver, 20).until(self._find_comprehension_tab)
        except TimeoutException:
            raise NoQuizAvailable(
                "No 'Comprehension test' on this activity "
                f"(url: {self.driver.current_url})."
            )
        safe_click(self.driver, tab)
