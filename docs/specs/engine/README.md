# Engine spec

The engine is the game with no story. It turns a scenario and a seed into a [tape](../../glossary.md), plays bets against it, keeps the [record](../../design/interface.md#tools), and holds every fixed [baseline](../../design/baselines.md) as a pure function from what it may see to bets. It is deterministic, depends on numpy only, and knows nothing about skins, inspect_ai or any model. Why the game is the way it is lives in [mechanics](../../design/mechanics.md), [interface](../../design/interface.md) and [scenarios](../../design/scenarios.md).

## Pages

| Page | What it specifies |
|---|---|
| [config](config.md) | `ScenarioConfig`, the event specs, the six scenarios, proposed defaults, `engine_hash` |
| [tape](tape.md) | `make_tape`: seed streams, the ladder, weather, the shared factor, events, pinning, `Tape` |
| [game](game.md) | `Game`, `Reading`, `Record`, `play`, bet validation |
| [policies](policies.md) | `View`, `Policy`, the six fixed baselines, what each may see |
| [tests](tests.md) | Every test the engine suite runs, with the page it checks |

## Exports

`paranoid.engine` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#four-layers).

| Name | Kind | Page |
|---|---|---|
| `ScenarioConfig`, `ShockSpec`, `SwitchSpec`, `DriftSpec` | Frozen dataclasses | [config](config.md) |
| `SCENARIOS` | `dict[str, ScenarioConfig]`, the six scenarios by code name | [config](config.md) |
| `engine_hash` | `(ScenarioConfig) -> str` | [config](config.md) |
| `make_tape`, `Tape`, `Event` | `(ScenarioConfig, int) -> Tape` and its result | [tape](tape.md) |
| `Game`, `Reading`, `BetError` | The round loop | [game](game.md) |
| `Record`, `Row` | The agent's play so far | [game](game.md) |
| `play` | `(Policy, Tape, ...) -> Record`, a whole run with no model | [game](game.md) |
| `View`, `Policy`, `Start`, `split_budget` | What a policy sees and what it is, and the largest-remainder split | [policies](policies.md) |
| `uniform`, `discerning`, `complacent`, `perfect`, `hedge_rule`, `scout_rule` | The fixed baselines | [policies](policies.md) |

## Modules

    src/paranoid/engine/
      __init__.py    the exports above, nothing else
      config.py      ScenarioConfig, the event specs, engine_hash
      scenarios.py   SCENARIOS
      tape.py        make_tape, Tape, Event
      game.py        Game, Reading, BetError, play
      record.py      Record, Row
      policies.py    View, Start, Policy, the six baselines

- Nothing outside `__init__.py` is public. Tests import from `paranoid.engine` only.
- The only third-party import is numpy. `import-linter` enforces it, see [layout](../../harness/layout.md#four-layers).

## Conventions

- **Rounds are numbered from 1.** Round 1 is the first round the agent plays. Arrays are indexed from 0, so round `r` is row `r - 1`.
- **Channels are numbered from 0** to `channels - 1`. Which one leads is drawn per seed.
- **Levels, readings and output are floats in level points**, rounded to one decimal place only where the agent sees them, see [game](game.md).
- **Sigma** means the own-weather scale, the weather's SD per round. Every event size drawn "in sigmas" is a multiple of it, see [difficulty](../../design/mechanics.md#difficulty).
