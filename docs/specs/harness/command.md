# Command

## Purpose

`paranoid` is the console script. `paranoid run` plays every row of a models config through the task, at one noise setting or over the noise grid. The proof of concept and the full study are both this command, with a different models file. `paranoid pilot <check>` runs one pilot cell, with no model where the check needs none, see [pilot](pilot.md). The models config and the reasoning mapping live here, as the command is what reads them. `paranoid analyse` belongs to the analysis layer and plugs in, see [subcommands](#subcommands) and the [analysis command](../analysis/command.md). The design is in [running](../../harness/running.md#commands) and [models](../../harness/models.md).

## Interface

```
paranoid run   [--models configs/models/poc.toml] [--skins example] [--seeds public]
               [--own-scale <value>|grid] [--limit N] [--log-dir logs/] [--only <id>] [--dry-run]
paranoid pilot <check> [--out logs/pilot/] [--models configs/models/poc.toml] [--only <id>] [--seeds N] [--workers N] [--dry-run]
paranoid analyse ...    registered by the analysis layer, see the analysis command page
```

```python
def main(argv: Sequence[str] | None = None) -> int

@dataclass(frozen=True)
class ModelRow:
    id: str                            # the inspect model string
    kind: Literal["llm", "baseline", "jev", "timestral"]
    reasoning: tuple[str, ...]         # one or more of the grid, or ("n/a",) for a provider row
    reasoning_kind: Literal["effort", "budget", "n/a"]   # what the provider takes, see Reasoning below
    max_tokens: int | None = None      # the model's own output limit, see models.md
    released: date | None = None
    eci: float | None = None
    notes: str = ""

REASONING = ("off", "low", "medium", "high", "max", "on")
EFFORT_PREFIXES = ("openai/", "anthropic/", "google/", "openrouter/")   # inspect maps an effort for all four
BUDGETS = {"low": 1024, "medium": 4096, "high": 16384, "max": 32768}    # reasoning_tokens per setting, see Reasoning below
SKIN_READERS = ("llm", "jev")          # the kinds whose model reads the skin, see run below

def load_models(path: str | Path) -> list[ModelRow]
def generate_config(row: ModelRow, reasoning: str) -> GenerateConfig
```

## Behaviour

### Subcommands

- **`main` loads `.env` first**, with `python-dotenv`, never overriding a variable already set. So `run`'s skin check sees `PARANOID_SKINS` from the file, as inspect's own command does.
- **`main`** parses `argv` with `argparse`, dispatches, and returns 0 on success and 1 on a `ValueError`, whose message it prints. Any other exception propagates with its traceback, bar one: `run` catches an eval that fails, prints it and carries on to the next, then returns 1, see [run](#run).
- **`run` and `pilot`** are built in.
- **Other subcommands come from the entry point group `paranoid.commands`.** The analysis layer registers `analyse = "paranoid.analysis.cli:analyse"`, see [analysis command](../analysis/command.md#dispatch). `main` discovers them with `importlib.metadata.entry_points` and loads one only when it is named, so the harness never imports the analysis layer and the layer rule holds, see [layout](../../harness/layout.md#six-layers).

### Models config

- **`load_models`** reads a TOML file of `[[model]]` tables with the columns in [models](../../harness/models.md#columns). `reasoning` may be a string or a list. Every row gets a `ModelRow`.
- **`reasoning_kind`** is `"n/a"` for a provider row. For an `llm` row it is the file's `reasoning_kind` column when present, else `"effort"` when `id` starts with one of `EFFORT_PREFIXES` and `"budget"` otherwise. The column is for the exceptions, such as `claude-haiku-4-5`, which is an Anthropic model that takes only a budget.
- **Validation** raises `ValueError` naming the row when:
  - `kind` is not one of the four, or `id` does not start with `baseline/`, `jev/` or `timestral/` when `kind` says it should, or does when it should not.
  - A `reasoning` value is not in `REASONING`, or a provider row has any value but `n/a`, or an `llm` row has `n/a`.
  - `reasoning_kind` in the file is not `effort` or `budget`, or is set on a provider row.
  - Two rows share `id` and a `reasoning` value.
  - `max_tokens`, when present, is not a positive whole number.
- **The two configs in `configs/models/`** both load clean. A test checks it, see [tests](tests.md#command).

### Reasoning

`generate_config(row, reasoning)` maps the shared grid to inspect's `GenerateConfig`, see [reasoning](../../harness/models.md#reasoning).

| Setting | `reasoning_kind = "effort"` | `reasoning_kind = "budget"` |
|---|---|---|
| `off` | `reasoning_effort="none"`, the explicit off | The same. A budget of 0 is not off, see [checked](#checked) |
| `low`, `medium`, `high` | `reasoning_effort` of the same name | `reasoning_tokens` from the budget table |
| `max` | `reasoning_effort="max"`. inspect sends the provider's highest effort where it has no `max` | The `max` budget |
| `on` | Nothing set. The model thinks and will not be told otherwise | The same |
| `n/a` | Nothing set | Nothing set |

- **`off` is sent, never left to a default.** A model that thinks unless told not to would otherwise play its `off` row with thinking on, and the row would equal its `on` row. `reasoning_effort="none"` is inspect's off on every provider in `configs/models/`, see [checked](#checked).
- **`max` is never `xhigh`.** On Claude 4.7 and later `xhigh` is a level of its own below `max`, so sending it would play the wrong row. The grid skips `xhigh`, see [reasoning](../../harness/models.md#reasoning).
- **A model that cannot turn thinking off does not list `off`**, see [reasoning](../../harness/models.md#reasoning). The harness cannot tell which models those are, so the file says, and a provider that rejects the off value fails that eval as any bad setting does.
- **The budget table** is `BUDGETS`: `low` 1024, `medium` 4096, `high` 16384, `max` 32768. The analysis reads a setting back through it, see [reasoning](../analysis/runs.md#reasoning). It is ours, so a row's budget does not move when inspect's own table does. A budget row is for a model that takes no effort, which today is `claude-haiku-4-5` alone. inspect raises on `reasoning_tokens` for Claude 4.7 and later, see [checked](#checked).
- **`max_tokens`** is set from the row when present, else left to the provider's default, see [sampling](../../harness/models.md#sampling).
- **Temperature is never set.**
- **`cache_prompt` is never set**, so inspect's default stands and the provider's prompt cache is on wherever there is one, see [prompt caching](../../harness/models.md#prompt-caching).

### `run`

- **`--skins` is a comma list of skin names**, `example` by default. The proof of concept passes its two held-out skins, see [running](../../harness/running.md#commands). Every name is checked against `load_skins()` before any eval runs. A name that is not loaded, or one given twice, raises `ValueError` listing the loaded names and naming `PARANOID_SKINS`, so `main` returns 1 and nothing is spent.
- **Only a row that reads the skin plays every skin.** A row whose `kind` is in `SKIN_READERS` plays each skin in the order given. Any other row plays the first skin only, as it never reads the story, see [two lists](../../harness/models.md#two-lists).
- **For every row, every `reasoning` value and every skin the row plays** it calls `inspect_ai.eval(paranoid, model=row.id, task_args={"skin": ..., "seeds": ...}, metadata={"reasoning": r, "kind": row.kind}, log_dir=..., limit=..., retry_on_error=1, **generate_config(row, r).model_dump(exclude_none=True))`, passing the `paranoid` task function itself, see [modules](README.md#modules), with `max_connections=4` on LLM rows and the provider's own cap on the rest. `eval` has no `config` argument, so the generate config goes in as keywords, see [checked](#checked). Provider rows pass `model_args` as the provider needs, none by default. The tool choice is the solver's to pick, see [each round](solver.md#each-round).
- **Order.** Provider rows first, then LLM rows in file order. Jev and Timestral rows are what the study compares against, so they run before anything that costs tokens. Within a row and setting the skins run in the order given, so a model has both sides of its [skin sensitivity](../analysis/tables.md#the-results-page) gap before the next model starts.
- **No baseline rows are needed.** Every sample's score already holds all six baselines' outputs on its own timeline, see [scoring one run](scorer.md#scoring-one-run), so the analysis reads the Complacent baseline's bar from any log. A `baseline/` row still runs if listed, which is how the provider invariant is checked, see [tests](tests.md#providers).
- **`--own-scale`** takes one value or the word `grid`, and is passed to the task as its `own_scale` arg, see [scenarios and config](task.md#scenarios-and-config). Unset, the task plays the frozen default and no events are pinned. `grid` plays every setting in `load_grid().own_scale` in file order, one eval per setting, inside each row, reasoning value and skin. A value that is not a positive number raises `ValueError` before any eval runs.
- **The full study is this command with the full list and the grid**: `paranoid run --models configs/models/full.toml --skins <a>,<b> --seeds held-out --own-scale grid`. The analysis reads the [noise threshold](../analysis/scores.md#noise-threshold) off those logs.
- **`--only <id>`** runs one row. **`--limit`** caps samples per eval, as inspect does. **`--dry-run`** prints each eval call and runs nothing.
- **A Timestral row with the extra missing** is skipped with one line saying so, and `run` carries on. A missing key for an LLM row is left to inspect, which fails that eval, and `run` carries on to the next row and returns 1 at the end.
- **Logs** go to `--log-dir`, named by inspect, one per eval and so one per skin. Each holds the metadata in [dataset](task.md#dataset), so the analysis layer can tell them apart without the config. A log from a held-out skin never leaves the machine, see [contamination](../../harness/contamination.md#public-and-held-out).
- **The log carries its setting.** `metadata` on the eval puts `reasoning` and `kind` in `EvalLog.eval.metadata`, as neither is in a sample's metadata, and `on` sets nothing a generate config would show. The analysis reads them first and falls back to the config, see [reasoning](../analysis/runs.md#reasoning).

### `pilot`

- **`paranoid pilot <check>`** builds a `CellArgs` from the options, with `seeds` capped by `PARANOID_PILOT_SEEDS` when set, and calls `run_cell(check, args)`, see [pilot](pilot.md#interface). It prints each path the cell wrote.
- **`--workers N`** splits an engine cell's seeds over `N` processes, 1 unless given. The CSV is the same bytes at any `N`, see [shared rules](pilot.md#shared-rules).
- **An unknown check** raises `ValueError` listing the names in `CELLS`, so `main` prints them and returns 1.
- **What each cell runs and writes** is on the [pilot](pilot.md) page, one section per cell. Nothing about a cell lives here.

## Invariants

- `load_models` on both files in `configs/models/` raises nothing.
- `generate_config` never sets `temperature` or `cache_prompt`.
- `generate_config` sets something for every setting but `on` and `n/a`, so no two settings of one row send the same config.
- `paranoid run --dry-run` runs no eval and touches no key. The pilot's invariants are on the [pilot](pilot.md#invariants) page.
- `run` runs no eval before every name in `--skins` is known to be loaded.
- A row whose `kind` is not in `SKIN_READERS` is played on one skin, however many are named.

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289, and read from its provider source. No key was used, so no provider was called.

| Question | Answer |
|---|---|
| Does `eval(metadata=...)` land in `EvalLog.eval.metadata` | Yes, as given |
| Does `eval` take a `config` | No. It raises on one. Generate config fields are keyword arguments, and they land in `EvalLog.eval.model_generate_config` |
| Does `eval` take `retry_on_error` | Yes, and `Task` does not, see [task settings](task.md#task-settings) |
| The values `reasoning_effort` takes | `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` |
| Do all four of `EFFORT_PREFIXES` take an effort | Yes. inspect maps `reasoning_effort` for each, so the default kind is right |

What inspect sends for each setting, by provider:

| Provider | `low`, `medium`, `high` | `max` | `none` | `reasoning_tokens` |
|---|---|---|---|---|
| Anthropic, Claude 4.6 and later | Adaptive thinking with `output_config.effort` of the same name | `max` | `thinking` `disabled` on 4.7 and later, `between_tools` on Sonnet 5.5. No `thinking` field on 4.6, which is off. Left on for Opus 5.5 and Fable, which cannot turn it off | Raises on 4.7 and later |
| Anthropic, before 4.6 | Extended thinking, with a budget from inspect's table: 4096, 10000, 16000 | A budget of 32000 | No `thinking` field, which is off | Sent as `budget_tokens`. 0 goes as a budget of 0, which is not off |
| OpenAI | `reasoning.effort` as given | `xhigh` before GPT-5.6 | `none` as given. Dropped with a warning on a model that has no reasoning, such as `gpt-4o` | Ignored |
| Google, Gemini 3 and later | `thinking_level` of the same name | `high` | `thinking_budget=0`. A Pro model gets a warning and keeps thinking | `thinking_budget` |
| OpenRouter | `reasoning.effort` as given | `max` as given | `reasoning.effort` of `none` | `reasoning.max_tokens` |

- **So no row needs a budget to turn thinking off**, and `reasoning_kind = "budget"` only picks who sets the budget, us or inspect.
- **A row that lists `off` for a model that cannot turn it off plays with thinking on** on Anthropic and Google, with a warning and no error. The models files must not list it, see [reasoning](#reasoning).

## Verify before code

Each needs a key, so none was run. One call per row and setting, with a small `max_tokens` and the [`submit`](solver.md#submit) tool.

- **That each provider takes what inspect sends.** For every `llm` row in `configs/models/` and every setting it lists, `get_model(row.id, config=generate_config(row, r)).generate(...)` returns without a 400. A setting that fails leaves the row, or the row gets a `reasoning_kind`. This also checks the model ids. The first `run` of that row waits on it.
- **That `off` is off.** The same call on every `off` row has `usage.reasoning_tokens` of 0 or `None`, and no reasoning block in the reply. OpenRouter passes `none` on to a model it does not own, so those rows are the ones in doubt. Every `off` row waits on it.
