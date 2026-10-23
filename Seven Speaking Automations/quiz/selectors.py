"""Every CSS/XPath selector the quiz code depends on, in one place.

If 7Speaking changes its markup, this is the only file to touch.
"""

# Quiz screen
QUESTION_TITLE = ".question__title"
RESULT_CONTAINER = ".result-container"
SUBMIT_BUTTON = 'button[type="submit"]'
SUBMIT_BUTTON_ENABLED = 'button[type="submit"]:not([disabled])'
CHOICE_BUTTON = 'button[value="{index}"]'
FILL_INPUT = 'input[placeholder="Enter your reply"]'

# Result screen
CONTINUE_BUTTON_XPATH = (
    "//button[.//span[normalize-space()='Continue' or normalize-space()='Continuer']]"
)
HOME_BUTTON = ".btns__container button[to='/home']"

# Home page marker (same one the SSO login waits for)
HOME_MARKER = "img[alt='Level_badge']"

# News activity page: the tab that opens the quiz
NEWS_TEST_TAB = ".appBarTabs__testTab"

# Business skills landing page: grid of categories (Letters, Phoning, ...)
BUSINESS_CATEGORY_TITLE = "h3.previewGris__title"

# Inside a category: the "Case study" cards (Sample letter/email n°X).
# The "Assimilation" list below them is vocabulary only, it has no quiz.
BUSINESS_ACTIVITY_TITLE = ".businessSkills__preview__list:not(.assimilationList) h3"

# Business activity page (/document/<id>): the red "Comprehension test" tab in
# the header, next to "Study process". Same tab class as the news pages, plus a
# text-based fallback in case the class name changes.
COMPREHENSION_TAB_CSS = NEWS_TEST_TAB
COMPREHENSION_TAB_XPATH = (
    "//*[self::div or self::button or self::a or self::li]"
    "[contains(@class, 'appBarTabs') or @role='button' or @role='tab']"
    "[contains(normalize-space(.), 'Comprehension test')]"
)
