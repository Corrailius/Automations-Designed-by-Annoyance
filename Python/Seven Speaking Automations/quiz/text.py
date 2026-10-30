import html
import re

_TAGS = re.compile(r"<[^>]+>")


def normalize(text):
    """Make a question title from the API comparable with the one on the page."""
    if text is None:
        return ""
    text = html.unescape(_TAGS.sub("", str(text)))
    text = text.replace("\\r", "").replace("\\n", "")
    return re.sub(r"[_\s]+", "", text).lower()
