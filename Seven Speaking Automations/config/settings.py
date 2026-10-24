"""All tunable values live here and can be overridden from credentials.env
(or a plain .env file, or real environment variables).

Edit credentials.env, not this file. Every variable is optional.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent

# Real environment variables win, then credentials.env, then .env.
load_dotenv(PROJECT_DIR / "credentials.env")
load_dotenv(PROJECT_DIR / ".env")


def _env_int(name, default, minimum=None):
    try:
        value = int(float(os.getenv(name, default)))
    except (TypeError, ValueError):
        value = default
    return value if minimum is None else max(minimum, value)


def _env_float(name, default, minimum=None):
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default
    return value if minimum is None else max(minimum, value)


def _env_range(name_min, name_max, default):
    """A (low, high) pair from two variables, always ordered low <= high."""
    low = _env_float(name_min, default[0], minimum=0.0)
    high = _env_float(name_max, default[1], minimum=0.0)
    return (min(low, high), max(low, high))


EMAIL = os.getenv("SEVEN_SPEAKING_EMAIL")
PASSWORD = os.getenv("SEVEN_SPEAKING_PASSWORD")

# ----------------------------------------------------------------------
# URLs / API
# ----------------------------------------------------------------------
LOGIN_URL = "https://user.7speaking.com/"
HOME_URL = "https://user.7speaking.com/home"
DOCUMENT_URL = "https://user.7speaking.com/document/{activity_id}?type=news"

API_BASE_URL = "https://platform.7speaking.com/apiws"
API_INTERFACE_LANGUAGE = os.getenv("SEVEN_SPEAKING_LI", "ENG")
API_LANGUAGE_TAUGHT = os.getenv("SEVEN_SPEAKING_LANGUAGE_TAUGHT", "ENG")

# ----------------------------------------------------------------------
# Answer mix
# Answers are handed out in cycles of GOOD + WRONG answers, shuffled inside
# each cycle. 2 / 1 = "2 right, 1 wrong, random order, repeat".
# WRONG_ANSWERS_PER_CYCLE=0 (or --perfect) always answers right.
# ----------------------------------------------------------------------
GOOD_ANSWERS_PER_CYCLE = _env_int("GOOD_ANSWERS_PER_CYCLE", 2, minimum=0)
WRONG_ANSWERS_PER_CYCLE = _env_int("WRONG_ANSWERS_PER_CYCLE", 0, minimum=0)

# ----------------------------------------------------------------------
# Already-completed lessons
# Completed lessons are NOT skipped. They are replayed, but picked with this
# weight compared to 1.0 for lessons that are not completed yet:
#   1.0 = no preference, 0.2 = five times less likely, 0 = never replay.
# ----------------------------------------------------------------------
COMPLETED_WEIGHT = _env_float("COMPLETED_WEIGHT", 0.2, minimum=0.0)

# ----------------------------------------------------------------------
# Pacing
# 7Speaking announces a duration per quiz. We spend QUIZ_MINUTES_PER_10
# minutes for every 10 minutes announced, split over the questions, randomised
# by +/- THINK_JITTER and clamped to [MIN, MAX] seconds.
# MAX_THINK_SECONDS=0 disables all waiting.
# ----------------------------------------------------------------------
QUIZ_MINUTES_PER_10 = _env_float("QUIZ_MINUTES_PER_10", 5, minimum=0.0)
MIN_THINK_SECONDS = _env_float("MIN_THINK_SECONDS", 2, minimum=0.0)
MAX_THINK_SECONDS = _env_float("MAX_THINK_SECONDS", 25, minimum=0.0)
THINK_JITTER = _env_float("THINK_JITTER", 0.3, minimum=0.0)

# Random pause (seconds) between two activities in the news flow.
PAUSE_BETWEEN_ACTIVITIES = _env_range("PAUSE_MIN_SECONDS", "PAUSE_MAX_SECONDS", (3.0, 8.0))

# Random delay (seconds) between API calls when listing the news topics.
API_CALL_DELAY = _env_range("API_DELAY_MIN_SECONDS", "API_DELAY_MAX_SECONDS", (0.8, 1.6))

# ----------------------------------------------------------------------
# Robustness
# ----------------------------------------------------------------------
# How long to wait for the quiz.cfc response after opening a quiz, before the
# script falls back to calling the API itself.
QUIZ_PAYLOAD_TIMEOUT = _env_int("QUIZ_PAYLOAD_TIMEOUT", 5, minimum=1)

# Stop a section after this many activities fail in a row.
MAX_CONSECUTIVE_FAILURES = _env_int("MAX_CONSECUTIVE_FAILURES", 3, minimum=1)


def describe(wrong_answers=None, completed_weight=None):
    """One line per tunable, printed at startup so the active values are visible."""
    wrong = WRONG_ANSWERS_PER_CYCLE if wrong_answers is None else wrong_answers
    weight = COMPLETED_WEIGHT if completed_weight is None else completed_weight
    replay = "never replayed" if weight <= 0 else f"weight {weight:g} vs 1 for new ones"
    return [
        f"Answers per cycle: {GOOD_ANSWERS_PER_CYCLE} right / {wrong} wrong",
        f"Completed lessons: {replay}",
        f"Quiz time: {QUIZ_MINUTES_PER_10:g} min per 10 announced, "
        f"think {MIN_THINK_SECONDS:g}-{MAX_THINK_SECONDS:g}s (+/-{THINK_JITTER:.0%})",
        f"Pause between news activities: {PAUSE_BETWEEN_ACTIVITIES[0]:g}-{PAUSE_BETWEEN_ACTIVITIES[1]:g}s",
        f"Stop a section after {MAX_CONSECUTIVE_FAILURES} failures in a row",
    ]
