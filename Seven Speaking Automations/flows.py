"""The three automation flows: grammar, business skills, news-based lessons."""

import traceback
from dataclasses import dataclass

from config import settings
from navigation.skills.business import BusinessSkills, NoQuizAvailable
from navigation.skills.grammar import Grammar
from navigation.skills.news import NewsLessons
from utils.deadline import TimeBudgetReached
from utils.debug import snapshot


@dataclass
class Context:
    driver: object
    menu: object
    quiz_data: object
    runner: object
    api: object
    pacing: object
    deadline: object


# ----------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------
def run_quiz(ctx, open_quiz, label, preloaded_payload=None):
    """Open a quiz, capture its questions and solve it.

    Returns True when the quiz was solved, False when it was skipped
    (already completed, or questions could not be captured).
    """
    if preloaded_payload and preloaded_payload.get("iscomplete"):
        print(f"{label}: already completed, skipping.")
        return False

    ctx.quiz_data.arm()
    open_quiz()

    # 1) the page's own quiz.cfc response, 2) the copy fetched before opening
    # (news), 3) the same API call made from the quiz URL.
    payload = ctx.quiz_data.get_payload(timeout=settings.QUIZ_PAYLOAD_TIMEOUT)
    payload = payload or preloaded_payload or ctx.api.get_quiz_for_current_page()

    if payload is None:
        print(f"{label}: could not get the quiz questions, skipping.")
        return False

    if payload.get("iscomplete"):
        print(f"{label}: already completed, skipping. ({_evidence(payload)})")
        return False

    ctx.runner.solve(payload)
    return True


def _evidence(payload):
    """What the server says about this quiz, to check the 'completed' flag."""
    questions = (payload.get("questions") or {}).get("data") or []
    answered = sum(
        1 for q in questions if q.get("useranswer") not in (None, "", 0, "0")
    )
    return f"server iscomplete={payload.get('iscomplete')!r}, {answered}/{len(questions)} questions answered"


def _report(ctx, exc, name):
    print(f"\n[ERROR] {name}: {exc!r}")
    traceback.print_exc()
    snapshot(ctx.driver, name, exc)


def _summary(title, done, skipped, failed):
    print(f"\n{title}: {done} solved, {skipped} skipped, {failed} failed.")


# ----------------------------------------------------------------------
# Grammar workshop
# ----------------------------------------------------------------------
def run_grammar(ctx, limit=None):
    print("\n=== Grammar workshop ===")
    grammar = Grammar(ctx.driver)

    def goto_list():
        ctx.menu.go_home()
        print("Opening General skills...")
        ctx.menu.open_general_skills()
        print("Opening Grammar Workshop...")
        ctx.menu.open_grammar()

    goto_list()
    total = len(grammar.get_cards())
    print(f"Found {total} grammar lessons.")

    done = skipped = failed = streak = 0

    for index in range(total):
        if limit is not None and done >= limit:
            break
        if ctx.deadline.expired():
            print("Time budget reached.")
            break

        label = f"Grammar lesson {index + 1}/{total}"
        print(f"\n--- {label} ---")
        ctx.menu.ensure_window()

        try:
            grammar.ensure_open(goto_list)
            if grammar.is_completed(index):
                print("Already completed (green check), skipping.")
                skipped += 1
                continue
            grammar.select_lesson(index)
            solved = run_quiz(ctx, grammar.open_quiz, label)
            streak = 0
            if solved:
                done += 1
            else:
                skipped += 1
                goto_list()  # we are stuck on the quiz screen
        except TimeBudgetReached:
            print("Time budget reached, stopping here.")
            break
        except Exception as exc:
            failed += 1
            streak += 1
            _report(ctx, exc, f"grammar-{index + 1}")
            if streak >= settings.MAX_CONSECUTIVE_FAILURES:
                print("Too many failures in a row, stopping Grammar.")
                break
            try:
                goto_list()
            except Exception:
                pass

    _summary("Grammar", done, skipped, failed)


# ----------------------------------------------------------------------
# Business skills (Professional competencies)
# ----------------------------------------------------------------------
def run_business(ctx, limit=None):
    print("\n=== Business Skills ===")
    business = BusinessSkills(ctx.driver)

    def goto_grid():
        ctx.menu.go_home()
        print("Opening Professional competencies...")
        ctx.menu.open_professional_competencies()
        print("Opening Business Skills...")
        ctx.menu.open_business_skills()
        return business.wait_view()

    view = goto_grid()
    if view == "grid":
        categories = business.list_categories()
        print(f"Found {len(categories)} categories: {categories}")
    elif view == "category":
        print("Business Skills opened straight inside a category, using it as is.")
        categories = [None]
    else:
        snapshot(ctx.driver, "business-unknown-view")
        raise RuntimeError("Business Skills page not recognised (see build.log).")

    done = skipped = failed = streak = 0
    abort = False
    on_grid = view == "grid"  # after a category we are NOT on the grid anymore

    for category in categories:
        if abort or (limit is not None and done >= limit) or ctx.deadline.expired():
            break

        name = category or "current category"
        print(f"\n##### Category: {name} #####")

        def goto_category(category=category):
            if goto_grid() == "grid" and category is not None:
                business.open_category(category)

        try:
            if category is not None:
                if not on_grid:
                    goto_grid()  # previous category left us inside its page
                business.open_category(category)
                on_grid = False
            titles = business.list_activities()
        except Exception as exc:
            failed += 1
            _report(ctx, exc, f"business-category-{name}")
            try:
                goto_grid()
                on_grid = True
            except Exception:
                pass
            continue

        if not titles:
            print(f"No activities recognised in '{name}', skipping.")
            snapshot(ctx.driver, f"business-empty-{name}")
            try:
                goto_grid()
                on_grid = True
            except Exception:
                pass
            continue

        print(f"Found {len(titles)} activities: {titles}")

        for position, title in enumerate(titles, start=1):
            if limit is not None and done >= limit:
                break
            if ctx.deadline.expired():
                print("Time budget reached.")
                abort = True
                break

            label = f"Business {name} / '{title}' ({position}/{len(titles)})"
            print(f"\n--- {label} ---")
            ctx.menu.ensure_window()

            solved = False
            try:
                business.open_activity(title, goto_category)
                solved = run_quiz(ctx, business.open_comprehension_test, label)
                streak = 0
                if solved:
                    done += 1
                else:
                    skipped += 1
                    goto_category()
            except TimeBudgetReached:
                print("Time budget reached, stopping here.")
                abort = True
                break
            except NoQuizAvailable as exc:
                print(f"{exc} Skipping.")
                snapshot(ctx.driver, f"business-noquiz-{name}-{position}")
                skipped += 1
                try:
                    goto_category()
                except Exception:
                    pass
            except Exception as exc:
                failed += 1
                streak += 1
                _report(ctx, exc, f"business-{name}-{position}")
                if streak >= settings.MAX_CONSECUTIVE_FAILURES:
                    print("Too many failures in a row, stopping Business Skills.")
                    abort = True
                    break
                try:
                    goto_category()
                except Exception:
                    pass
                continue

            # After a finished quiz the site returns to its home page.
            if solved:
                try:
                    goto_category()
                except Exception:
                    pass

    _summary("Business Skills", done, skipped, failed)


# ----------------------------------------------------------------------
# News-based lessons (ported from the bot's activity loop)
# ----------------------------------------------------------------------
def run_news(ctx, limit=None):
    print("\n=== News-based lessons ===")
    news = NewsLessons(ctx.driver, ctx.api)

    ctx.menu.go_home()  # make sure we are on a 7speaking page with a session

    total = ctx.api.get_total_completed()
    if total is not None:
        print(f"Activities completed so far on your account: {total}")

    attempted = set()
    done = skipped = failed = streak = 0

    while limit is None or done < limit:
        if ctx.deadline.expired():
            print("Time budget reached.")
            break

        try:
            activity = news.next_activity(attempted)
        except Exception as exc:
            _report(ctx, exc, "news-lookup")
            break

        if activity is None:
            print("No incomplete activity left.")
            break

        activity_id = activity["id"]
        attempted.add(activity_id)  # never retry the same one in this run
        label = f"Activity {activity_id} ({activity.get('title', 'untitled')})"
        print(f"\n--- {label} ---")
        ctx.menu.ensure_window()

        try:
            news.open_activity(activity_id)
            preloaded = ctx.api.get_quiz(activity_id)
            solved = run_quiz(ctx, news.open_quiz_tab, label, preloaded)
            streak = 0
            if solved:
                done += 1
            else:
                skipped += 1
        except TimeBudgetReached:
            print("Time budget reached, stopping here.")
            break
        except Exception as exc:
            failed += 1
            streak += 1
            _report(ctx, exc, f"news-{activity_id}")
            if streak >= settings.MAX_CONSECUTIVE_FAILURES:
                print("Too many failures in a row, stopping News lessons.")
                break

        ctx.pacing.pause(settings.PAUSE_BETWEEN_ACTIVITIES)

    total = ctx.api.get_total_completed() if _on_site(ctx.driver) else None
    if total is not None:
        print(f"Activities completed on your account now: {total}")
    _summary("News lessons", done, skipped, failed)


def _on_site(driver):
    try:
        return "7speaking.com" in driver.current_url
    except Exception:
        return False
