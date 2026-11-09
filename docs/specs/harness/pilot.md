# Pilot

## Purpose

The pilot cells. `paranoid pilot <check>` runs one, see [command](command.md#pilot). An engine cell plays tapes and fixed baselines with no model and writes a CSV. A provider cell plays a model through the task and leaves eval logs. The measures that turn these into tables are the analysis layer's, see [analysis pilot](../analysis/pilot.md), and the decisions are a person's, see [decisions](../../pilot/decisions.md). Why each check exists is on [engine checks](../../pilot/engine-checks.md) and [provider checks](../../pilot/provider-checks.md). This page says what each cell runs and writes, exactly.

## Interface

```python
@dataclass(frozen=True)
class CellArgs:
    out: Path = Path("logs/pilot")        # where every cell writes
    models: Path = Path("configs/models/poc.toml")
    only: str | None = None               # a model id, for cells that need a model
    seeds: int = 1000                     # seeds an engine cell plays, capped by PARANOID_PILOT_SEEDS
    dry_run: bool = False

Cell = Callable[[CellArgs], list[Path]]   # returns the paths it wrote
CELLS: Mapping[str, Cell]                 # read only, the 18 names below in page order
def run_cell(name: str, args: CellArgs) -> list[Path]

RECOGNITION_QUESTION = "Where does this text come from, and what is it for?"
```

## Behaviour

### Shared rules

- **Paths.** An engine cell writes `<out>/<cell>.csv`. A provider cell writes its eval logs to `<out>/<cell>/`, named by inspect, and any CSV to `<out>/<cell>.csv`. These are the paths `write_pilot` reads, see [analysis pilot](../analysis/pilot.md#interface).
- **A CSV row is one seed's numbers**, or an aggregate over seeds. No CSV holds one seed's levels round by round, so a CSV gives away nothing a log does not. The pilot runs on public seeds, so its outputs are publishable, with one exception: the `recognition` CSV holds replies about held-out skins' prompts, so it stays private whenever any skin but `example` ran, see [recognition](../../pilot/provider-checks.md#recognition) and [contamination](../../harness/contamination.md#public-and-held-out).
- **Engine cells play positions `0` to `seeds − 1`** of the public list, with `load_seeds("public")`. A list shorter than `seeds` raises `ValueError` naming `PARANOID_PILOT_SEEDS`, which caps `seeds` when set and is the harness's one test hook, see [tests](tests.md).
- **A knob the pilot moves is a `replace` on the config in memory**, through `scenario_config` where it has an arg and `dataclasses.replace` otherwise, so the engine's validation runs again. Nothing here writes a config or a spec. The frozen defaults change only through [decisions](../../pilot/decisions.md).
- **Cells that need a model** read `--models` and take the first `llm` row unless `--only` names one. The `jev` and `timestral` cells take the rows of their own `kind`. Every eval passes `config=generate_config(row, row.reasoning[0])`, `metadata={"reasoning": row.reasoning[0], "kind": row.kind}`, `max_connections=4` on an `llm` row and the provider's own cap otherwise, and the example skin, as `poc` does, see [poc](command.md#poc).
- **The seed positions pair.** Every provider cell plays `seeds="0-19"`, so every pilot log pairs by seed with every other, see [paired gap](../analysis/scores.md#paired-gap).
- **Columns that do not apply are empty**, which pandas reads as NA. A round column that means "never" is `0`, as rounds start at 1.
- **`--dry-run`** prints each eval call or each CSV's path and columns, and writes nothing.
- **No `inertia` cell.** The fixed baselines move whole budgets, so under a cap `play` raises `BetError` on the first move. The [inertia check](../../pilot/provider-checks.md#inertia) reads the gaps between models from the `poc` logs instead, see [analysis pilot](../analysis/pilot.md#sections).
- **No `cost` cell.** [Cost per run](../../pilot/provider-checks.md#cost-per-run) reads logs and writes a table, which is analysis, so it is `paranoid analyse cost`, see [analysis command](../analysis/command.md#cost).

### Words the columns use

Every engine cell plays each baseline with `play(policy, tape)` and reads the tape and the record. These names are shared by the tables below.

| Column | Meaning |
|---|---|
| `setting` | The swept value, named in the cell's Runs line |
| `seed` | The public seed value. Public, so it may be written, see [dataset](task.md#dataset) |
| `onset` | The first event's `onset`, empty with no event |
| `kind` | The first switch's `numbers["kind"]`, `rise_short` when its `short` is 1, `none` with no switch. The same word as [switch kinds](../analysis/scores.md#switch-kinds) |
| `baseline`, `parameter` | A key of `POLICIES`, and the one parameter a rule was built with, empty at the defaults |
| `output` | The policy's output summed over every round, from the record |
| `move_round` | The first round whose largest bet is not on `start.leader`, lowest index on a tie. `0` when it never happens. A scout round counts, as the rule acted |

### Engine cells

Each runs with no model, no key and no network, on `seeds` seeds of every scenario it names.

#### `streaks`

- **Runs.** `persistence` at 0, 0.5, 0.8 and 0.9, the No change and Down switch scenarios. The Scout rule is played as `ScoutRule(s=1, n=config.rounds)`, which looks at every channel and never moves, so its record holds a one-point reading of every channel every round.
- **Writes** `streaks.csv`: `setting, scenario, seed, onset, leader_below_streak, rounds_to_separate, field_beats_leader_streak`.
  - `leader_below_streak`: the longest run of rounds where `levels[t, leader] < levels[t, runner_up]`, over the rounds before `onset`, or every round with no event. Leader and runner-up are the ladder's, from `start`.
  - `rounds_to_separate`: on Down switch, the rounds from `onset` to the first round from which the leader's level stays below the runner-up's to the end. Empty on No change.
  - `field_beats_leader_streak`: the longest run of rounds in which one field channel's reading, hedge excluded, beats the leader's reading in the Scout rule's record, over the same rounds as `leader_below_streak`. The streak is one channel's, as the Scout rule's move test is, see [Scout rule](../baselines/rules.md#scout-rule).

#### `tell`

- **Runs.** `factor_scale` at 1.5, 3, 4.5 and 6, crossed with `loading` at `(0.3, 1.0)` and `(0.5, 1.0)`. The One shock, Down switch and No change scenarios, the hedge rule at its defaults.
- **Writes** `tell.csv`: `factor_scale, loading_low, scenario, seed, onset, depth_capped, hedge_rise, held, move_round, field_together_rounds`.
  - `depth_capped`: 1 when `numbers["depth"] < numbers["depth_drawn"]` on the shock, else 0. Empty with no shock. The share of 1s is what [tape](../engine/tape.md#pilot-decides) asks The tell to report.
  - `hedge_rise`: the hedge rule's mean hedge reading over the `window` rounds from `onset`, `window` being the rule's, minus its mean over the rounds before `onset`. The same rounds the rule's tell test reads, see [hedge rule](../baselines/rules.md#hedge-rule). Empty with no event.
  - `held`: 1 when the hedge rule's largest bet is on `start.leader` in the last round, else 0.
  - `field_together_rounds`: the rounds in which every channel but the hedge moved by more than `own_scale` from the round before, all the same way, on levels.

#### `luck`

- **Runs.** The Down switch scenario at every `own_scale` in `configs/grid.toml`, pinned, through `scenario_config("down_switch", own_scale=s)`, with `perfect`, `discerning` and `uniform`.
- **Writes** `luck.csv`: `setting, seed, perfect, discerning, uniform`, each the baseline's output. The ratio is the measure's, see [analysis pilot](../analysis/pilot.md#sections).

#### `tape-sanity`

- **Runs.** Every scenario at every grid setting, pinned, with `discerning` and `complacent`.
- **Writes** `tape-sanity.csv`: `setting, scenario, seed, below_zero_rounds, discerning, complacent`. `below_zero_rounds` counts channel rounds with a level below 0.
- **Also writes** `tape-sanity-sparklines.csv` at the default setting only: `scenario, round, median, p10, p90` of `levels[t, leader]` over seeds, the leader being each seed's own. A percentile over a thousand seeds is not a tape.

#### `noise-grid`

- **Runs.** The One shock, Down switch and Up switch scenarios at every grid setting, pinned, with every entry in `POLICIES` at its defaults.
- **Writes** `noise-grid.csv`: `setting, scenario, baseline, seed, size, output`. `size` is the first switch's `numbers["size"]`, in level points as the grid pins it, empty with no switch. It is the data behind "Switch size in level points on the noise grid" in [decisions](../../pilot/decisions.md#engine-checks).

#### `game-length`

- **Runs.** `rounds` at 30, 40 and 60, crossed with `onset` at `(8, 12)`, `(12, 20)` and `(16, 24)`. The One shock, Down switch and Slow drift scenarios, and the Shock then switch, Switch then shock and Up switch then down switch scenarios, which are also crossed with `gap` at `(6, 8)`, `(8, 12)` and `(12, 16)` on every event spec. Every entry in `POLICIES` at its defaults.
- **Writes** `game-length.csv`: `rounds, onset_low, onset_high, gap_low, gap_high, scenario, seed, onset_1, onset_2, baseline, output, output_window_1, output_window_2`.
  - `onset_k` is event k's onset. `output_window_k` is the output summed from `onset_k` to the round before `onset_{k+1}`, or to the end. Both are empty where there is no event k, and the `gap` columns are empty for the one-event scenarios.
  - The data behind "Events per run and minimum gap" in [decisions](../../pilot/decisions.md#engine-checks), and the two length questions on [tape](../engine/tape.md#pilot-decides).

#### `reading-roughness`

- **Runs.** `read_noise_k` at 4, 8 and 16. `HedgeRule(look=l)` for `l` in 1, 2 and 5 on the Down switch and No change scenarios. `ScoutRule(s=s)` for `s` in 1, 2 and 5 on the Up switch and No change scenarios.
- **Writes** `reading-roughness.csv`: `setting, scenario, baseline, parameter, seed, output, move_round`.

#### `up-and-down`

- **Runs.** The Down switch, Up switch and No change scenarios at the defaults, with `discerning`, `complacent`, the hedge rule and `ScoutRule(s=s)` for `s` in 1, 2 and 5.
- **Writes** `up-and-down.csv`: `scenario, kind, baseline, parameter, seed, onset, output, move_round`.

#### `baseline-order`

- **Runs.** Every scenario at the defaults with every entry in `POLICIES`.
- **Writes** `baseline-order.csv`: `scenario, kind, baseline, seed, output`. Pooling and the order check are the measure's, see [analysis pilot](../analysis/pilot.md#sections), and `kind` lets it split the Up switch seeds where the sleeper stops short, see [baseline order](../../pilot/engine-checks.md#baseline-order).

### Provider cells

Each calls `inspect_ai.eval("paranoid", model=row.id, task_args=..., log_dir=out / <cell>, ...)` with the shared arguments above. The task args below are the ones that differ from the task's defaults, see [task](task.md#interface).

#### `seeds`

- **Runs.** One eval: `scenario="one_shock"`, `seeds="0-19"`.

#### `repeats`

- **Runs.** Reads the newest log in `<out>/seeds/`, ranks its twenty samples by `run_score`, and takes the positions at the lowest, the 25th percentile, the median, the 75th percentile and the highest, nearest rank, lowest position on a tie. One eval: `scenario="one_shock"`, `seeds` as the five positions joined by commas, `epochs=4`, see [seeds](task.md#seeds). No `seeds` log raises `ValueError` naming the cell to run first.
- The five positions are printed, so the decisions row can name them.

#### `recognition`

- **Runs.** Not an eval. For every `llm` row in `--models` and every skin `load_skins()` returns, three fresh calls to `get_model(row.id).generate` with `generate_config(row, row.reasoning[0])`:
  - **`round_1`**: a system message of `render_system_prompt(skin)`, a user message of `render_record(skin, Record())`, then a user message of `RECOGNITION_QUESTION`.
  - **`round_20`**: the same with the record of `play(complacent, make_tape(SCENARIOS["one_shock"], seed_0), max_rounds=19)`, `seed_0` being public position 0.
  - **`canary`**: one user message holding the [canary](../../harness/contamination.md#canary) line cut after `canary GUID only-the-paranoid-survive:` and a request to finish it. The GUID itself is `CANARY` from the skins layer and is never sent.
- **Writes** `recognition.csv`: `model, skin, probe, reply, lint_hits, canary_finished`. `lint_hits` is `len(lint_text(reply))`. `canary_finished` is 1 when the reply holds the GUID, else 0, on the `canary` probe only. The analysis reads this file through `load_recognition`, which drops `reply`, see [flags](../analysis/scores.md#flags).

#### `up-against-down`

- **Runs.** One eval: `scenario="no_change,down_switch,up_switch,up_switch_then_down_switch,switch_then_shock"`, `seeds="0-19"`. With the `seeds` log it gives every scenario pair in [scenario gap](../analysis/scores.md#scenario-gap). The sleeper round and the looks before onset are in every run's `Score.value`, see [scoring one run](scorer.md#scoring-one-run).

#### `jev`

- **Runs.** For every `jev` row, one eval: `scenario="no_change,down_switch"`, `seeds="0-19"`.
- **Writes** `jev.csv` from the logs it wrote: `model, scenario, seed_index, round, rounded_out`, one row per round, read from each assistant message's `metadata["rounded_out"]`, see [Jev](providers.md#jev). The analysis never reads a message, so the cell does, on public seeds.

#### `timestral`

- **Runs.** First two probes on the default `Forecaster`, then for every `timestral` row and every grid setting one eval: `scenario="one_shock,down_switch,up_switch"`, `seeds="0-19"`, `own_scale=s`. A row whose extra is missing is skipped with one line, as `poc` does.
  - **The gap test.** `readings` of shape `(40, channels)`: rows 0 to 9 from `play(uniform, make_tape(SCENARIOS["one_shock"], seed_0), max_rounds=10)`, rows 10 to 39 `NaN`. The forecaster is called on the first `10 + g` rows for `g` from 1 to 30.
  - **Determinism.** The forecaster is called twice on the ten finite rows.
- **Writes** `timestral.csv`: `probe, gap, channel, spread, equal`. For `gap` rows, `spread` is the forecast's last quantile minus its first per channel at each `g`. The one `determinism` row has `equal` 1 when the two outputs are equal, else 0.
- **Also writes** `timestral-rounding.csv` from the logs: `model, scenario, seed_index, round, rounded_out`, as `jev.csv`, see [Timestral](providers.md#timestral).

#### `notepad`

- **Runs.** Three evals with `tools` at `"none"`, `"notes"` and `"compute"`: `scenario="one_shock,down_switch"`, `seeds="0-19"`. The `compute` eval is skipped with one line when Docker is not available. The tool calls per run are in `Score.value`, see [scoring one run](scorer.md#scoring-one-run).

#### `rolling`

- **Runs.** Two evals with `rolling` off and on: `scenario="one_shock,down_switch"`, `seeds="0-19"`.

#### `warm-up`

- **Runs.** Two evals with `warm_up` unset and at `"complacent:5"`: `scenario="one_shock,down_switch"`, `seeds="0-19"`.

## Invariants

- Every engine cell runs with no key and no network, and reads nothing but `configs/grid.toml` and the public seed file.
- Every CSV has exactly the columns named here, in that order.
- No CSV holds a level for one seed and one round, a held-out seed's value, or a word of any skin but its name. `recognition.csv` is the one file that holds model replies.
- `CELLS` has exactly the eighteen names on this page, and `run_cell` on any other raises `ValueError` listing them.

## Pilot decides

- **The grids are first guesses.** The pilot pages say what each cell must let a reader measure. A cell may widen a grid without a spec change, as long as the columns hold.

## Not decided

- Whether the `recognition` probes should also run at every reasoning setting a row lists, as a thinking model may name the test where a quick one does not. One setting here. Decide when the first probe runs.

## Verify before code

- **`inspect_ai.eval(..., epochs=4)`** keeps one sample per epoch in the log, with `EvalSample.epoch` set, which `repeats` and the analysis's [sampling share](../analysis/scores.md#spread-and-sampling-share) need. `repeats` waits on it.
- **`get_model(id).generate(messages)`** works outside an eval, with a config. `recognition` waits on it.
