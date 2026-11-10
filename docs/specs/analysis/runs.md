# Runs

## Purpose

`load_runs` turns a set of `.eval` logs into the run table: one row per run, with everything the layer needs and nothing a log should not give away. `Setting` says what was played and `ResultKey` says who played it, so together they say which rows belong to one result row. Every other page starts from this table. What a log holds is in [dataset](../harness/task.md#dataset) and [scoring one run](../harness/scorer.md#scoring-one-run).

## Interface

```python
@dataclass(frozen=True)
class Setting:                        # what was played, apart from who played it
    skin: str
    seed_set: Literal["public", "held-out"]
    own_scale: float | None           # None means the frozen default
    rounds: int
    tools: str
    warm_up: str | None
    rolling: bool
    tool_choice: Literal["any", "auto"]
    inertia: int | None
    prompt_hash: str
    generator_version: int
    harness_version: str

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
- **A log that is not the `paranoid` task** is skipped and listed in the report, see [the report](#the-report).

### One row per run

The run table has these columns, in this order. `RUN_COLUMNS` holds the names.

| Group | Columns | From |
|---|---|---|
| Log | `log` (the path relative to the folder it was found under, or the file name when given as a file), `started` (the eval's start time) | `log.eval` |
| Key | `model`, `reasoning`, then every field of `Setting` in its order | `result_key(log)` |
| Run | `kind`, `scenario`, `seed_index`, `seed`, `engine_hash`, `numpy_version`, `epoch`, `epochs` | `metadata`, see below |
| Score | every key of `Score.value` in the [scorer's table](../harness/scorer.md#scoring-one-run): `output`, the six baselines, `gain`, `gap`, `run_score`, `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `gave_up`, `bad_calls`, `no_calls`, `cut_offs`, `notes_rounds`, `compute_rounds`, `unchanged_rounds` | `sample.scores["gain"].value` |
| Usage | `input_tokens`, `cache_read_tokens`, `cache_write_tokens`, `output_tokens`, `reasoning_tokens`, `total_tokens`, summed over the sample's model calls | `sample.model_usage` |
| State | `errored` | whether the sample has a score |

- **`kind`** is `log.eval.metadata["kind"]`, which [`poc`](../harness/command.md#poc) writes. Without it, `baseline`, `jev` or `timestral` when the model string starts with that prefix and a slash, else `llm`.
- **`scenario`, `seed_index`, `seed`, `engine_hash`, `numpy_version`** come from `sample.metadata`. `seed` is the metadata's `seed` key for a public sample and NA for a held-out one, see [privacy](#privacy).
- **`engine_hash` is per row, not per key.** It hashes the scenario's config, events included, so one result row has one hash per scenario, see [engine hash](../engine/config.md#engine-hash). `generator_version` is what the key carries, as it is the part of the hash every scenario shares.
- **Cached tokens are counted apart.** `cache_read_tokens` and `cache_write_tokens` are inspect's `input_tokens_cache_read` and `input_tokens_cache_write`, 0 when a provider reports none. inspect leaves both out of `input_tokens`, so the three add up to what the model read, and a cost from `input_tokens` alone is too low, see [cost](tables.md#cost).
- **One row per epoch.** `epoch` is the sample's epoch and `epochs` how many the sample has. A log at one epoch has `epoch == 1` on every row.
- **Numbers keep their types.** Counts are ints, outputs and scores are floats, `gave_up` and `errored` are bools. No column holds an array or an object.

### Result key

- **`model` is `log.eval.model`** and `reasoning` is below. Both are per log.
- **Every field of `Setting` comes from sample metadata**, read from every sample. A log whose samples disagree on a field raises `ValueError` naming the log and the field, so a key is always one setting.
- **`result_key` reads nothing but `log.eval` and `sample.metadata`.**

### Mean over epochs

`mean_over_epochs` gives one row per sample id. It is what every page but [sampling share](scores.md#spread-and-sampling-share) reads.

- **Averaged**: `output`, the six baselines, `gain`, `gap`, `run_score`. Means over the epochs that scored, in `epoch` order.
- **Summed**: `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `bad_calls`, `no_calls`, `cut_offs`, `notes_rounds`, `compute_rounds`, `unchanged_rounds` and the usage columns, so `sum(retry_rounds) / sum(rounds)` still reads as a share.
- **Any**: `gave_up`. A seed that gave up in any epoch counts as failed, see [flags](scores.md#flags).
- **`errored`** is true when no epoch scored. An epoch with no score is left out of the means and counted in the report.
- **`epoch` is dropped.** `epochs` stays. The columns are `RUN_COLUMNS` without `epoch`.
- **At one epoch it is the identity** on every column but `epoch`, so the headline, which plays each seed once, never depends on this rule.

### Reasoning

`reasoning` is the [reasoning setting](../../harness/models.md#reasoning) the log played.

- **From the log's metadata** when `log.eval.metadata` has `reasoning`, which [`poc`](../harness/command.md#poc) writes for every eval it runs.
- **Else read back from the generate config.** `reasoning_effort` set gives its name, with `xhigh` read as `max`. `reasoning_tokens` set gives the key of the [budget table](../harness/command.md#reasoning) whose value it equals, or `unknown` if none does. Nothing set gives `unknown`, as `off` and `on` look alike in a config.
- **A provider row** is `n/a`, whatever the config says.
- **`unknown` is a value**, not an error. It appears in the table as it is, so a log run by hand with `inspect eval` still loads.

### Errored samples

- **A sample with no `gain` score errored**, see [giving up](../harness/scorer.md#giving-up). It gets a row with `errored` true and NA in every score and usage column, so the report can count it, and it is in no score on any other page.
- **A log where every sample errored** still loads, and the report says so.

### Duplicates

- **Two logs share a result row** when `result_key` is equal and they hold a sample id in common.
- **The later `started` wins when it covers the earlier log**, that is, when its sample ids are a superset of the earlier log's. Every sample of the earlier log is dropped, not just the shared ones, so a result row never mixes two evals. The dropped log is listed in the report.
- **Otherwise it is a `ValueError`** naming both logs and the sample ids each has that the other lacks. A `--limit 2` run after a full run must not replace it, and the loader cannot know which the user meant. Delete one, or rerun.
- **No flag keeps both.** Rerun the eval instead, so a result row is always one log.
- **Two logs with one key and no sample in common** are both kept, as `--limit` or a seed range makes a partial log and a second run fills it.

### Guards

Checks on what a log says about itself. The harness writes none of these wrong, see [dataset](../harness/task.md#dataset), so each is a guard against a log from elsewhere. Every one raises `ValueError` naming the log.

- **`scenario`** is a key of `SCENARIOS`.
- **`skin`** matches the skins layer's name pattern, `^[a-z][a-z0-9_]*$`, see [validation](../skins/skin.md#validation-on-construction).
- **`model`** matches `^[A-Za-z0-9][A-Za-z0-9_.:@/-]*$` and holds no `..`. The three strings go into table cells, plot titles and file names, see [tables](tables.md), so none may hold a `|`, a space or a path step.
- **`seed_set`** is `public` or `held-out`, and `seed_index` is a whole number from 0.
- **`tool_choice`** is `any` or `auto`, see [each round](../harness/solver.md#each-round).

### Privacy

The rules that make the run table publishable. They are invariants, not options, see [contamination](../../harness/contamination.md#who-can-see-them).

- **`seed` is NA for a held-out sample.** A held-out sample whose metadata has a `seed` key raises `ValueError` naming the log and the sample id.
- **The loader reads `sample.scores`, `sample.metadata`, `sample.model_usage`, `sample.epoch`, `log.eval` and `log.results`** and nothing else. It never reads `sample.messages`, `sample.store`, `sample.input` or `Score.answer`, so no reading, bet or skin word enters the table.
- **A skin is its name.** The table holds `skin` as the metadata's name and `prompt_hash`, nothing more.
- **The timeline is never rebuilt here.** `switch_kinds` does that, on its own terms, see [switch kinds](scores.md#switch-kinds).

### The report

`load_runs` attaches a report to the table's `attrs["report"]`: the logs read with their sample counts, the logs skipped as not `paranoid`, the logs dropped as duplicates with the log that won, the errored samples per log, and any result row whose rows hold more than one `numpy_version`, as timelines are bit equal within one environment only, see [what a log carries](../README.md#what-a-log-carries). The [command](command.md#behaviour) prints it.

## Invariants

- `run_score == gain / gap` and `gap > 0` on every row that did not error.
- `len(table) == ` the number of sample epochs in the loaded logs, after duplicates are dropped. After `mean_over_epochs`, the number of distinct sample ids.
- `table.columns == RUN_COLUMNS`, and `RUN_COLUMNS` without `epoch` after `mean_over_epochs`.
- Every row of one `ResultKey` has the same `Setting`, by construction, and rows of one key and scenario have the same `engine_hash`.
- `mean_over_epochs` on a table where every `epochs == 1` changes no value.
- No column has dtype `object` except the strings, and no cell holds an array.

## Not decided

- Whether a log from a later `harness_version` with the same hashes should count as the same result row. It does not here, as the round loop is what the version covers, see [what a log carries](../README.md#what-a-log-carries). Decide when the first release ships.

## Verify before code

- **inspect's log API.** The names assumed on this page: `read_eval_log`, `EvalLog.eval.metadata`, `.eval.model`, `.eval.model_generate_config`, `.eval.created`, `.eval.task`, `EvalLog.results.scores[].metrics`, `EvalSample.id`, `.epoch`, `.metadata`, `.scores`, `.model_usage` with its `input_tokens_cache_read` and `input_tokens_cache_write`, and that `Score.value` comes back as a dict. `load_runs` waits on it.
- **How inspect's `"mean"` reducer treats a dict `Score.value`.** [Mean over epochs](#mean-over-epochs) averages the scores and sums the counts. If inspect does otherwise, the log's own metrics at more than one epoch differ from this layer's, and [AS1](tests.md#scores) holds at one epoch only. Decide then whether the harness's reducer changes, see [task settings](../harness/task.md#task-settings).
