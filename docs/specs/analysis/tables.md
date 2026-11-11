# Tables

## Purpose

`write_results` writes the results page and the run CSV beside it, from the run table. `write_cost` builds the cost table the [cost check](../../pilot/provider-checks.md#cost-per-run) reads. Every number on a page is in the CSV or follows from it by `pooled_score`, so a reader can check our work from the CSV alone. The design is in [scoring](../../design/scoring.md#how-we-score) and [contamination](../../harness/contamination.md#public-and-held-out).

## Interface

```python
def write_results(runs: pd.DataFrame, out: Path, name: str, *, models: Path | None = None,
                  recognition: pd.DataFrame | None = None, plots: bool = False,
                  eci_read_on: date | None = None, dry_run: bool = False) -> list[Path]
# runs as load_runs gives it. Writes out/<name>.md, out/<name>.csv and, with plots, out/<name>/*.svg.
# Returns what it wrote, or with dry_run what it would write

def write_run_csv(runs: pd.DataFrame, path: Path) -> None

CSV_COLUMNS: tuple[str, ...]           # see The run CSV

def write_cost(runs: pd.DataFrame, *, models: Path | None = None, seeds: int | None = None,
               prices: Path | None = None) -> pd.DataFrame
# runs as load_runs gives it. Returns the table and writes nothing
```

## Behaviour

### The results page

`out/<name>.md`. The [proof of concept page](../../results/poc.md) holds a hand-written stand-in until its first run rewrites it.

- **`name` is a bare file stem.** A `name` with a path separator or `..` raises `ValueError`, so nothing lands outside `out`.
- **`write_results` averages epochs first** with [`mean_over_epochs`](runs.md#mean-over-epochs), and keeps the table it was given for the sampling share.
- **`dry_run` writes nothing.** It builds every table, so it raises what a real run would, and returns the paths a real run would write.
- **`eci_read_on`** is the date on the ECI plot's credit, see [trend plots](plots.md#trend-plots). With `plots` on, a `models` file that has an `eci` value and no date, `write_results` raises `ValueError` before it writes anything.
- **The page is never read before it is written**, so the output depends on the logs alone.

### Page outline

The page has these parts, in this order. A part with no rows is left out.

| Part | Heading | What it holds |
|---|---|---|
| Header | `# Results: <name>` | A fixed template in the code: a line saying the page is written by `paranoid analyse` and never edited by hand, then three bullets that hold on any page. One table per setting and a skin is its name only. Scores run from the Uniform baseline at 0 to the Discerning baseline at 1, with the headline their plain mean. `Tools` is how often each tool was used |
| Stamp | None | `Written by paranoid analyse from <n> logs at harness version <v> on <date>, see <name>.csv.` Then, when any sample errored, `<k> samples errored and are in no score.` |
| One section per setting | `## <setting heading>` | The versions line, the scores table, its legend, then `### Marks` and `### Spread`, then links to that setting's plots |
| Sensitivity | `## Sensitivity` | One table, see below |
| Public gap | `## Public gap` | One table |
| Skin sensitivity | `## Skin sensitivity` | One table |
| Noise threshold | `## Noise threshold, <curve heading>` | One section per curve, each with its table, the line naming models left out, and a link to its plot |

- **The stamp's `v`** is the logs' `harness_version`, each listed when they differ, never the installed package's. The date is the latest `started` among the logs, not today, so a rerun on the same logs gives the same bytes.
- **One section per setting**, with `harness_version` left out as [comparing settings](runs.md#comparing-settings) says. Skins, seed sets and noise settings are never pooled, see [spread](../../design/scoring.md#spread).
- **Sections are ordered** by `skin`, then `seed_set` with public first, then `own_scale` with the default first and the rest rising, then each later field of `Setting` in its order, a default before any other value.

### Headings and file names

- **A setting's heading** names the skin and the seed set, then every knob off its default, then each of `prompt_hash`, `generator_version` and `release` in which two settings on the page differ. Parts are joined by `, `. So no two sections share a heading, and two rows that differ only in a knob never share a label.

| Field | Default | In a heading when off it |
|---|---|---|
| `own_scale` | Unset | `own_scale 4.0` |
| `game_rounds` | The engine's `rounds`, from `SCENARIOS` | `rounds 20` |
| `tools` | `notes,compute` | `tools none` |
| `warm_up` | Unset | `warm_up complacent:5` |
| `rolling` | False | `rolling` |
| `tool_choice` | `any` | `tool_choice auto` |
| `inertia` | Unset | `inertia 10` |
| `prompt_hash`, `generator_version`, `release` | None. Named only where two settings differ | `prompt_hash 3fa29c01`, the first eight characters, `generator_version 2`, `release r1` |

- **The versions line** under a heading gives `prompt_hash`, `generator_version`, `release` and every `harness_version` among the section's rows. The skin is its name only.
- **A curve heading** is the heading of a curve's settings without the `own_scale` part, see [noise threshold](#the-noise-threshold-table).
- **A slug** is a heading or a row's label in lower case, with every run of characters outside `[a-z0-9._]` as one `-`, and none at either end. `example, public, tools none` gives `example-public-tools-none`.
- **Plots** go under `out/<name>/`, and the page links each from its section, see [plots](plots.md).

| Plot | File | Written |
|---|---|---|
| Strip | `<setting slug>-strip-<row slug>.svg` | Once per result row |
| Profile | `<setting slug>-profile.svg` | Once per setting |
| Trend | `<setting slug>-trend-released.svg` and `<setting slug>-trend-eci.svg` | Once per setting when `models` is given, each only when it has a point |
| Noise | `<curve slug>-noise.svg` | Once per noise threshold table |

- **Every part of a file name is a guarded string**, see [guards](runs.md#guards), so no name holds a path step. Two files that would share a name raise `ValueError` naming both rows, before anything is written.

### The scores table

One row per result row and twelve columns: `Model`, the eight scenarios in `SCENARIOS` order under their design names, `Headline`, `Weakest trait`, `Tools`.

- **`Model` is the row's label**: the model string, then the reasoning setting in parentheses when it is not `n/a`, such as `anthropic/claude-haiku-5-5 (low)`. When two rows of a table would share a label, as they differ in `harness_version` alone, each ends with ` at <harness_version>`.
- **A scenario cell** is the score to two decimals, the bar in brackets, then the flags: `0.76 [0.71, 0.80] †`.
- **`Headline`** is the same shape. `Weakest trait` is the trait's name, then its scenario's score and bar: `Patience 0.41 [0.35, 0.47]`. The bar is the scenario's own, copied, so the cell never disagrees with the column it came from. When two scenarios tie to two decimals the first in `SCENARIOS` order is named.
- **`Tools`** is the two tool use shares over the row's runs, `notes 0.40, compute 0.95`, so the page shows whether a model used what it was given. Empty on a provider row and on a row at `tools none`.
- **A result row that did not play a scenario** has an empty cell, and its headline says how many scenarios it averages: `0.70 [0.66, 0.74] of 3`.
- **Row order** follows the models file when `models` is given: provider rows first, then LLM rows in file order, each setting in the row's `reasoning` order, as [`run`](../harness/command.md#run) runs them. A result row not in the file goes at the end, by headline. Without a file, headline descending. A tie goes to the label, in string order.
- **The legend** under the table names every flag used, with counts: `† 3 runs gave up and scored as the Uniform baseline. ‡ Retry share over 0.1. § Recognised the prompt on over a quarter of probes. ¶ Finished the canary, see recognition.` A flag no row carries is left out.
- **`### Marks`** has one row per scenario: the pooled scores of the Complacent, hedge rule, Scout rule and Perfect baselines on the seeds the table scored. The Uniform baseline is 0 and the Discerning baseline 1 by construction, so neither is a column.
- **`### Spread`** has `sd` and `p10` per result row and scenario, and the sampling share when the logs have epochs, see [spread and sampling share](scores.md#spread-and-sampling-share).

### The cross setting tables

Each compares two result rows of one model and reasoning setting, so each has a `Model` column and a `Setting` column holding the heading of the first row's section. Rows go in section order, then the scores table's order.

- **The sensitivity table** has a row wherever a model has two result rows that differ in one of `tools`, `rolling` and `tool_choice` and in nothing else, the first at that knob's default in the table above.
  - The columns are `Model`, `Setting`, `Knob` as a heading names it, such as `tools none`, the second row's headline with its bar, and the `headline` row of the [paired gap](scores.md#paired-gap), the first row minus the second.
  - The row at `tools none` is the bare gap, see [bare harness](../../pilot/provider-checks.md#bare-harness).
  - Nothing is picked: every model plays the same headline setting, and this table says what each knob did for it.
  - The second row keeps its own section too.
- **The public gap table** has a row wherever [`public_gap`](scores.md#public-gap) finds a public row its held-out partner: public minus held-out per scenario and headline, with its interval.
- **The skin sensitivity table** has a row wherever a model has two result rows whose settings differ in `skin` and in nothing else but `prompt_hash`.
  - The columns are `Model`, `Setting`, `Skins` as `<a> − <b>`, then the eight scenarios and `Headline`.
  - Each cell is the `diff` of the [paired gap](scores.md#paired-gap) with its interval, `a`'s row minus `b`'s.
  - Pairs go in name order, so two skins give one row and three give three.
  - Skins are names only, and the table says which story swayed a model, never why, see [spread](../../design/scoring.md#spread).
- **A model with two candidates for one side**, as they differ in `harness_version` alone, has no row in these three tables, and a line under the table names it and both versions.

### The noise threshold table

Written when any model has three or more result rows that differ only in `own_scale`, see [noise threshold](scores.md#noise-threshold). It is the full study's headline, and [`run --own-scale grid`](../harness/command.md#run) writes the logs it needs. A curve is the settings that are equal in every field but `own_scale`, and each curve gets a section. One row per model and reasoning setting, in the scores table's order:

| Column | What it shows |
|---|---|
| `Model` | As in the scores table |
| `Threshold` | `snr` with its bar, `2.1 [1.7, 2.6]`, or the `status` when the model is off the grid. With `uncrossed_draws` above 0 the cell ends `, <n> of 1000 draws off the grid` |
| `At 80%` | `snr_80` |
| `Own-weather scale` | `own_scale` at the threshold, to read against the grid |
| `Complacent` | `complacent`, then `complacent_drift` in brackets as `±` |
| `Settings` | `settings`, how many grid settings the row was fitted on |

- **A model with fewer than three settings has no row**, and a line under the table names it and how many it has. So does one `noise_threshold` raised for, with the reason.
- **The noise plot** is drawn once per table, from the same `Threshold`s.

### The run CSV

`out/<name>.csv`, one row per run, in `CSV_COLUMNS` order. Sorted by the key fields, then `scenario`, then `seed_index`, NA first, so the file is stable.

| Column | From |
|---|---|
| `model`, `reasoning`, `skin`, `scenario`, `seed_set`, `seed_index` | The run table |
| `seed` | The seed value for a public seed, blank for a held-out one |
| `run_score`, `gain`, `gap` | The score and the two numbers that pool it, averaged over epochs |
| `epochs` | How many epochs the row averages |
| `gave_up`, `retry_rounds`, `rounds`, `cut_offs` | The counts behind the flags |
| `notes_rounds`, `compute_rounds` | The counts behind the `Tools` column |
| `own_scale`, `game_rounds`, `tools`, `warm_up`, `rolling`, `tool_choice`, `inertia` | The noise setting and the knobs. `game_rounds` is the game length, where `rounds` above is how many the agent played, see [result key](runs.md#result-key) |
| `engine_hash`, `prompt_hash`, `generator_version`, `harness_version`, `release` | The versions |
| `log` | The log's path, as the run table has it |

- **Every field of `Setting` is a column**, so the rows of one section on the page are the CSV rows that share those columns, and a reader can rebuild any table from the file alone. Two settings that differ only in a knob never collapse into one.
- **One score per run, and the two numbers that pool it.** `gain` and `gap` are what `pooled_score` needs to rebuild every score on the page, and together they say nothing about any round. The run's `output` and the baselines' outputs stay out, so the CSV holds no total that could place a timeline, see [who can see them](../../harness/contamination.md#who-can-see-them).
- **Errored rows are left out.** The page's stamp counts them.
- **Written with `lineterminator="\n"`, no index, floats as `repr`, booleans as `1` and `0` as the pilot CSVs write them, NA as an empty cell**, so the same table gives the same bytes on every machine.

### Cost

`write_cost` returns one row per result row, for the [cost check](../../pilot/provider-checks.md#cost-per-run). It writes and prints nothing. The [command](command.md#cost) prints it and the [pilot](pilot.md#sections) writes it.

| Column | What it is |
|---|---|
| `model`, `reasoning`, `kind`, `skin` | The row. `skin` keeps a model's two skins apart |
| `runs` | Rows scored, one per epoch of each sample |
| `input`, `cache_read`, `cache_write`, `output`, `reasoning_tokens` | Mean tokens per run. `input` is the tokens billed in full, so the three input columns add up to what the model read |
| `cached_share` | `sum(cache_read) / sum(input + cache_read + cache_write)`, see [prompt caching](../../harness/models.md#prompt-caching). Near 0 on a provider that caches means the cache is missing |
| `cut_off_share` | `sum(cut_offs) / sum(rounds)`, see [sampling](../../harness/models.md#sampling) |
| `projected` | Mean tokens per run of each of the four kinds × `seeds` × eight scenarios × the row's settings in `models`, when both are given. One result row is one skin, so a model's skins are separate rows and the table's total counts each |
| `cost` | `projected` priced from `prices`, each kind at its own price. The column is there only when `prices` is given |

- **It takes the table with one row per epoch**, as `load_runs` gives it. An epoch is a run, and [`mean_over_epochs`](runs.md#mean-over-epochs) sums tokens over epochs, so a mean taken after it would be several runs' tokens.
- **`prices`** is a TOML file of `[[price]]` tables with `id`, `input`, `output`, `cache_read` and `cache_write` per million tokens, and a top-level `read_on` date. A missing `cache_read` or `cache_write` is priced as `input`, so a forgotten cache price overstates the cost and never understates it. A row with no price has an empty `cost`. The date is in the table's `attrs["read_on"]`, for whoever prints it.
- **Provider rows** have zero usage, see [shared behaviour](../harness/providers.md#shared-behaviour), so their `projected` is 0 and they appear for completeness only.

## Invariants

- `write_results` twice on the same table writes byte-identical files, and the files do not depend on what was in `out` before.
- Every scenario score on the page equals `pooled_score` over the CSV's `gain` and `gap` for that model, setting and scenario, to the two decimals shown. Every `Tools` cell equals the shares of the CSV's `notes_rounds`, `compute_rounds` and `rounds`.
- No written file holds a held-out seed's value, an output, a reading, a message, a recognition reply or any skin text. `seed` is blank on every held-out row.
- Every path `write_results` writes is under `out`, no two share a name, and with `dry_run` there are none.
- `CSV_COLUMNS` is a subset of `RUN_COLUMNS` plus nothing. It holds `model`, `reasoning` and every field of `Setting`, so grouping the CSV by them gives the page's result rows.

## Not decided

- Whether the page should show the 10th percentile run beside each score, as [spread](../../design/scoring.md#spread) suggests, or leave it to the spread table as here. Decide when the first page is read.
