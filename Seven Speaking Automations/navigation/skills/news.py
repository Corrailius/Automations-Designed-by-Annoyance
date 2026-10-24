import random
import time

from config.settings import API_CALL_DELAY, DOCUMENT_URL
from quiz import selectors as S
from utils.weighting import pick_weighted, weight_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class NewsLessons:
    """'Video by topics' activities, ported from the bot's getNextActivity()."""

    def __init__(self, driver, api, rng=None):
        self.driver = driver
        self.api = api
        self.rng = rng or random.Random()
        self._activities = None  # every activity of every topic, loaded once

    def _load_all(self):
        topics = self.api.get_topics()
        if topics is None:
            raise RuntimeError("Could not load the topic list.")
        print(f"Found {len(topics)} topics, listing their activities...")

        activities = []
        for topic in topics:
            time.sleep(random.uniform(*API_CALL_DELAY))  # polite rate limiting
            found = self.api.get_topic_activities(topic["id"])
            if found is None:
                raise RuntimeError(f"Could not load activities of topic {topic['id']}.")
            activities.extend(found)

        done = sum(1 for a in activities if self.is_completed(a))
        print(f"Found {len(activities)} activities ({done} already completed).")
        return activities

    @staticmethod
    def is_completed(activity):
        return (activity.get("countersProps") or {}).get("completion") is True

    def mark_completed(self, activity_id):
        """Remember locally that an activity was just played."""
        for activity in self._activities or []:
            if activity["id"] == activity_id:
                activity.setdefault("countersProps", {})["completion"] = True

    def next_activity(self, skip_ids, completed_weight=1.0):
        """Pick the next activity, or None when nothing is left to play.

        Activities that are not completed have weight 1, completed ones have
        `completed_weight` (0 = never replay). Ids in `skip_ids` are excluded.
        """
        if self._activities is None:
            self._activities = self._load_all()

        pool = [a for a in self._activities if a["id"] not in skip_ids]
        weights = [weight_for(self.is_completed(a), completed_weight) for a in pool]
        return pick_weighted(pool, weights, self.rng)

    def open_activity(self, activity_id):
        self.driver.get(DOCUMENT_URL.format(activity_id=activity_id))

    def open_quiz_tab(self):
        tab = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, S.NEWS_TEST_TAB))
        )
        tab.click()
