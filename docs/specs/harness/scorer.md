# Scorer

## Purpose

`gain` scores one run: its output, and the output of every fixed baseline on the same tape over the same rounds. The metrics pool those per scenario into the scenario score, bootstrap its error bar, and build the headline, the weakest trait and the retry share. The design is in [scoring](../../design/scoring.md) and [metrics](../../harness/inspect.md#metrics).

## Interface

```python
@scorer(metrics=[scenario_score(), headline(), weakest_trait(), retry_share()])
def gain() -> Scorer
# Score.value: dict with the keys in the table below
# Score.answer: store.record().to_csv() with default names
# Score.metadata: scenario, seed, seed_index, engine_hash

BOOTSTRAP_DRAWS = 1000
BOOTSTRAP_SEED = 0
TRAITS: Mapping[str, str]            # scenario code name -> trait, from scoring.md

def pooled_score(gains: Sequence[float], gaps: Sequence[float]) -> float
def bootstrap(gains: Sequence[float], gaps: Sequence[float], *, draws: int = BOOTSTRAP_DRAWS,
              rng: np.random.Generator | None = None) -> tuple[float, float]   # 2.5th and 97.5th percentiles

@metric
def scenario_score() -> Metric      # {"<scenario>": s, "<scenario>_lo": lo, "<scenario>_hi": hi, "<scenario>_n": seeds, "<scenario>_failed": k}
@metric
def headline() -> Metric            # {"headline": h, "lo": lo, "hi": hi, "scenarios": n}
@metric
def weakest_trait() -> Metric       # {"scenario": name, "trait": TRAITS[name], "score": s}
@metric
def retry_share() -> Metric         # {"<scenario>": share, "all": share, "cut_off_share": share}
```

## Behaviour

### Scoring one run

`Score.value` holds these keys, all floats or ints:

| Key | Value |
|---|---|
| `output` | The sum of `row.output` over the rounds the agent played, `rows[warm_up_rounds:]` |
| `uniform`, `discerning`, `complacent`, `perfect`, `hedge_rule`, `scout_rule` | Each baseline's output over the same rounds, from `play(policy, tape)` with the run's warm up record as its start, see [play](../engine/game.md#play) |
| `gain` | `output − uniform` |
| `gap` | `discerning − uniform` |
| `run_score` | `gain / gap`. The dot on the strip, see [spread](../../design/scoring.md#spread) |
| `rounds`, `warm_up_rounds` | Rounds the agent played, rounds a baseline played first |
| `retries` | `sum(tries) − len(tries)`, the generate calls beyond the first per round |
| `retry_rounds` | Rounds with `tries > 1` |
| `bad_calls`, `no_calls`, `cut_offs` | From the store |
| `unchanged_rounds` | `len(record.unchanged_rounds())` over the agent's rounds only |

- **The baselines replay the agent's warm up.** `play(policy, tape, record=warm_up_record)` starts each baseline where the agent started, so with an empty warm up it is the plain full run. Their outputs are then summed over the same rounds as the agent's.
- **Every number comes from the record's rounded outputs**, never from the tape's levels, see [readings](../engine/game.md#readings). The agent and the scorer agree on every number.
- **The baselines are deterministic**, so across epochs they are constant and the mean reducer leaves them alone.
- **The scorer never reads the messages.** The store is the run.

### Pooling

- **`pooled_score(gains, gaps)`** is `sum(gains) / sum(gaps)`. Not a mean of run scores, see [pooling seeds](../../design/scoring.md#pooling-seeds). An empty input or a zero gap sum raises `ValueError`.
- **`bootstrap`** draws `draws` resamples of the seed indices with replacement, computes the pooled score of each, and returns the 2.5th and 97.5th percentiles with `np.percentile`, linear interpolation. `rng` defaults to `default_rng(BOOTSTRAP_SEED)`, so the bars are the same on every run of the metric. One seed gives `lo == hi == score`.

### Scenario score

- **Group by `sample_metadata["scenario"]`.** Within a group, each `SampleScore` is one seed, already averaged over epochs by inspect's reducer.
- **Score** is `pooled_score` over the group's `gain` and `gap`. **`lo` and `hi`** are its bootstrap.
- **`n`** is the number of seeds expected, `failed` the number with no score, see below.

### Missing seeds

A sample that errored twice has no `SampleScore`, see [task settings](task.md#task-settings). The [retry rule](../../harness/prompts.md#retry-rule) says it scores as the Uniform baseline on that seed.

- **The expected seeds** come from `parse_seeds(seeds_arg, scenario)` with `seeds_arg` from any present sample's metadata. The seed files must be where they were at eval time.
- **Each missing seed adds `gain = 0`** and a `gap` of `discerning − uniform` from `play` on that seed's tape, built with the same knobs and warm up as the present samples.
- **A group with every seed missing** has a score of 0 and `failed == n`.
- **It never happens silently.** `failed` is in the value, and the analysis layer marks the bar.

### Headline

- **The plain mean of the scenario scores present in the log.** `scenarios` says how many. A full headline has eight, see [how we score](../../design/scoring.md#how-we-score).
- **Bars.** Each bootstrap draw resamples seeds within every scenario with one `rng`, then takes the mean of the pooled scores. Scenarios are never resampled, see [error bars](../../design/scoring.md#error-bars).

### Weakest trait

- The scenario with the lowest score, its trait from `TRAITS`, and the score. Ties go to `SCENARIOS` order.
- `TRAITS` holds the eight pairs in [traits](../../design/scoring.md#traits): `no_change` to `"composure"`, `one_shock` to `"patience"`, `down_switch` to `"doubt"`, `up_switch` to `"curiosity"`, `shock_then_switch` to `"unlearning"`, `slow_drift` to `"vigilance"`, `switch_then_shock` to `"conviction"`, `up_switch_then_down_switch` to `"recall"`.

### Retry share

- **Per scenario and overall**, `sum(retry_rounds) / sum(rounds)` over the scored samples. Missing seeds count their `rounds` as all retried, as they ended in ten failed tries.
- **`cut_off_share`** is `sum(cut_offs) / sum(rounds)` overall, kept apart so a cap problem cannot pass as a model problem, see [sampling](../../harness/models.md#sampling).
- The share that marks a bar is a pilot decision, see [decisions](../../pilot/decisions.md#provider-checks).

### Not here

- **Gaps between models** need two logs and are paired by seed in the analysis layer, see [metrics](../../harness/inspect.md#metrics).
- **The noise threshold** needs every grid setting, so it is analysis too, see [noise threshold](../../design/scoring.md#noise-threshold).

## Invariants

- A run of `baseline/uniform` has `gain == 0` and a run of `baseline/discerning` has `gain == gap`, exactly, on every seed and warm up. So their scenario scores are 0 and 1.
- `pooled_score` equals the gap-weighted mean of the run scores.
- The same log gives the same metrics on every machine.
- No metric reads the tape for a seed that has a score. Only missing seeds rebuild one.
- `perfect ≥ discerning` on every seed, see [P6](../engine/tests.md#policies).

## Tests

See [tests](tests.md#scorer).

## Open

- `BOOTSTRAP_DRAWS` at 1000 is a convention, not a pilot knob. Raise it if the bars wobble between runs of the analysis at the seed counts the pilot picks.
- Whether `failed` should also mark the bar inside inspect's own view, or only in the analysis layer's tables.
