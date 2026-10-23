import base64
import json
import threading
import time

QUIZ_URL_MARKER = "quiz.cfc"


def _get(obj, key):
    """Read a field from either a dict or an object (Selenium versions differ)."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


class QuizData:
    """Captures the quiz questions from the page's own quiz.cfc response.

    Create ONE instance per driver. Before every action that loads a quiz
    (clicking the quiz button...), call arm(), then get_payload() afterwards.
    """

    def __init__(self, driver):
        self.driver = driver
        self._lock = threading.Lock()
        self._signal = threading.Event()
        self._candidates = []
        self._handlers = []
        self._request_ids = {}  # url -> request id, from before_request_sent
        self._events_seen = 0

        collector = driver.network.add_data_collector(
            data_types=["response"], max_encoded_data_size=5 * 1024 * 1024
        )
        self.collector_id = _get(collector, "collector")

        for event, callback in (
            ("before_request_sent", self._on_before_request_sent),
            ("response_completed", self._on_response_completed),
        ):
            handler_id = driver.network.add_event_handler(event, callback)
            self._handlers.append((event, handler_id))

    # ------------------------------------------------------------------
    def _on_before_request_sent(self, event):
        try:
            self._events_seen += 1
            request = _get(event, "request")
            url = _get(request, "url") or ""
            request_id = _get(request, "request")
            if QUIZ_URL_MARKER in url and request_id is not None:
                with self._lock:
                    self._request_ids[url] = request_id
                    self._last_request_id = request_id
        except Exception as exc:  # never let a listener crash silently
            print(f"[capture] request handler error: {exc!r}")

    def _on_response_completed(self, event):
        try:
            self._events_seen += 1
            request = _get(event, "request")
            response = _get(event, "response")

            url = _get(response, "url") or _get(request, "url") or ""
            if QUIZ_URL_MARKER not in url:
                return

            # Request id: from this event when present, else the one remembered
            # from before_request_sent (the older Selenium shape).
            request_id = _get(request, "request")
            with self._lock:
                if request_id is None:
                    request_id = self._request_ids.get(url) or getattr(
                        self, "_last_request_id", None
                    )
                if request_id is None:
                    print("[capture] quiz.cfc response seen but no request id found.")
                    return
                self._candidates.append(request_id)
            self._signal.set()
            print(
                "[capture] quiz.cfc response seen "
                f"({url.split('method=')[-1].split('&')[0]})"
            )
        except Exception as exc:
            print(f"[capture] response handler error: {exc!r}")

    def arm(self):
        """Forget previous responses. Call right before triggering a quiz load."""
        with self._lock:
            self._candidates = []
        self._signal.clear()

    # ------------------------------------------------------------------
    def _take_candidates(self):
        with self._lock:
            taken, self._candidates = self._candidates, []
        return taken

    def _read_payload(self, request_id):
        try:
            data = self.driver.network.get_data(
                data_type="response",
                collector=self.collector_id,
                request=request_id,
            )
            body = _get(data, "bytes")
            value = _get(body, "value")
            if _get(body, "type") == "base64":
                value = base64.b64decode(value).decode("utf-8")
            parsed = json.loads(value)
        except Exception:
            return None

        return self.extract_payload(parsed)

    @staticmethod
    def extract_payload(parsed):
        """Return the quiz payload if `parsed` really is a quiz, else None.

        quiz.cfc is also used to save answers, those responses are ignored.
        """
        if not isinstance(parsed, dict):
            return None
        payload = parsed.get("payload")
        if not isinstance(payload, dict):
            return None
        questions = payload.get("questions")
        if isinstance(questions, dict) and isinstance(questions.get("data"), list):
            return payload
        return None

    # ------------------------------------------------------------------
    def get_payload(self, timeout=30):
        """Wait for the quiz response. Returns the payload dict or None."""
        print("Waiting for quiz API response...")
        deadline = time.monotonic() + timeout

        while True:
            for request_id in self._take_candidates():
                payload = self._read_payload(request_id)
                if payload is not None:
                    questions = payload["questions"]["data"]
                    print(f"Received {len(questions)} questions (from the page's own request).")
                    return payload
                print("[capture] that quiz.cfc response was not a quiz (or unreadable), ignoring.")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                print(
                    "No quiz response captured "
                    f"({self._events_seen} network events seen in total)."
                )
                return None

            self._signal.wait(min(remaining, 0.5))
            self._signal.clear()

    def get_questions(self, timeout=30):
        payload = self.get_payload(timeout)
        if payload is None:
            raise TimeoutError("Quiz API response not received.")
        return payload["questions"]["data"]

    def close(self):
        for event, handler_id in self._handlers:
            try:
                self.driver.network.remove_event_handler(event, handler_id)
            except Exception:
                pass
        self._handlers = []
