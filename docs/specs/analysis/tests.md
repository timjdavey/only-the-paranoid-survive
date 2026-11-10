# Tests

Every test the analysis suite runs, in `tests/analysis/`. Ids start `A` for analysis, then the page's letter, see [test ids](../README.md#rules). They need no key and no network. Logs come from `inspect eval paranoid` run inside the suite with `baseline/uniform`, `baseline/discerning`, `baseline/complacent` and `mockllm/model` on `seeds="0-4"` into a temp folder, built once per session, plus hand-built `EvalLog` objects for the edge cases. **The `mockllm` run is scripted to a valid call every round**, as the harness suite does, see [harness tests](../harness/tests.md), else every run gives up and every score is 0 with `†`. The example skin is the skin throughout. A held-out fixture is a temp `held-out.txt` of three random seeds with `PARANOID_SEEDS` pointing at it, so the suite can check that no value leaks.

## Runs

| Id | Test | Page |
|---|---|---|
| AR1 | `load_runs` on the fixture folder has `columns == RUN_COLUMNS`, one row per sample epoch, `epoch == 1` throughout, and `run_score == gain / gap` on every row. `mean_over_epochs` on it changes no value and drops `epoch` | [runs](runs.md#one-row-per-run) |
| AR2 | A log on the held-out fixture: `seed` is NA on every row and the three seed values appear nowhere in the table's string form. The same log with a `seed` key planted in one sample's metadata raises `ValueError` naming the log and the sample | [runs](runs.md#privacy) |
| AR3 | Two logs with one `ResultKey`, the later holding every id of the earlier and one more: the later wins, the earlier is in `attrs["report"]` as dropped, and none of its rows load. The later holding two of the earlier's five ids: `ValueError` naming both logs. Two with disjoint ids both load | [runs](runs.md#duplicates) |
| AR4 | `reasoning` is `"low"` from `eval.metadata`, `"high"` from a config with `reasoning_effort="high"` and no metadata, `"medium"` from `reasoning_tokens=4096`, `"unknown"` from an empty config, and `"n/a"` for `baseline/uniform` | [runs](runs.md#reasoning) |
| AR5 | A hand-built log with one errored sample: the row has `errored` true and NA scores, the report counts it, and `scenario_scores` ignores it | [runs](runs.md#errored-samples) |
| AR6 | A log at `--epochs 2`: `load_runs` gives two rows per id with `epoch` 1 and 2. `mean_over_epochs` gives one row per id with `epochs == 2`, the mean of the two `run_score`s, the sum of the two `rounds`, and `gave_up` true when either epoch gave up | [runs](runs.md#mean-over-epochs) |
| AR7 | A folder holding a non-`paranoid` log and a file that is not a log: the first is skipped and listed, the second raises `ValueError` naming it | [runs](runs.md#discovering-logs) |
| AR8 | Hand-built logs with a `scenario` not in `SCENARIOS`, a `skin` of `Rome`, and a `model` holding `..` each raise `ValueError` naming the log. A log whose samples disagree on `tools` raises naming the field, and one whose `tool_choice` is `maybe` raises naming it | [runs](runs.md#guards) |
| AR9 | Two logs of one key whose samples carry different `numpy_version`s load, and the report names the key and both versions | [runs](runs.md#the-report) |

## Scores

| Id | Test | Page |
|---|---|---|
| AS1 | `scenario_scores` on the `mockllm` log equals the log's `scenario_score` metric in `score`, `lo`, `hi`, `n` and `failed` to `1e-9`, and `headlines` equals its `headline` metric in `headline`, `lo` and `hi`, and its `weakest_trait` metric | [scores](scores.md#scenario-scores) |
| AS2 | `baseline/uniform` scores exactly 0 and `baseline/discerning` exactly 1 in every scenario, and the `complacent` mark on `baseline/complacent`'s own log equals its score | [scores](scores.md#invariants) |
| AS3 | `paired_gap(runs, a, a)` has `diff == lo == hi == 0` on every row. `paired_gap(runs, discerning, uniform)` has `diff == 1` with `lo == hi == 1`. Two keys with different `seed_set`, or one scenario's `engine_hash` differing between them, raise `ValueError` | [scores](scores.md#paired-gap) |
| AS4 | `scenario_gap` on `baseline/complacent` between No change and Down switch is `1 − complacent's Down switch score`, within the bar | [scores](scores.md#scenario-gap) |
| AS5 | `switch_kinds` on the public fixture equals the `kind` and `short` of the first switch `Event` of `make_timeline` on each seed, with `none` for No change. On the held-out fixture it returns a kind per row and writes no file. On a log played at `inertia=10` the hash check passes | [scores](scores.md#switch-kinds) |
| AS6 | `noise_threshold` on hand-built result rows whose headlines follow `h(x)` at `x0 = log(2)`, `k = 2`, floor 0.55, over five settings, recovers `snr` within 2% and `snr_80` within 5%, `status == "crossed"`, and `floor_drift == 0`. Headlines all above the half way mark give `"off the noisy end"`, all below give `"off the quiet end"`, each with `snr is None`. Two settings raise `ValueError` | [scores](scores.md#noise-threshold) |
| AS7 | `signal_points(scenario_config("down_switch"))` is the midpoint of its `SwitchSpec.size_points`, and `scenario_config("no_change")` raises `ValueError` | [scores](scores.md#noise-threshold) |
| AS8 | `sampling_share` on a hand-built two-epoch table is 0 when every seed's epochs are equal and 1 when every seed's mean is equal and epochs differ | [scores](scores.md#spread-and-sampling-share) |
| AS9 | `spread` on five seeds has `sd` equal to `numpy.std(ddof=1)` and `p10` to `numpy.percentile(10)`, and NA on one seed | [scores](scores.md#spread-and-sampling-share) |
| AS10 | A hand-built log with one gave up run has `†` in that scenario's `flags` and in the headline's. A `retry_share` of 0.2 gives `‡`. A `recognition` table with half the model's rows at `lint_hits > 0` gives `§` on every row, and one with `canary_finished` true gives `¶` on every row | [scores](scores.md#flags) |
| AS11 | `public_gap` on two result rows that differ only in `seed_set` returns a row per scenario plus `headline`, and raises `ValueError` naming `skin` when the skins differ | [scores](scores.md#public-gap) |
| AS12 | `load_recognition` on a CSV with a `reply` column returns `model`, `skin`, `lint_hits` and `canary_finished` only, and the reply text is in no cell. Every gap function returns `GAP_COLUMNS` | [scores](scores.md#flags) |
| AS13 | `notes_share` on a hand-built table with `notes_rounds` 4 and 0 over `rounds` 40 and 40 is 0.05, and `compute_share` with `compute_rounds` 0 and 0 is 0 | [scores](scores.md#scenario-scores) |

## Tables

| Id | Test | Page |
|---|---|---|
| AT1 | `write_results` on the fixture writes `<name>.md` with the header line naming the logs' `harness_version`, the eleven columns in order, one row per result row in models file order with provider rows first, and a legend naming `†` when a run gave up | [tables](tables.md#the-results-page) |
| AT2 | The CSV has exactly `CSV_COLUMNS`, one row per scored run, `seed` filled on public rows and blank on held-out rows, and no `output` column | [tables](tables.md#the-run-csv) |
| AT3 | `write_results` twice on the same table gives byte-identical `.md` and `.csv`, and the same bytes again after a line is appended to `<name>.md` between runs | [tables](tables.md#invariants) |
| AT4 | On the held-out fixture, with a `recognition` table built from a CSV holding a planted reply string, none of the three seed values, the reply string, a reading or a word of the example skin's `intro` appears in any file written | [tables](tables.md#invariants) |
| AT5 | `pooled_score` over the CSV's `gain` and `gap` per scenario equals the page's score to two decimals | [tables](tables.md#invariants) |
| AT6 | `write_cost` on the `mockllm` log has the columns in the table, zero usage on a baseline row, `projected` set when `models` and `seeds` are given, and `cost` set only with a `prices` file | [tables](tables.md#cost) |
| AT7 | Two logs of one model that differ only in `tools` give two tables, each heading naming the setting that is off its default. A `name` of `../x` raises `ValueError` and writes nothing | [tables](tables.md#the-results-page) |
| AT8 | Two logs of one model on the same seeds, the second at `tools="none"`: the page has a sensitivity table with one row naming `tools none`, that row's headline, and a gap equal to `paired_gap`'s `headline` row, headline minus bare. With the headline log alone there is no such table | [tables](tables.md#the-results-page) |

## Plots

| Id | Test | Page |
|---|---|---|
| AP1 | Each of the four plot functions writes an SVG that parses as XML, and twice on the same inputs gives equal bytes | [plots](plots.md#every-plot) |
| AP2 | The ECI trend plot's SVG contains `Epoch AI`, `CC BY 4.0` and the date passed, and the title of a strip plot contains the skin name and seed set and no seed value | [plots](plots.md#trend-plots) |
| AP3 | `trend_plot` with `x="eci"` and no `eci_read_on` raises `ValueError`. A model row with no `eci` is named in the footer and has no point | [plots](plots.md#trend-plots) |

## Pilot

| Id | Test | Page |
|---|---|---|
| AI1 | `write_pilot` on an empty folder writes `results.md` with every heading in `SECTIONS` and `_Not run yet._` under each, and no other file. `SECTIONS` equals the headings of the repo's pilot results page | [pilot](pilot.md#writing-the-page) |
| AI2 | With a hand-built `baseline-order.csv`, the Baseline order section has one row per scenario and baseline, an order line that holds, and a `**bold**` line for a planted break. The other sections still read `_Not run yet._` | [pilot](pilot.md#sections) |
| AI3 | With a hand-built `recognition.csv` holding a reply column, the section's table has counts and shares and the reply text appears nowhere in the page or its CSV | [pilot](pilot.md#sections) |
| AI4 | An existing `results.md` with one heading renamed raises `ValueError` naming it, and the file is unchanged | [pilot](pilot.md#writing-the-page) |

## Command

| Id | Test | Page |
|---|---|---|
| AM1 | The harness's `main(["analyse", "--dry-run", <fixture>])` returns 0, prints the report and the paths it would write, and writes nothing | [command](command.md#dispatch) |
| AM2 | `analyse([<fixture>, "--out", tmp, "--name", "t"])` writes `t.md` and `t.csv` under `tmp` and nothing elsewhere, the bare form being `results` | [command](command.md#results) |
| AM3 | `analyse(["gap", <discerning log>, <uniform log>])` prints a table with `diff == 1` on every scenario row. With a log that holds two result rows it returns 1 with a message naming the log | [command](command.md#gap) |
| AM4 | `analyse(["cost", <fixture>])` prints the cost columns and returns 0. `analyse(["results", "/nope"])` returns 1 and prints a message | [command](command.md#cost) |
| AM5 | Every subcommand runs with the network blocked by a socket monkeypatch and no key in the environment | [command](command.md#invariants) |
| AM6 | `--name ../x` returns 1 and writes nothing. `--plots` with a models file that has `eci` and no `--eci-read-on` returns 1 and writes nothing | [command](command.md#results) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| AY1 | For any table of positive gaps and finite gains over two scenarios, `pooled_score` over the CSV `write_run_csv` writes equals `scenario_scores` on the table, and `paired_gap(a, a)` is zero |
| AY2 | For any headlines on a logistic curve with floor in `[0.4, 0.7]`, `k` in `[0.5, 4]` and `x0` inside the grid, `noise_threshold` returns `crossed` with `lo ≤ snr ≤ hi` |
| AY3 | For any model, skin and scenario strings that pass the [guards](runs.md#guards), every file name `write_results` builds from them resolves under `out` |

## Not decided

- Whether the fixture logs should be built once and committed under `tests/analysis/logs/`, so the suite needs no inspect run. They are built per session here, as a committed log goes stale with every harness change. Decide when the suite's run time is known.
