"""RunStore and StoredRow, the per-sample state. See docs/specs/harness/task.md#store.

The timeline is derived, never stored: a module-level LRU keyed by (engine_hash, seed) holds it,
so nothing on the timeline reaches the log.
"""

from collections import OrderedDict
from dataclasses import replace

from inspect_ai.util import StoreModel
from pydantic import BaseModel

from paranoid.engine import Game, Record, Row, ScenarioConfig, Timeline, engine_hash, make_timeline

from .config import scenario_config
from .seeds import SeedSet, load_seeds

TIMELINE_CACHE = 1024
_timelines: OrderedDict[tuple[str, int], Timeline] = OrderedDict()


def timeline_for(config: ScenarioConfig, seed: int) -> Timeline:
    """make_timeline(config, seed), from the LRU when it is there."""
    key = (engine_hash(config), seed)
    timeline = _timelines.get(key)
    if timeline is None:
        timeline = make_timeline(config, seed)
        _timelines[key] = timeline
        if len(_timelines) > TIMELINE_CACHE:
            _timelines.popitem(last=False)
    else:
        _timelines.move_to_end(key)
    return timeline


def uncapped(config: ScenarioConfig) -> ScenarioConfig:
    """The config with inertia_cap cleared. make_timeline never reads the cap, so the arrays are the same."""
    return config if config.inertia_cap is None else replace(config, inertia_cap=None)


class StoredRow(BaseModel):
    round: int
    bets: list[int]
    readings: list[float | None]  # the three fields of an engine Row. Output is never stored

    def row(self) -> Row:
        return Row(round=self.round, bets=tuple(self.bets), readings=tuple(self.readings))

    @classmethod
    def of(cls, row: Row) -> "StoredRow":
        return cls(round=row.round, bets=list(row.bets), readings=list(row.readings))


class RunStore(StoreModel):
    scenario: str = ""
    seed_set: str = ""  # "public" or "held-out"
    seed_index: int = 0  # the position in the seed list. Never the held-out value
    skin: str = ""
    rounds: int | None = None
    inertia: int | None = None
    own_scale: float | None = None
    tool_choice: str = ""  # "any" or "auto", as the solver resolved it
    rows: list[StoredRow] = []  # the record so far, warm up rows first
    warm_up_rounds: int = 0
    awaiting_submit: bool = False  # True while a round is waiting for a valid submit
    tries: list[int] = []  # generate calls per round the agent played
    gave_up: bool = False
    bad_calls: int = 0
    no_calls: int = 0
    cut_offs: int = 0
    notes_rounds: int = 0  # rounds with at least one notes call
    compute_rounds: int = 0  # rounds with at least one compute call
    notes: str = ""

    def seed(self) -> int:
        seed_set: SeedSet = "held-out" if self.seed_set == "held-out" else "public"
        return load_seeds(seed_set)[self.seed_index]

    def config(self) -> ScenarioConfig:
        return scenario_config(self.scenario, rounds=self.rounds, inertia=self.inertia, own_scale=self.own_scale)

    def timeline(self) -> Timeline:
        return timeline_for(self.config(), self.seed())

    def record(self) -> Record:
        return Record(stored.row() for stored in self.rows)

    def game(self) -> Game:
        return Game(self.timeline(), self.record())

    def round(self) -> int:
        return len(self.rows) + 1
