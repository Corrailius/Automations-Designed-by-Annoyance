"""Weighted ordering: lessons that are not completed come first more often,
completed ones are still played, just with a lower weight."""

import random


def weight_for(completed, completed_weight):
    """1.0 for a lesson that is not completed, `completed_weight` otherwise."""
    return max(0.0, completed_weight) if completed else 1.0


def weighted_order(items, weights, rng=None):
    """Return `items` in a random order where a higher weight tends to come first.

    Weighted sampling without replacement (Efraimidis-Spirakis). Items with a
    weight of 0 are dropped.
    """
    rng = rng or random.Random()
    keyed = []
    for item, weight in zip(items, weights):
        if weight <= 0:
            continue
        keyed.append((rng.random() ** (1.0 / weight), item))
    keyed.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in keyed]


def pick_weighted(items, weights, rng=None):
    """One item chosen with probability proportional to its weight, else None."""
    ordered = weighted_order(items, weights, rng)
    return ordered[0] if ordered else None
