"""gain, the scorer. See docs/specs/harness/scorer.md#scoring-one-run.

The scorer is the only reader of a timeline, and only through the store. It never reads the messages.
"""

from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Any

from inspect_ai.scorer import Score, Scorer, Target, scorer
from inspect_ai.solver import TaskState

from paranoid.baselines import complacent, discerning, hedge_rule, perfect, scout_rule, uniform
from paranoid.engine import Policy, Record, Row, Timeline, play
from paranoid.skins import render_record

from .config import skin_named
from .metrics import headline, retry_share, scenario_score, tool_use_share, weakest_trait
from .store import RunStore, timeline_for, uncapped

# The six marks in Score.value, each at its defaults.
MARKS: Mapping[str, Policy] = MappingProxyType(
    {
        "uniform": uniform,
        "discerning": discerning,
        "complacent": complacent,
        "perfect": perfect,
        "hedge_rule": hedge_rule,
        "scout_rule": scout_rule,
    }
)


def total(rows: Iterable[Row]) -> float:
    """The one sum of output, so the agent and every baseline are summed the same way."""
    return sum((row.output for row in rows), 0.0)


def explore_points(rows: tuple[Row, ...], timeline: Timeline, budget: int) -> float | None:
    """Mean of budget − max(bets) over the agent's rounds before the first onset, or every round with no event."""
    onset = timeline.events[0].onset if timeline.events else None
    before = [budget - max(row.bets) for row in rows if onset is None or row.round < onset]
    return sum(before) / len(before) if before else None


def sleeper_round(rows: tuple[Row, ...], timeline: Timeline) -> int | None:
    """The first agent round at or after the sleeper's event with a bet on the sleeper. 0 if never."""
    if timeline.sleeper is None:
        return None
    onset = [event.onset for event in timeline.events if event.sleeper is not None][-1]
    return next((row.round for row in rows if row.round >= onset and row.bets[timeline.sleeper] >= 1), 0)


def score_value(store: RunStore) -> dict[str, Any]:
    """Every key of Score.value. See the table in docs/specs/harness/scorer.md#scoring-one-run."""
    config, record = store.config(), store.record()
    timeline = store.timeline()
    warm = store.warm_up_rounds
    agent = record.rows[warm:]
    marks_timeline = timeline_for(uncapped(config), timeline.seed)
    start = Record(record.rows[:warm])
    marks = {name: total(play(policy, marks_timeline, record=start).rows[warm:]) for name, policy in MARKS.items()}
    output = total(agent)
    gain = 0.0 if store.gave_up else output - marks["uniform"]
    gap = marks["discerning"] - marks["uniform"]
    tries = store.tries
    return {
        "output": output,
        **marks,
        "gain": gain,
        "gap": gap,
        "run_score": gain / gap if gap else None,
        "rounds": len(tries),
        "warm_up_rounds": warm,
        "retries": sum(tries) - len(tries),
        "retry_rounds": sum(1 for t in tries if t > 1),
        "gave_up": int(store.gave_up),
        "bad_calls": store.bad_calls,
        "no_calls": store.no_calls,
        "cut_offs": store.cut_offs,
        "notes_rounds": store.notes_rounds,
        "compute_rounds": store.compute_rounds,
        "unchanged_rounds": sum(1 for r in record.unchanged_rounds() if r > warm),
        "explore_points": explore_points(agent, timeline, config.budget),
        "sleeper_round": sleeper_round(agent, timeline),
    }


@scorer(metrics=[scenario_score(), headline(), weakest_trait(), retry_share(), tool_use_share()])
def gain() -> Scorer:
    """The run's output beside the six baselines' on the same timeline over the same rounds."""

    async def score(state: TaskState, target: Target) -> Score:
        store = state.store_as(RunStore)
        metadata = {key: getattr(store, key) for key in ("scenario", "seed_set", "seed_index")}
        metadata["engine_hash"] = store.timeline().engine_hash
        if store.seed_set == "public":
            metadata["seed"] = store.seed()
        answer = render_record(skin_named(store.skin), store.record())
        return Score(value=score_value(store), answer=answer, metadata=metadata)

    return score
