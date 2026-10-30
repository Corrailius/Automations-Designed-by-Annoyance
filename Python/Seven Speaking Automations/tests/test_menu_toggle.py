"""The side menu entries are toggles: opening must work from both states."""
from navigation.menu import GRAMMAR_WORKSHOP, Menu


class El:
    def __init__(self, shown): self._shown = shown
    def is_displayed(self): return self._shown()
    def is_enabled(self): return True


class FakeNav:
    def __init__(self, expanded):
        self.expanded = expanded
        self.clicked = []
        self.height = 900

    def execute_script(self, script, *args):
        if "innerHeight" in script:
            return self.height
        if "arguments[0].click" in script or "scrollIntoView" in script:
            return None

    def find_elements(self, by, value):
        if (by, value) == GRAMMAR_WORKSHOP:
            return [El(lambda: self.expanded)]
        return []

    def find_element(self, by, value):
        return self.find_elements(by, value)[0]


def make_menu(expanded, monkeypatch):
    nav = FakeNav(expanded)
    menu = Menu(nav)

    parent = El(lambda: True)

    def click_parent(driver, element):
        if element is parent:
            nav.expanded = not nav.expanded  # toggle, like the real menu
            nav.clicked.append("parent")

    monkeypatch.setattr("navigation.menu.safe_click", click_parent)
    monkeypatch.setattr(
        "navigation.menu.EC.element_to_be_clickable", lambda locator: (lambda d: parent)
    )
    return nav, menu


def test_opens_when_collapsed(monkeypatch):
    nav, menu = make_menu(False, monkeypatch)
    menu.open_general_skills()
    assert nav.expanded and nav.clicked == ["parent"]


def test_does_not_close_when_already_open(monkeypatch):
    nav, menu = make_menu(True, monkeypatch)
    menu.open_general_skills()
    assert nav.expanded and nav.clicked == []


def test_restores_collapsed_window():
    nav = FakeNav(True)
    nav.height = 31
    calls = []
    nav.set_window_rect = lambda *a: calls.append("rect")
    nav.maximize_window = lambda: calls.append("max")
    Menu(nav).ensure_window()
    assert calls == ["rect", "max"]
