import random
import time


class Pacing:
    """Human-like waiting, ported from the bot's quizDuration logic."""

    FALLBACK_THINK_RANGE = (3.0, 8.0)

    def __init__(
        self,
        minutes_per_10,
        min_think,
        max_think,
        rng=None,
        sleeper=time.sleep,
        jitter=0.3,
    ):
        self.minutes_per_10 = minutes_per_10
        self.min_think = min_think
        self.max_think = max_think
        self.rng = rng or random.Random()
        self.sleeper = sleeper
        self.jitter = max(0.0, jitter)

    def think_time(self, payload, question_count):
        """Seconds to wait before answering one question."""
        if self.max_think <= 0:
            return 0.0

        try:
            duration = float((payload or {}).get("duration") or 0)
        except (TypeError, ValueError):
            duration = 0.0

        if duration > 0 and question_count > 0 and self.minutes_per_10 > 0:
            base = duration / 10 * self.minutes_per_10 * 60 / (question_count * 2)
        else:
            base = self.rng.uniform(*self.FALLBACK_THINK_RANGE)

        base *= self.rng.uniform(1 - self.jitter, 1 + self.jitter)
        return max(self.min_think, min(self.max_think, base))

    def wait(self, seconds):
        if seconds > 0:
            self.sleeper(seconds)

    def pause(self, bounds):
        self.wait(self.rng.uniform(*bounds))
