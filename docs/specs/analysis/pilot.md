# Pilot

## Purpose

`write_pilot` rewrites [pilot results](../../pilot/results.md) section by section from the CSVs the [pilot cells](../harness/pilot.md) write and the eval logs they leave, so every measure on [engine checks](../../pilot/engine-checks.md) and [provider checks](../../pilot/provider-checks.md) has a table, and the decisions in [decisions](../../pilot/decisions.md) can be typed from them.

## Interface

```python
SECTIONS: tuple[str, ...]             # the page's headings, in page order, see Sections
REACHABLE_GAIN_FLOOR = 0.3            # the reachable gain check's pass lines
BAYESIAN_GAIN_PERCENTAGE_FLOOR = 50

def write_pilot(logs: Path, out: Path) -> list[Path]
# reads logs/pilot/<cell>.csv and logs/pilot/<cell>/*.eval, rewrites out/results.md,
# writes out/results/<section>.csv and out/results/<section>.svg. Returns what it wrote
```

## Behaviour

### Sections

One row per section of the pilot results page, in page order. `SECTIONS` holds the headings. The input column names the cell, see [pilot cells](../harness/pilot.md). **The measures are the check's**, so each row links to the check whose Measure list is the table's columns, and this page adds only what the maths needs from [scores](scores.md).

| Section | Input | From scores | Plot | Check |
|---|---|---|---|---|
| Weather | `streaks`, `tell`, `luck`, `timeline-sanity` and `timeline-sanity-sparklines` CSVs | Pooled outputs per setting, `(perfect − discerning) / (discerning − uniform)`, the share of `depth_capped`, the share of channel rounds with a level below 0 and the share of runs with a reading below 0 per setting, the leader's median level per round per scenario | Streak histograms, the tell rates against scale | [Streaks](../../pilot/engine-checks.md#streaks), [The tell](../../pilot/engine-checks.md#the-tell), [Luck on offer](../../pilot/engine-checks.md#luck-on-offer), [Timeline sanity](../../pilot/engine-checks.md#timeline-sanity) |
| Seeds and repeats | `seeds` and `repeats` logs | `spread` per result row and scenario, the widest `sd` with the row and scenario that set it, the seeds needed `ceil(1.5 × (sd / target)²)` from that `sd` at targets 0.02, 0.05 and 0.1, `sampling_share` | The strip plot of the seeds logs | [Seeds](../../pilot/provider-checks.md#seeds), [Repeats](../../pilot/provider-checks.md#repeats) |
| Recognition | `recognition` CSV through `load_recognition` | Hits per model and skin as counts and shares, canary finishes as a count | None | [Recognition](../../pilot/provider-checks.md#recognition) |
| Channel order | `channel-order` CSV | Per model, skin and shape, and pooled per model: the probes, the share with `called`, the share with `valid`, the slip share and the own numbers share, which is the rows with neither `matched` nor `slipped`, both over the valid rows, and the slips counted by the first place where `sent` differs from `wanted` | None | [Channel order](../../pilot/provider-checks.md#channel-order) |
| Up against down | `up-against-down` and `seeds` logs, and the proof of concept logs for inertia | Run score by `switch_kinds` kind paired by seed, the four `scenario_gap`s, the share of runs with `sleeper_round > 0` and its median, the mean `explore_points`, the inertia gaps as `paired_gap` | Run score by kind | [Up against down](../../pilot/provider-checks.md#up-against-down), [Inertia](../../pilot/provider-checks.md#inertia) |
| Noise | `noise-grid` and `timestral-grid` CSVs | Every fixed baseline's pooled scenario score per setting with signal to noise beside `own_scale`, Timestral's rows beside them | Scenario score against signal to noise, one curve per baseline. Drawn here from the CSV, not by `noise_plot`, which fits a model's headline | [Noise grid](../../pilot/engine-checks.md#noise-grid), [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Game length and switch round | `game-length` CSV | Per `rounds` and `onset`: `discerning − complacent` in level points, the hedge rule's pooled scenario score, the share of seeds where the hedge rule and the Scout rule each have no move round, counted where the check says each should move, the median rounds left after the last event ends, and reachable gain and Bayesian gain percentage per scenario as the Reachable gain row computes them | Gap against rounds after onset | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| Reading roughness | `reading-roughness` CSV | Pooled output per `read_noise_k` and explore bet size | Output against `k` per explore bet size | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| Up and down | `up-and-down` CSV | Per `setting` and kind: pooled scenario score per baseline, scored against the `uniform` and `discerning` rows, and reachable gain in level points and as a score | Reachable gain per kind, one line per `setting` | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| Bayesian frontier | `bayesian-frontier` CSV | Pooled scenario score and headline per player, the best headline on seeds 0 to 499 and that player's scores on 500 to 999, irreducible lag | The two planes with the envelope and the fixed baselines marked | [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier) |
| Baseline order | `baseline-order` CSV | Pooled output per baseline, each order line with holds or breaks, a break in bold | None | [Baseline order](../../pilot/engine-checks.md#baseline-order) |
| Reachable gain | `baseline-order` CSV | Per scenario with a switch or drift: reachable gain, Bayesian gain and Bayesian gain percentage from pooled scenario scores, with `stayer` for `complacent` in Up switch then down switch. Explore cost per blind baseline on No change, and the share of Up switch then down switch seeds where `bayesian` has a move round. Each pass line with holds or breaks against `REACHABLE_GAIN_FLOOR` and `BAYESIAN_GAIN_PERCENTAGE_FLOOR`, a break in bold | Reachable gain against Bayesian gain per scenario, the floors drawn | [Reachable gain](../../pilot/engine-checks.md#reachable-gain) |
| Jev checks | `jev` log and `jev.csv` | The mean `rounded_out` a round, the share of rounds where it is above 0, and the mean `explore_points` on No change | None | [Jev checks](../../pilot/provider-checks.md#jev-checks) |
| Timestral checks | `timestral`, `timestral-rounding` and `timestral-grid` CSVs, and the `noise-grid` CSV for the marks | The gap test's spread per gap and input shape, the determinism rows, the mean `rounded_out` a round and the share of rounds where it is above 0, each policy's pooled place against the hedge rule and Complacent marks | Spread against gap length | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Bare harness | `bare` logs | Scenario scores per model and `tools`, `paired_gap` of each other setting against `notes,compute` per model with its bar, `notes_share` and `compute_share` | None | [Bare harness](../../pilot/provider-checks.md#bare-harness) |
| Tool choice | `tool-choice` logs | Scenario scores per model and `tool_choice`, `paired_gap` of `auto` against `any` per model with its bar, the no call share in each | None | [Tool choice](../../pilot/provider-checks.md#tool-choice) |
| Rolling conversation | `rolling` logs | Scenario scores fresh and rolling per model, `paired_gap` per model and whether its `headline` bar clears zero, tokens per run and input tokens per round | None | [Rolling conversation](../../pilot/provider-checks.md#rolling-conversation) |
| Warm up | `warm-up` logs | Scenario scores with an empty record and pre-filled per model, `paired_gap` | None | [Warm up](../../pilot/provider-checks.md#warm-up) |
| Cost per run | `seeds` and `repeats` logs | `write_cost`, and the retry share per result row, `sum(retry_rounds) / sum(rounds)` | None | [Cost per run](../../pilot/provider-checks.md#cost-per-run) |

- **Recognition shows numbers and skin names only.** The CSV holds replies about held-out prompts and is private whenever a held-out skin ran, see [recognition](../../pilot/provider-checks.md#recognition). `load_recognition` drops the reply on read, see [flags](scores.md#flags), so the section cannot hold one.
- **The inertia check reads the main logs**, so it appears as paired gaps in the Up against down section, see [inertia](../../pilot/provider-checks.md#inertia). The warm up check has its own cell and section.
- **Each cell's folder is loaded on its own.** `load_runs` is called once per input, never over `logs/pilot/` as a whole, so the `repeats` log, whose ids are ten of one `seeds` log's twenty, is never dropped as its duplicate, see [duplicates](runs.md#duplicates).
- **The pilot keys in `Score.value`**, `explore_points`, `sleeper_round`, `notes_rounds` and `compute_rounds`, are run table columns like any other, see [scoring one run](../harness/scorer.md#scoring-one-run). The two rounding CSVs exist because `rounded_out` sits on a message, which this layer never reads.

### Writing the page

- **A section whose input is missing** writes `_Not run yet._` under its heading, as the page has now, and the page stays valid.
- **Each table also goes to `out/results/<section>.csv`**, one file per section, and each plot to `out/results/<section>.svg`, so the page can link them and a reader can check.
- **Headings are `SECTIONS`.** `write_pilot` writes every heading in order and replaces the body under each. When `out/results.md` exists, its headings must equal `SECTIONS`, else `ValueError` naming the odd one, so a new section is a change to the page, this table and `SECTIONS` together.
- **Every rule on [tables](tables.md) holds here**: deterministic bytes, held-out seeds by position, no timeline, no message, no skin text.
- **Pilot CSVs hold one seed's numbers per row, never a timeline**, see [pilot cells](../harness/pilot.md#shared-rules), so reading them adds nothing a log does not already give away.

## Invariants

- `write_pilot` on an empty folder writes the page with every section `_Not run yet._` and no CSV or SVG.
- Every measure named on the two pilot pages has a column in some section's table, and every column comes from a score, a log's metadata or a CSV a pilot cell wrote.
- `SECTIONS` equals the headings of [pilot results](../../pilot/results.md), in order.
- The decisions table in [decisions](../../pilot/decisions.md) is never written by this layer.

## Not decided

- Whether the pilot sections should also report the reasoning setting the cell's model played, as the pilot runs one setting per model. They do not here, as the log's `reasoning` is in each table's key. Decide when the first pilot runs.
