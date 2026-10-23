import time


class TimeBudgetReached(Exception):
    """Raised inside a quiz when the run's time budget is used up."""


class Deadline:
    """Total run time budget. Deadline(None) never expires."""

    def __init__(self, minutes=None, clock=time.monotonic):
        self.clock = clock
        self.end = None if minutes is None else clock() + minutes * 60

    def expired(self):
        return self.end is not None and self.clock() >= self.end

    def remaining(self):
        return float("inf") if self.end is None else max(0.0, self.end - self.clock())

    def check(self):
        if self.expired():
            raise TimeBudgetReached()
