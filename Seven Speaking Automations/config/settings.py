import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / "credentials.env")


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


EMAIL = os.getenv("SEVEN_SPEAKING_EMAIL")
PASSWORD = os.getenv("SEVEN_SPEAKING_PASSWORD")

# ----------------------------------------------------------------------
# URLs
# ----------------------------------------------------------------------
LOGIN_URL = "https://user.7speaking.com/"
HOME_URL = "https://user.7speaking.com/home"
DOCUMENT_URL = "https://user.7speaking.com/document/{activity_id}?type=news"

API_BASE_URL = "https://platform.7speaking.com/apiws"
API_INTERFACE_LANGUAGE = os.getenv("SEVEN_SPEAKING_LI", "ENG")
API_LANGUAGE_TAUGHT = os.getenv("SEVEN_SPEAKING_LANGUAGE_TAUGHT", "ENG")

# ----------------------------------------------------------------------
# Answer mix (ported from the bot's goodOne / falseOne)
#
# Answers are handed out in cycles of GOOD + WRONG answers, shuffled inside
# each cycle. 2 / 1 means "2 right, 1 wrong, in random order, repeat".
# Set WRONG_ANSWERS_PER_CYCLE=0 (or run with --perfect) to always answer right.
# All of these can be overridden in credentials.env.
# ----------------------------------------------------------------------
GOOD_ANSWERS_PER_CYCLE = _env_int("GOOD_ANSWERS_PER_CYCLE", 2)
WRONG_ANSWERS_PER_CYCLE = _env_int("WRONG_ANSWERS_PER_CYCLE", 0)

# ----------------------------------------------------------------------
# Pacing (ported from the bot's quizDuration)
#
# 7Speaking announces a duration per quiz. The bot spends QUIZ_MINUTES_PER_10
# minutes for every 10 minutes announced, split over the questions.
# Each wait is randomised +/-30% and clamped to [MIN, MAX] seconds.
# Set MAX_THINK_SECONDS=0 to disable all waiting.
# ----------------------------------------------------------------------
QUIZ_MINUTES_PER_10 = _env_float("QUIZ_MINUTES_PER_10", 5)
MIN_THINK_SECONDS = _env_float("MIN_THINK_SECONDS", 2)
MAX_THINK_SECONDS = _env_float("MAX_THINK_SECONDS", 25)

# Random pause (seconds) between two activities in the news flow.
PAUSE_BETWEEN_ACTIVITIES = (3.0, 8.0)

# How long to wait for the quiz.cfc response after opening a quiz, before the
# script falls back to calling the API itself.
QUIZ_PAYLOAD_TIMEOUT = _env_int("QUIZ_PAYLOAD_TIMEOUT", 5)

# Stop a section after this many activities fail in a row.
MAX_CONSECUTIVE_FAILURES = 3
