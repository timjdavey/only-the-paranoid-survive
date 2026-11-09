# Harness spec

The harness is the inspect_ai layer. It turns one run of the game into one inspect sample, plays a model through it one fresh call a round, scores the run against the fixed [baselines](../../design/baselines.md) on the same tape, and reads the metrics off the log. It also plays the models that cannot call a tool, through providers, and holds the `paranoid` command. It depends on the skins layer, the engine and inspect_ai, and knows nothing about pandas or plots. Why it is shaped this way lives in [inspect](../../harness/inspect.md), [prompts](../../harness/prompts.md), [interface](../../design/interface.md) and [scoring](../../design/scoring.md).

## Pages

| Page | What it specifies |
|---|---|
| [task](task.md) | The `paranoid` task and its args, seeds and seed files, the dataset, sample metadata, `RunStore`, warm up, the noise grid |
| [solver](solver.md) | `round_loop`, the `submit` tool, the retry rule and giving up, tool choice, the pilot's `notes` and `compute` tools |
| [providers](providers.md) | `StoreAPI` and the three providers, `baseline/`, `jev/` and `timestral/` |
| [scorer](scorer.md) | `gain`, the pooled scenario score, error bars, headline, weakest trait, retry share |
| [command](command.md) | `paranoid poc` and `paranoid pilot`, the models config, reasoning settings |
| [tests](tests.md) | Every test the harness suite runs, with the page it checks |

## Exports

`paranoid.harness` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#four-layers).

| Name | Kind | Page |
|---|---|---|
| `paranoid` | The inspect `@task` | [task](task.md) |
| `RunStore`, `StoredRow` | The `StoreModel` on every sample, and its row type | [task](task.md) |
| `load_seeds`, `parse_seeds`, `scenario_config` | Seed files, the `seeds` arg, the config a sample plays | [task](task.md) |
| `round_loop`, `tool_choice_for` | The round loop solver and the forced or auto rule | [solver](solver.md) |
| `submit`, `notes`, `compute` | The tools | [solver](solver.md) |
| `StoreAPI`, `BaselineAPI`, `JevAPI`, `TimestralAPI` | The provider base and the three providers | [providers](providers.md) |
| `JevAnswer`, `JevClient`, `Forecaster` | Jev's reply, and the two seams a test fakes | [providers](providers.md) |
| `POLICIES`, `TIMESTRAL_POLICIES` | Baseline names to engine policies, Timestral ids to forecast rules | [providers](providers.md) |
| `gain` | The `@scorer` | [scorer](scorer.md) |
| `scenario_score`, `headline`, `weakest_trait`, `retry_share` | The `@metric`s | [scorer](scorer.md) |
| `pooled_score`, `bootstrap`, `TRAITS` | The maths the metrics share, and scenario to trait | [scorer](scorer.md) |
| `load_models`, `ModelRow`, `generate_config` | The models config and the reasoning mapping | [command](command.md) |
| `REASONING`, `EFFORT_PREFIXES` | The reasoning grid, and the providers that take an effort rather than a budget | [command](command.md) |
| `main` | The `paranoid` console script | [command](command.md) |

## Modules

    src/paranoid/harness/
      __init__.py      the exports above, nothing else
      task.py          paranoid, scenario_config, the dataset
      seeds.py         load_seeds, parse_seeds
      store.py         RunStore, StoredRow
      solver.py        round_loop, tool_choice_for
      tools.py         submit, notes, compute
      compose.yaml     the sandbox for compute, network off
      scorer.py        gain
      metrics.py       the four metrics, pooled_score, bootstrap, TRAITS
      providers/
        __init__.py    the @modelapi registrations, StoreAPI
        baseline.py    BaselineAPI, POLICIES
        jev.py         JevAPI, JevClient
        timestral.py   TimestralAPI, Forecaster, TIMESTRAL_POLICIES
      models.py        load_models, ModelRow, generate_config
      cli.py           main, poc, pilot
      pilot/           one module per pilot page, one function per cell

- Nothing outside `__init__.py` is public. Tests import from `paranoid.harness` only.
- Third-party imports are inspect_ai, numpy, pydantic and tomllib, plus `typesafe-sdk` inside `jev.py` and torch and Timestral inside `timestral.py`, imported lazily so the default install runs without them. `import-linter` enforces the layer rule, see [layout](../../harness/layout.md#four-layers).
- `pyproject.toml` registers the providers under the `inspect_ai` entry point and `main` as the `paranoid` console script, and ships `compose.yaml` as package data.

## Names from the engine

The harness imports these from `paranoid.engine`. Their behaviour is in the [engine spec](../engine/README.md#exports), and the engine's side of this boundary is [what the layers above read](../engine/README.md#what-the-layers-above-read).

| Name | What the harness uses it for |
|---|---|
| `SCENARIOS`, `ScenarioConfig`, `engine_hash`, `GENERATOR_VERSION` | The config a sample plays, and the hash and version in its metadata, see [scenarios and config](task.md#scenarios-and-config) |
| `make_tape`, `Tape` | The tape the store rebuilds from config and seed, see [store](task.md#store) |
| `Game`, `Record`, `Row`, `BetError` | The round the `submit` tool plays and the rows the store keeps, see [submit](solver.md#submit) |
| `play` | Warm up rows, and every baseline's output in the score, see [warm up](task.md#warm-up) and [scoring one run](scorer.md#scoring-one-run) |
| `Policy`, `HedgeRule`, `ScoutRule`, `uniform`, `discerning`, `complacent`, `perfect`, `hedge_rule`, `scout_rule` | `POLICIES` in the baseline provider, see [baseline](providers.md#baseline) |
| `split_budget` | Jev's probabilities and Timestral's odds into bets, see [Jev](providers.md#jev) and [Timestral](providers.md#timestral) |

## Names from the skins layer

The harness imports these from `paranoid.skins`. Their signatures and behaviour are in the [skins spec](../skins/README.md#exports), and what the harness reads from a skin is in [what the harness reads](../skins/README.md#what-the-harness-reads).

| Name | What the harness uses it for |
|---|---|
| `Skin`, `SkinError` | The skin a run plays. `SkinError` covers `LintError`, so a bad skin is one error on load |
| `load_skins` | Every skin by name, the example skin always, see [task settings](task.md#task-settings) |
| `render_system_prompt`, `render_record` | The system prompt and the record, the one way the harness renders either, see [each round](solver.md#each-round) |
| `prompt_hash` | The skin's hash in log metadata. It covers every word the model reads from the skin, `bets_text` included, see [prompt hash](../skins/render.md#prompt-hash) |
| `lint_text` | The banned word check on messages and replies, see [tests](tests.md) and [command](command.md) |

## Conventions

- **One sample is one run.** One scenario, one seed, one skin. Its id is `<scenario>/<seed position>`, see [task](task.md#dataset).
- **The tape is never in the log.** The store holds the scenario, the seed and the knobs, and every reader rebuilds the tape with `make_tape`, see [tape](../engine/tape.md#interface).
- **The harness writes no text for the agent.** Every word the model sees comes from the skin or from the record's own CSV, the tool's parameter text included. The one thing the harness composes is the tool result, which is a CSV row, see [submit](solver.md#submit). The pilot tools are the exception: the notes echo and compute's output are whatever came back, and neither runs in the headline.
- **A run never errors on the model's account.** Ten failed tries in a round is a give up, scored as a gain of 0, see [giving up](scorer.md#giving-up). An error in a log is infrastructure.
- **Rounds are numbered from 1**, as in the [engine](../engine/README.md#conventions). The store's `rows` list is indexed from 0, so round `r` is `rows[r − 1]`.
- **Warm up rows are not the agent's.** A record pre-filled by a baseline counts toward the record the agent sees, never toward its score, see [scorer](scorer.md#scoring-one-run).
- **A held-out seed's value is never in a log**, see [dataset](task.md#dataset).
- **Tests need no network and no key.** They play `mockllm/model` and the baseline provider, and fake Jev and Timestral, see [tests](tests.md).
