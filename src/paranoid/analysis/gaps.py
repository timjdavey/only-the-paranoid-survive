"""paired_gap, scenario_gap and public_gap. See docs/specs/analysis/scores.md#gaps.

A paired gap gives each side its own rng seeded alike and walks both in the same order over the same seeds,
so draw i is the same resample on both and level luck cancels.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd

from paranoid.engine import SCENARIOS

from .keys import ResultKey, differing, keys_in, label, rows_of
from .pool import by_scenario, draws, fresh_rng, percentiles, pooled

GAP_COLUMNS = ("pair", "diff", "lo", "hi", "n_shared")


def gap_row(pair: str, diff: float, drawn: np.ndarray, n_shared: int) -> dict:
    lo, hi = percentiles(drawn)
    return {"pair": pair, "diff": diff, "lo": lo, "hi": hi, "n_shared": n_shared}


def shared(a: pd.DataFrame, b: pd.DataFrame, seeds: Sequence[int] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The rows of each side on the seed_index values both scored, ordered by seed_index."""
    common = set(a["seed_index"]) & set(b["seed_index"])
    if seeds is not None:
        common &= set(seeds)
    return a[a["seed_index"].isin(common)], b[b["seed_index"].isin(common)]


def paired(a: pd.DataFrame, b: pd.DataFrame, pair: str) -> dict:
    """a's pooled score minus b's, with two rngs seeded alike."""
    return gap_row(pair, pooled(a) - pooled(b), draws(a, fresh_rng()) - draws(b, fresh_rng()), len(a))


def paired_gap(runs: pd.DataFrame, a: ResultKey, b: ResultKey) -> pd.DataFrame:
    """a minus b per scenario both scored, plus "headline", on the seeds both scored."""
    if a.setting.seed_set != b.setting.seed_set:
        raise ValueError(
            f"a paired gap needs one seed set, {label(a)} played {a.setting.seed_set} and {label(b)} {b.setting.seed_set}"
        )
    left, right = by_scenario(rows_of(runs, a)), by_scenario(rows_of(runs, b))
    pairs: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}
    for scenario in SCENARIOS:
        if scenario not in left or scenario not in right:
            continue
        hashes = set(left[scenario]["engine_hash"]) | set(right[scenario]["engine_hash"])
        if len(hashes) > 1:
            raise ValueError(f"{scenario} has engine hashes {', '.join(sorted(hashes))} across {label(a)} and {label(b)}")
        mine, theirs = shared(left[scenario], right[scenario])
        if len(mine):
            pairs[scenario] = (mine, theirs)
    if not pairs:
        raise ValueError(f"{label(a)} and {label(b)} share no seed")
    rows = [paired(mine, theirs, scenario) for scenario, (mine, theirs) in pairs.items()]
    rng_a, rng_b = fresh_rng(), fresh_rng()  # the headline walks both over every shared scenario, as its bar does
    drawn_a = np.mean([draws(mine, rng_a) for mine, _ in pairs.values()], axis=0)
    drawn_b = np.mean([draws(theirs, rng_b) for _, theirs in pairs.values()], axis=0)
    diff = float(np.mean([pooled(m) for m, _ in pairs.values()]) - np.mean([pooled(t) for _, t in pairs.values()]))
    rows.append(gap_row("headline", diff, drawn_a - drawn_b, min(len(m) for m, _ in pairs.values())))
    return pd.DataFrame(rows, columns=list(GAP_COLUMNS))


def scenario_gap(runs: pd.DataFrame, key: ResultKey, a: str, b: str, seeds: Sequence[int] | None = None) -> pd.DataFrame:
    """a's pooled score minus b's for one result row, on the seeds both scored, paired the same way."""
    groups = by_scenario(rows_of(runs, key))
    if a not in groups or b not in groups:
        raise ValueError(f"{label(key)} did not score both {a} and {b}")
    mine, theirs = shared(groups[a], groups[b], seeds)
    if not len(mine):
        raise ValueError(f"{label(key)} shares no seed between {a} and {b}")
    return pd.DataFrame([paired(mine, theirs, f"{a} − {b}")], columns=list(GAP_COLUMNS))


def partner(runs: pd.DataFrame, key: ResultKey) -> ResultKey:
    """The one result row of key's model and reasoning on the other seed set, equal in every other field."""
    other = "held-out" if key.setting.seed_set == "public" else "public"
    candidates = [
        k for k in keys_in(runs) if (k.model, k.reasoning) == (key.model, key.reasoning) and k.setting.seed_set == other
    ]
    found = [k for k in candidates if differing(key.setting, k.setting) == ["seed_set"]]
    if len(found) > 1:
        versions = " and ".join(k.setting.harness_version for k in found)
        raise ValueError(f"{label(key)} has two {other} rows to pair with, at harness versions {versions}")
    if found:
        return found[0]
    if not candidates:
        raise ValueError(f"{label(key)} has no {other} row, so there is no public gap")
    nearest = min((differing(key.setting, k.setting) for k in candidates), key=len)
    fields = ", ".join(name for name in nearest if name != "seed_set")
    raise ValueError(f"{label(key)}'s nearest {other} row also differs in {fields}")


def public_gap(runs: pd.DataFrame, key: ResultKey) -> pd.DataFrame:
    """Public minus held-out per scenario and headline. Not paired: each side is resampled on its own from one rng."""
    other = partner(runs, key)
    public, held = (key, other) if key.setting.seed_set == "public" else (other, key)
    left, right = by_scenario(rows_of(runs, public)), by_scenario(rows_of(runs, held))
    scenarios = [s for s in SCENARIOS if s in left and s in right]
    rows = []
    for scenario in scenarios:
        rng = fresh_rng()  # the public block first
        drawn = draws(left[scenario], rng) - draws(right[scenario], rng)
        n = min(len(left[scenario]), len(right[scenario]))
        rows.append(gap_row(scenario, pooled(left[scenario]) - pooled(right[scenario]), drawn, n))
    if not scenarios:
        raise ValueError(f"{label(public)} and {label(held)} scored no scenario in common")
    rng = fresh_rng()  # every public block in SCENARIOS order, then every held-out block
    drawn_public = np.mean([draws(left[s], rng) for s in scenarios], axis=0)
    drawn_held = np.mean([draws(right[s], rng) for s in scenarios], axis=0)
    diff = float(np.mean([pooled(left[s]) for s in scenarios]) - np.mean([pooled(right[s]) for s in scenarios]))
    n = min(min(len(left[s]), len(right[s])) for s in scenarios)
    rows.append(gap_row("headline", diff, drawn_public - drawn_held, n))
    return pd.DataFrame(rows, columns=list(GAP_COLUMNS))
