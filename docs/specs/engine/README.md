# Engine spec

The engine is the game with no story. It turns a scenario and a seed into a [timeline](../../glossary.md), plays bets against it, keeps the [record](../../design/interface.md#tools), and says what a policy may see, so the [baselines layer](../baselines/README.md) can hold every fixed [baseline](../../design/baselines.md) as a pure function from that view to bets. It is deterministic, depends on numpy only, and knows nothing about skins, inspect_ai or any model. Why the game is the way it is lives in [mechanics](../../design/mechanics.md), [interface](../../design/interface.md) and [scenarios](../../design/scenarios.md).

## Pages

| Page | What it specifies |
|---|---|
| [config](config.md) | `ScenarioConfig`, the event specs, the eight scenarios, proposed defaults, `engine_hash` |
| [timeline](timeline.md) | `make_timeline`: seed streams, the ladder, weather, the shared factor, events, pinning, `Timeline` |
| [game](game.md) | `Game`, `Record`, `Row`, `play`, bet validation |
| [view](view.md) | `View`, `Start`, `Dials`, `Policy`, what a policy may see and is handed, and `split_budget` |
| [tests](tests.md) | Every test the engine suite runs, with the page it checks |

## Exports

`paranoid.engine` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#six-layers).

| Name | Kind | Page |
|---|---|---|
| `ScenarioConfig`, `ShockSpec`, `SwitchSpec`, `DriftSpec` | Frozen dataclasses | [config](config.md) |
| `SCENARIOS` | Read only `Mapping[str, ScenarioConfig]`, the eight scenarios by code name | [config](config.md) |
| `engine_hash`, `GENERATOR_VERSION` | `(ScenarioConfig) -> str` and the int it covers | [config](config.md) |
| `make_timeline`, `Timeline`, `Event` | `(ScenarioConfig, int) -> Timeline` and its result | [timeline](timeline.md) |
| `Game`, `BetError` | The round loop | [game](game.md) |
| `Record`, `Row` | The agent's play so far | [game](game.md) |
| `Bets` | `tuple[int, ...]`, one whole number per channel summing to the budget | [game](game.md) |
| `play` | `(Policy, Timeline, ...) -> Record`, a whole run with no model | [game](game.md) |
| `View`, `Policy`, `Start`, `Dials`, `split_budget` | What a policy sees, what it is handed, what it is, and the largest-remainder split | [view](view.md) |

## What the layers above read

The engine is the bottom layer, so it takes nothing from another. What each layer above takes from it is listed on that layer's README, so every boundary is written on both sides, see [specs](../README.md#rules).

| Layer | Its list |
|---|---|
| baselines | [Names from the engine](../baselines/README.md#names-from-the-engine): `View`, `Start`, `Dials`, `Policy`, `Bets`, `Timeline`, `Record` and `split_budget`, and `play`, `make_timeline`, `SCENARIOS`, `Game` and `Row` in its tests |
| skins | [Names from the engine](../skins/README.md#names-from-the-engine): `Record` and `Row` to render, and `play`, `make_timeline` and `SCENARIOS` in its tests |
| harness | [Names from the engine](../harness/README.md#names-from-the-engine): the config and its hash, the timeline, the game, `Bets`, `play`, `Policy` and `split_budget` |
| analysis | [Names from the engine](../analysis/README.md#names-from-the-engine): `make_timeline`, `Timeline` and `Event` for the switch kind a seed drew, `SwitchSpec` for the signal on the noise axis, and `SCENARIOS` to check the names a log claims |

## Modules

    src/paranoid/engine/
      __init__.py    the exports above, nothing else
      specs.py       Range, IntRange, the event specs, their casts and checks
      config.py      ScenarioConfig, GENERATOR_VERSION, engine_hash
      scenarios.py   SCENARIOS
      draws.py       the seed streams and the four draws
      ladder.py      the order, the ladder and the loadings
      weather.py     own weather, the shared factor, read noise
      world.py       the arrays events edit, on the longer horizon
      events.py      Event, each shape's draws, onsets, no two alike
      shock.py       a shock's impulse and its cap
      switch.py      a fall, a rise and an undo
      drift.py       a drift
      timeline.py    make_timeline, Timeline
      game.py        Game, BetError, play
      record.py      Record, Row, Bets
      view.py        View, Start, Dials, Policy, split_budget

- Nothing outside `__init__.py` is public. Tests import from `paranoid.engine` only.
- Every file stays under 300 lines, so the timeline is split by step. `timeline.py` wires the steps in the order of [timeline](timeline.md).
- `Bets` lives in `record.py`, as `Row` holds it. So `view.py` never imports `game.py`, which imports it.
- The only third-party import is numpy. `import-linter` enforces it, see [layout](../../harness/layout.md#six-layers).

## Conventions

- **Rounds are numbered from 1.** Round 1 is the first round the agent plays. Arrays are indexed from 0, so round `r` is row `r - 1`.
- **Channels are numbered from 0** to `channels - 1`. Which one leads is drawn per seed.
- **Levels, readings and output are floats in level points.** A reading is rounded to one decimal place, as the agent sees it, and output is worked out from the rounded readings, see [game](game.md#readings).
- **Sigma** means the own-weather scale, the weather's SD per round. Every event size drawn "in sigmas" is a multiple of it, see [difficulty](../../design/mechanics.md#difficulty).
- **The record is the only engine object that leaves the engine.** The skins layer renders it and the harness logs it. A timeline or a view never leaves, see [timeline](timeline.md#interface).
- **The engine writes no text.** Nothing in it renders a prompt, a CSV or a message for a model. The skins layer renders the record, see [render](../skins/render.md#record).
