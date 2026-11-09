# Pilot

## Purpose

`write_pilot` rewrites [pilot results](../../pilot/results.md) section by section from the CSVs the [pilot cells](../harness/command.md#pilot-cells) write and the eval logs they leave, so every measure on [engine checks](../../pilot/engine-checks.md) and [provider checks](../../pilot/provider-checks.md) has a table, and the decisions in [decisions](../../pilot/decisions.md) can be typed from them.

## Interface

```python
def write_pilot(logs: Path, out: Path) -> list[Path]
# reads logs/pilot/<cell>.csv and logs/pilot/<cell>/*.eval, rewrites out/results.md,
# writes out/results/<section>.csv and out/results/<section>.svg. Returns what it wrote
```

## Behaviour

### Sections

One row per section of the pilot results page, in page order. The input column names the cell, see [pilot cells](../harness/command.md#pilot-cells). The measure column links to the check the table serves.

| Section | Input | Table written | Plot | Measure |
|---|---|---|---|---|
| Weather | `streaks`, `tell`, `luck`, `tape-sanity` CSVs | Per `persistence`: the share of No change tapes with a three round streak of the leader below the runner-up, the median rounds a switch takes to separate, the share with a field streak above the leader. Per `factor_scale`: hit rate, false tell rate, field moving together. Per grid setting: `(perfect − discerning) / (discerning − uniform)` pooled, the share of channel rounds below 0, and `discerning − complacent` in level points | Streak histograms, the tell rates against scale | [Streaks](../../pilot/engine-checks.md#streaks), [The tell](../../pilot/engine-checks.md#the-tell), [Luck on offer](../../pilot/engine-checks.md#luck-on-offer), [Tape sanity](../../pilot/engine-checks.md#tape-sanity) |
| Seeds and repeats | `seeds` and `repeats` logs | `spread` per scenario, and the seeds needed, `ceil((sd / target)²)`, at targets 0.02, 0.05 and 0.1. `sampling_share` per scenario from the repeats log | The strip plot of the seeds log | [Seeds](../../pilot/provider-checks.md#seeds), [Repeats](../../pilot/provider-checks.md#repeats) |
| Up against down | `up-against-down` log | Run score by `switch_kinds` kind, paired by seed. The share of runs with any bet on the sleeper after onset and the median round it first does. Mean points on unfunded channels before onset. The two `scenario_gap`s, revert and whipsaw | Run score by kind | [Up against down](../../pilot/provider-checks.md#up-against-down) |
| Noise | `noise-grid` CSV, `timestral` logs | Per setting: every fixed baseline's pooled scenario score on the three scenarios, with signal to noise beside `own_scale`. Timestral's rows beside them | The noise plot with the hedge rule and Scout rule curves | [Noise grid](../../pilot/engine-checks.md#noise-grid), [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Game length and switch round | `game-length` CSV | Per `rounds` and `onset`: `discerning − complacent` in level points and the rounds until it passes one sigma, per scenario | Gap against rounds after onset | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| Reading roughness | `reading-roughness` CSV | Per `read_noise_k` and look size: pooled output, the median move round, the cost of the look on No change | Output against `k` per look size | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| Up and down | `up-and-down` CSV | Sleeper share. Prize in level points per kind. The Scout rule's pooled score and median move round per `s` on Up switch, its false moves and cost on No change, and its moves on short seeds | Prize per kind | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| Baseline order | `baseline-order` CSV | Per scenario, every fixed baseline's pooled output in order, and each order line from the check with holds or breaks, a break in bold | None | [Baseline order](../../pilot/engine-checks.md#baseline-order) |
| Jev checks | `jev` log | The share of rounds with a channel at 0 after rounding, and mean points off the top channel on No change | None | [Jev checks](../../pilot/provider-checks.md#jev-checks) |
| Timestral checks | `timestral` CSV and logs | The gap test's quantile spread by gap length, determinism, the rounding share, and each policy's place against the hedge rule and Complacent marks on the grid | Spread against gap length | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| Notepad and compute | `notepad` logs | Scenario scores at `none`, `notes` and `compute`, the paired gaps against `none`, and the share of rounds each tool was called | None | [Notepad and compute](../../pilot/provider-checks.md#notepad-and-compute) |
| Rolling conversation | `rolling` logs | Scenario scores fresh and rolling, the paired gap, tokens per run each way | None | [Rolling conversation](../../pilot/provider-checks.md#rolling-conversation) |
| Cost per run | `seeds` and `repeats` logs | `write_cost` | None | [Cost per run](../../pilot/provider-checks.md#cost-per-run) |

- **Recognition** gets a section too: hits per model and skin as counts and shares, canary finishes as a count, and never a reply. The CSV is private whenever a held-out skin ran, see [recognition](../../pilot/provider-checks.md#recognition), so the section shows numbers only and the skin's name.
- **The inertia and warm up checks** read the main logs, so they appear as paired gaps in the Up against down and Seeds and repeats sections, see [inertia](../../pilot/provider-checks.md#inertia).

### Writing the page

- **A section whose input is missing** writes `_Not run yet._` under its heading, as the page has now, and the page stays valid.
- **Each table also goes to `out/results/<section>.csv`**, one file per section, and each plot to `out/results/<section>.svg`, so the page can link them and a reader can check.
- **Headings are the page's as they stand.** `write_pilot` replaces the body under each and adds none, so a new section is a change to the page and this table first.
- **Every rule on [tables](tables.md) holds here**: deterministic bytes, held-out seeds by position, no tape, no message, no skin text.
- **Pilot CSVs hold one row per seed, never a tape**, see [pilot cells](../harness/command.md#pilot-cells), so reading them adds nothing a log does not already give away.

## Invariants

- `write_pilot` on an empty folder writes the page with every section `_Not run yet._` and no CSV or SVG.
- Every measure named on the two pilot pages has a column in some section's table.
- The decisions table in [decisions](../../pilot/decisions.md) is never written by this layer.

## Not decided

- Whether the pilot sections should also report the reasoning setting the cell's model played, as the pilot runs one setting per model. They do not here, as the log's `reasoning` is in each table's key. Decide when the first pilot runs.
