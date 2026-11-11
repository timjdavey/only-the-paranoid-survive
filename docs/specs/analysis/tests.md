# Tests

Every test the analysis suite runs, in `tests/analysis/`. Ids start `A` for analysis, then the page's letter, see [test ids](../README.md#rules). They need no key and no network.

- **Fixture logs** come from `inspect_ai.eval(paranoid, ...)` run inside the suite with `baseline/uniform`, `baseline/discerning`, `baseline/complacent` and `mockllm/model` on `seeds="0-4"`, at `rounds=20` and `tools="none"` so they are quick and need no Docker. They are built once per session into a temp folder.
- **The `mockllm` run is scripted to a valid call every round**, as the harness suite does, see [harness tests](../harness/tests.md), else every run gives up and every score is 0 with `†`.
- **An edited log** is a copy of a fixture log with a value changed and `results` set to `None`, written back with `write_eval_log`, see [checked](runs.md#checked). `results` goes because the [metric check](runs.md#metric-check) would catch the edit. Every "edited log" below is one.
- **The example skin is the skin throughout**, bar AT9, which adds a copy of it under a second name.
- **A held-out fixture** is a temp `held-out.txt` of three random seeds with `PARANOID_SEEDS` pointing at it, so the suite can check that no value leaks.

## Runs

| Id | Test | Page |
|---|---|---|
| AR1 | `load_runs` on the fixture folder has `columns == RUN_COLUMNS`, every column at the dtype its table names, one row per sample epoch, `epoch == 1` throughout, and `run_score == gain / gap` on every row. `mean_over_epochs` on it changes no value and drops `epoch` | [runs](runs.md#one-row-per-run) |
| AR2 | A log on the held-out fixture: `seed` is NA on every row and the three seed values appear nowhere in the table's string form. The same log with a `seed` key planted in one sample's metadata raises `ValueError` naming the log and the sample | [runs](runs.md#privacy) |
| AR3 | Two logs with one `ResultKey`, the later holding every id of the earlier and one more: the later wins, the earlier is in `attrs["report"]` as dropped, and none of its rows load. The later holding two of the earlier's five ids: `ValueError` naming both logs. Two with disjoint ids both load. Two with equal `started` and equal ids: the later in path order wins | [runs](runs.md#duplicates) |
| AR4 | `reasoning` is `"low"` from `eval.metadata`, `"high"` from a config with `reasoning_effort="high"` and no metadata, `"medium"` from `reasoning_tokens` equal to the harness's `BUDGETS["medium"]`, `"off"` from `reasoning_effort="none"`, `"unknown"` from `reasoning_tokens=0`, from `reasoning_tokens=5` and from an empty config, and `"n/a"` for `baseline/uniform` | [runs](runs.md#reasoning) |
| AR5 | An edited log with one errored sample: the row has `errored` true and NA scores, the report counts it, and `scenario_scores` ignores it | [runs](runs.md#errored-samples) |
| AR6 | A log at `--epochs 2`: `load_runs` gives two rows per id with `epoch` 1 and 2. `mean_over_epochs` gives one row per id with `epochs == 2`, the mean of the two `run_score`s, the sum of the two `rounds`, and `gave_up` true when either epoch gave up. With `sleeper_round` edited to 0 and 7 it gives 7, to 0 and 0 it gives 0, and `explore_points` of 2 and `None` gives 2 | [runs](runs.md#mean-over-epochs) |
| AR7 | A folder holding a log whose `eval.task` is not `paranoid/paranoid` and a file that is not a log: the first is skipped and listed, the second raises `ValueError` naming it | [runs](runs.md#discovering-logs) |
| AR8 | Edited logs with a `scenario` not in `SCENARIOS`, a `skin` of `Rome`, a `model` holding `..`, a `model` holding a space, a `seed_set` of `private` and a `seed_index` of −1 each raise `ValueError` naming the log. A log whose samples disagree on `tools` raises naming the field, and one whose `tool_choice` is `maybe` raises naming it | [runs](runs.md#guards) |
| AR9 | Two logs of one key whose samples carry different `numpy_version`s load, and the report names the key and both versions | [runs](runs.md#the-report) |
| AR10 | An edited log whose `model_usage` has `input_tokens_cache_read` of 300 and `input_tokens_cache_write` of 50 gives `cache_read_tokens == 300` and `cache_write_tokens == 50` on its row, and a log with both as `None` gives 0 for both | [runs](runs.md#one-row-per-run) |
| AR11 | A log played at `rounds=20` on which the agent gave up in round 3 has `game_rounds == 20` and `rounds == 3` on that row, `RUN_COLUMNS` has no name twice, and a log with `release` `r1` gives a `ResultKey` unequal to the same log at `dev` | [runs](runs.md#result-key) |
| AR12 | A fixture log with one sample's `gain` changed and `results` left in place raises `ValueError` naming the log and the scenario. The same log with `results` as `None` loads. The untouched fixture loads, and its report counts every log as checked | [runs](runs.md#metric-check) |
| AR13 | A log with `tool_choice` missing from one errored sample's metadata loads with the other samples' value. With it missing from every sample the key's `tool_choice` is `None`. A log with `skin` missing from one sample raises `ValueError` naming the field | [runs](runs.md#result-key) |
| AR14 | On the fixture, where `own_scale`, `warm_up` and `inertia` are NA on every row, `mean_over_epochs`, `scenario_scores` and `headlines` lose no row and give one group per key | [runs](runs.md#types) |
| AR15 | Two logs that differ only in `harness_version` and hold the same ids both load, as two result rows | [runs](runs.md#comparing-settings) |
| AR16 | An edited log with every sample removed, beside a fixture log: `load_runs` loads the other log and the report says `Skipped <name>, it holds no samples`. The command on the empty log alone returns 0 and prints that line | [runs](runs.md#discovering-logs) |
| AR17 | Edited logs at `a/x.eval` and `b/x.eval`, passed as two files or as the folders `a` and `b`, raise `ValueError` naming both paths | [runs](runs.md#discovering-logs) |
| AR18 | Two edited logs of one key with disjoint ids, one with the `engine_hash` of one scenario changed on every sample, raise `ValueError` naming the scenario and both hashes. Changed on a scenario the other log does not play, they load | [runs](runs.md#one-row-per-run) |

## Scores

| Id | Test | Page |
|---|---|---|
| AS1 | `scenario_scores` on the `mockllm` log equals the log's `scenario_score` metric in `score`, `lo`, `hi`, `n` and `failed` to `1e-9`, and `headlines` equals its `headline` metric in `headline`, `lo` and `hi`, and its `weakest_trait` metric. Each metric is found by its group and name | [scores](scores.md#pooling) |
| AS2 | `baseline/uniform` scores exactly 0 and `baseline/discerning` exactly 1 in every scenario, and the `complacent` mark on `baseline/complacent`'s own log equals its score | [scores](scores.md#invariants) |
| AS3 | `paired_gap(runs, a, a)` has `diff == lo == hi == 0` on every row. `paired_gap(runs, discerning, uniform)` has `diff == 1` with `lo == hi == 1`. Two keys with different `seed_set`, or one scenario's `engine_hash` differing between them, raise `ValueError` | [scores](scores.md#paired-gap) |
| AS4 | `scenario_gap` on `baseline/complacent` between No change and Down switch is `1 − complacent's Down switch score`, within the bar | [scores](scores.md#scenario-gap) |
| AS5 | `switch_kinds` on the public fixture has a `switch_kind` column that equals the `kind` of the first switch `Event` of `make_timeline` on each seed, `rise_short` where its `short` is 1 and `none` for No change, and no `kind` column. On the held-out fixture it returns a switch kind per row and writes no file. On a log played at `inertia=10` the hash check passes | [scores](scores.md#switch-kinds) |
| AS6 | `noise_threshold` on edited logs whose headlines follow `h(x)` at `x0 = log(2)`, `k = 2` and a Complacent headline of 0.55, over five settings, recovers `snr` within 2%, `snr_80` within 5% and `k` within 10%, with `status == "crossed"`, `settings == 5`, `complacent == 0.55`, `complacent_drift == 0` and `key` the key passed. Headlines all above the half way mark give `"off the noisy end"`, all below give `"off the quiet end"`, each with `snr is None` and `k is None`. Two settings raise `ValueError`, as do two rows at one `own_scale` | [scores](scores.md#noise-threshold) |
| AS7 | `signal_points(scenario_config("down_switch"))` is the midpoint of its `SwitchSpec.size_points`, and `scenario_config("no_change")` raises `ValueError` | [scores](scores.md#noise-threshold) |
| AS8 | `sampling_share` on a two-epoch table is 0 when every seed's epochs are equal and 1 when every seed's mean is equal and epochs differ | [scores](scores.md#spread-and-sampling-share) |
| AS9 | `spread` on five seeds has `sd` equal to `numpy.std(ddof=1)` and `p10` to `numpy.percentile(10)`, and NA on one seed | [scores](scores.md#spread-and-sampling-share) |
| AS10 | An edited log with one gave up run has `†` in that scenario's `flags` and in the headline's. A `retry_share` of 0.2 gives `‡`. A `recognition` table with 2 of the model's 6 `round_1` and `round_20` rows at `lint_hits > 0`, beside 3 `canary` rows, gives `§` on every row, as the share is a third and not two ninths. One with `canary_finished` true gives `¶` on every row | [scores](scores.md#flags) |
| AS11 | `public_gap(runs, key)` on two result rows that differ only in `seed_set` returns a row per scenario plus `headline`, the same from either row's key. It raises `ValueError` naming `skin` when the skins differ, and naming `held-out` when the model has public rows alone | [scores](scores.md#public-gap) |
| AS12 | `load_recognition` on a CSV with a `reply` column returns `model`, `skin`, `probe`, `lint_hits` and `canary_finished` only, and the reply text is in no cell. Every gap function returns `GAP_COLUMNS` | [scores](scores.md#flags) |
| AS13 | `notes_share` on a table with `notes_rounds` 4 and 0 over `rounds` 40 and 40 is 0.05, and `compute_share` with `compute_rounds` 0 and 0 is 0 | [scores](scores.md#scenario-scores) |
| AS14 | On four edited logs whose headlines sit so close to the half way mark that some draws miss it, `uncrossed_draws` is above 0 and `lo ≤ snr ≤ hi` over the rest | [scores](scores.md#noise-threshold) |

## Tables

| Id | Test | Page |
|---|---|---|
| AT1 | `write_results` on the fixture writes `<name>.md` titled `# Results: <name>`, with the stamp naming the logs' `harness_version`, the twelve columns in order, one row per result row in models file order with provider rows first, and a legend naming `†` when a run gave up | [tables](tables.md#the-scores-table) |
| AT2 | The CSV has exactly `CSV_COLUMNS`, one row per scored run, `seed` filled on public rows and blank on held-out rows, and no `output` column | [tables](tables.md#the-run-csv) |
| AT3 | `write_results` twice on the same table gives byte-identical `.md` and `.csv`, and the same bytes again after a line is appended to `<name>.md` between runs | [tables](tables.md#invariants) |
| AT4 | On the held-out fixture, with a `recognition` table built from a CSV holding a planted reply string, no file written holds any of the three seed values, the reply string, a reading, a channel name of the example skin or any run of five words from its `intro` | [tables](tables.md#invariants) |
| AT5 | `pooled_score` over the CSV's `gain` and `gap` per scenario equals the page's score to two decimals, and the shares of its `notes_rounds`, `compute_rounds` and `rounds` equal the `Tools` cell | [tables](tables.md#invariants) |
| AT6 | `write_cost` on the `mockllm` log has the columns in the table, `skin` among them, zero usage on a baseline row, `projected` set when `models` and `seeds` are given, a `cost` column only with a `prices` file, and prints nothing. On an edited log with 100 `input_tokens`, 300 `cache_read_tokens` and 0 `cache_write_tokens` a run, `cached_share` is 0.75, and `cost` with a `cache_read` price is lower than with none. On a log at two epochs `runs` counts both and `input` is one epoch's tokens | [tables](tables.md#cost) |
| AT7 | Two logs of one model that differ only in `tools` give two sections, each heading naming the knob that is off its default, in the stated order. Two that differ only in `release` give two headings that each name their `release`. A `name` of `../x` raises `ValueError` and writes nothing | [tables](tables.md#headings-and-file-names) |
| AT8 | Two logs of one model on the same seeds, a fixture log at `tools="none"` and an edited copy whose `tools` reads `notes,compute`: the page has a sensitivity table with one row whose `Knob` is `tools none`, the fixture log's headline, and a gap equal to `paired_gap`'s `headline` row, the copy minus the fixture log. With one log alone there is no such table | [tables](tables.md#the-cross-setting-tables) |
| AT9 | Two logs of `baseline/complacent` on the same seeds, one on `example` and one on a copy of it under the stem `b`, with `PARANOID_SKINS` at the temp folder that holds the copy: the page has two sections and a skin sensitivity table with one row, `Skins` reading `b − example` and every `diff` 0. On two edited logs whose run scores differ, each cell equals `paired_gap`'s row for that scenario and for `headline`. With one log alone there is no such table | [tables](tables.md#the-cross-setting-tables) |
| AT10 | Four edited logs of one model that differ only in `own_scale`, with headlines that straddle the half way mark: the page has one noise threshold section with one row, whose `Threshold` cell equals `noise_threshold`'s `snr`, `lo` and `hi` to one decimal and whose `Settings` cell is 4, and with `plots` on a `<curve slug>-noise.svg`. With two edited logs of a second model beside the four, the second has no row and the line under the table names it and `2` | [tables](tables.md#the-noise-threshold-table) |
| AT11 | Two logs of one model that differ only in `tools`: grouping the CSV by `model`, `reasoning` and every `Setting` column gives two groups, each with the rows of one section on the page. Two logs that differ only in `release` give two sections | [tables](tables.md#the-run-csv) |
| AT12 | The `Weakest trait` cell of every row equals the trait of its lowest scenario, then that scenario's score and bar as they stand in its own column | [tables](tables.md#the-scores-table) |
| AT13 | A public log and a held-out log of one model: the page has a public gap table with one row, each cell equal to `public_gap`'s row. With the public log alone there is no such table | [tables](tables.md#the-cross-setting-tables) |
| AT14 | Every section has a `### Marks` table whose `Complacent` column equals `scenario_scores`' `complacent` mark, and a `### Spread` table equal to `spread`. On a log at two epochs the spread table has the sampling share | [tables](tables.md#the-scores-table) |
| AT15 | Edited logs with a `retry_share` of 0.2, a `recognition` table that sets `§` and one that sets `¶` each give a legend naming that flag and no other | [tables](tables.md#the-scores-table) |
| AT16 | `write_results` with `dry_run` writes nothing and returns the paths a real run then writes. With `plots` on, a models file that has an `eci` and no `eci_read_on`, it raises `ValueError` and writes nothing. With a models file that has no `eci` at all, no `-trend-eci.svg` is written | [tables](tables.md#the-results-page) |
| AT17 | Two logs of one model that differ only in `harness_version` share one section, each `Model` cell ends ` at <its version>`, and the versions line lists both. Two rows of one model at `low` and `high`, with `plots` on, give two strip plots with different names | [tables](tables.md#the-scores-table) |
| AT18 | Two logs in one section, each with one errored sample on a different seed: every `### Marks` cell equals the `complacent` mark of `scenario_scores` on the untouched fixture, so neither errored seed loses its mark | [tables](tables.md#the-scores-table) |
| AT19 | `markdown_table` with a cell holding a pipe and one holding a line break writes the pipe after a backslash and the break as a space, and every line of the table has the same number of unescaped pipes | [tables](tables.md#invariants) |

## Plots

| Id | Test | Page |
|---|---|---|
| AP1 | Each of the four plot functions writes an SVG that parses as XML, and twice on the same inputs gives equal bytes | [plots](plots.md#every-plot) |
| AP2 | The ECI trend plot's SVG contains `Epoch AI`, `CC BY 4.0` and the date passed, and the title of a strip plot contains the skin name and seed set and no seed value | [plots](plots.md#trend-plots) |
| AP3 | `trend_plot` with `x="eci"` and no `eci_read_on` raises `ValueError`. A model row with no `eci` is named in the footer and has no point | [plots](plots.md#trend-plots) |

## Pilot

Engine sections read hand-built CSVs with their cell's columns. Provider sections read edited logs placed under `<logs>/<cell>/`.

| Id | Test | Page |
|---|---|---|
| AI1 | `write_pilot` on an empty folder writes `results.md` with every heading in `SECTIONS` and `_Not run yet._` under each, and no other file. `SECTIONS` equals the headings of the repo's pilot results page. With `dry_run` it writes nothing | [pilot](pilot.md#writing-the-page) |
| AI2 | With a hand-built `baseline-order.csv`, the Baseline order section has one row per scenario and baseline, an order line that holds, and a `**bold**` line for a planted break. Its files are `baseline-order-outputs.csv` and `baseline-order-orders.csv`. Every section but Baseline order and Reachable gain still reads `_Not run yet._` | [pilot](pilot.md#sections) |
| AI3 | With a hand-built `recognition.csv` holding a reply column, the section's table has counts and shares over the `round_1` and `round_20` rows, and the reply text appears nowhere in the page or its CSV | [pilot](pilot.md#sections) |
| AI4 | An existing `results.md` with one heading renamed raises `ValueError` naming it, and the file is unchanged | [pilot](pilot.md#writing-the-page) |
| AI5 | With an `up-against-down` log of four Up switch runs, two edited to a `sleeper_round` of 9 and 13 and two to 0, the `sleeper` table reports a share of 0.5 and a median of 11. With a `seeds` log beside it that holds the same Up switch ids, the section loads without a duplicate error and its `gaps` table has the One shock against Down switch row | [pilot](pilot.md#reading-the-inputs) |
| AI6 | With a hand-built `channel-order.csv` of twelve rows for one model, ten valid, two of those with `slipped` 1 and one with neither `matched` nor `slipped`, the Channel order section reports a valid share of 10 in 12, a slip share of 0.2 and an own numbers share of 0.1 | [pilot](pilot.md#sections) |
| AI7 | With a hand-built `baseline-order.csv` whose Up switch scenario has a reachable gain of 0.2 and whose Down switch scenario has a Bayesian gain percentage of 40%, the Reachable gain section has one row per scenario with a switch or drift and a `**bold**` line for each of the two breaks. Its Up switch then down switch row reads its gains from the `stayer` rows, not `complacent`, and a `bayesian` move share of 0.4 there breaks the third line | [pilot](pilot.md#sections) |
| AI8 | Weather: a `tell.csv` of ten One shock seeds, eight with `fall_rounds` 2 and `tell_rounds` 2, one with 2 and 1 and one with 0 and 0, gives a hit rate of 8 in 9 and a never fired share of 0.1. A `luck.csv` with pooled outputs 130, 120 and 100 gives 0.5 | [pilot](pilot.md#sections) |
| AI9 | Seeds and repeats: with a `seeds` log whose widest `sd` is edited to 0.2, `seeds-needed` names that row and scenario and reads 24 at a target of 0.05. With a `repeats` log beside it that shares ten ids, both load and `sampling-share` has a row | [pilot](pilot.md#reading-the-inputs) |
| AI10 | Noise: a `noise-grid.csv` where `complacent`'s output is half way from `uniform`'s to `discerning`'s at one setting gives a score of 0.5 there, with signal to noise as `signal_points` over the setting | [pilot](pilot.md#reading-the-inputs) |
| AI11 | Game length: a `game-length.csv` of four seeds with `clear_round_1` at onset plus 2, 4 and 6 and one at 0 gives a median of 4 rounds and a never share of 0.25 | [pilot](pilot.md#sections) |
| AI12 | Reading roughness: a `reading-roughness.csv` whose No change `complacent` rows sum to 1000 and whose `hedge_rule` rows at `explore` 2 sum to 950 gives an explore cost of 50 over the seeds | [pilot](pilot.md#sections) |
| AI13 | Up and down: an `up-and-down.csv` with three `fall` seeds and one `fall_and_rise` on Down switch gives those seed counts per kind, and a reachable gain as a score of 1 minus the `complacent` score | [pilot](pilot.md#sections) |
| AI14 | Bayesian frontier: a `bayesian-frontier.csv` with seeds 0, 1, 500 and 501, in which one player has the best headline on the lower half, seeds 0 and 1, names that player in `pick`, with an irreducible lag of one minus its Down switch score on the upper half | [pilot](pilot.md#sections) |
| AI15 | Jev checks: a `jev.csv` of ten rounds, three with `rounded_out` 2, gives a mean of 0.6 and a share of 0.3 | [pilot](pilot.md#sections) |
| AI16 | Timestral checks: a `timestral.csv` with a `determinism` row at `equal` 0 shows it, and `timestral-grid.csv` joined to `noise-grid.csv` puts a policy's score beside the two marks | [pilot](pilot.md#sections) |
| AI17 | Bare harness: four `bare` logs of one model, one per `tools` value, give a `gaps` table of three rows, each equal to `paired_gap` against the `notes,compute` row | [pilot](pilot.md#sections) |
| AI18 | Tool choice: two `tool-choice` logs, the `auto` one edited to `no_calls` 4 over `rounds` 40, give a no call share of 0.1 beside it and a `gaps` row of `auto` minus `any` | [pilot](pilot.md#sections) |
| AI19 | Rolling conversation: two `rolling` logs and a `rolling-tokens.csv` whose rolling rows grow by 100 `input_tokens` a round give a `tokens` table with a mean per round for each, and a `gaps` row that says whether the bar clears zero | [pilot](pilot.md#sections) |
| AI20 | Warm up: two `warm-up` logs, the pre-filled one edited to `warm_up_kept` 1 on half its runs, give a mean of 0.5 beside it and NA beside the empty one | [pilot](pilot.md#sections) |
| AI21 | Cost per run: `seeds` and `repeats` logs give a `cost` table with a row per result row and cell, equal to `write_cost` on each folder, with the retry share | [pilot](pilot.md#sections) |
| AI22 | A `luck.csv` with a column its cell does not write raises `ValueError` naming the file and the column. With `main` holding two models' logs the `inertia` table has one row for the pair, and without it the section says `_Inertia needs --main._` | [pilot](pilot.md#reading-the-inputs) |
| AI23 | Every CSV column a section reads is named in that cell's Writes line in the [harness pilot spec](../harness/pilot.md), read from the page itself | [pilot](pilot.md#invariants) |
| AI24 | Timestral checks: a `noise-grid.csv` of 30 seeds and a `timestral-grid.csv` of 20 of them give a `grid` table whose `hedge_rule` and `complacent` rows have `seeds` 20, and scores pooled on those 20 alone | [pilot](pilot.md#sections) |
| AI25 | Up against down: the `up-against-down` folder holding logs of two models gives `kinds` and `sleeper` tables with a `model` column and each model's own rows, each equal to that model's log read alone | [pilot](pilot.md#sections) |
| AI26 | Up and down: a player whose `move_round` is 0, 4 and 8 on three seeds has a `median_move_round` of 6, and one that never moved has none | [pilot](pilot.md#sections) |
| AI27 | A `baseline-order.csv` of 20 output rows shows the first 15 on the page, says `15 of 20 rows shown` on the link line, and writes all 20 to the CSV | [pilot](pilot.md#writing-the-page) |

## Command

| Id | Test | Page |
|---|---|---|
| AM1 | The harness's `main(["analyse", "--dry-run", <fixture>])` returns 0, prints the report and the paths it would write, and writes nothing | [command](command.md#dispatch) |
| AM2 | `analyse([<fixture>, "--out", tmp, "--name", "t"])` writes `t.md` and `t.csv` under `tmp` and nothing elsewhere, the bare form being `results` | [command](command.md#results) |
| AM3 | `analyse(["gap", <discerning log>, <uniform log>])` prints a table with `diff == 1` on every scenario row. With a log that holds two result rows it returns 1 with a message naming the log. With two logs of one key it returns 1 with a message naming the key | [command](command.md#gap) |
| AM4 | `analyse(["cost", <fixture>])` reads `configs/prices.toml`, prints a `cost` column and the date the prices were read on, and returns 0. With that default patched to a path that is not there it prints the cost columns without `cost`, says no prices were found, and returns 0. `configs/prices.toml` has a `read_on` date and a price for every `llm` row in `configs/models/poc.toml`, each with a cache read price below its input price. With `--prices /nope` it returns 1. `analyse(["results", "/nope"])` returns 1 and prints a message | [command](command.md#cost) |
| AM5 | Every subcommand runs with the network blocked by a socket monkeypatch and no key in the environment | [command](command.md#invariants) |
| AM6 | `--name ../x` returns 1 and writes nothing. `--plots` with a models file that has `eci` and no `--eci-read-on` returns 1 and writes nothing | [command](command.md#results) |
| AM7 | `analyse(["pilot", "--logs", <folder with a baseline-order.csv>, "--out", tmp])` writes `results.md` and the two sections' CSVs under `tmp` and returns 0. With `--dry-run` it prints the same paths and writes nothing | [command](command.md#pilot) |
| AM8 | `paranoid.analysis.__all__` equals the names in the README's Exports table, read from the page itself | [README](README.md#exports) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| AY1 | For any table of positive gaps and finite gains over two scenarios, `pooled_score` over the CSV `write_run_csv` writes equals `scenario_scores` on the table, and `paired_gap(a, a)` is zero |
| AY2 | For any headlines on a logistic curve with a Complacent headline in `[0.4, 0.7]`, `k` in `[0.5, 4]` and `x0` inside the grid, `noise_threshold` returns `crossed` with `lo ≤ snr ≤ hi` |
| AY3 | For any model, skin and scenario strings that pass the [guards](runs.md#guards), every file name `write_results` builds from them resolves under `out` |

## Not decided

- Whether the fixture logs should be built once and committed under `tests/analysis/logs/`, so the suite needs no inspect run. They are built per session here, as a committed log goes stale with every harness change. Decide when the suite's run time is known.
