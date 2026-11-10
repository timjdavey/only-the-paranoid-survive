# Command

## Purpose

`paranoid` is the console script. `paranoid run` plays every row of a models config through the task, at one noise setting or over the noise grid. The proof of concept and the full study are both this command, with a different models file. `paranoid pilot <check>` runs one pilot cell, with no model where the check needs none. The models config and the reasoning mapping live here, as the command is what reads them. `paranoid analyse` belongs to the analysis layer and plugs in, see [subcommands](#subcommands) and the [analysis command](../analysis/command.md). The design is in [running](../../harness/running.md#commands) and [models](../../harness/models.md).

## Interface

```
paranoid run   [--models configs/models/poc.toml] [--skins example] [--seeds public]
               [--own-scale <value>|grid] [--limit N] [--log-dir logs/] [--only <id>] [--dry-run]
paranoid pilot <check> [--out logs/pilot/] [--models configs/models/poc.toml] [--dry-run]
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
SKIN_READERS = ("llm", "jev")          # the kinds whose model reads the skin, see run below

def load_models(path: str | Path) -> list[ModelRow]
def generate_config(row: ModelRow, reasoning: str) -> GenerateConfig
```

## Behaviour

### Subcommands

- **`main`** parses `argv` with `argparse`, dispatches, and returns 0 on success and 1 on a `ValueError`, whose message it prints. Any other exception propagates with its traceback.
- **`run` and `pilot`** are built in.
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
| `off` | `reasoning_effort="none"`, the explicit off | `reasoning_tokens=0`, the explicit off |
| `low`, `medium`, `high` | `reasoning_effort` of the same name | `reasoning_tokens` from the budget table |
| `max` | `reasoning_effort="xhigh"`. inspect maps it to the provider's highest effort where there is no `xhigh` | The `max` budget |
| `on` | Nothing set. The model thinks and will not be told otherwise | The same |
| `n/a` | Nothing set | Nothing set |

- **`off` is sent, never left to a default.** A model that thinks unless told not to would otherwise play its `off` row with thinking on, and the row would equal its `on` row. The two values in the table are what inspect is assumed to pass through as off, see [verify before code](#verify-before-code).
- **A model that cannot turn thinking off does not list `off`.** Its row in the models file lists its lowest setting, or `on` when nothing can be set, see [reasoning](../../harness/models.md#reasoning). The harness cannot tell which models those are, so the file says, and a provider that rejects the off value fails that eval as any bad setting does.
- **The budget table**: `low` 1024, `medium` 4096, `high` 16384, `max` 32768. These are a convention to verify against each provider before the first run, see [verify before code](#verify-before-code).
- **`max_tokens`** is set from the row when present, else left to the provider's default, see [sampling](../../harness/models.md#sampling).
- **Temperature is never set.**
- **`cache_prompt` is never set**, so inspect's default stands and the provider's prompt cache is on wherever there is one, see [prompt caching](../../harness/models.md#prompt-caching).

### `run`

- **`--skins` is a comma list of skin names**, `example` by default. The proof of concept passes its two held-out skins, see [running](../../harness/running.md#commands). Every name is checked against `load_skins()` before any eval runs. A name that is not loaded, or one given twice, raises `ValueError` listing the loaded names and naming `PARANOID_SKINS`, so `main` returns 1 and nothing is spent.
- **Only a row that reads the skin plays every skin.** A row whose `kind` is in `SKIN_READERS` plays each skin in the order given. Any other row plays the first skin only: Timestral and the fixed baselines read numbers and never the story, so a second skin would repeat the first to the last digit, see [two lists](../../harness/models.md#two-lists).
- **For every row, every `reasoning` value and every skin the row plays** it calls `inspect_ai.eval("paranoid", model=row.id, task_args={"skin": ..., "seeds": ...}, config=generate_config(row, r), metadata={"reasoning": r, "kind": row.kind}, log_dir=..., limit=...)`, with `max_connections=4` on LLM rows and the provider's own cap on the rest. Provider rows pass `model_args` as the provider needs, none by default. The tool choice is the solver's to pick, see [each round](solver.md#each-round).
- **Order.** Provider rows first, then LLM rows in file order. Jev and Timestral rows are what the study compares against, so they run before anything that costs tokens. Within a row and setting the skins run in the order given, so a model has both sides of its [skin sensitivity](../analysis/tables.md#the-results-page) gap before the next model starts.
- **No baseline rows are needed.** Every sample's score already holds all six baselines' outputs on its own timeline, see [scoring one run](scorer.md#scoring-one-run), so the analysis reads the Complacent baseline's bar from any log. A `baseline/` row still runs if listed, which is how the provider invariant is checked, see [tests](tests.md#providers).
- **`--own-scale`** takes one value or the word `grid`, and is passed to the task as its `own_scale` arg, see [scenarios and config](task.md#scenarios-and-config). Unset, the task plays the frozen default and no events are pinned. `grid` plays every setting in `load_grid().own_scale` in file order, one eval per setting, inside each row, reasoning value and skin. A value that is not a positive number raises `ValueError` before any eval runs.
- **The full study is this command with the full list and the grid**: `paranoid run --models configs/models/full.toml --skins <a>,<b> --seeds held-out --own-scale grid`. The analysis reads the [noise threshold](../analysis/scores.md#noise-threshold) off those logs.
- **`--only <id>`** runs one row. **`--limit`** caps samples per eval, as inspect does. **`--dry-run`** prints each eval call and runs nothing.
- **A Timestral row with the extra missing** is skipped with one line saying so, and `run` carries on. A missing key for an LLM row is left to inspect, which fails that eval, and `run` carries on to the next row and returns 1 at the end.
- **Logs** go to `--log-dir`, named by inspect, one per eval and so one per skin. Each holds the metadata in [dataset](task.md#dataset), so the analysis layer can tell them apart without the config. A log from a held-out skin never leaves the machine, see [contamination](../../harness/contamination.md#public-and-held-out).
- **The log carries its setting.** `metadata` on the eval puts `reasoning` and `kind` in `EvalLog.eval.metadata`, as neither is in a sample's metadata, and `on` sets nothing a generate config would show. The analysis reads them first and falls back to the config, see [reasoning](../analysis/runs.md#reasoning).

### Pilot cells

`paranoid pilot <check>` runs one cell. Each is a function in the `pilot/` package, one module per pilot page, named below. Measures and decisions are on the pilot pages, the function writes the data they need.

| Check | Needs a model | What it runs | Writes |
|---|---|---|---|
| `streaks` | No | Timelines over a grid of `persistence`, 1000 seeds each, the No change and Down switch scenarios | A CSV: setting, seed, longest run of rounds the leader reads below the runner-up by chance, and the round the Scout rule moves |
| `tell` | No | Timelines over a grid of `factor_scale`, One shock and Down switch, 1000 seeds | A CSV: setting, seed, hedge move at the trough, and the hedge rule's hold or move |
| `luck` | No | `perfect` minus `discerning` on every scenario at every grid setting | A CSV: scenario, setting, seed, gap |
| `timeline-sanity` | No | [BP14](../baselines/tests.md#policies) and [BP7](../baselines/tests.md#policies) at every setting in `configs/grid.toml` | A CSV: scenario, setting, baseline, pooled output |
| `noise-grid` | No | Every fixed baseline on One shock, Down switch and Up switch at every setting in `configs/grid.toml`, 1000 seeds | A CSV: scenario, setting, baseline, seed, output |
| `game-length` | No | The baselines at `rounds` of 30, 40 and 60 and `onset` ranges around the default, One shock, Down switch, Slow drift and the two-event scenarios | A CSV: scenario, rounds, onset, baseline, seed, output, move round, and the round the last event ends, see [rounds to spare](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `reading-roughness` | No | `HedgeRule(explore=1,2,5)` and `ScoutRule(s=1,2,5)` over a grid of `read_noise_k` | A CSV: setting, baseline, parameter, seed, output, move round |
| `up-and-down` | No | Discerning, Complacent, hedge rule and Scout rule at `s` 1, 2, 5 on 1000 Down switch, Up switch and No change seeds | A CSV: scenario, kind of switch, baseline, seed, output, move round |
| `bayesian-frontier` | No | Every `Bayesian(hazard, rule)` over `HAZARDS` × `BAYESIAN_RULES`, with `uniform`, `discerning`, `complacent`, `hedge_rule` and `scout_rule`, on 1000 seeds of every scenario | A CSV: scenario, baseline, hazard, rule, seed, output. Hazard and rule are blank on the five fixed baselines |
| `baseline-order` | No | Every fixed baseline on every scenario, 1000 seeds | A CSV: scenario, baseline, pooled output, and a line per order that breaks |
| `seeds` | Yes | Every LLM row on One shock and Up switch, twenty public seeds | An eval log per row |
| `repeats` | Yes | The row and scenario with the widest SD of `run_score` in the `seeds` logs, ten of its seeds picked across the range of its run scores, at `--epochs 4` | An eval log |
| `recognition` | Yes | A fresh call per model and skin with the round 1 and round 20 prompts, then the cut canary, see [recognition](../../pilot/provider-checks.md#recognition) | A CSV: model, skin, reply, lint hits, canary finished |
| `up-against-down` | Yes | One LLM row on Down switch, Up switch, Up switch then down switch and Switch then shock, the `seeds` seeds | An eval log, and a [bets CSV](#bets-csv) |
| `jev` | Yes | `jev/jev-latest` on No change and Down switch | An eval log, and a [bets CSV](#bets-csv) |
| `timestral` | Yes | The gap test on a hand-built record, determinism twice on one input, then every `timestral/` row at every grid setting | A CSV for the gap test and determinism, eval logs, and a [bets CSV](#bets-csv) |
| `bare` | Yes | Every LLM row with `tools` at `notes,compute`, `notes`, `compute` and `none` on One shock and Down switch, the `seeds` seeds | Four eval logs per row |
| `tool-choice` | Yes | Every LLM row whose `tool_choice_for` is `any`, at `tool_choice` `any` and `auto`, on One shock and Down switch, the `seeds` seeds | Two eval logs per row |
| `rolling` | Yes | Every LLM row on No change, One shock and Down switch, with `rolling` off and on | Two eval logs per row |
| `warm-up` | Yes | Every LLM row on No change and Down switch, with `warm_up` unset and at `complacent:5` | Two eval logs per row |

- **Every CSV has one row per seed, never a timeline.** The pilot runs on public seeds, so its outputs are publishable, with one exception: the `recognition` CSV holds replies about held-out skins' prompts, so it stays private whenever any skin but `example` ran, see [recognition](../../pilot/provider-checks.md#recognition) and [contamination](../../harness/contamination.md#public-and-held-out).
- **Cells that need a model** read the row from `--models` and take the first `llm` row unless `--only` names one. The `seeds`, `bare`, `tool-choice`, `rolling` and `warm-up` cells take every `llm` row, as their checks ask, and `--only` narrows them. The `repeats` cell reads the `seeds` logs in `--out` to pick its row, and fails with one line naming the `seeds` cell when there are none.
#### Bets CSV

Three checks measure how a model placed its bets, which a score cannot say and the analysis may not read from a message, see [what the analysis reads](../analysis/README.md#conventions). So the cell that ran the eval writes the counts itself.

- **`<cell>-bets.csv`**, beside the cell's logs, one row per run. The cell reads each sample's `RunStore` from the log its own eval returned, rebuilds the timeline for the event rounds, and counts.
- **Columns.** `model`, `reasoning`, `skin`, `scenario`, `seed_index`, then:

| Column | What it counts |
|---|---|
| `onset` | The first event's onset round, blank in No change |
| `sleeper_round` | The first round at or after onset with a bet above 0 on the sleeper, blank when there is no sleeper or no such round |
| `explore_points_before` | Mean points per round off the channel with the largest bet, over the rounds before onset, or over every round in No change |
| `explore_points` | The same over every round the agent played |
| `zero_rounds` | Channel rounds where a bet of 0 followed a bet above 0 on the same channel, so a channel fell out of view |
| `rounds` | The rounds the agent played, so each count can be turned into a share |

- **One row per run, never a round.** The file holds counts and one onset round, no bet, no reading and no level, so it is as publishable as the cell's other CSVs. The pilot runs on public seeds.
- **Only these three cells write one.** The headline logs and the score value do not change for the pilot's sake, see [scoring one run](scorer.md#scoring-one-run).

- **Nothing here changes a config.** A knob the pilot moves is passed as a task arg or a `replace` on the config in memory. The frozen defaults change only through [decisions](../../pilot/decisions.md).
- **No `inertia` cell.** The fixed baselines move whole budgets, so under a cap `play` raises `BetError` on the first move. The [inertia check](../../pilot/provider-checks.md#inertia) reads the gaps between models from the main pilot logs instead.
- **No `cost` cell.** [Cost per run](../../pilot/provider-checks.md#cost-per-run) reads logs and writes a table, which is analysis, so it is `paranoid analyse cost`.

## Invariants

- `load_models` on both files in `configs/models/` raises nothing.
- `generate_config` never sets `temperature` or `cache_prompt`.
- `generate_config` sets something for every setting but `on` and `n/a`, so no two settings of one row send the same config.
- `paranoid run --dry-run` runs no eval and touches no key.
- A bets CSV has one row per run and no column that holds a bet, a reading or a level.
- `run` runs no eval before every name in `--skins` is known to be loaded.
- A row whose `kind` is not in `SKIN_READERS` is played on one skin, however many are named.
- Every engine-only cell runs with no key and no network.

## Pilot decides

- **The pilot cells' exact grids** are first guesses. The pilot pages say what each measures, the function may widen a grid without a spec change, as long as the CSV columns hold.

## Verify before code

- **The off value per provider.** That `reasoning_effort="none"` and `reasoning_tokens=0` reach each provider in `configs/models/` as thinking off, and which models reject them. If a provider needs another value, `generate_config` takes it from a table keyed by `id` prefix, as the budgets are. Every `off` row in the two models files waits on it.
- **The budget table and the effort names per provider**, against inspect's `GenerateConfig` and each provider's API, see the "to verify" notes in [`full.toml`](../../../configs/models/full.toml). `EFFORT_PREFIXES` is a first guess for the same reason. `generate_config` waits on it.
- **That `eval(metadata=...)` lands in `EvalLog.eval.metadata`.** If inspect has no such argument, `run` writes the two keys into every sample's metadata through a task arg instead. `run` waits on it.
