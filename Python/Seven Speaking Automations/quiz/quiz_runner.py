import time

from quiz import selectors as S
from quiz.choice_handler import ChoiceHandler
from quiz.fill_handler import FillHandler
from quiz.text import normalize
from utils.deadline import Deadline
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UnsupportedQuestion(RuntimeError):
    pass


class QuizRunner:
    def __init__(self, driver, planner, pacing, deadline=None):
        self.driver = driver
        self.planner = planner
        self.pacing = pacing
        self.deadline = deadline or Deadline(None)
        self.wait = WebDriverWait(driver, 30)

        self.handlers = [ChoiceHandler(), FillHandler()]

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def solve(self, quiz, retake=False):
        """Solve a quiz. `quiz` is the quiz.cfc payload (or a list of questions).

        `retake=True` replays an already completed quiz: the saved answers of the
        previous attempt are ignored and every question is answered again.
        """
        payload = quiz if isinstance(quiz, dict) else {"questions": {"data": quiz}}
        questions = payload["questions"]["data"]
        total = len(questions)

        summary = {"correct": 0, "wrong": 0, "skipped": 0}
        done_ids = set()

        self._wait_for_quiz_screen()

        # Hard guard so a stuck page can never loop forever.
        for _ in range(total * 3 + 5):
            self.deadline.check()
            if self.is_finished() or len(done_ids) >= total:
                break

            question = self.pick_question(questions, done_ids)
            if question is None:
                break

            variant = question["variant"]
            print(f"\nQuestion {len(done_ids) + 1}/{total}")
            print(f"Solving {variant} question...")

            previous_title = self.current_title()

            if not retake and self._already_answered(question):
                print("Already answered earlier, moving on.")
                self._click_next()
                summary["skipped"] += 1
            else:
                handler = self.get_handler(question)
                if handler is None:
                    raise UnsupportedQuestion(
                        f"Unsupported question type: {variant}. Answer it manually."
                    )

                think = min(
                    self.pacing.think_time(payload, total), self.deadline.remaining()
                )
                if think > 0:
                    print(f"Thinking for {think:.1f}s...")
                    self.pacing.wait(think)

                correct = self.planner.next_is_correct()
                self.deadline.check()
                handler.solve(self.driver, question, correct=correct)

                self.validate()
                self._click_next()
                summary["correct" if correct else "wrong"] += 1

            done_ids.add(question["id"])
            print("Question completed.")
            self._wait_for_progress(previous_title)

        self.finish()

        print(
            f"Quiz summary: {summary['correct']} right, "
            f"{summary['wrong']} wrong on purpose, {summary['skipped']} skipped."
        )
        return summary

    # ------------------------------------------------------------------
    # Question matching (the bot matches page title <-> API question)
    # ------------------------------------------------------------------
    def get_handler(self, question):
        for handler in self.handlers:
            if handler.supports(question):
                return handler
        return None

    def current_title(self):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, S.QUESTION_TITLE)
            return elements[0].text.strip() if elements else None
        except StaleElementReferenceException:
            return None

    def pick_question(self, questions, done_ids):
        remaining = [q for q in questions if q["id"] not in done_ids]
        if not remaining:
            return None

        title = normalize(self.current_title())
        if title:
            for question in remaining:
                if normalize(question.get("question")) == title:
                    return question
            for question in remaining:
                other = normalize(question.get("question"))
                if other and (title in other or other in title):
                    return question
            print("Warning: page title not matched, falling back to question order.")

        return remaining[0]

    @staticmethod
    def _already_answered(question):
        return question.get("useranswer") not in (None, "", 0, "0")

    # ------------------------------------------------------------------
    # Page state
    # ------------------------------------------------------------------
    def is_finished(self):
        d = self.driver
        try:
            return bool(
                d.find_elements(By.CSS_SELECTOR, S.RESULT_CONTAINER)
                or d.find_elements(By.XPATH, S.CONTINUE_BUTTON_XPATH)
            )
        except StaleElementReferenceException:
            return False

    def _wait_for_quiz_screen(self):
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: self.current_title() or self.is_finished()
            )
        except TimeoutException:
            print("Warning: question title not found, continuing anyway.")

    def _wait_for_progress(self, previous_title, timeout=15):
        """Wait until the page moved on to the next question (or the results)."""
        previous = normalize(previous_title)
        if not previous:
            time.sleep(1.5)
            return

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.is_finished():
                return
            title = self.current_title()
            if title and normalize(title) != previous:
                return
            time.sleep(0.2)
        # Same title twice in a row is legal, the caller tracks done ids itself.

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------
    def _submit_label(self):
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, S.SUBMIT_BUTTON)
            return buttons[0].text.strip() if buttons else None
        except StaleElementReferenceException:
            return ""

    def _label_changed(self, label, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            current = self._submit_label()
            if current is None or current != label:
                return True
            time.sleep(0.1)
        return False

    def _click_submit(self):
        button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, S.SUBMIT_BUTTON_ENABLED))
        )
        label = button.text.strip()
        button.click()
        return label

    def validate(self):
        """Click 'Validate' and wait until the server accepted the answer.

        The button label changes (Validate -> Next) once it did. The bot retries
        once when that does not happen, because 7Speaking sometimes answers 503.
        """
        label = self._click_submit()
        if not label:
            time.sleep(1)
            return

        if self._label_changed(label, timeout=10):
            return

        print("Answer not accepted yet, retrying once...")
        try:
            self._click_submit()
        except TimeoutException:
            return
        if not self._label_changed(label, timeout=10):
            print("Warning: validation still pending, continuing.")

    def _click_next(self):
        self._click_submit()

    def finish(self):
        def continue_button(driver):
            candidates = driver.find_elements(
                By.XPATH, S.CONTINUE_BUTTON_XPATH
            ) + driver.find_elements(By.CSS_SELECTOR, S.HOME_BUTTON)
            for element in candidates:
                if element.is_displayed() and element.is_enabled():
                    return element
            return False

        try:
            button = WebDriverWait(self.driver, 30).until(continue_button)
        except TimeoutException:
            print("No Continue button found, assuming the quiz is closed.")
            return

        button.click()
        print("Quiz completed.")
