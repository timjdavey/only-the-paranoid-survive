# Command

## Purpose

`paranoid` is the console script. `paranoid poc` plays every row of a models config through the task. `paranoid pilot <check>` runs one pilot cell, with no model where the check needs none, see [pilot](pilot.md). The models config and the reasoning mapping live here, as the command is what reads them. `paranoid analyse` belongs to the analysis layer and plugs in, see [subcommands](#subcommands) and the [analysis command](../analysis/command.md). The design is in [running](../../harness/running.md#commands) and [models](../../harness/models.md).

## Interface

```
paranoid poc   [--models configs/models/poc.toml] [--skin example] [--seeds public]
               [--limit N] [--log-dir logs/] [--only <id>] [--dry-run]
paranoid pilot <check> [--out logs/pilot/] [--models configs/models/poc.toml] [--only <id>] [--seeds N] [--dry-run]
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
EFFORT_PREFIXES = ("openai/", "anthropic/", "google/", "openrouter/")

def load_models(path: str | Path) -> list[ModelRow]
def generate_config(row: ModelRow, reasoning: str) -> GenerateConfig
```

## Behaviour

### Subcommands

- **`main`** parses `argv` with `argparse`, dispatches, and returns 0 on success and 1 on a `ValueError`, whose message it prints. Any other exception propagates with its traceback.
- **`poc` and `pilot`** are built in.
- **Other subcommands come from the entry point group `paranoid.commands`.** The analysis layer registers `analyse = "paranoid.analysis.cli:analyse"`, see [analysis command](../analysis/command.md#dispatch). `main` discovers them with `importlib.metadata.entry_points` and loads one only when it is named, so the harness never imports the analysis layer and the layer rule holds, see [layout](../../harness/layout.md#five-layers).

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
| `off` | Nothing set. The provider's default, which is no thinking where it can be off | The same |
| `low`, `medium`, `high` | `reasoning_effort` of the same name | `reasoning_tokens` from the budget table |
| `max` | `reasoning_effort="xhigh"`. inspect maps it to the provider's highest effort where there is no `xhigh` | The `max` budget |
| `on` | Nothing set. The model thinks and will not be told otherwise | The same |
| `n/a` | Nothing set | Nothing set |

- **The budget table**: `low` 1024, `medium` 4096, `high` 16384, `max` 32768. These are a convention to verify against each provider before the first run, see [verify before code](#verify-before-code).
- **`max_tokens`** is set from the row when present, else left to the provider's default, see [sampling](../../harness/models.md#sampling).
- **Temperature is never set.**

### `poc`

- **For every row and every `reasoning` value** it calls `inspect_ai.eval("paranoid", model=row.id, task_args={"skin": ..., "seeds": ...}, config=generate_config(row, r), metadata={"reasoning": r, "kind": row.kind}, log_dir=..., limit=...)`, with `max_connections=4` on LLM rows and the provider's own cap on the rest. Provider rows pass `model_args` as the provider needs, none by default. The tool choice is the solver's to pick, see [each round](solver.md#each-round).
- **Order.** Provider rows first, then LLM rows in file order. Jev and Timestral rows are what the study compares against, so they run before anything that costs tokens.
- **No baseline rows are needed.** Every sample's score already holds all six baselines' outputs on its own tape, see [scoring one run](scorer.md#scoring-one-run), so the analysis reads the Complacent baseline's bar from any log. A `baseline/` row still runs if listed, which is how the provider invariant is checked, see [tests](tests.md#providers).
- **`--only <id>`** runs one row. **`--limit`** caps samples per eval, as inspect does. **`--dry-run`** prints each eval call and runs nothing.
- **A Timestral row with the extra missing** is skipped with one line saying so, and `poc` carries on. A missing key for an LLM row is left to inspect, which fails that eval, and `poc` carries on to the next row and returns 1 at the end.
- **Logs** go to `--log-dir`, named by inspect. Each holds the metadata in [dataset](task.md#dataset), so the analysis layer can tell them apart without the config.
- **The log carries its setting.** `metadata` on the eval puts `reasoning` and `kind` in `EvalLog.eval.metadata`, as neither is in a sample's metadata or readable from a generate config for `off` and `on`. The analysis reads them first and falls back to the config, see [reasoning](../analysis/runs.md#reasoning).

### `pilot`

- **`paranoid pilot <check>`** builds a `CellArgs` from the options, with `seeds` capped by `PARANOID_PILOT_SEEDS` when set, and calls `run_cell(check, args)`, see [pilot](pilot.md#interface). It prints each path the cell wrote.
- **An unknown check** raises `ValueError` listing the names in `CELLS`, so `main` prints them and returns 1.
- **What each cell runs and writes** is on the [pilot](pilot.md) page, one section per cell. Nothing about a cell lives here.

## Invariants

- `load_models` on both files in `configs/models/` raises nothing.
- `generate_config` never sets `temperature`.
- `paranoid poc --dry-run` runs no eval and touches no key. The pilot's invariants are on the [pilot](pilot.md#invariants) page.

## Verify before code

- **The budget table and the effort names per provider**, against inspect's `GenerateConfig` and each provider's API, see the "to verify" notes in [`full.toml`](../../../configs/models/full.toml). `EFFORT_PREFIXES` is a first guess for the same reason. `generate_config` waits on it.
- **That `eval(metadata=...)` lands in `EvalLog.eval.metadata`.** If inspect has no such argument, `poc` writes the two keys into every sample's metadata through a task arg instead. `poc` waits on it.
