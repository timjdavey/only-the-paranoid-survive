# Tables

## Purpose

`write_results` writes the results page and the run CSV beside it, from the run table. `write_cost` writes the cost table the [cost check](../../pilot/provider-checks.md#cost-per-run) reads. Every number on a page is in the CSV or follows from it by `pooled_score`, so a reader can check our work from the CSV alone. The design is in [scoring](../../design/scoring.md#how-we-score) and [contamination](../../harness/contamination.md#public-and-held-out).

## Interface

```python
def write_results(runs: pd.DataFrame, out: Path, name: str, *, models: Path | None = None,
                  recognition: pd.DataFrame | None = None, plots: bool = False) -> list[Path]
# runs as load_runs gives it. Writes out/<name>.md, out/<name>.csv and, with plots, out/<name>/*.svg.
# Returns what it wrote

def write_run_csv(runs: pd.DataFrame, path: Path) -> None

CSV_COLUMNS: tuple[str, ...]           # see The run CSV

def write_cost(runs: pd.DataFrame, *, models: Path | None = None, seeds: int | None = None,
               prices: Path | None = None) -> pd.DataFrame
```

## Behaviour

### The results page

`out/<name>.md`, the shape already on [proof of concept results](../../results/poc.md).

- **`name` is a bare file stem.** A `name` with a path separator or `..` raises `ValueError`, so nothing lands outside `out`.
- **`write_results` averages epochs first** with [`mean_over_epochs`](runs.md#mean-over-epochs), and keeps the table it was given for the sampling share.
- **The header** is a fixed template in `tables.py`: the title and intro bullets as on the proof of concept page. The page is never read before it is written, so the output depends on the logs alone. Under the header one line: `Written by paranoid analyse from <n> logs at harness version <v> on <date>, see <name>.csv.` `v` is the logs' `harness_version`, each listed when they differ, never the installed package's. The date is the latest `started` among the logs, not today, so a rerun on the same logs gives the same bytes.
- **One table per `Setting`**, see [runs](runs.md#interface). Skins, seed sets and noise settings are never pooled, see [spread](../../design/scoring.md#spread), and two rows that differ only in a knob must not share a label. The heading names the skin and seed set, then the noise setting and any knob off its default, such as `example, public, tools none` or `example, public, tool_choice auto`. Under it one line gives `prompt_hash`, `generator_version` and `harness_version`. The skin is its name only.
- **The scores table** has one row per result row and the twelve columns on the proof of concept page: `Model`, the eight scenarios in `SCENARIOS` order under their design names, `Headline`, `Weakest trait`, `Tools`.
  - `Model` is the model string, then the reasoning setting in parentheses when it is not `n/a`, such as `anthropic/claude-haiku-5-5 (low)`.
  - A scenario cell is the score to two decimals, the bar in brackets, then the flags: `0.76 [0.71, 0.80] †`.
  - `Headline` is the same shape. `Weakest trait` is the trait's name and its score: `Patience 0.41`.
  - `Tools` is the two tool use shares over the row's runs, `notes 0.40, compute 0.95`, so the page shows whether a model used what it was given. Empty on a provider row and on a row at `tools none`.
  - A result row that did not play a scenario has an empty cell, and its headline says how many scenarios it averages: `0.70 [0.66, 0.74] of 3`.
- **Row order** follows the models file when `models` is given: provider rows first, then LLM rows in file order, each setting in the row's `reasoning` order, as [`poc`](../harness/command.md#poc) runs them. A result row not in the file goes at the end, by headline. Without a file, headline descending.
- **The legend** under each table names every flag used, with counts: `† 3 runs gave up and scored as the Uniform baseline. ‡ Retry share over 0.1. § Recognised the prompt on over a quarter of probes. ¶ Finished the canary, see recognition.` A flag no row carries is left out.
- **The marks table** follows: one row per scenario, the pooled scores of the Complacent, hedge rule, Scout rule and Perfect baselines on the seeds the table scored. The Uniform baseline is 0 and the Discerning baseline 1 by construction, so neither is a column.
- **The sensitivity table** follows when a model has a second result row that differs from its headline row only in `tools`, `rolling` or `tool_choice`: `Model`, the knob and its value, that row's headline with its bar, and the `headline` row of the [paired gap](scores.md#paired-gap), headline row minus that row. The row at `tools none` is the bare gap, see [bare harness](../../pilot/provider-checks.md#bare-harness). One row per model and knob, nothing picked: every model plays the same headline setting, and this table says what each knob did for it. The second row keeps its own table too.
- **The public gap table** follows when a model has both seed sets: public minus held-out per scenario and headline, with its interval, see [public gap](scores.md#public-gap).
- **The spread table** follows: `sd` and `p10` per result row and scenario, and the sampling share when the logs have epochs, see [spread and sampling share](scores.md#spread-and-sampling-share).
- **Plots**, when asked for, go under `out/<name>/` and the page links each under its table, see [plots](plots.md). A file is `<skin>-<seed_set>[-own<own_scale>]-<plot>[-<model>].svg`, the model string with `/` and `:` as `-`. Every part is a guarded string, see [guards](runs.md#guards), so no name holds a path step.

### The run CSV

`out/<name>.csv`, one row per run, in `CSV_COLUMNS` order, sorted by the key fields then `scenario` then `seed_index`, so the file is stable.

| Column | From |
|---|---|
| `model`, `reasoning`, `skin`, `scenario`, `seed_set`, `seed_index` | The run table |
| `seed` | The seed value for a public seed, blank for a held-out one |
| `run_score`, `gain`, `gap` | The score and the two numbers that pool it, averaged over epochs |
| `epochs` | How many epochs the row averages |
| `gave_up`, `retry_rounds`, `rounds`, `cut_offs` | The counts behind the flags |
| `own_scale`, `engine_hash`, `prompt_hash`, `harness_version` | What the run played |
| `log` | The log's path, as the run table has it |

- **One score per run, and the two numbers that pool it.** `gain` and `gap` are what `pooled_score` needs to rebuild every score on the page, and together they say nothing about any round. The run's `output` and the baselines' outputs stay out, so the CSV holds no total that could place a timeline, see [who can see them](../../harness/contamination.md#who-can-see-them).
- **Errored rows are left out.** The page's header counts them.
- **Written with `lineterminator="\n"`, no index, floats as `repr`**, so the same table gives the same bytes on every machine.

### Cost

`write_cost` returns and prints a table per result row, for the [cost check](../../pilot/provider-checks.md#cost-per-run).

| Column | What it is |
|---|---|
| `model`, `reasoning`, `kind` | The row |
| `runs` | Rows scored |
| `input`, `output`, `reasoning_tokens` | Mean tokens per run |
| `cut_off_share` | `sum(cut_offs) / sum(rounds)`, see [sampling](../../harness/models.md#sampling) |
| `projected` | Mean total tokens per run × `seeds` × eight scenarios × the row's settings in `models`, when both are given |
| `cost` | `projected` priced from `prices`, when given |

- **`prices`** is a TOML file of `[[price]]` tables with `id`, `input` and `output` per million tokens, and a top-level `read_on` date. A row with no price has an empty `cost`. The printed table says the date.
- **Provider rows** have zero usage, see [shared behaviour](../harness/providers.md#shared-behaviour), so their `projected` is 0 and they appear for completeness only.

## Invariants

- `write_results` twice on the same table writes byte-identical files, and the files do not depend on what was in `out` before.
- Every scenario score on the page equals `pooled_score` over the CSV's `gain` and `gap` for that model, setting and scenario, to the two decimals shown.
- No written file holds a held-out seed's value, an output, a reading, a message, a recognition reply or any skin text. `seed` is blank on every held-out row.
- Every path `write_results` writes is under `out`.
- `CSV_COLUMNS` is a subset of `RUN_COLUMNS` plus nothing.

## Not decided

- Whether the page should show the 10th percentile run beside each score, as [spread](../../design/scoring.md#spread) suggests, or leave it to the spread table as here. Decide when the first page is read.
