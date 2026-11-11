"""The one-step lookahead over the five forecast rules' splits. Private.

See docs/specs/baselines/bayesian.md#rules. Every candidate reads the same draws,
so the comparison between them is paired.
"""

from collections.abc import Sequence

import numpy as np

from paranoid.engine import Bets, View

from .filter import Family, Runs, sample, step, update
from .forecast import fixed_draws


def best_split(
    view: View, runs: Runs, family: Family, mean: np.ndarray, candidates: Sequence[Bets], draws: int
) -> Bets:
    """The candidate with the highest value this round plus the rounds left times next round's best, first on a tie."""
    picks, level_normals, read_normals = fixed_draws(1, draws, view.channels, 2)
    levels = sample(runs, picks, level_normals)
    batch = runs.broadcast(draws)
    rounds_left = view.dials.rounds - view.round
    best, top = candidates[0], -np.inf
    for split in candidates:
        bets = np.array(split)
        value = float(bets @ mean) / view.budget
        if rounds_left > 0:
            noise = family.read_noise_k / np.sqrt(np.maximum(bets, 1))
            readings = np.where(bets > 0, levels + noise * read_normals, np.nan)
            ahead, _ = step(update(batch, family, readings, bets), family).mixture()
            value += rounds_left * float(ahead.max(axis=-1).mean())
        if value > top:
            best, top = split, value
    return best
