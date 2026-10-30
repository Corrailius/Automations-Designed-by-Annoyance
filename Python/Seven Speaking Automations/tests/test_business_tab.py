"""The Comprehension test tab is found via the header tab class, then by text."""
from types import SimpleNamespace

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from navigation.skills import business as biz
from navigation.skills.business import BusinessSkills, NoQuizAvailable
from quiz import selectors as S


class El:
    def __init__(self, shown=True):
        self.shown = shown

    def is_displayed(self):
        return self.shown


class FakeDriver:
    def __init__(self, found):
        self.found = found  # {(by, selector): [elements]}
        self.current_url = "https://user.7speaking.com/business-skill/1"

    def find_elements(self, by, selector):
        return self.found.get((by, selector), [])


def make(found):
    skills = BusinessSkills.__new__(BusinessSkills)
    skills.driver = FakeDriver(found)
    return skills


def test_finds_header_tab_by_class():
    tab = El()
    skills = make({(By.CSS_SELECTOR, S.COMPREHENSION_TAB_CSS): [tab]})
    assert skills._find_comprehension_tab(skills.driver) is tab


def test_falls_back_to_text_and_ignores_hidden():
    hidden, shown = El(False), El(True)
    skills = make(
        {
            (By.CSS_SELECTOR, S.COMPREHENSION_TAB_CSS): [hidden],
            (By.XPATH, S.COMPREHENSION_TAB_XPATH): [shown],
        }
    )
    assert skills._find_comprehension_tab(skills.driver) is shown


def test_missing_tab_raises_no_quiz(monkeypatch):
    class Instant:
        def __init__(self, driver, timeout):
            self.driver = driver

        def until(self, cond):
            if cond(self.driver):
                return cond(self.driver)
            raise TimeoutException()

    monkeypatch.setattr(biz, "WebDriverWait", Instant)
    skills = make({})
    with pytest.raises(NoQuizAvailable):
        skills.open_comprehension_test()
