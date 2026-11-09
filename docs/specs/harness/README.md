# Harness spec

The harness is the inspect_ai layer. It turns one run of the game into one inspect sample, plays a model through it one fresh call a round, scores the run against the fixed [baselines](../../design/baselines.md) on the same tape, and reads the metrics off the log. It also plays the models that cannot call a tool, through providers, and holds the `paranoid` command. It depends on the skins layer, the engine and inspect_ai, and knows nothing about pandas or plots. Why it is shaped this way lives in [inspect](../../harness/inspect.md), [prompts](../../harness/prompts.md), [interface](../../design/interface.md) and [scoring](../../design/scoring.md).

## Pages

| Page | What it specifies |
|---|---|
| [task](task.md) | The `paranoid` task and its args, seeds and seed files, the dataset, sample metadata, `RunStore`, warm up, the noise grid |
| [solver](solver.md) | `round_loop`, the `submit` tool, the retry rule, tool choice, the pilot's `notes` and `compute` tools |
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
| `load_seeds`, `parse_seeds`, `scenario_config`, `prompt_hash` | Seed files, the `seeds` arg, the config a sample plays, the prompt's hash | [task](task.md) |
| `round_loop`, `RoundError` | The round loop solver and the error after ten failed tries | [solver](solver.md) |
| `submit`, `notes`, `compute` | The tools | [solver](solver.md) |
| `StoreAPI`, `BaselineAPI`, `JevAPI`, `TimestralAPI` | The provider base and the three providers | [providers](providers.md) |
| `POLICIES`, `TIMESTRAL_POLICIES` | Baseline names to engine policies, Timestral ids to forecast rules | [providers](providers.md) |
| `gain` | The `@scorer` | [scorer](scorer.md) |
| `scenario_score`, `headline`, `weakest_trait`, `retry_share` | The `@metric`s | [scorer](scorer.md) |
| `pooled_score`, `bootstrap`, `TRAITS` | The maths the metrics share, and scenario to trait | [scorer](scorer.md) |
| `load_models`, `ModelRow`, `generate_config` | The models config and the reasoning mapping | [command](command.md) |
| `main` | The `paranoid` console script | [command](command.md) |

## Modules

    src/paranoid/harness/
      __init__.py      the exports above, nothing else
      task.py          paranoid, scenario_config, prompt_hash, the dataset
      seeds.py         load_seeds, parse_seeds
      store.py         RunStore, StoredRow
      solver.py        round_loop, RoundError
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
      pilot.py         one function per pilot cell

- Nothing outside `__init__.py` is public. Tests import from `paranoid.harness` only.
- Third-party imports are inspect_ai, numpy, pydantic and tomllib, plus `typesafe-sdk` inside `jev.py` and torch and Timestral inside `timestral.py`, imported lazily so the default install runs without them. `import-linter` enforces the layer rule, see [layout](../../harness/layout.md#four-layers).
- `pyproject.toml` registers the providers under the `inspect_ai` entry point and `main` as the `paranoid` console script.

## Names from the skins layer

The harness uses these skins names, from [layout](../../harness/layout.md#four-layers) and [skins](../../harness/skins.md). The skins spec, to come, fixes their signatures. Until then this page assumes:

| Name | Assumed signature |
|---|---|
| `Skin` | A frozen dataclass with the fields in [what a skin file holds](../../harness/skins.md#what-a-skin-file-holds) |
| `load_skins(path: str \| None = None) -> Mapping[str, Skin]` | Every skin by name. The example skin always. `PARANOID_SKINS` when set |
| `render_system_prompt(skin: Skin) -> str` | The four-part system prompt, see [prompts](../../harness/prompts.md#system-prompt) |
| `render_record(skin: Skin, record: Record) -> str` | The record as CSV in the skin's channel names, see [user message](../../harness/prompts.md#user-message) |
| `lint(text: str) -> list[str]` | The banned words found, empty when clean |

## Conventions

- **One sample is one run.** One scenario, one seed, one skin. Its id is `<scenario>/<seed position>`, see [task](task.md#dataset).
- **The tape is never in the log.** The store holds the scenario, the seed and the knobs, and every reader rebuilds the tape with `make_tape`, see [tape](../engine/tape.md#interface).
- **The harness writes no text for the agent.** Every word the model sees comes from the skin or from the record's own CSV. The one thing the harness composes is the tool result, which is a CSV row, see [submit](solver.md#submit).
- **Rounds are numbered from 1**, as in the [engine](../engine/README.md#conventions). The store's `rows` list is indexed from 0, so round `r` is `rows[r − 1]`.
- **Warm up rows are not the agent's.** A record pre-filled by a baseline counts toward the record the agent sees, never toward its score, see [scorer](scorer.md#scoring-one-run).
- **Tests need no network and no key.** They play `mockllm/model` and the baseline provider, and fake Jev and Timestral, see [tests](tests.md).
