import argparse
import sys

from selenium import webdriver

from authentication.sso import SSO
from config import settings
from flows import Context, run_business, run_grammar, run_news
from navigation.menu import Menu
from quiz.answer_planner import AnswerPlanner
from quiz.pacing import Pacing
from quiz.quiz_data import QuizData
from quiz.quiz_runner import QuizRunner
from utils.deadline import Deadline
from utils.debug import snapshot
from utils.seven_api import SevenSpeakingAPI

SECTIONS = {
    "grammar": run_grammar,
    "business": run_business,
    "news": run_news,
}


def parse_args():
    parser = argparse.ArgumentParser(description="7Speaking automation")
    parser.add_argument(
        "--mode",
        choices=[*SECTIONS, "all"],
        default="all",
        help="what to run (default: all = grammar, business, news)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="max quizzes to solve per section (default: no limit)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="total run time in minutes, e.g. 60 (default: until all work is done)",
    )
    parser.add_argument(
        "--perfect",
        action="store_true",
        help="never answer wrong on purpose",
    )
    parser.add_argument(
        "--keep-open",
        action="store_true",
        help="wait for Enter before closing the browser",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=== 7Speaking Automation ===")
    print()

    if not settings.EMAIL or not settings.PASSWORD:
        sys.exit(
            "Missing credentials. Copy credentials.env.example to credentials.env "
            "and fill in SEVEN_SPEAKING_EMAIL / SEVEN_SPEAKING_PASSWORD."
        )

    wrong = 0 if args.perfect else settings.WRONG_ANSWERS_PER_CYCLE
    planner = AnswerPlanner(settings.GOOD_ANSWERS_PER_CYCLE, wrong)
    pacing = Pacing(
        settings.QUIZ_MINUTES_PER_10,
        settings.MIN_THINK_SECONDS,
        settings.MAX_THINK_SECONDS,
    )

    deadline = Deadline(args.duration)
    if args.duration:
        print(f"Time budget: {args.duration:g} minutes.")

    print("Starting Firefox...")
    options = webdriver.FirefoxOptions()
    options.enable_bidi = True
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1400, 900)

    quiz_data = None
    try:
        print("Opening 7Speaking...")
        driver.get(settings.LOGIN_URL)

        SSO(driver, settings.EMAIL, settings.PASSWORD).login()

        quiz_data = QuizData(driver)  # one listener for the whole run
        ctx = Context(
            driver=driver,
            menu=Menu(driver),
            quiz_data=quiz_data,
            runner=QuizRunner(driver, planner, pacing, deadline),
            api=SevenSpeakingAPI(driver),
            pacing=pacing,
            deadline=deadline,
        )

        names = list(SECTIONS) if args.mode == "all" else [args.mode]
        for name in names:
            if deadline.expired():
                break
            SECTIONS[name](ctx, args.limit)

        print("\nAll done.")

        if args.keep_open:
            input("\nPress Enter to close...")

    except Exception as exc:
        snapshot(driver, "fatal", exc)
        raise
    finally:
        if quiz_data is not None:
            quiz_data.close()
        driver.quit()


if __name__ == "__main__":
    main()
