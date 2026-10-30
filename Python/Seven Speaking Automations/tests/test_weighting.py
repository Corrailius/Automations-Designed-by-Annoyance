import random
from types import SimpleNamespace

import flows
from navigation.skills.news import NewsLessons
from utils.deadline import Deadline
from utils.weighting import pick_weighted, weight_for, weighted_order


def test_zero_weight_is_dropped_and_all_others_kept():
    order = weighted_order(["a", "b", "c"], [1, 0, 1], random.Random(1))
    assert sorted(order) == ["a", "c"]


def test_lower_weight_comes_later_on_average():
    rng = random.Random(0)
    first_new = sum(
        weighted_order(["new", "old"], [1.0, 0.2], rng)[0] == "new" for _ in range(2000)
    )
    assert 0.78 < first_new / 2000 < 0.90  # expected 1 / 1.2 = 0.83


def test_equal_weights_give_no_preference():
    rng = random.Random(0)
    first = sum(weighted_order(["a", "b"], [1, 1], rng)[0] == "a" for _ in range(2000))
    assert 0.45 < first / 2000 < 0.55


def test_weight_for_and_empty_pick():
    assert weight_for(False, 0.2) == 1.0
    assert weight_for(True, 0.2) == 0.2
    assert pick_weighted([], []) is None


def _activity(i, done):
    return {"id": i, "countersProps": {"completion": done}}


def make_news(activities, seed=0):
    api = SimpleNamespace(
        get_topics=lambda: [{"id": 1}],
        get_topic_activities=lambda topic_id: activities,
    )
    return NewsLessons(None, api, random.Random(seed))


def test_news_never_replays_with_zero_weight(monkeypatch):
    monkeypatch.setattr("navigation.skills.news.time.sleep", lambda s: None)
    news = make_news([_activity(1, True), _activity(2, False)])
    assert news.next_activity(set(), 0)["id"] == 2
    assert news.next_activity({2}, 0) is None


def test_news_replays_completed_when_weighted(monkeypatch):
    monkeypatch.setattr("navigation.skills.news.time.sleep", lambda s: None)
    news = make_news([_activity(1, True), _activity(2, False)])
    assert news.next_activity({2}, 0.2)["id"] == 1  # only a completed one is left
    news.mark_completed(2)
    assert news.is_completed(news._activities[1])


def test_run_quiz_replays_completed_quiz():
    calls = []
    ctx = SimpleNamespace(
        quiz_data=SimpleNamespace(
            arm=lambda: None,
            get_payload=lambda timeout=0: {
                "iscomplete": True,
                "questions": {"data": []},
            },
        ),
        runner=SimpleNamespace(solve=lambda p, retake=False: calls.append(retake)),
        api=None,
    )
    assert flows.run_quiz(ctx, lambda: None, "x") is True
    assert calls == [True]
