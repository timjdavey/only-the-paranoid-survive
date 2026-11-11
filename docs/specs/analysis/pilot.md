# Pilot

## Purpose

`write_pilot` rewrites [pilot results](../../pilot/results.md) section by section from the CSVs the [pilot cells](../harness/pilot.md) write and the eval logs they leave, so every measure on [engine checks](../../pilot/engine-checks.md) and [provider checks](../../pilot/provider-checks.md) has a table, and the decisions in [decisions](../../pilot/decisions.md) can be typed from them.

## Interface

```python
SECTIONS: tuple[str, ...]             # the page's headings, in page order, see Sections
REACHABLE_GAIN_FLOOR = 0.3            # the reachable gain check's three pass lines
BAYESIAN_GAIN_PERCENTAGE_FLOOR = 50
BAYESIAN_MOVE_SHARE_FLOOR = 0.5

def write_pilot(logs: Path, out: Path, *, main: Path | None = None, dry_run: bool = False) -> list[Path]
# logs is the folder the cells wrote to: it reads logs/<cell>.csv and logs/<cell>/*.eval.
# main is a folder of logs from `paranoid run`, for the inertia table.
# Rewrites out/results.md, writes out/results/<section>-<table>.csv and out/results/<section>-<plot>.svg.
# Returns what it wrote, or with dry_run what it would write
```

## Behaviour

### Sections

One row per section of the pilot results page, in page order. `SECTIONS` holds the headings. The input column names the cell, see [pilot cells](../harness/pilot.md). **The measures are the check's**, so each row links to the check whose Measure list is the table's columns, and this page adds only the name of each table and what the maths needs from [scores](scores.md).

| Section | Input | Tables | Plots | Check |
|---|---|---|---|---|
| Weather | `streaks`, `tell`, `luck`, `timeline-sanity` and `timeline-sanity-sparklines` CSVs | `streaks`: per `setting`, the share of No change seeds with a `leader_below_streak` of 3 or more, the median `rounds_to_separate` on Down switch, and the share of No change seeds with a `field_beats_leader_streak` of at least `n`, for `n` from 2 to 5. `tell`: per `factor_scale`, `loading_low` and threshold set, the hit rate, the false tell rate, the share of seeds where the fall test never fired, the share of No change seeds with a `field_together_rounds` above 0, and the share of `depth_capped`. `luck`: `(perfect − discerning) / (discerning − uniform)` on pooled outputs per setting. `sanity`: per setting, the share of channel rounds with a level below 0, the share of runs with a reading below 0, and `discerning − complacent` in level points per scenario | `streaks`: streak histograms. `tell`: the two rates against scale. `sparklines`: the leader's median level per round, one panel per scenario | [Streaks](../../pilot/engine-checks.md#streaks), [The tell](../../pilot/engine-checks.md#the-tell), [Luck on offer](../../pilot/engine-checks.md#luck-on-offer), [Timeline sanity](../../pilot/engine-checks.md#timeline-sanity) |
| Seeds and repeats | `seeds` and `repeats` logs | `spread`: `spread` per result row and scenario of the `seeds` logs. `seeds-needed`: the widest `sd` with the row and scenario that set it, and the seeds needed, `ceil(1.5 × (sd / target)²)`, at targets 0.02, 0.05 and 0.1. `sampling-share`: `sampling_share` of the `repeats` log | `strip-<row slug>`: the strip plot of each `seeds` result row | [Seeds](../../pilot/provider-checks.md#seeds), [Repeats](../../pilot/provider-checks.md#repeats) |
| Recognition | `recognition` CSV through `load_recognition` | `hits`: per model and skin, the `round_1` and `round_20` probes, the hits among them as a count and a share, and canary finishes as a count | None | [Recognition](../../pilot/provider-checks.md#recognition) |
| Channel order | `channel-order` CSV | `shares`: per model, skin and shape, and pooled per model: the probes, the share with `called`, the share with `valid`, the slip share and the own numbers share, which is the rows with neither `matched` nor `slipped`, both over the valid rows. `slips`: the slips counted by the first place where `sent` differs from `wanted` | None | [Channel order](../../pilot/provider-checks.md#channel-order) |
| Up against down | `up-against-down` and `seeds` logs, and `main` for inertia | `kinds`: per model, scenario and `switch_kinds` kind, the seeds and the pooled score with its bar. `gaps`: the four `scenario_gap`s per model. `sleeper`: per model and scenario, the share of runs with `sleeper_round > 0`, the median of those rounds, and the mean `explore_points`. `inertia`: see below | `kinds`: run score by switch kind, one panel per model | [Up against down](../../pilot/provider-checks.md#up-against-down), [Inertia](../../pilot/provider-checks.md#inertia) |
| Noise | `noise-grid` and `timestral-grid` CSVs | `scores`: every fixed baseline's pooled scenario score per setting with signal to noise beside `own_scale`, Timestral's rows beside them | `curves`: scenario score against signal to noise, one curve per baseline. Drawn here from the CSV, not by `noise_plot`, which fits a model's headline | [Noise grid](../../pilot/engine-checks.md#noise-grid), [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Game length and switch round | `game-length` CSV | `length`: per `rounds`, `onset`, `gap` and scenario. For each event window, `discerning − complacent` in level points, the median rounds from the window's onset to `clear_round`, and the share of seeds that never pull clear. Then the share of seeds where the hedge rule and the Scout rule each have no move round, counted where the check says each should move, the median rounds left after the last event ends, the hedge rule's pooled scenario score, and reachable gain and Bayesian gain percentage as the Reachable gain row computes them | `gap`: gap against rounds after onset | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| Reading roughness | `reading-roughness` CSV | `roughness`: per `read_noise_k`, rule, explore bet size and `scout_rounds`: pooled output, the share of seeds with a move round, and the explore cost in level points, the `complacent` rows' output minus the rule's on No change | `output`: output against `k` per explore bet size | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| Up and down | `up-and-down` CSV | `kinds`: per `setting` and switch kind, the seeds, each baseline's pooled scenario score and median move round over the seeds where it moved, as a move round of 0 means it never did, and reachable gain in level points and as a score | `gain`: reachable gain per kind, one line per `setting` | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| Bayesian frontier | `bayesian-frontier` CSV | `players`: pooled scenario score and headline per player. `pick`: the best headline on the lower half of the seeds, that player's scores on the upper half, and the irreducible lag | `planes`: the two planes with the envelope and the fixed baselines marked | [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier) |
| Baseline order | `baseline-order` CSV | `outputs`: pooled output and scenario score per scenario and baseline, with the Up switch seeds whose kind is `rise_short` in rows of their own. `orders`: each order line with holds or breaks, a break in bold | None | [Baseline order](../../pilot/engine-checks.md#baseline-order) |
| Reachable gain | `baseline-order` CSV | `gains`: per scenario with a switch or drift, reachable gain, Bayesian gain and Bayesian gain percentage from pooled scenario scores, with `stayer` for `complacent` in Up switch then down switch, and there the share of seeds where `bayesian` has a move round. `explore-cost`: one minus each blind baseline's No change score. `lines`: each pass line with holds or breaks against the three floors, a break in bold | `gains`: reachable gain against Bayesian gain per scenario, the floors drawn | [Reachable gain](../../pilot/engine-checks.md#reachable-gain) |
| Jev checks | `jev` log and `jev.csv` | `rounding`: the mean `rounded_out` a round and the share of rounds where it is above 0. `explore`: the mean `explore_points` on No change | None | [Jev checks](../../pilot/provider-checks.md#jev-checks) |
| Timestral checks | `timestral`, `timestral-rounding` and `timestral-grid` CSVs, and the `noise-grid` CSV for the marks | `gap-test`: the spread per gap and input shape, and the determinism rows. `rounding`: the mean `rounded_out` a round and the share of rounds where it is above 0. `grid`: each policy's pooled scenario score per setting beside the hedge rule and Complacent marks, the marks pooled on the seeds the policies played in that setting and scenario, not the whole noise grid | `gap-test`: spread against gap length | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Bare harness | `bare` logs | `scores`: scenario scores per model and `tools`, with `notes_share` and `compute_share`. `gaps`: `paired_gap` of each other setting against `notes,compute` per model with its bar | None | [Bare harness](../../pilot/provider-checks.md#bare-harness) |
| Tool choice | `tool-choice` logs | `scores`: scenario scores per model and `tool_choice`, with the no call share, `sum(no_calls) / sum(rounds)`. `gaps`: `paired_gap` of `auto` against `any` per model with its bar | None | [Tool choice](../../pilot/provider-checks.md#tool-choice) |
| Rolling conversation | `rolling` logs and `rolling-tokens.csv` | `scores`: scenario scores fresh and rolling per model. `gaps`: `paired_gap` per model and whether its `headline` bar clears zero. `tokens`: per model and `rolling`, tokens per run from the logs and mean input tokens per round from the CSV | `tokens`: input tokens against round, fresh and rolling | [Rolling conversation](../../pilot/provider-checks.md#rolling-conversation) |
| Warm up | `warm-up` logs | `scores`: scenario scores with an empty record and pre-filled per model, with the mean `warm_up_kept`. `gaps`: `paired_gap` per model | None | [Warm up](../../pilot/provider-checks.md#warm-up) |
| Cost per run | `seeds` and `repeats` logs and `seeds-tokens.csv` | `cost`: `write_cost` on each cell's logs, with a `cell` column and the retry share per result row, `sum(retry_rounds) / sum(rounds)`. `tokens`: per model, mean input tokens per round, cached and not | `tokens`: input tokens against round, cached and not | [Cost per run](../../pilot/provider-checks.md#cost-per-run) |

### Reading the inputs

- **Each cell's folder is loaded on its own.** `load_runs` is called once per input, never over `logs` as a whole, so the `repeats` log, whose ids are ten of one `seeds` log's twenty, is never dropped as its duplicate, see [duplicates](runs.md#duplicates).
- **Up against down takes rows from two folders.** Every row of the `up-against-down` log, and from the `seeds` logs only the One shock rows of the same model and reasoning whose setting equals that log's, see [comparing settings](runs.md#comparing-settings). The `seeds` logs' Up switch rows are left out, as the `up-against-down` log played those ids too and the two would clash as [duplicates](runs.md#duplicates). In the section's own copy of the table the rows it took from `seeds` carry the `up-against-down` log's `harness_version`, so `scenario_gap` finds both scenarios under one key.
- **The inertia table reads `main`**, the logs `paranoid run` wrote, as the [inertia check](../../pilot/provider-checks.md#inertia) has no cell. One row per two result rows of `main` that share a setting: the Down switch and Slow drift rows of their `paired_gap`. Without `main` the table is left out and the section says `_Inertia needs --main._`.
- **A pooled score from an engine CSV** is `pooled_score` over each seed's `output − uniform` and `discerning − uniform`, the three rows joined on the seed and the cell's setting columns.
- **A pooled output is a sum over seeds**, in level points, as in the Baseline order and Reading roughness tables, and the explore cost there is the `complacent` rows' summed output minus the rule's on the same No change seeds.
- **Where a check leaves a word loose, the section says how it reads it.**
  - **≈ and ≥ in an order line** allow 0.02 of a scenario score: two scores are ≈ within 0.02, and `a ≥ b` holds while `a` is no more than 0.02 below `b`. `>` is strict.
  - **The hedge rule's unmoved share** in Game length counts the seeds where the Discerning baseline moves, outside Up switch and Up switch then down switch, where the leader never falls. The Scout rule's counts every seed where the Discerning baseline moves.
  - **Rounds to pull clear** are `clear_round − onset`, over the seeds that pull clear.
  - **The Bayesian frontier's split** is on the seed value: the seeds in the file in order, the lower half to pick and the rest to report, the middle seed reporting when the count is odd. The cell's ten seeds split into 0 to 4 and 5 to 9, and a thousand would split at 500. The pick is the Bayesian player with the best headline on the lower half.
- **A CSV must have exactly its cell's columns**, the ones its Writes line names in the [harness pilot spec](../harness/pilot.md). Any other set raises `ValueError` naming the file and the odd column, so a cell and its section cannot drift apart. An extra column raises as a missing one does: dropped quietly, it would let a stale file, or a measure no section shows, pass as fine.
- **Recognition shows numbers and skin names only.** The CSV holds replies about held-out prompts and is private whenever a held-out skin ran, see [recognition](../../pilot/provider-checks.md#recognition). `load_recognition` drops the reply on read, see [flags](scores.md#flags), so the section cannot hold one.
- **The pilot keys in `Score.value`**, `explore_points`, `sleeper_round`, `warm_up_kept`, `notes_rounds` and `compute_rounds`, are run table columns like any other, see [scoring one run](../harness/scorer.md#scoring-one-run). The rounding and token CSVs exist because `rounded_out` sits on a message and a round's tokens on an event, which this layer never reads.

### Writing the page

- **A section whose input is missing** writes `_Not run yet._` under its heading, as the page has now, and the page stays valid. A section with some of its inputs writes the tables it can.
- **Each table is a `###` heading of its name, the table, and a link to its CSV.** A whole number shows as it is and any other number to three significant places. The CSV holds every digit.
- **Each table also goes to `out/results/<section>-<table>.csv`** and each plot to `out/results/<section>-<plot>.svg`, so the page can link them and a reader can check. `<section>` is the heading's [slug](tables.md#headings-and-file-names), such as `seeds-and-repeats`, and the table and plot names are the ones above.
- **Headings are `SECTIONS`.** `write_pilot` writes every heading in order and replaces the body under each. When `out/results.md` exists, its `##` headings must equal `SECTIONS`, else `ValueError` naming the odd one, so a new section is a change to the page, this table and `SECTIONS` together.
- **`dry_run` writes nothing** and returns the paths a real run would write.
- **Every rule on [tables](tables.md) holds here**: deterministic bytes, held-out seeds by position, no timeline, no message, no skin text.
- **Pilot CSVs hold one seed's numbers per row, never a timeline**, see [pilot cells](../harness/pilot.md#shared-rules), so reading them adds nothing a log does not already give away.

## Invariants

- `write_pilot` on an empty folder writes the page with every section `_Not run yet._` and no CSV or SVG.
- Every measure named on the two pilot pages has a column in some section's table, and every column comes from a score, a log's metadata or a CSV a pilot cell wrote.
- Every CSV column a section reads is in that cell's Writes line.
- `SECTIONS` equals the headings of [pilot results](../../pilot/results.md), in order.
- The decisions table in [decisions](../../pilot/decisions.md) is never written by this layer.

## Not decided

- Whether the pilot sections should also report the reasoning setting the cell's model played, as the pilot runs one setting per model. They do not here, as the log's `reasoning` is in each table's key. Decide when the first pilot runs.
