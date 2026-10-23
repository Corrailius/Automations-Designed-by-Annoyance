import random


class AnswerPlanner:
    """Decides whether the next answer is right or deliberately wrong.

    Port of the bot's goodOne / falseOne logic: answers come in cycles of
    `good` right + `wrong` wrong answers, shuffled inside each cycle.
    """

    def __init__(self, good=2, wrong=1, rng=None):
        self.good = max(0, int(good))
        self.wrong = max(0, int(wrong))
        self.rng = rng or random.Random()
        self._queue = []

    def next_is_correct(self):
        if self.wrong == 0:
            return True
        if not self._queue:
            self._queue = [True] * self.good + [False] * self.wrong
            self.rng.shuffle(self._queue)
        return self._queue.pop()
