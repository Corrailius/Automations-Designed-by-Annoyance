import json
import random

from navigation.skills.business import xpath_literal
from quiz.answer_planner import AnswerPlanner
from quiz.pacing import Pacing
from quiz.quiz_data import QuizData
from quiz.text import normalize


def test_planner_respects_cycle_ratio():
    planner = AnswerPlanner(2, 1, rng=random.Random(1))
    answers = [planner.next_is_correct() for _ in range(30)]
    for i in range(0, 30, 3):
        assert sorted(answers[i : i + 3]) == [False, True, True]


def test_planner_perfect_mode():
    planner = AnswerPlanner(2, 0)
    assert all(planner.next_is_correct() for _ in range(20))


def test_pacing_uses_duration_and_clamps():
    pacing = Pacing(5, 2, 25, rng=random.Random(0))
    # 10 min quiz, 10 questions -> base 15s, jitter 0.7-1.3
    for _ in range(50):
        assert 10 <= pacing.think_time({"duration": 10}, 10) <= 20
    # clamped
    assert pacing.think_time({"duration": 1000}, 1) == 25
    assert pacing.think_time({"duration": 0.01}, 100) == 2


def test_pacing_disabled_and_fallback():
    assert Pacing(5, 2, 0).think_time({"duration": 10}, 10) == 0
    t = Pacing(5, 2, 25, rng=random.Random(0)).think_time({}, 5)
    assert 2 <= t <= 25


def test_normalize_matches_page_and_api_titles():
    api = "Complete: She ____ to school <b>every</b> day.\\r\\n"
    page = "Complete: She  to school every day."
    assert normalize(api) == normalize(page)


def test_xpath_literal():
    assert xpath_literal("Sample letter n°1") == "'Sample letter n°1'"
    assert xpath_literal("It's") == '"It\'s"'
    assert xpath_literal("a'b\"c").startswith("concat(")


class FakeNetwork:
    def __init__(self, bodies):
        self.bodies = bodies
        self.handlers = {}

    def add_data_collector(self, **kw):
        return {"collector": "c1"}

    def add_event_handler(self, event, cb):
        self.handlers[event] = cb
        return 7

    def remove_event_handler(self, event, hid):
        self.handlers.pop(event, None)

    def get_data(self, data_type, collector, request):
        return {"bytes": {"type": "string", "value": self.bodies[request]}}


class FakeDriver:
    def __init__(self, bodies):
        self.network = FakeNetwork(bodies)


def _event(url, rid):
    # dict style and attribute style must both work
    return {"request": {"request": rid, "url": url}, "response": {"url": url}}


def test_quiz_data_ignores_answer_saves_and_returns_quiz():
    quiz = {"payload": {"duration": 10, "questions": {"data": [{"id": 1}]}}}
    bodies = {"r1": json.dumps({"payload": {"saved": True}}), "r2": json.dumps(quiz)}
    driver = FakeDriver(bodies)
    qd = QuizData(driver)
    qd.arm()
    cb = driver.network.handlers["response_completed"]
    cb(_event("https://x/quiz.cfc?method=saveanswer", "r1"))
    cb(_event("https://x/other.cfc", "rX"))
    cb(_event("https://x/quiz.cfc?method=getquiz", "r2"))
    assert qd.get_payload(timeout=1)["duration"] == 10
    qd.arm()
    assert qd.get_payload(timeout=0.2) is None  # arm() drops stale responses
    qd.close()
    assert driver.network.handlers == {}


def test_quiz_url_parsing():
    from utils.seven_api import QUIZ_URL

    m = QUIZ_URL.search("https://user.7speaking.com/quiz/grammar/2")
    assert m.groups() == ("grammar", "2")
    m = QUIZ_URL.search("https://user.7speaking.com/quiz/news/12345?x=1")
    assert m.groups() == ("news", "12345")
    assert QUIZ_URL.search("https://user.7speaking.com/home") is None


def test_quiz_data_old_selenium_shape_request_id_from_before_request_sent():
    """Older Selenium: the response event has no request id, only the
    before_request_sent event does (like the user's original script)."""
    quiz = {"payload": {"questions": {"data": [{"id": 1}, {"id": 2}]}}}
    url = "https://x/quiz.cfc?method=getquiz&typesource=grammar&sourceid=26"
    driver = FakeDriver({"req-9": json.dumps(quiz)})
    qd = QuizData(driver)
    qd.arm()
    before = driver.network.handlers["before_request_sent"]
    done = driver.network.handlers["response_completed"]
    before({"request": {"request": "req-9", "url": url}})
    done({"response": {"url": url}})  # no 'request' key at all
    payload = qd.get_payload(timeout=1)
    assert len(payload["questions"]["data"]) == 2


def test_quiz_data_handler_errors_do_not_escape():
    driver = FakeDriver({})
    QuizData(driver)
    driver.network.handlers["response_completed"](object())  # garbage event
    driver.network.handlers["before_request_sent"](None)


def test_snapshot_names_are_filesystem_safe():
    from utils.debug import safe_name

    assert safe_name("business-category-Phoning / Calls: 1?") == "business-category-Phoning_Calls_1"
    assert safe_name("///") == "snapshot"
