# Runs

## Purpose

`load_runs` turns a set of `.eval` logs into the [run table](../../glossary.md#scoring): one row per run, with everything the layer needs and nothing a log should not give away. `Setting` says what was played and `ResultKey` says who played it, so together they say which rows belong to one result row. Every other page starts from this table. What a log holds is in [dataset](../harness/task.md#dataset) and [scoring one run](../harness/scorer.md#scoring-one-run).

## Interface

```python
@dataclass(frozen=True)
class Setting:                        # what was played, apart from who played it
    skin: str
    seed_set: Literal["public", "held-out"]
    own_scale: float | None           # None means the frozen default
    game_rounds: int                  # the metadata's `rounds`, the game length. Renamed, see below
    tools: str
    warm_up: str | None
    rolling: bool
    tool_choice: Literal["any", "auto"] | None   # None only when no sample reached round 1, see Result key
    inertia: int | None
    prompt_hash: str
    generator_version: int
    harness_version: str
    release: str                      # the release the log played, see the task spec

@dataclass(frozen=True)
class ResultKey:
    model: str                        # the inspect model string, such as "anthropic/claude-haiku-5-5"
    reasoning: str                    # one of REASONING, "n/a" for a provider, or "unknown", see below
    setting: Setting

RUN_COLUMNS: tuple[str, ...]          # the columns of the run table, in order, see below

def load_runs(paths: Iterable[str | Path]) -> pd.DataFrame      # one row per epoch of every sample
def mean_over_epochs(runs: pd.DataFrame) -> pd.DataFrame        # one row per sample
def result_key(log: EvalLog) -> ResultKey
```

## Behaviour

### Discovering logs

- **`paths`** are files or folders. A folder is searched for `*.eval` recursively. The list is sorted by path, so the same folder loads in the same order on every machine.
- **Each log is read once** with `read_eval_log`. A file that is not an inspect log raises `ValueError` naming it.
- **A log is the `paranoid` task when `log.eval.task` is `paranoid/paranoid`**, the name inspect gives it however it was run, see [checked](#checked). Any other log is skipped and listed in the report, see [the report](#the-report).

### One row per run

The run table has these columns, in this order. `RUN_COLUMNS` holds the names.

| Group | Columns | From |
|---|---|---|
| Log | `log` (the path relative to the folder it was found under, or the file name when given as a file), `started` (the eval's start time) | `log.eval` |
| Key | `model`, `reasoning`, then every field of `Setting` in its order | `result_key(log)` |
| Run | `kind`, `scenario`, `seed_index`, `seed`, `engine_hash`, `numpy_version`, `epoch`, `epochs` | `metadata`, see below |
| Score | every key of `Score.value` in the [scorer's table](../harness/scorer.md#scoring-one-run), in its order: `output`, the six baselines, `gain`, `gap`, `run_score`, `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `gave_up`, `bad_calls`, `no_calls`, `cut_offs`, `notes_rounds`, `compute_rounds`, `unchanged_rounds`, `explore_points`, `sleeper_round`, `warm_up_kept` | `sample.scores["gain"].value` |
| Usage | `input_tokens`, `cache_read_tokens`, `cache_write_tokens`, `output_tokens`, `reasoning_tokens`, `total_tokens`, summed over the sample's model calls | `sample.model_usage` |
| State | `errored` | whether the sample has a score |

- **`kind`** is `log.eval.metadata["kind"]`, which [`run`](../harness/command.md#run) writes. Without it, `baseline`, `jev` or `timestral` when the model string starts with that prefix and a slash, else `llm`. It is the model's kind. A switch's is `switch_kind`, see [switch kinds](scores.md#switch-kinds).
- **`scenario`, `seed_index`, `seed`, `engine_hash`, `numpy_version`** come from `sample.metadata`. `seed` is the metadata's `seed` key for a public sample and NA for a held-out one, see [privacy](#privacy).
- **`engine_hash` is per row, not per key.** It hashes the scenario's config, events included, so one result row has one hash per scenario, see [engine hash](../engine/config.md#engine-hash). `generator_version` is what the key carries, as it is the part of the hash every scenario shares.
- **A sample is named by `sample.id`**, which is `<scenario>/<seed_index>`, see [dataset](../harness/task.md#dataset). The id is what [duplicates](#duplicates) compares and what an error names. It is no column, as `scenario` and `seed_index` already say it.
- **Cached tokens are counted apart.** `cache_read_tokens` and `cache_write_tokens` are inspect's `input_tokens_cache_read` and `input_tokens_cache_write`. A field a provider leaves as `None` is 0. inspect leaves both out of `input_tokens`, so the three add up to what the model read, and a cost from `input_tokens` alone is too low, see [cost](tables.md#cost).
- **One row per epoch.** `epoch` is the sample's epoch and `epochs` how many the sample has. A log at one epoch has `epoch == 1` on every row.

### Types

Every column has one of four dtypes, bar `started`, which is a UTC timestamp. No column has dtype `object` and no cell holds an array.

| Dtype | Columns |
|---|---|
| `str` | `log`, `model`, `reasoning`, `skin`, `seed_set`, `tools`, `warm_up`, `tool_choice`, `prompt_hash`, `harness_version`, `release`, `kind`, `scenario`, `engine_hash`, `numpy_version` |
| `Int64` | `game_rounds`, `inertia`, `generator_version`, `seed_index`, `seed`, `epoch`, `epochs`, the usage columns, and the counts in the score: `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `bad_calls`, `no_calls`, `cut_offs`, `notes_rounds`, `compute_rounds`, `unchanged_rounds`, `sleeper_round` |
| `float64` | `own_scale`, `output`, the six baselines, `gain`, `gap`, `run_score`, `explore_points`, `warm_up_kept` |
| `boolean` | `rolling`, `gave_up`, `errored` |

- **Empty is NA, never a stand-in value.** `own_scale`, `warm_up` and `inertia` are NA at the frozen default. `seed` is NA on a held-out row. `run_score`, `explore_points`, `sleeper_round` and `warm_up_kept` are NA where the scorer wrote `None`. A `float64` column holds its NA as NaN.
- **A group by a key column keeps NA.** Every `groupby` on the key columns passes `dropna=False`, as most rows have NA in `own_scale`, `warm_up` and `inertia`, and pandas would drop them without a word.

### Result key

- **`model` is `log.eval.model`** and `reasoning` is below. Both are per log.
- **`game_rounds` is the metadata's `rounds`**, the length of the game. The score has a `rounds` of its own, the rounds the agent played, and one table cannot hold two columns of one name, so the setting's is renamed on the way in. In the run table `rounds` always means rounds played.
- **Every field of `Setting` comes from sample metadata**, read from every sample that holds it. A log whose samples disagree on a field raises `ValueError` naming the log and the field, so a key is always one setting.
- **The dataset writes every field but one on every sample**, so a sample that lacks one of those raises `ValueError` naming the log, the sample and the field. `tool_choice` is the solver's, written in round 1, see [dataset](../harness/task.md#dataset). A sample that errored before then lacks it and is left out of that field's read. A log on which no sample holds it has `tool_choice` as `None`.
- **`result_key` reads nothing but `log.eval` and `sample.metadata`.**

### Comparing settings

- **`harness_version` is left out whenever two settings are compared.** It carries the git commit when run from a checkout, see [dataset](../harness/task.md#dataset), so two runs either side of a docs commit would otherwise never share a table or pair. Every rule in this layer that says "one table per setting", "differs only in" or "equal in every field but" compares every field of `Setting` but this one.
- **It still splits result rows.** Two logs of one model and reasoning that differ in `harness_version` alone are two result rows, never [duplicates](#duplicates). A scores table shows both and names the version on each, see [the results page](tables.md#the-results-page). A rule that needs one row a side raises `ValueError` naming both, see [public gap](scores.md#public-gap) and [noise threshold](scores.md#noise-threshold).

### Mean over epochs

`mean_over_epochs` gives one row per sample id of each log. It is what every page but [sampling share](scores.md#spread-and-sampling-share) reads.

- **Averaged**: `output`, the six baselines, `gain`, `gap`, `run_score`, `explore_points`, `warm_up_kept`. Means over the epochs that scored and hold a value, in `epoch` order. NA when none does.
- **Summed**: `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `bad_calls`, `no_calls`, `cut_offs`, `notes_rounds`, `compute_rounds`, `unchanged_rounds` and the usage columns, so `sum(retry_rounds) / sum(rounds)` still reads as a share.
- **Smallest positive**: `sleeper_round`, the earliest round any epoch reached the sleeper. 0 when no epoch did, and NA when the timeline has no sleeper.
- **Any**: `gave_up`. A seed that gave up in any epoch counts as failed, see [flags](scores.md#flags).
- **`errored`** is true when no epoch scored. An epoch with no score is left out of the means and counted in the report.
- **`epoch` is dropped.** `epochs` stays. The columns are `RUN_COLUMNS` without `epoch`, with the dtypes above, and the report is carried across.
- **At one epoch it is the identity** on every column but `epoch`, so the headline, which plays each seed once, never depends on this rule.

### Reasoning

`reasoning` is the [reasoning setting](../../harness/models.md#reasoning) the log played.

- **From the log's metadata** when `log.eval.metadata` has `reasoning`, which [`run`](../harness/command.md#run) writes for every eval it runs.
- **Else read back from the generate config.** `reasoning_effort` set gives its name, with `none` read as `off`. `xhigh` and `minimal` are not on the grid, so they give `unknown`. `reasoning_tokens` set gives the key of the harness's `BUDGETS` whose value it equals, see the [budget table](../harness/command.md#reasoning), or `unknown` if none does. Nothing set gives `unknown`, as `on` and a hand run that set nothing look alike in a config.
- **A budget of 0 is `unknown`, never `off`.** The harness sends `reasoning_effort="none"` for `off` on every row, and a budget of 0 is not off on the providers that take one, see [reasoning](../harness/command.md#reasoning).
- **A provider row** is `n/a`, whatever the config says.
- **`unknown` is a value**, not an error. It appears in the table as it is, so a log run by hand with `inspect eval` still loads.

### Errored samples

- **A sample with no `gain` score errored**, see [giving up](../harness/scorer.md#giving-up). It gets a row with `errored` true and NA in every score and usage column, so the report can count it, and it is in no score on any other page.
- **A log where every sample errored** still loads, and the report says so.

### Duplicates

- **Two logs share a result row** when `result_key` is equal and they hold a sample id in common.
- **The later `started` wins when it covers the earlier log**, that is, when its sample ids are a superset of the earlier log's. Every sample of the earlier log is dropped, not just the shared ones, so a result row never mixes two evals. The dropped log is listed in the report. On equal `started` the log later in path order is the later one.
- **Otherwise it is a `ValueError`** naming both logs and the sample ids each has that the other lacks. A `--limit 2` run after a full run must not replace it, and the loader cannot know which the user meant. Delete one, or rerun.
- **No flag keeps both.** Rerun the eval instead, so a result row is always one log.
- **Two logs with one key and no sample in common** are both kept, as `--limit` or a seed range makes a partial log and a second run fills it.

### Metric check

The harness's metrics on a log are a check on the loader, never a source of a number.

- **Per log, before duplicates are dropped.** When `log.results` holds the `scenario_score` metric and every sample has one epoch, `load_runs` pools that log's own rows per scenario as [pooling](scores.md#pooling) says. The score, `lo`, `hi`, `n` and `failed` must equal the metric's `<scenario>`, `<scenario>_lo`, `<scenario>_hi`, `<scenario>_n` and `<scenario>_failed` to `1e-9`, else `ValueError` naming the log, the scenario and the key. This is how the layer knows it read the right numbers.
- **A metric is found by `EvalMetric.group` and `EvalMetric.name`**, the metric function's name and the key it returned. The key of inspect's own `metrics` dict is not used, as inspect adds a digit to it when two metrics return one name, see [checked](#checked).
- **Skipped** on a log with no `results`, without that metric, or at more than one epoch, where the log's metric is over inspect's reduced scores, see [checked](#checked). The report counts the logs checked.

### Guards

Checks on what a log says about itself. The harness writes none of these wrong, see [dataset](../harness/task.md#dataset), so each is a guard against a log from elsewhere. Every one raises `ValueError` naming the log.

- **`scenario`** is a key of `SCENARIOS`.
- **`skin`** matches the skins layer's name pattern, `^[a-z][a-z0-9_]*$`, see [validation](../skins/skin.md#validation-on-construction).
- **`model`** matches `^[A-Za-z0-9][A-Za-z0-9_.:@/-]*$` and holds no `..`. The three strings go into table cells, plot titles and file names, see [tables](tables.md), so none may hold a `|`, a space or a path step.
- **`seed_set`** is `public` or `held-out`, and `seed_index` is a whole number from 0.
- **`tool_choice`** is `any` or `auto` wherever a sample holds it, see [each round](../harness/solver.md#each-round).

### Privacy

The rules that make the run table publishable. They are invariants, not options, see [contamination](../../harness/contamination.md#who-can-see-them).

- **`seed` is NA for a held-out sample.** A held-out sample whose metadata has a `seed` key raises `ValueError` naming the log and the sample id.
- **The loader reads `sample.id`, `sample.scores`, `sample.metadata`, `sample.model_usage`, `sample.epoch`, `log.eval` and `log.results`** and nothing else. It never reads `sample.messages`, `sample.store`, `sample.input`, `sample.events` or `Score.answer`, so no reading, bet or skin word enters the table.
- **A skin is its name.** The table holds `skin` as the metadata's name and `prompt_hash`, nothing more.
- **The timeline is never rebuilt here.** `switch_kinds` does that, on its own terms, see [switch kinds](scores.md#switch-kinds).

### The report

`load_runs` attaches a report to the table's `attrs["report"]`: the logs read with their sample counts, how many had their metrics checked, the logs skipped as not `paranoid`, the logs dropped as duplicates with the log that won, the errored samples per log, and any result row whose rows hold more than one `numpy_version`, as timelines are bit equal within one environment only, see [what a log carries](../README.md#what-a-log-carries). The [command](command.md#behaviour) prints it.

## Invariants

- On every row that did not error, `run_score == gain / gap` where `gap` is not 0, and `run_score` is NA where it is.
- `len(table) == ` the number of sample epochs in the loaded logs, after duplicates are dropped. After `mean_over_epochs`, the number of distinct sample ids per log.
- `table.columns == RUN_COLUMNS`, and `RUN_COLUMNS` without `epoch` after `mean_over_epochs`.
- Every row of one `ResultKey` has the same `Setting`, by construction, and rows of one key and scenario have the same `engine_hash`.
- `mean_over_epochs` on a table where every `epochs == 1` changes no value.
- No row is lost to a group by, whatever is NA in its key columns.

## Not decided

- Whether a log from a later `harness_version` with the same hashes should count as the same result row. It does not here, as the round loop is what the version covers, see [what a log carries](../README.md#what-a-log-carries). It shares a table and is named there, see [comparing settings](#comparing-settings). Decide when the first release ships.

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289, on a log of two samples at four epochs with a dict score, and on a log the harness wrote for `baseline/complacent`. No key was used.

| Question | Answer |
|---|---|
| Do the names this page reads exist | Yes: `read_eval_log`, `EvalLog.eval.metadata`, `.eval.model`, `.eval.model_generate_config`, `.eval.task`, `EvalLog.results.scores[].metrics`, `EvalSample.id`, `.epoch`, `.metadata`, `.scores` and `.model_usage` |
| `.eval.task` on a log the harness wrote | `paranoid/paranoid`, though `run` passes the task function and not that name |
| `.eval.created` | An ISO 8601 string with its offset, so `started` parses it |
| `Score.value` | Comes back as the dict the scorer wrote, ints still ints and `None` still `None` |
| `sample.model_usage` | A dict keyed by model string. Each value has `input_tokens`, `output_tokens`, `total_tokens`, `input_tokens_cache_read`, `input_tokens_cache_write` and `reasoning_tokens`. A provider row has one entry of zeros, with the two cache fields and `reasoning_tokens` as `None` |
| Where a log keeps its metrics | `log.results.scores[0].metrics`, a dict of `EvalMetric`. `.group` is the metric function's name, such as `scenario_score`, and `.name` the key it returned, such as `down_switch_lo`. The dict's own key is the name, with a digit added on a clash: `retry_share` returns a `no_change` too, and its key is `no_change2` |
| Does a log keep every epoch | Yes. `log.samples` has one entry per id and epoch, and `log.reductions` has the reduced value per id |
| How the `"mean"` reducer treats a dict score | It averages every key on its own, counts too. A value that is not a number becomes 0 |
| Does an edited log survive a write and a read | Yes. A log with one sample's metadata changed and `results` set to `None`, written with `write_eval_log`, reads back with both |

- **So the layer never reads a reduced score.** [Mean over epochs](#mean-over-epochs) works from the per-epoch samples, and sums the counts itself.
- **The harness's reducer stays `"mean"`.** A share of two counts is the same summed or averaged, as both are divided by the same number of epochs, and the scores are averaged either way. The one thing that differs is a bare count on the log, which nothing reads. The log's own metrics are still checked at one epoch only, see [metric check](#metric-check).

## Verify before code

- **pandas on NA keys.** That a `groupby` with `dropna=False` keeps a group whose key is NA in a `str`, an `Int64` and a `float64` column at once, and that two NA keys land in one group. Every group by in the layer waits on it. Run one on a three row frame at the pinned pandas.
- **pandas `attrs`.** Whether `attrs["report"]` survives `copy`, `concat` and a `groupby` result. `mean_over_epochs` carries the report across by hand if not. The report waits on it.
