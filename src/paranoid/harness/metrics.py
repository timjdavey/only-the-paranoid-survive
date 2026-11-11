"""The five metrics and the maths they share. See docs/specs/harness/scorer.md#pooling.

Every number a metric needs is in Score.value, so a log scores the same with no seed file and no engine.
Seeds are sorted by seed_index and scenarios walked in SCENARIOS order, so the analysis layer's
bootstrap sees the same draws, see docs/specs/analysis/scores.md.
"""

from collections.abc import Mapping, Sequence
from types import MappingProxyType

import numpy as np
from inspect_ai.scorer import Metric, SampleScore, metric

from paranoid.engine import SCENARIOS

BOOTSTRAP_DRAWS = 1000
BOOTSTRAP_SEED = 0

# Scenario code name to trait, from docs/design/scoring.md#traits.
TRAITS: Mapping[str, str] = MappingProxyType(
    {
        "no_change": "composure",
        "one_shock": "patience",
        "down_switch": "doubt",
        "up_switch": "curiosity",
        "shock_then_switch": "unlearning",
        "slow_drift": "vigilance",
        "switch_then_shock": "conviction",
        "up_switch_then_down_switch": "recall",
    }
)


def pooled_score(gains: Sequence[float], gaps: Sequence[float]) -> float:
    """sum(gains) / sum(gaps). Not a mean of run scores."""
    if len(gains) == 0 or len(gains) != len(gaps):
        raise ValueError("pooled_score needs one gap per gain, and at least one of each")
    total = float(np.sum(gaps))
    if total == 0:
        raise ValueError("pooled_score needs gaps that do not sum to 0")
    return float(np.sum(gains)) / total


def draws_of(gains: np.ndarray, gaps: np.ndarray, rng: np.random.Generator, draws: int) -> np.ndarray:
    """The pooled score of `draws` resamples of the seed indices, with replacement."""
    index = rng.integers(0, len(gains), size=(draws, len(gains)))
    return gains[index].sum(axis=1) / gaps[index].sum(axis=1)


def percentiles(values: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(lo), float(hi)


def bootstrap(
    gains: Sequence[float],
    gaps: Sequence[float],
    *,
    draws: int = BOOTSTRAP_DRAWS,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    """The 2.5th and 97.5th percentiles of the pooled score over resampled seeds."""
    pooled_score(gains, gaps)  # the same checks
    rng = np.random.default_rng(BOOTSTRAP_SEED) if rng is None else rng
    return percentiles(draws_of(np.asarray(gains, float), np.asarray(gaps, float), rng, draws))


def value(score: SampleScore, key: str) -> float:
    return float(score.score.value[key])  # type: ignore[index]


def by_scenario(scores: list[SampleScore]) -> dict[str, list[SampleScore]]:
    """Scored samples per scenario, scenarios in SCENARIOS order and seeds by seed_index."""
    groups: dict[str, list[SampleScore]] = {name: [] for name in SCENARIOS}
    for score in scores:
        groups.setdefault((score.sample_metadata or {})["scenario"], []).append(score)
    return {
        name: sorted(group, key=lambda s: (s.sample_metadata or {}).get("seed_index", 0))
        for name, group in groups.items()
        if group
    }


def arrays(group: list[SampleScore]) -> tuple[np.ndarray, np.ndarray]:
    return np.array([value(s, "gain") for s in group]), np.array([value(s, "gap") for s in group])


def share(group: list[SampleScore], key: str) -> float:
    rounds = sum(value(s, "rounds") for s in group)
    return sum(value(s, key) for s in group) / rounds if rounds else 0.0


@metric
def scenario_score() -> Metric:
    """{"<scenario>": s, "<scenario>_lo": lo, "<scenario>_hi": hi, "<scenario>_n": seeds, "<scenario>_failed": k}"""

    def compute(scores: list[SampleScore]) -> dict[str, float]:
        result: dict[str, float] = {}
        for name, group in by_scenario(scores).items():
            gains, gaps = arrays(group)
            lo, hi = bootstrap(gains, gaps)
            result |= {
                name: pooled_score(gains, gaps),
                f"{name}_lo": lo,
                f"{name}_hi": hi,
                f"{name}_n": float(len(group)),
                f"{name}_failed": sum(value(s, "gave_up") for s in group),
            }
        return result

    return compute


@metric
def headline() -> Metric:
    """{"headline": h, "lo": lo, "hi": hi, "scenarios": n}. Seeds resampled within each scenario, one rng."""

    def compute(scores: list[SampleScore]) -> dict[str, float]:
        groups = [arrays(group) for group in by_scenario(scores).values()]
        if not groups:
            raise ValueError("headline needs at least one scored sample")
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        drawn = np.mean([draws_of(gains, gaps, rng, BOOTSTRAP_DRAWS) for gains, gaps in groups], axis=0)
        lo, hi = percentiles(drawn)
        mean = float(np.mean([pooled_score(gains, gaps) for gains, gaps in groups]))
        return {"headline": mean, "lo": lo, "hi": hi, "scenarios": float(len(groups))}

    return compute


@metric
def weakest_trait() -> Metric:
    """{"<trait>": s}, one key. The lowest scenario score, ties to SCENARIOS order."""

    def compute(scores: list[SampleScore]) -> dict[str, float]:
        pooled = {name: pooled_score(*arrays(group)) for name, group in by_scenario(scores).items()}
        if not pooled:
            raise ValueError("weakest_trait needs at least one scored sample")
        name = min(pooled, key=lambda n: pooled[n])  # min keeps the first of a tie, and the dict is in SCENARIOS order
        return {TRAITS[name]: pooled[name]}

    return compute


@metric
def retry_share() -> Metric:
    """{"<scenario>": share, "all": share, "cut_off_share": share}, over rounds."""

    def compute(scores: list[SampleScore]) -> dict[str, float]:
        result = {name: share(group, "retry_rounds") for name, group in by_scenario(scores).items()}
        return result | {"all": share(scores, "retry_rounds"), "cut_off_share": share(scores, "cut_offs")}

    return compute


@metric
def tool_use_share() -> Metric:
    """{"notes": share, "compute": share}: rounds with a call over rounds played, overall."""

    def compute(scores: list[SampleScore]) -> dict[str, float]:
        return {"notes": share(scores, "notes_rounds"), "compute": share(scores, "compute_rounds")}

    return compute
