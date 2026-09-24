import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / "credentials.env")


EMAIL = os.getenv("SEVEN_SPEAKING_EMAIL")
PASSWORD = os.getenv("SEVEN_SPEAKING_PASSWORD")

LOGIN_URL = "https://user.7speaking.com/"
