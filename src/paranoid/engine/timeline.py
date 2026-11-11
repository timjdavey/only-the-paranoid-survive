"""make_timeline and Timeline. See docs/specs/engine/timeline.md.

Wires the steps in the spec's order: seed streams, ladder, loadings, weather,
the shared factor, onset, read noise, then the events on a longer horizon.
"""

from dataclasses import dataclass

import numpy as np

from .config import ScenarioConfig, engine_hash
from .draws import make_streams, whole
from .events import Event, apply_events
from .ladder import draw_ladder, draw_loadings
from .weather import draw_factor, draw_read_noise, draw_weather
from .world import World


@dataclass(frozen=True, eq=False)
class Timeline:
    config: ScenarioConfig
    seed: int
    engine_hash: str
    levels: np.ndarray  # (rounds, channels). base + weather + loadings × factor + impulse
    base: np.ndarray  # (rounds, channels). The climate, after events
    weather: np.ndarray  # (rounds, channels). Own weather
    factor: np.ndarray  # (rounds,). The shared factor, shock impulses included
    loadings: np.ndarray  # (rounds, channels). Per round, as a switch redraws the sleeper's
    impulse: np.ndarray  # (rounds, channels). A one-channel shock. All zeros otherwise
    read_noise_z: np.ndarray  # (rounds, channels). Standard normals, see game.md
    leader: int
    runner_up: int
    field: tuple[int, ...]  # the other channels, hedge included
    hedge: int
    sleeper: int | None
    events: tuple[Event, ...]

    def climate_leader(self, round: int) -> int:
        """Argmax of base in that round, lowest index on a tie."""
        if not 1 <= round <= self.config.rounds:
            raise ValueError(f"round must lie in [1, {self.config.rounds}], got {round}")
        return int(np.argmax(self.base[round - 1]))


def read_only(array: np.ndarray) -> np.ndarray:
    array = np.ascontiguousarray(array).copy()
    array.setflags(write=False)
    return array


def make_timeline(config: ScenarioConfig, seed: int) -> Timeline:
    streams = make_streams(seed, len(config.events))
    ladder = draw_ladder(streams.ladder, config)
    loadings = draw_loadings(streams.loadings, config, ladder.hedge)
    weather = draw_weather(streams.weather, config)
    factor = draw_factor(streams.factor, config)
    first_onset = whole(streams.onset, config.onset)
    read_noise_z = draw_read_noise(streams.read_noise, config)

    world = World.start(config, ladder, loadings)
    events = apply_events(world, streams.events, first_onset)

    rounds = config.rounds
    base = world.base[:rounds]
    run_loadings = world.loadings[:rounds]
    impulse = world.impulse[:rounds]
    factor = factor + world.shock[:rounds]
    levels = base + weather + run_loadings * factor[:, None] + impulse
    sleepers = [event.sleeper for event in events if event.sleeper is not None]

    return Timeline(
        config=config,
        seed=int(seed),
        engine_hash=engine_hash(config),
        levels=read_only(levels),
        base=read_only(base),
        weather=read_only(weather),
        factor=read_only(factor),
        loadings=read_only(run_loadings),
        impulse=read_only(impulse),
        read_noise_z=read_only(read_noise_z),
        leader=ladder.leader,
        runner_up=ladder.runner_up,
        field=ladder.field,
        hedge=ladder.hedge,
        sleeper=sleepers[-1] if sleepers else None,
        events=events,
    )
