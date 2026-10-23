import re
import time
from urllib.parse import urlencode

from config import settings
from quiz.quiz_data import QuizData

QUIZ_URL = re.compile(r"/quiz/([A-Za-z]+)/(\d+)")

# Runs inside the page so the request comes from the real browser session.
_FETCH_JS = """
const url = arguments[0];
const done = arguments[arguments.length - 1];
fetch(url, {headers: {"Accept": "application/json, text/plain, */*"}})
  .then(r => r.ok ? r.json() : null)
  .then(done)
  .catch(() => done(null));
"""


class SevenSpeakingAPI:
    """Calls the 7Speaking API from inside the logged-in browser page.

    Port of the bot's fetch helpers. Must be used while the driver is on a
    user.7speaking.com page (CORS + localStorage session).
    """

    def __init__(self, driver):
        self.driver = driver
        self.driver.set_script_timeout(30)

    def session_id(self):
        return self.driver.execute_script(
            "return window.localStorage.getItem('sessionId');"
        )

    def call(self, endpoint, **params):
        session_id = self.session_id()
        if not session_id:
            raise RuntimeError("No sessionId in localStorage, are you logged in?")

        query = urlencode(
            {
                "sessionId": session_id,
                "LI": settings.API_INTERFACE_LANGUAGE,
                "languagetaught": settings.API_LANGUAGE_TAUGHT,
                **params,
            }
        )
        url = f"{settings.API_BASE_URL}/{endpoint}?{query}"
        return self.driver.execute_async_script(_FETCH_JS, url)

    # ------------------------------------------------------------------
    def get_quiz(self, source_id, type_source="news"):
        data = self.call(
            "quiz.cfc",
            method="getquiz",
            typesource=type_source,
            sourceid=source_id,
            **{"bs-faei": 0},
        )
        return QuizData.extract_payload(data)

    def get_quiz_for_current_page(self, wait_seconds=10):
        """Fetch the quiz of the page we are on, e.g. /quiz/grammar/2.

        Fallback for when the network capture missed the page's own request.
        """
        deadline = time.monotonic() + wait_seconds
        while True:
            match = QUIZ_URL.search(self.driver.current_url)
            if match:
                type_source, source_id = match.group(1), match.group(2)
                print(f"Fetching quiz from the API (typesource={type_source}, id={source_id})...")
                return self.get_quiz(source_id, type_source)
            if time.monotonic() >= deadline:
                return None
            time.sleep(0.3)

    def get_topics(self):
        data = self.call("videobytopic.cfc", method="getlisttopic")
        try:
            topics = []
            for category in data["payload"]["categories"]:
                topics.extend(category.get("topics", []))
            return topics
        except (TypeError, KeyError):
            return None

    def get_topic_activities(self, topic_id):
        data = self.call("videobytopic.cfc", method="gettopicdetail", topicid=topic_id)
        try:
            return data["payload"]["data"]
        except (TypeError, KeyError):
            return None

    def get_total_completed(self):
        data = self.call("logs.cfc", method="getactivitylog", reload=1)
        try:
            return data["payload"]["elearninglog"]["totalCompleted"]
        except (TypeError, KeyError):
            return None

