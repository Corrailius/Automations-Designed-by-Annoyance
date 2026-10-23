import random
import time

from config.settings import DOCUMENT_URL
from quiz import selectors as S
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class NewsLessons:
    """'Video by topics' activities, ported from the bot's getNextActivity()."""

    def __init__(self, driver, api):
        self.driver = driver
        self.api = api
        self._topics = None
        self._start = 0  # topics before this index are fully done

    def next_activity(self, skip_ids):
        """First activity that is not completed and not in `skip_ids`, else None."""
        if self._topics is None:
            self._topics = self.api.get_topics()
            if self._topics is None:
                raise RuntimeError("Could not load the topic list.")
            print(f"Found {len(self._topics)} topics.")

        for i in range(self._start, len(self._topics)):
            topic = self._topics[i]

            # Polite rate limiting, like the bot.
            time.sleep(random.uniform(0.8, 1.6))

            activities = self.api.get_topic_activities(topic["id"])
            if activities is None:
                raise RuntimeError(f"Could not load activities of topic {topic['id']}.")

            for activity in activities:
                completed = (activity.get("countersProps") or {}).get("completion") is True
                if not completed and activity["id"] not in skip_ids:
                    return activity

            self._start = i + 1

        return None

    def open_activity(self, activity_id):
        self.driver.get(DOCUMENT_URL.format(activity_id=activity_id))

    def open_quiz_tab(self):
        tab = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, S.NEWS_TEST_TAB))
        )
        tab.click()
