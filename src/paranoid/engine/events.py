"""Event and the event list. The shapes arrive in the next commit, see docs/specs/engine/timeline.md#events."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from .world import World

Numbers = Mapping[str, float | int | str | None]


@dataclass(frozen=True)
class Event:
    shape: Literal["shock", "switch", "drift"]
    onset: int  # first round it edits, from 1
    channel: int | None  # the channel that moved down, else None
    sleeper: int | None  # the channel that rose, if one did
    numbers: Numbers = field(hash=False)  # every per-seed draw by name


def apply_events(world: World, rngs: Sequence[np.random.Generator], first_onset: int) -> tuple[Event, ...]:
    if world.config.events:
        raise NotImplementedError("events arrive in the next commit")
    return ()
