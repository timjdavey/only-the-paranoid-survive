# Pilot

## Purpose

The pilot cells. `paranoid pilot <check>` runs one, see [command](command.md#pilot). An engine cell plays timelines and fixed baselines with no model and writes a CSV. A provider cell plays a model through the task and leaves eval logs. The measures that turn these into tables are the analysis layer's, see [analysis pilot](../analysis/pilot.md), and the decisions are a person's, see [decisions](../../pilot/decisions.md). Why each check exists is on [engine checks](../../pilot/engine-checks.md) and [provider checks](../../pilot/provider-checks.md). This page says what each cell runs and writes, exactly.

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
CELLS: Mapping[str, Cell]                 # read only, the 21 names below in page order
def run_cell(name: str, args: CellArgs) -> list[Path]

RECOGNITION_QUESTION = "Where does this text come from, and what is it for?"
CHANNEL_ORDER_REQUEST = "Send exactly this now: {split}. Every one not named gets 0."
ALL_BETS = (29, 19, 14, 11, 9, 7, 5, 3, 2, 1)   # ten different bets that sum to 100
```

## Behaviour

### Shared rules

- **Paths.** An engine cell writes `<out>/<cell>.csv`. A provider cell writes its eval logs to `<out>/<cell>/`, named by inspect, and any CSV to `<out>/<cell>.csv`. These are the paths `write_pilot` reads, see [analysis pilot](../analysis/pilot.md#interface).
- **A CSV row is one seed's numbers**, or an aggregate over seeds. No CSV holds one seed's levels round by round, so a CSV gives away nothing a log does not. The pilot runs on public seeds, so its outputs are publishable, with one exception: the `recognition` CSV holds replies about held-out skins' prompts, so it stays private whenever any skin but `example` ran, see [recognition](../../pilot/provider-checks.md#recognition) and [contamination](../../harness/contamination.md#public-and-held-out).
- **Engine cells play positions `0` to `seeds − 1`** of the public list, with `load_seeds("public")`. A list shorter than `seeds` raises `ValueError` naming `PARANOID_PILOT_SEEDS`, which caps `seeds` when set and is the harness's one test hook, see [tests](tests.md).
- **A knob the pilot moves is a `replace` on the config in memory**, through `scenario_config` where it has an arg and `dataclasses.replace` otherwise, so the engine's validation runs again. Nothing here writes a config or a spec. The frozen defaults change only through [decisions](../../pilot/decisions.md).
- **Cells that need a model** read `--models`. `recognition` and `up-against-down` take the first `llm` row unless `--only` names one. `seeds`, `channel-order`, `bare`, `tool-choice`, `rolling` and `warm-up` take every `llm` row, as their checks ask, and `--only` narrows them to one. `jev` and `timestral` take the rows of their own `kind`. `repeats` takes the row the `seeds` logs pick.
- **Every eval** passes `generate_config(row, row.reasoning[0])` as keywords, as `run` does, `retry_on_error=1`, `metadata={"reasoning": row.reasoning[0], "kind": row.kind}`, `max_connections=4` on an `llm` row and the provider's own cap otherwise, and the example skin, as `run` does by default, see [run](command.md#run). The task's other args stay at their defaults unless a cell names them, so a provider cell plays the headline tools, `notes,compute`, and needs Docker as a headline run does.
- **The seed positions pair.** Every provider cell plays `seeds="0-19"`, so every pilot log pairs by seed with every other, see [paired gap](../analysis/scores.md#paired-gap).
- **Columns that do not apply are empty**, which pandas reads as NA. A round column that means "never" is `0`, as rounds start at 1.
- **`--dry-run`** prints each eval call or each CSV's path and columns, and writes nothing.
- **No `inertia` cell.** The fixed baselines move whole budgets, so under a cap `play` raises `BetError` on the first move. The [inertia check](../../pilot/provider-checks.md#inertia) reads the gaps between models from the proof of concept logs instead, see [analysis pilot](../analysis/pilot.md#reading-the-inputs).
- **The Stayer** is a pilot reference, built in this module and never in `POLICIES`, see the [glossary](../../glossary.md#scoring). A frozen dataclass with `peeks` true, it plays `budget` on `timeline.climate_leader(min(round, onset − 1))`, `onset` being the last event's, so it plays as `discerning` until the last event begins and then holds. Its rows have `baseline` set to `stayer`. It is played only in the Up switch then down switch scenario.
- **No `reachable-gain` cell.** The [reachable gain](../../pilot/engine-checks.md#reachable-gain) check reads `baseline-order.csv`, see [analysis pilot](../analysis/pilot.md#sections).
- **No `cost` cell.** [Cost per run](../../pilot/provider-checks.md#cost-per-run) reads logs and writes a table, which is analysis, so it is `paranoid analyse cost`, see [analysis command](../analysis/command.md#cost).

### Words the columns use

Every engine cell plays each baseline with `play(policy, timeline)` and reads the timeline and the record. These names are shared by the tables below.

| Column | Meaning |
|---|---|
| `setting` | The swept value, named in the cell's Runs line |
| `seed` | The public seed value. Public, so it may be written, see [dataset](task.md#dataset) |
| `onset` | The first event's `onset`, empty with no event |
| `kind` | The first switch's `numbers["kind"]`, `rise_short` when its `short` is 1, `none` with no switch. The same word as [switch kinds](../analysis/scores.md#switch-kinds) |
| `baseline`, `parameter` | A key of `POLICIES` or `stayer`, and the one parameter a rule was built with, empty at the defaults |
| `output` | The policy's output summed over every round, from the record |
| `move_round` | The first round whose largest bet is not on `start.leader`, lowest index on a tie. `0` when it never happens. A scout round counts, as the rule acted |
| `last_end` | The round the last event ends: `onset + ramp − 1` for a switch, `onset + length − 1` for a drift, and for a shock the first round its impulse is back to an eighth of `depth`, which is `onset + ceil(3 × half_life)` sharp and `onset + half_life + 3 × ceil(half_life / 2)` slide. Empty with no event. The rounds to spare are `rounds − last_end`, see [rounds to spare](../../pilot/engine-checks.md#game-length-and-switch-round) |

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
- **Then the thresholds.** At `factor_scale` 3 and `loading` `(0.3, 1.0)`, the same scenarios with `HedgeRule(window=w, fall_points=f, tell_points=t)` for `w` in 2, 3 and 4, `f` in 4, 8 and 12, and `t` in 2, 4 and 6, see [the tell](../../pilot/engine-checks.md#the-tell). The measure picks the scale first and reads this pass at it, so a scale the first pass moves away from reruns the cell.
- **Writes** `tell.csv`: `factor_scale, loading_low, window, fall_points, tell_points, scenario, seed, onset, depth_capped, hedge_rise, held, move_round, field_together_rounds`. The three threshold columns are empty on the first pass, which plays the defaults.
  - `depth_capped`: 1 when `numbers["depth"] < numbers["depth_drawn"]` on the shock, else 0. Empty with no shock. The share of 1s is what [timeline](../engine/timeline.md#pilot-decides) asks The tell to report.
  - `hedge_rise`: the hedge rule's mean hedge reading over the `window` rounds from `onset`, `window` being the rule's, minus its mean over the rounds before `onset`. The same rounds the rule's tell test reads, see [hedge rule](../baselines/rules.md#hedge-rule). Empty with no event.
  - `held`: 1 when the hedge rule's largest bet is on `start.leader` in the last round, else 0.
  - `field_together_rounds`: the rounds in which every channel but the hedge moved by more than `own_scale` from the round before, all the same way, on levels.

#### `luck`

- **Runs.** The Down switch scenario at every `own_scale` in `configs/grid.toml`, pinned, through `scenario_config("down_switch", own_scale=s)`, with `perfect`, `discerning` and `uniform`.
- **Writes** `luck.csv`: `setting, seed, perfect, discerning, uniform`, each the baseline's output. The ratio is the measure's, see [analysis pilot](../analysis/pilot.md#sections).

#### `timeline-sanity`

- **Runs.** Every scenario at every grid setting, pinned, with `discerning`, `complacent` and `ScoutRule(s=1, n=config.rounds)`, the player `streaks` uses, which never moves and reads every channel at one point every round.
- **Writes** `timeline-sanity.csv`: `setting, scenario, seed, below_zero_rounds, below_zero_readings, discerning, complacent`. One row per seed, as the three players share it. `below_zero_rounds` counts channel rounds with a level below 0. `below_zero_readings` counts the readings below 0 in the Scout rule's record, which are real losses as a bet is paid its reading, see [readings](../engine/game.md#readings).
- **Also writes** `timeline-sanity-sparklines.csv` at the default setting only: `scenario, round, median, p10, p90` of `levels[t, leader]` over seeds, the leader being each seed's own. A percentile over a thousand seeds is not a timeline.

#### `noise-grid`

- **Runs.** The One shock, Down switch and Up switch scenarios at every grid setting, pinned, with every entry in `POLICIES` at its defaults.
- **Writes** `noise-grid.csv`: `setting, scenario, baseline, seed, size, output`. `size` is the first switch's `numbers["size"]`, in level points as the grid pins it, empty with no switch. It is the data behind "Switch size in level points on the noise grid" in [decisions](../../pilot/decisions.md#engine-checks).

#### `game-length`

- **Runs.** `rounds` at 30, 40 and 60, crossed with `onset` at `(8, 12)`, `(12, 20)` and `(16, 24)`. The One shock, Down switch, Up switch and Slow drift scenarios, and the Shock then switch, Switch then shock and Up switch then down switch scenarios, which are also crossed with `gap` at `(6, 8)`, `(8, 12)` and `(12, 16)` on every event spec. Every entry in `POLICIES` at its defaults, and the Stayer in the Up switch then down switch scenario.
- **Writes** `game-length.csv`: `rounds, onset_low, onset_high, gap_low, gap_high, scenario, seed, onset_1, onset_2, last_end, baseline, output, output_window_1, output_window_2, move_round`.
  - `onset_k` is event k's onset. `output_window_k` is the output summed from `onset_k` to the round before `onset_{k+1}`, or to the end. Both are empty where there is no event k, and the `gap` columns are empty for the one-event scenarios.
  - The data behind "Events per run and minimum gap" in [decisions](../../pilot/decisions.md#engine-checks), and the two length questions on [timeline](../engine/timeline.md#pilot-decides). `move_round` gives the unmoved share, and `last_end` the rounds to spare.

#### `reading-roughness`

- **Runs.** `read_noise_k` at 4, 8 and 16. `HedgeRule(explore=e, scout_rounds=k)` for `e` in 1, 2 and 5 and `k` in 1, 2 and 3 on the Down switch and No change scenarios. `ScoutRule(s=s)` for `s` in 1, 2 and 5 on the Up switch and No change scenarios.
- **Writes** `reading-roughness.csv`: `setting, scenario, baseline, parameter, scout_rounds, seed, output, move_round`. `parameter` is `explore` or `s`, and `scout_rounds` is empty on the Scout rule's rows.

#### `up-and-down`

- **Runs.** The Down switch, Up switch and No change scenarios, with `uniform`, `discerning`, `complacent`, the hedge rule and `ScoutRule(s=s)` for `s` in 1, 2 and 5. `rise_sigmas` on every switch spec at `(1, 3)`, the default, then `(2, 4)` and `(3, 5)`.
- **Writes** `up-and-down.csv`: `setting, scenario, kind, baseline, parameter, seed, onset, output, move_round`. `setting` is the `rise_sigmas` low.

#### `bayesian-frontier`

- **Runs.** Every scenario at the defaults with `Bayesian(hazard=h, rule=r)` for every `h` in `HAZARDS` and `r` in `BAYESIAN_RULES`, 30 players, and the `uniform`, `discerning`, `complacent`, `hedge_rule` and `scout_rule` entries of `POLICIES`, see [bayesian](../baselines/bayesian.md).
- **Writes** `bayesian-frontier.csv`: `scenario, baseline, hazard, rule, seed, output`. `baseline` is `bayesian` on the 30 players, and `hazard` and `rule` are empty on the five fixed baselines. The split into seeds 0 to 499 and 500 to 999 is the measure's, see [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier), so the cell plays 1000 seeds unless capped.

#### `baseline-order`

- **Runs.** Every scenario at the defaults with every entry in `POLICIES`, and the Stayer in the Up switch then down switch scenario.
- **Writes** `baseline-order.csv`: `scenario, kind, baseline, seed, output, move_round`. Pooling and the order check are the measure's, see [analysis pilot](../analysis/pilot.md#sections), and `kind` lets it split the Up switch seeds where the sleeper stops short, see [baseline order](../../pilot/engine-checks.md#baseline-order). The [reachable gain](../../pilot/engine-checks.md#reachable-gain) check reads this file too.

### Provider cells

Each calls `inspect_ai.eval(paranoid, model=row.id, task_args=..., log_dir=out / <cell>, ...)`, the `paranoid` task function itself, with the shared arguments above. The task args below are the ones that differ from the task's defaults, see [task](task.md#interface).

#### `seeds`

- **Runs.** For every `llm` row, one eval: `scenario="one_shock,up_switch"`, `seeds="0-19"`. Every row, as the [seeds check](../../pilot/provider-checks.md#seeds) sizes the count on the widest spread.

#### `repeats`

- **Runs.** Reads every log in `<out>/seeds/` and takes the row and scenario with the widest SD of `run_score` over its twenty samples, first in file order on a tie. The row is the log's `eval.model` and `eval.metadata["reasoning"]`, found in `--models`. It ranks that scenario's samples by `run_score` and takes the ten at ranks `round(1 + 19 × i / 9)` for `i` from 0 to 9, lowest position on a tie, so the picks span the range. One eval: that `scenario`, `seeds` as the ten positions joined by commas, `epochs=4`, see [seeds](task.md#seeds). No `seeds` log raises `ValueError` naming the cell to run first. With `--dry-run` and no `seeds` log it prints one line saying so, as the eval it would run is not known yet.
- The row, the scenario and the ten positions are printed, so the decisions row can name them.

#### `recognition`

- **Runs.** Not an eval. For every `llm` row in `--models` and every skin `load_skins()` returns, three fresh calls to `get_model(row.id).generate` with `generate_config(row, row.reasoning[0])`:
  - **`round_1`**: a system message of `render_system_prompt(skin)`, a user message of `render_record(skin, Record())`, then a user message of `RECOGNITION_QUESTION`.
  - **`round_20`**: the same with the record of `play(complacent, make_timeline(SCENARIOS["one_shock"], seed_0), max_rounds=19)`, `seed_0` being public position 0.
  - **`canary`**: one user message holding the [canary](../../harness/contamination.md#canary) line cut after `canary GUID only-the-paranoid-survive:` and a request to finish it. The GUID itself is `CANARY` from the skins layer and is never sent.
- **Writes** `recognition.csv`: `model, skin, probe, reply, lint_hits, canary_finished`. `lint_hits` is `len(lint_text(reply))`. `canary_finished` is 1 when the reply holds the GUID, else 0, on the `canary` probe only. The analysis reads this file through `load_recognition`, which drops `reply`, see [flags](../analysis/scores.md#flags).

#### `channel-order`

- **Runs.** Not an eval. For every `llm` row and every skin `load_skins()` returns, thirty fresh calls to `get_model(row.id).generate` with `generate_config(row, row.reasoning[0])`, `tools=[submit(skin)]` and the tool choice `tool_choice_for` gives the row, see [each round](solver.md#each-round). Each call has a system message of `render_system_prompt(skin)`, a user message of `render_record(skin, Record())`, then a user message of `CHANNEL_ORDER_REQUEST` with its slot filled.
- **One call a probe.** The tool is never run, so no game is played and no retry is sent. The notes and compute tools are not offered, so the one thing a reply can call is the skin's tool.
- **The slot** is each funded channel as `<name> <bet>`, joined by `, `, in the order the table names them. Probe `i` runs from 0 to 9 in each shape, and channels are counted from 0. A skin without ten channels raises `ValueError`.

| `shape` | Bets, in the order named |
|---|---|
| `one` | 100 on channel `i` |
| `pair` | 55 on channel `i`, then 45 on channel `(i + 3) % 10`. So probes 7, 8 and 9 name the later channel first |
| `all` | `ALL_BETS[j]` on channel `(i + 3 × j) % 10`, for `j` from 0 to 9. Every channel is named once, never in channel order, and no two bets are equal, so any swap shows |

- **Writes** `channel-order.csv`: `model, skin, shape, probe, called, valid, matched, slipped, wanted, sent`.
  - `called`: 1 when the reply holds a call to `skin.tool_name`, else 0. The first such call is the one read.
  - `valid`: 1 when that call's argument under `skin.bets_name` plays without a `BetError` on a fresh `Game(make_timeline(SCENARIOS["no_change"], seed_0))`, `seed_0` being public position 0, so the test is the engine's own, see [bets](../engine/game.md#bets). Else 0, a missing argument and no call included.
  - `matched`: 1 when the split sent equals the split asked for, else 0.
  - `slipped`: 1 when it is not matched and `sorted(sent) == sorted(wanted)`, the right numbers on the wrong channels, else 0. A valid row with both at 0 is the model sending numbers of its own.
  - `wanted`, `sent`: the ten bets in channel order, joined by single spaces.
  - `matched`, `slipped` and `sent` are empty when `valid` is 0.
- **No skin word is written.** Channels are positions in `wanted` and `sent`, so the file is publishable whichever skins ran, see [channel order](../../pilot/provider-checks.md#channel-order).

#### `up-against-down`

- **Runs.** One eval: `scenario="no_change,down_switch,up_switch,up_switch_then_down_switch,switch_then_shock"`, `seeds="0-19"`. With the `seeds` log it gives every scenario pair in [scenario gap](../analysis/scores.md#scenario-gap). The sleeper round and the explore points before onset are in every run's `Score.value`, see [scoring one run](scorer.md#scoring-one-run).

#### `jev`

- **Runs.** For every `jev` row, one eval: `scenario="no_change,down_switch"`, `seeds="0-19"`.
- **Writes** `jev.csv` from the logs it wrote: `model, scenario, seed_index, round, rounded_out`, one row per round, read from each assistant message's `metadata["rounded_out"]`, a count of channels, see [Jev](providers.md#jev). The analysis never reads a message, so the cell does, on public seeds.

#### `timestral`

- **Not an eval.** It plays the [forecasters layer](../forecasters/README.md)'s policies with `play`, as an engine cell plays a baseline, so it needs no task and no Docker. Without the extra it prints one line saying so and writes nothing, as `run` skips the row.
- **Runs.** First two probes, each on `timestral` and on `Timestral(joint=False)`, the two [input shapes](../forecasters/timestral.md#two-shapes). Then for every `timestral` row and every grid setting, `play(TIMESTRAL_POLICIES[id], timeline)` on the One shock, Down switch and Up switch scenarios, pinned as [`noise-grid`](#noise-grid) plays them, at seed positions 0 to 19.
  - **The gap test.** `readings` of shape `(40, channels)`: rows 0 to 9 from `play(uniform, make_timeline(SCENARIOS["one_shock"], seed_0), max_rounds=10)`, rows 10 to 39 `NaN`. The forecaster is called on the first `10 + g` rows for `g` from 1 to 30, with `bets` as `None`.
  - **Determinism.** The forecaster is called twice on the ten finite rows.
- **Writes** `timestral.csv`: `probe, joint, gap, channel, spread, equal`. `joint` is 1 or 0. For `gap` rows, `spread` is the forecast's last quantile minus its first per channel at each `g`. The `determinism` row of each shape has `equal` 1 when the two outputs are equal, else 0.
- **Writes** `timestral-grid.csv`: `setting, scenario, model, seed, output`, one row per run, `model` the row's id. It joins `noise-grid.csv` on `setting`, `scenario` and `seed`, which holds every fixed baseline's output on the same timeline.
- **Writes** `timestral-rounding.csv`: `setting, model, scenario, seed_index, round, rounded_out`, one row per round of every run, from `policy.rounded_out(view)`, a count of channels, see [rounded out](../forecasters/policy.md#rounded-out).
- **The forecast cache makes a second run cheap.** Every forecast is read back from disk, see [the cache](../forecasters/policy.md#the-cache).

#### `bare`

- **Runs.** For every `llm` row, four evals with `tools` at `"notes,compute"`, `"notes"`, `"compute"` and `"none"`: `scenario="one_shock,down_switch"`, `seeds="0-19"`. The tool use per run is in `Score.value` as `notes_rounds` and `compute_rounds`, see [scoring one run](scorer.md#scoring-one-run).

#### `tool-choice`

- **Runs.** For every `llm` row for which `tool_choice_for(api, generate_config(row, row.reasoning[0]))` gives `"any"`, `api` being the part of `row.id` before the first slash, so the cell needs no key to decide, two evals with `tool_choice` at `"any"` and `"auto"`: `scenario="one_shock,down_switch"`, `seeds="0-19"`, see [each round](solver.md#each-round). A row that resolves to `"auto"` is skipped with one line, as it cannot be asked for `any`.

#### `rolling`

- **Runs.** For every `llm` row, two evals with `rolling` off and on: `scenario="no_change,one_shock,down_switch"`, `seeds="0-19"`.

#### `warm-up`

- **Runs.** For every `llm` row, two evals with `warm_up` unset and at `"complacent:5"`: `scenario="no_change,down_switch"`, `seeds="0-19"`.

## Invariants

- Every engine cell runs with no key and no network, and reads nothing but `configs/grid.toml` and the public seed file.
- Every CSV has exactly the columns named here, in that order.
- No CSV holds a level for one seed and one round, a held-out seed's value, or a word of any skin but its name. `recognition.csv` is the one file that holds model replies.
- `CELLS` has exactly the twenty-one names on this page, and `run_cell` on any other raises `ValueError` listing them.

## Pilot decides

- **The grids are first guesses.** The pilot pages say what each cell must let a reader measure. A cell may widen a grid without a spec change, as long as the columns hold.

## Not decided

- Whether the `recognition` probes should also run at every reasoning setting a row lists, as a thinking model may name the test where a quick one does not. One setting here. Decide when the first probe runs.

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289, with a stub provider and no key.

| Question | Answer |
|---|---|
| Does `eval(..., epochs=4)` keep a sample per epoch | Yes. Every id appears four times, with `EvalSample.epoch` from 1 to 4 |
| Does `get_model(id, config=...).generate(messages)` work outside an eval | Yes, and the config reaches the provider |
| Does the same call with `tools` and `tool_choice` run the tool | No. The call comes back in `output.message.tool_calls` under the parameter's given name, and nothing is executed |
