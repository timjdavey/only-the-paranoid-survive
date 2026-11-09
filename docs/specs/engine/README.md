# Engine spec

The engine is the game with no story. It turns a scenario and a seed into a [tape](../../glossary.md), plays bets against it, keeps the [record](../../design/interface.md#tools), and holds every fixed [baseline](../../design/baselines.md) as a pure function from what it may see to bets. It is deterministic, depends on numpy only, and knows nothing about skins, inspect_ai or any model. Why the game is the way it is lives in [mechanics](../../design/mechanics.md), [interface](../../design/interface.md) and [scenarios](../../design/scenarios.md).

## Pages

| Page | What it specifies |
|---|---|
| [config](config.md) | `ScenarioConfig`, the event specs, the eight scenarios, proposed defaults, `engine_hash` |
| [tape](tape.md) | `make_tape`: seed streams, the ladder, weather, the shared factor, events, pinning, `Tape` |
| [game](game.md) | `Game`, `Record`, `Row`, `play`, bet validation |
| [policies](policies.md) | `View`, `Policy`, the six fixed baselines, what each may see |
| [tests](tests.md) | Every test the engine suite runs, with the page it checks |

## Exports

`paranoid.engine` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#four-layers).

| Name | Kind | Page |
|---|---|---|
| `ScenarioConfig`, `ShockSpec`, `SwitchSpec`, `DriftSpec` | Frozen dataclasses | [config](config.md) |
| `SCENARIOS` | Read only `Mapping[str, ScenarioConfig]`, the eight scenarios by code name | [config](config.md) |
| `engine_hash`, `GENERATOR_VERSION` | `(ScenarioConfig) -> str` and the int it covers | [config](config.md) |
| `make_tape`, `Tape`, `Event` | `(ScenarioConfig, int) -> Tape` and its result | [tape](tape.md) |
| `Game`, `BetError` | The round loop | [game](game.md) |
| `Record`, `Row` | The agent's play so far | [game](game.md) |
| `play` | `(Policy, Tape, ...) -> Record`, a whole run with no model | [game](game.md) |
| `View`, `Policy`, `Start`, `split_budget` | What a policy sees and what it is, and the largest-remainder split | [policies](policies.md) |
| `uniform`, `discerning`, `complacent`, `perfect`, `hedge_rule`, `scout_rule` | The fixed baselines, as instances | [policies](policies.md) |
| `HedgeRule`, `ScoutRule` | The two baselines with parameters, for pilot sweeps | [policies](policies.md) |

## What the layers above read

The engine is the bottom layer, so it takes nothing from another. What each layer above takes from it is listed on that layer's README, so every boundary is written on both sides, see [specs](../README.md#rules).

| Layer | Its list |
|---|---|
| skins | [Names from the engine](../skins/README.md#names-from-the-engine): `Record` and `Row` to render, and `play`, `make_tape`, `SCENARIOS` and `uniform` in its tests |
| harness | [Names from the engine](../harness/README.md#names-from-the-engine): the config and its hash, the tape, the game, `play`, the policies and `split_budget` |

## Modules

    src/paranoid/engine/
      __init__.py    the exports above, nothing else
      config.py      ScenarioConfig, the event specs, engine_hash
      scenarios.py   SCENARIOS
      tape.py        make_tape, Tape, Event
      game.py        Game, BetError, play
      record.py      Record, Row
      policies.py    View, Start, Policy, the six baselines

- Nothing outside `__init__.py` is public. Tests import from `paranoid.engine` only.
- The only third-party import is numpy. `import-linter` enforces it, see [layout](../../harness/layout.md#four-layers).

## Conventions

- **Rounds are numbered from 1.** Round 1 is the first round the agent plays. Arrays are indexed from 0, so round `r` is row `r - 1`.
- **Channels are numbered from 0** to `channels - 1`. Which one leads is drawn per seed.
- **Levels, readings and output are floats in level points**, rounded to one decimal place only where the agent sees them, see [game](game.md).
- **Sigma** means the own-weather scale, the weather's SD per round. Every event size drawn "in sigmas" is a multiple of it, see [difficulty](../../design/mechanics.md#difficulty).
- **The record is the only engine object that leaves the engine.** The skins layer renders it and the harness logs it. A tape or a view never leaves, see [tape](tape.md#interface).
- **The engine writes no text.** Nothing in it renders a prompt, a CSV or a message for a model. The skins layer renders the record, see [render](../skins/render.md#record).
