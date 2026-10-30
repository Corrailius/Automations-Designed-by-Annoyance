import re
import time
import traceback

from config.settings import PROJECT_DIR

LOG_DIR = PROJECT_DIR / "build.log"


def safe_name(name):
    """Category/activity titles may contain / : ? etc., illegal in file names."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("_")[:80] or "snapshot"


def snapshot(driver, name, exc=None):
    """Save screenshot + page source (+ the error) to build.log/ for debugging."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        base = LOG_DIR / f"{stamp}-{safe_name(name)}"
        driver.save_screenshot(str(base) + ".png")
        base.with_suffix(".html").write_text(driver.page_source, encoding="utf-8")

        lines = [f"url: {driver.current_url}"]
        if exc is not None:
            lines.append(f"error: {exc!r}")
            lines.append("".join(traceback.format_exception(exc)))
        base.with_suffix(".txt").write_text("\n".join(lines), encoding="utf-8")

        print(f"Debug snapshot saved: {base}.png / .html / .txt")
    except Exception as err:
        print(f"Could not save debug snapshot: {err!r}")
