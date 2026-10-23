"""Runs QuizRunner against a fake quiz page that mimics the real UI flow:
answer -> Validate -> Next -> ... -> results screen with a Continue button."""
import random

from quiz.answer_planner import AnswerPlanner
from quiz.pacing import Pacing
from quiz.quiz_runner import QuizRunner, UnsupportedQuestion
from selenium.common.exceptions import NoSuchElementException


class El:
    def __init__(self, page, kind, key=None, text=""):
        self.page, self.kind, self.key, self.text = page, kind, key, text

    def is_displayed(self): return True
    def is_enabled(self): return True
    def clear(self): self.page.typed = ""
    def send_keys(self, s): self.page.typed += s

    def click(self):
        p = self.page
        if self.kind == "choice":
            p.selected.append(self.key)
        elif self.kind == "submit":
            if p.phase == "answering":
                if p.selected or p.typed:
                    p.record()
                    p.phase = "validated"
            elif p.phase == "validated":
                p.idx += 1
                p.selected, p.typed = [], ""
                p.phase = "finished" if p.idx >= len(p.questions) else "answering"
        elif self.kind == "continue":
            p.continued = True


class FakePage:
    def __init__(self, questions):
        self.questions = questions
        self.idx, self.phase = 0, "answering"
        self.selected, self.typed = [], ""
        self.results, self.continued = [], False

    def record(self):
        q = self.questions[self.idx]
        if q["variant"] == "choice":
            ids = [q["answerOptions"]["options"][i]["id"] for i in self.selected]
            ok = ids == [a["id"] for a in q["answerOptions"]["answer"]]
        else:
            ok = self.typed == q["answerOptions"]["answer"][0]["value"]
        self.results.append(ok)

    # --- driver API -----------------------------------------------------
    def find_elements(self, by, sel):
        fin = self.phase == "finished"
        if "question__title" in sel:
            return [] if fin else [El(self, "title", text=self.questions[self.idx]["question"])]
        if "result-container" in sel:
            return [El(self, "result")] if fin else []
        if "Continue" in sel:
            return [El(self, "continue")] if fin else []
        if "btns__container" in sel:
            return []
        if sel.startswith("button[type"):
            if fin:
                return []
            return [El(self, "submit", text="Validate" if self.phase == "answering" else "Next")]
        if sel.startswith("button[value="):
            if fin:
                return []
            return [El(self, "choice", key=int(sel.split('"')[1]))]
        if "input[placeholder" in sel:
            return [El(self, "input")] if not fin else []
        return []

    def find_element(self, by, sel):
        found = self.find_elements(by, sel)
        if not found:
            raise NoSuchElementException(sel)
        return found[0]


def choice_q(i, correct_idx, title=None):
    opts = [{"id": 10 * i + k, "value": f"opt{k}"} for k in range(4)]
    return {"id": i, "variant": "choice", "question": title or f"Pick the right one {i}",
            "answerOptions": {"options": opts, "answer": [opts[correct_idx]]}}


def fill_q(i, value):
    return {"id": i, "variant": "fill", "question": f"Fill the gap {i} ____ please",
            "answerOptions": {"answer": [{"value": value}]}}


def make_runner(page, wrong):
    planner = AnswerPlanner(2, wrong, rng=random.Random(3))
    pacing = Pacing(5, 0, 0)  # no waiting in tests
    return QuizRunner(page, planner, pacing)


def test_perfect_run_answers_everything_right_and_continues():
    qs = [choice_q(1, 2), fill_q(2, "went"), choice_q(3, 0), fill_q(4, "has been")]
    page = FakePage(qs)
    summary = make_runner(page, wrong=0).solve({"duration": 10, "questions": {"data": qs}})
    assert page.results == [True] * 4
    assert summary == {"correct": 4, "wrong": 0, "skipped": 0}
    assert page.continued


def test_mixed_run_makes_planned_mistakes():
    qs = [choice_q(i, i % 4) for i in range(1, 10)]
    page = FakePage(qs)
    summary = make_runner(page, wrong=1).solve({"questions": {"data": qs}})
    assert summary["correct"] == 6 and summary["wrong"] == 3
    assert page.results.count(False) == 3  # wrong picks really were wrong
    assert page.continued


def test_duplicate_titles_are_resolved_by_order():
    qs = [choice_q(1, 1, "Same title"), choice_q(2, 3, "Same title")]
    page = FakePage(qs)
    make_runner(page, wrong=0).solve({"questions": {"data": qs}})
    assert page.results == [True, True]


def test_unsupported_variant_stops_instead_of_looping():
    qs = [{"id": 1, "variant": "drag", "question": "Pick the right one 1",
           "answerOptions": {}}]
    page = FakePage(qs)
    try:
        make_runner(page, wrong=0).solve({"questions": {"data": qs}})
        assert False, "should raise"
    except UnsupportedQuestion:
        pass


def test_deadline_stops_quiz_between_questions():
    from utils.deadline import Deadline, TimeBudgetReached

    qs = [choice_q(i, 0) for i in range(1, 6)]
    page = FakePage(qs)
    # fake clock = number of answers given so far; budget of 2 "seconds"
    deadline = Deadline(2 / 60, clock=lambda: len(page.results))
    runner = QuizRunner(page, AnswerPlanner(2, 0), Pacing(5, 0, 0), deadline)
    try:
        runner.solve({"questions": {"data": qs}})
        assert False, "should raise"
    except TimeBudgetReached:
        pass
    assert len(page.results) == 2  # stopped exactly when the budget ran out


def test_no_deadline_never_expires():
    from utils.deadline import Deadline

    d = Deadline(None)
    assert not d.expired() and d.remaining() == float("inf")
