"""run_business with stubbed navigation: category loop, no-quiz skip, recovery."""
from types import SimpleNamespace

import flows
from navigation.skills.business import NoQuizAvailable
from utils.deadline import Deadline


class FakeBusiness:
    instances = []

    def __init__(self, driver):
        self.opened = []
        self.activities = {"Letters": ["A", "B"], "Phoning": ["C"]}
        self.current = None
        FakeBusiness.instances.append(self)

    def wait_view(self, timeout=20):
        return "grid"

    def list_categories(self):
        return list(self.activities)

    def open_category(self, name):
        self.current = name

    def list_activities(self):
        return self.activities[self.current]

    def open_activity(self, title, recover):
        self.opened.append((self.current, title))

    def open_comprehension_test(self):
        title = self.opened[-1][1]
        if title == "B":
            raise NoQuizAvailable("No 'Comprehension test' on this activity.")


def make_ctx():
    menu = SimpleNamespace(
        go_home=lambda: None,
        open_professional_competencies=lambda: None,
        open_business_skills=lambda: None,
        ensure_window=lambda: None,
    )
    runner = SimpleNamespace(solved=[])
    runner.solve = lambda payload, retake=False: runner.solved.append(payload)
    quiz_data = SimpleNamespace(
        arm=lambda: None, get_payload=lambda timeout=0: {"questions": {"data": []}}
    )
    return SimpleNamespace(
        driver=SimpleNamespace(current_url="x"),
        menu=menu,
        quiz_data=quiz_data,
        runner=runner,
        api=SimpleNamespace(get_quiz_for_current_page=lambda: None),
        pacing=None,
        deadline=Deadline(None),
    )


def test_business_visits_every_category_and_skips_activities_without_quiz(monkeypatch):
    monkeypatch.setattr(flows, "BusinessSkills", FakeBusiness)
    ctx = make_ctx()
    flows.run_business(ctx)
    fake = FakeBusiness.instances[-1]
    assert fake.opened == [("Letters", "A"), ("Letters", "B"), ("Phoning", "C")]
    assert len(ctx.runner.solved) == 2  # B had no quiz


def test_business_limit_counts_solved_quizzes(monkeypatch):
    monkeypatch.setattr(flows, "BusinessSkills", FakeBusiness)
    ctx = make_ctx()
    flows.run_business(ctx, limit=1)
    assert len(ctx.runner.solved) == 1


class StrictBusiness(FakeBusiness):
    """Like the real site: a category card only exists on the grid page."""

    def __init__(self, driver):
        super().__init__(driver)
        self.activities = {"Letters": ["A"], "Phoning": ["C"], "Meetings": ["D"]}
        self.on_grid = False

    def wait_view(self, timeout=20):
        self.on_grid = True  # goto_grid() just reloaded the grid
        return "grid"

    def open_category(self, name):
        if not self.on_grid:
            raise TimeoutError(f"'{name}' not found: not on the category grid")
        self.on_grid = False
        super().open_category(name)


def test_business_returns_to_grid_between_categories(monkeypatch):
    """Regression: every second category used to time out (build.log, Oct 16)."""
    monkeypatch.setattr(flows, "BusinessSkills", StrictBusiness)
    ctx = make_ctx()
    flows.run_business(ctx)
    fake = FakeBusiness.instances[-1]
    assert fake.opened == [("Letters", "A"), ("Phoning", "C"), ("Meetings", "D")]
    assert len(ctx.runner.solved) == 3
