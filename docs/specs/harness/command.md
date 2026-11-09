# Command

## Purpose

`paranoid` is the console script. `paranoid poc` plays every row of a models config through the task. `paranoid pilot <check>` runs one pilot cell, with no model where the check needs none. The models config and the reasoning mapping live here, as the command is what reads them. `paranoid analyse` belongs to the analysis layer and plugs in, see [subcommands](#subcommands). The design is in [running](../../harness/running.md#commands) and [models](../../harness/models.md).

## Interface

```
paranoid poc   [--models configs/models/poc.toml] [--skin example] [--seeds public]
               [--limit N] [--log-dir logs/] [--only <id>] [--dry-run]
paranoid pilot <check> [--out logs/pilot/] [--models configs/models/poc.toml] [--dry-run]
paranoid analyse ...    registered by the analysis layer
```

```python
def main(argv: Sequence[str] | None = None) -> int

@dataclass(frozen=True)
class ModelRow:
    id: str                            # the inspect model string
    kind: Literal["llm", "baseline", "jev", "timestral"]
    reasoning: tuple[str, ...]         # one or more of the grid, or ("n/a",) for a provider row
    max_tokens: int | None = None      # the model's own output limit, see models.md
    released: date | None = None
    eci: float | None = None
    notes: str = ""

REASONING = ("off", "low", "medium", "high", "max", "on")

def load_models(path: str | Path) -> list[ModelRow]
def generate_config(row: ModelRow, reasoning: str) -> GenerateConfig
def tool_choice_for(row: ModelRow, reasoning: str) -> Literal["forced", "auto"]
```

## Behaviour

### Subcommands

- **`main`** parses `argv` with `argparse`, dispatches, and returns 0 on success and 1 on a `ValueError`, whose message it prints. Any other exception propagates with its traceback.
- **`poc` and `pilot`** are built in.
- **Other subcommands come from the entry point group `paranoid.commands`.** The analysis layer registers `analyse = "paranoid.analysis.cli:analyse"`. `main` discovers them with `importlib.metadata.entry_points` and loads one only when it is named, so the harness never imports the analysis layer and the layer rule holds, see [layout](../../harness/layout.md#four-layers).

### Models config

- **`load_models`** reads a TOML file of `[[model]]` tables with the columns in [models](../../harness/models.md#columns). `reasoning` may be a string or a list. Every row gets a `ModelRow`.
- **Validation** raises `ValueError` naming the row when:
  - `kind` is not one of the four, or `id` does not start with `baseline/`, `jev/` or `timestral/` when `kind` says it should, or does when it should not.
  - A `reasoning` value is not in `REASONING`, or a provider row has any value but `n/a`, or an `llm` row has `n/a`.
  - Two rows share `id` and a `reasoning` value.
  - `max_tokens`, when present, is not a positive whole number.
- **The two configs in `configs/models/`** both load clean. A test checks it, see [tests](tests.md#command).

### Reasoning

`generate_config(row, reasoning)` maps the shared grid to inspect's `GenerateConfig`, see [reasoning](../../harness/models.md#reasoning).

| Setting | `GenerateConfig` |
|---|---|
| `off` | Nothing set. The provider's default, which is no thinking where it can be off |
| `low`, `medium`, `high` | `reasoning_effort` of the same name where the provider takes an effort. Else `reasoning_tokens` from the budget table |
| `max` | `reasoning_effort="xhigh"` where the provider takes it, else the provider's highest effort, else the `max` budget |
| `on` | Nothing set. The model thinks and will not be told otherwise |
| `n/a` | Nothing set |

- **The budget table** for providers that take only a token budget: `low` 1024, `medium` 4096, `high` 16384, `max` 32768. These are a convention to verify against each provider before the first run, see [Open](#open).
- **`max_tokens`** is set from the row when present, else left to the provider's default, see [sampling](../../harness/models.md#sampling).
- **Temperature is never set.**

### Tool choice

- **`tool_choice_for`** returns `"auto"` when the row's `id` starts with `anthropic/` and `reasoning` is not `off` or `n/a`, else `"forced"`. Claude rejects a forced tool with thinking on, see [the round loop](../../harness/inspect.md#the-round-loop).
- The value goes to the task as `-T tool_choice=...`, see [task](task.md#interface).

### `poc`

- **For every row and every `reasoning` value** it calls `inspect_ai.eval("paranoid", model=row.id, task_args={"skin": ..., "seeds": ..., "tool_choice": ...}, config=generate_config(row, r), log_dir=..., limit=..., max_connections=4)`. Provider rows pass `model_args` as the provider needs, none by default.
- **Order.** Provider rows first, baselines before Jev and Timestral, then LLM rows in file order. The baselines are cheap and their logs are what the LLM logs are read against.
- **`--only <id>`** runs one row. **`--limit`** caps samples per eval, as inspect does. **`--dry-run`** prints each eval call and runs nothing.
- **A Timestral row with the extra missing** is skipped with one line saying so, and `poc` carries on. A missing key for an LLM row is left to inspect, which fails that eval, and `poc` carries on to the next row and returns 1 at the end.
- **Logs** go to `--log-dir`, named by inspect. Each holds the metadata in [dataset](task.md#dataset), so the analysis layer can tell them apart without the config.

### Pilot cells

`paranoid pilot <check>` runs one cell. Each is a function in `pilot.py`, named below. Measures and decisions are on the pilot pages, the function writes the data they need.

| Check | Needs a model | What it runs | Writes |
|---|---|---|---|
| `streaks` | No | Tapes over a grid of `persistence`, 1000 seeds each, the No change and Down switch scenarios | A CSV: setting, seed, longest run of rounds the leader reads below the runner-up by chance, and the round the Scout rule moves |
| `tell` | No | Tapes over a grid of `factor_scale`, One shock and Down switch, 1000 seeds | A CSV: setting, seed, hedge move at the trough, and the hedge rule's hold or move |
| `luck` | No | `perfect` minus `discerning` on every scenario at every grid setting | A CSV: scenario, setting, seed, gap |
| `tape-sanity` | No | T22 and P12 from the [engine tests](../engine/tests.md#tape) at every setting in `configs/grid.toml` | A CSV: scenario, setting, baseline, pooled output |
| `noise-grid` | No | Every fixed baseline on One shock, Down switch and Up switch at every setting in `configs/grid.toml`, 1000 seeds | A CSV: scenario, setting, baseline, seed, output |
| `game-length` | No | The baselines at `rounds` of 30, 40 and 60 and `onset` ranges around the default, One shock, Down switch and the two-event scenarios | A CSV: scenario, rounds, onset, baseline, seed, output |
| `reading-roughness` | No | `HedgeRule(look=1,2,5)` and `ScoutRule(s=1,2,5)` over a grid of `read_noise_k` | A CSV: setting, baseline, parameter, seed, output, move round |
| `up-and-down` | No | Discerning, Complacent, hedge rule and Scout rule at `s` 1, 2, 5 on 1000 Down switch, Up switch and No change seeds | A CSV: scenario, kind of switch, baseline, seed, output, move round |
| `baseline-order` | No | Every fixed baseline on every scenario, 1000 seeds | A CSV: scenario, baseline, pooled output, and a line per order that breaks |
| `seeds` | Yes | One LLM row on One shock, twenty public seeds | An eval log |
| `repeats` | Yes | Five of those seeds at `--epochs 4` | An eval log |
| `recognition` | Yes | A fresh call per model and skin with the round 1 and round 20 prompts, then the cut canary, see [recognition](../../pilot/provider-checks.md#recognition) | A CSV: model, skin, reply, lint hits, canary finished |
| `up-against-down` | Yes | One LLM row on Down switch, Up switch, Up switch then down switch and Switch then shock, the `seeds` seeds | An eval log |
| `jev` | Yes | `jev/jev-latest` on No change and Down switch | An eval log |
| `timestral` | Yes | The gap test on a hand-built record, determinism twice on one input, then every `timestral/` row at every grid setting | A CSV for the gap test and determinism, and eval logs |
| `notepad` | Yes | One LLM row with `tools` at `none`, `notes`, `compute` on the `seeds` seeds | Three eval logs |
| `rolling` | Yes | One LLM row on One shock and Down switch, with `rolling` off and on | Two eval logs |
| `inertia` | No | The baselines with `inertia` at 10 and 20 on Down switch and Slow drift | A CSV |
| `cost` | No | Tokens per run read from the `seeds` and `repeats` logs | A CSV: model, mean tokens, cut off share |
| `warm-up` | Yes | One LLM row with `warm_up` unset and at `complacent:5` | Two eval logs |

- **Every CSV has one row per seed, never a tape.** The pilot runs on public seeds, so its outputs are publishable, see [contamination](../../harness/contamination.md#public-and-held-out).
- **Cells that need a model** read the row from `--models` and take the first `llm` row unless `--only` names one.
- **Nothing here changes a config.** A knob the pilot moves is passed as a task arg or a `replace` on the config in memory. The frozen defaults change only through [decisions](../../pilot/decisions.md).

## Invariants

- `load_models` on both files in `configs/models/` raises nothing.
- `generate_config` never sets `temperature`.
- `paranoid poc --dry-run` runs no eval and touches no key.
- Every engine-only cell runs with no key and no network.

## Tests

See [tests](tests.md#command).

## Open

- **The budget table and the effort names per provider are to verify** against inspect's `GenerateConfig` and each provider's API before the first run, see the "to verify" notes in [`full.toml`](../../../configs/models/full.toml).
- **Whether `tool_choice_for` needs more rows than Anthropic.** Add a provider here when a run shows it refusing a forced tool.
- **The pilot cells' exact grids** are first guesses. The pilot pages say what each measures, the function may widen a grid without a spec change, as long as the CSV columns hold.
