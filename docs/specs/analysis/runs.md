# Runs

## Purpose

`load_runs` turns a set of `.eval` logs into the run table: one row per run, with everything the layer needs and nothing a log should not give away. `ResultKey` says which rows belong to one result row. Every other page starts from this table. What a log holds is in [dataset](../harness/task.md#dataset) and [scoring one run](../harness/scorer.md#scoring-one-run).

## Interface

```python
@dataclass(frozen=True)
class ResultKey:
    model: str                        # the inspect model string, such as "anthropic/claude-haiku-5-5"
    reasoning: str                    # one of REASONING, "n/a" for a provider, or "unknown", see below
    skin: str
    seed_set: Literal["public", "held-out"]
    own_scale: float | None           # None means the frozen default
    engine_hash: str
    prompt_hash: str
    harness_version: str
    rounds: int
    tools: str
    warm_up: str | None
    rolling: bool
    inertia: int | None

RUN_COLUMNS: tuple[str, ...]          # the columns of the run table, in order, see below

def load_runs(paths: Iterable[str | Path], *, epochs: Literal["mean", "all"] = "mean") -> pd.DataFrame
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
| Log | `log` (the file name), `started` (the eval's start time) | `log.eval` |
| Key | every field of `ResultKey`, in its order | `result_key(log)` |
| Run | `kind`, `scenario`, `seed_index`, `seed`, `epochs` | `metadata`, see below |
| Score | every key of `Score.value` in the [scorer's table](../harness/scorer.md#scoring-one-run): `output`, the six baselines, `gain`, `gap`, `run_score`, `rounds`, `warm_up_rounds`, `retries`, `retry_rounds`, `gave_up`, `bad_calls`, `no_calls`, `cut_offs`, `unchanged_rounds` | `sample.scores["gain"].value` |
| Usage | `input_tokens`, `output_tokens`, `reasoning_tokens`, `total_tokens`, summed over the sample's model calls | `sample.model_usage` |
| State | `errored` | whether the sample has a score |

- **`kind`** is `log.eval.metadata["kind"]`, which [`poc`](../harness/command.md#poc) writes. Without it, `baseline`, `jev` or `timestral` when the model string starts with that prefix and a slash, else `llm`.
- **`scenario`, `seed_index`, `seed`** come from `sample.metadata`. `seed` is the metadata's `seed` key for a public sample and NA for a held-out one, see [privacy](#privacy).
- **`epochs="mean"`** gives one row per sample id, with every score column averaged over the sample's epochs the way inspect's `"mean"` reducer does, see [task settings](../harness/task.md#task-settings). `epochs` holds how many were averaged. Usage is summed over epochs.
- **`epochs="all"`** gives one row per epoch, with an extra `epoch` column after `epochs`. It is for [sampling share](scores.md#spread-and-sampling-share) and nothing else.
- **Numbers keep their types.** Counts are ints, outputs and scores are floats, `gave_up` and `errored` are bools. No column holds an array or an object.

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
- **The later `started` wins.** Every sample of the earlier log is dropped, not just the shared ones, so a result row never mixes two evals. The dropped log is listed in the report.
- **No flag keeps both.** Rerun the eval instead, so a result row is always one log.
- **Two logs with one key and no sample in common** are both kept, as `--limit` or a seed range makes a partial log and a second run fills it.

### Privacy

The rules that make the run table publishable. They are invariants, not options, see [contamination](../../harness/contamination.md#who-can-see-them).

- **`seed` is NA for a held-out sample.** A held-out sample whose metadata has a `seed` key raises `ValueError` naming the log and the sample id. The harness never writes one, see [dataset](../harness/task.md#dataset), so this is a guard against a log from elsewhere.
- **The loader reads `sample.scores`, `sample.metadata`, `sample.model_usage`, `sample.epoch`, `log.eval` and `log.results`** and nothing else. It never reads `sample.messages`, `sample.store`, `sample.input` or `Score.answer`, so no reading, bet or skin word enters the table.
- **A skin is its name.** The table holds `skin` as the metadata's name and `prompt_hash`, nothing more.
- **The tape is never rebuilt here.** `switch_kinds` does that, on its own terms, see [switch kinds](scores.md#switch-kinds).

### The report

`load_runs` attaches a report to the table's `attrs["report"]`: the logs read with their sample counts, the logs skipped as not `paranoid`, the logs dropped as duplicates with the log that won, and the errored samples per log. The [command](command.md#behaviour) prints it.

## Invariants

- `run_score == gain / gap` and `gap > 0` on every row that did not error.
- `len(table) == ` the number of samples in the loaded logs, after duplicates are dropped, with `epochs="all"`, or the number of distinct sample ids with `"mean"`.
- `table.columns == RUN_COLUMNS` with `epochs="mean"`, and `RUN_COLUMNS` with `epoch` inserted after `epochs` with `"all"`.
- Every row of one `ResultKey` has the same `engine_hash`, `prompt_hash` and `harness_version`, by construction.
- No column has dtype `object` except the strings, and no cell holds an array.

## Not decided

- Whether a log from a later `harness_version` with the same hashes should count as the same result row. It does not here, as the round loop is what the version covers, see [what a log carries](../README.md#what-a-log-carries). Decide when the first release ships.

## Verify before code

- **inspect's log API.** The names assumed on this page: `read_eval_log`, `EvalLog.eval.metadata`, `.eval.model`, `.eval.model_generate_config`, `.eval.created`, `.eval.task`, `EvalLog.results.scores[].metrics`, `EvalSample.id`, `.epoch`, `.metadata`, `.scores`, `.model_usage`, and that `Score.value` comes back as a dict. `load_runs` waits on it.
- **How inspect's `"mean"` reducer treats a dict `Score.value`.** It is assumed to average each key. If it does not, the harness side changes, see [task settings](../harness/task.md#task-settings), and `epochs="mean"` follows.
