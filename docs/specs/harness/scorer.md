# Scorer

## Purpose

`gain` scores one run: its output, and the output of every fixed baseline on the same tape over the same rounds. The metrics pool those per scenario into the scenario score, bootstrap its error bar, and build the headline, the weakest trait and the retry share. The design is in [scoring](../../design/scoring.md) and [metrics](../../harness/inspect.md#metrics).

## Interface

```python
@scorer(metrics=[scenario_score(), headline(), weakest_trait(), retry_share()])
def gain() -> Scorer
# Score.value: dict with the keys in the table below
# Score.answer: render_record(skin, store.record()), the record as the agent last saw it
# Score.metadata: scenario, seed_set, seed_index, engine_hash. seed too, for a public seed only

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
| `uniform`, `discerning`, `complacent`, `perfect`, `hedge_rule`, `scout_rule` | Each baseline's output over the agent's rounds, `warm_up_rounds + 1` to the config's `rounds`, from `play(policy, tape)` with the run's warm up record as its start, each policy at its defaults from the [baselines layer](../baselines/README.md#exports), see [play](../engine/game.md#play) |
| `gain` | `output − uniform`, or 0 when the run gave up, see [giving up](#giving-up) |
| `gap` | `discerning − uniform` |
| `run_score` | `gain / gap`. The dot on the strip, see [spread](../../design/scoring.md#spread) |
| `rounds`, `warm_up_rounds` | `len(tries)`: the rounds the agent played, plus the one it gave up on if it did. And the rounds a baseline played first |
| `retries` | `sum(tries) − len(tries)`, the generate calls beyond the first per round |
| `retry_rounds` | Rounds with `tries > 1` |
| `gave_up` | 1 when the run gave up, else 0 |
| `bad_calls`, `no_calls`, `cut_offs` | From the store |
| `unchanged_rounds` | `len(record.unchanged_rounds())` over the agent's rounds only |

- **The baselines replay the agent's warm up.** `play(policy, tape, record=warm_up_record)` starts each baseline where the agent started, so with an empty warm up it is the plain full run. Their outputs are summed over every round after the warm up, to the end of the run, whether or not the agent got there.
- **The baselines play with `inertia_cap` cleared.** They move whole budgets, so under a cap `play` would raise at the first move, see [pilot cells](command.md#pilot-cells). The score needs them whatever the agent's config, so `gain` plays them against a tape made from the run's config with `inertia_cap` set to `None`, which draws the same arrays because `make_tape` never reads the cap, see [config](../engine/config.md#fields).
- **Every number comes from the record's rounded outputs**, never from the tape's levels, see [readings](../engine/game.md#readings). The agent and the scorer agree on every number.
- **The baselines are deterministic**, so across epochs they are constant and the mean reducer leaves them alone.
- **The scorer never reads the messages.** The store is the run.

### Pooling

- **`pooled_score(gains, gaps)`** is `sum(gains) / sum(gaps)`. Not a mean of run scores, see [pooling seeds](../../design/scoring.md#pooling-seeds). An empty input or a zero gap sum raises `ValueError`.
- **`bootstrap`** draws `draws` resamples of the seed indices with replacement, computes the pooled score of each, and returns the 2.5th and 97.5th percentiles with `np.percentile`, linear interpolation. `rng` defaults to `default_rng(BOOTSTRAP_SEED)`, so the bars are the same on every run of the metric. One seed gives `lo == hi == score`.

### Scenario score

- **Group by `sample_metadata["scenario"]`.** Within a group, each `SampleScore` is one seed, already averaged over epochs by inspect's reducer.
- **Score** is `pooled_score` over the group's `gain` and `gap`. **`lo` and `hi`** are its bootstrap.
- **`n`** is the number of seeds scored, `failed` the number that gave up, see below.

### Giving up

A run that hit ten failed tries in one round gave up, see [tries](solver.md#tries). The [retry rule](../../harness/prompts.md#retry-rule) says it scores as the Uniform baseline on that seed.

- **The scorer still runs**, as the solver raised nothing. `gave_up` is 1, `gain` is 0 whatever the agent earned before it stopped, so `run_score` is 0. `output` keeps the real partial sum for the reader. `gap` is the full gap, so the seed keeps its weight in the pool.
- **`failed`** counts them per scenario. A group where every run gave up has a score of 0 and `failed == n`.
- **It never happens silently.** `failed` is in the value, and the analysis layer flags the bar, see [flags](../analysis/scores.md#flags). inspect's own view shows `failed` as a metric key and nothing more.
- **Nothing is rebuilt.** Every number a metric needs is in `Score.value`, so a log scores the same with no seed file, no `PARANOID_SEEDS` and no engine, and `--limit 2` scores two seeds rather than reporting the rest as failed.
- **An errored sample is infrastructure**, see [task settings](task.md#task-settings). It has no `SampleScore` and is in no metric. inspect's own log says how many errored, and the eval fails past a tenth.

### Headline

- **The plain mean of the scenario scores present in the log.** `scenarios` says how many. A full headline has eight, see [how we score](../../design/scoring.md#how-we-score).
- **Bars.** Each bootstrap draw resamples seeds within every scenario with one `rng`, then takes the mean of the pooled scores. Scenarios are never resampled, see [error bars](../../design/scoring.md#error-bars).

### Weakest trait

- The scenario with the lowest score, its trait from `TRAITS`, and the score. Ties go to `SCENARIOS` order.
- `TRAITS` holds the eight pairs in [traits](../../design/scoring.md#traits): `no_change` to `"composure"`, `one_shock` to `"patience"`, `down_switch` to `"doubt"`, `up_switch` to `"curiosity"`, `shock_then_switch` to `"unlearning"`, `slow_drift` to `"vigilance"`, `switch_then_shock` to `"conviction"`, `up_switch_then_down_switch` to `"recall"`.

### Retry share

- **Per scenario and overall**, `sum(retry_rounds) / sum(rounds)` over the scored samples. A run that gave up counts its last round as retried, as its ten tries say.
- **`cut_off_share`** is `sum(cut_offs) / sum(rounds)` overall, kept apart so a cap problem cannot pass as a model problem, see [sampling](../../harness/models.md#sampling).
- The share that marks a bar is a pilot decision, see [decisions](../../pilot/decisions.md#provider-checks).

### Not here

- **Gaps between models** need two logs and are paired by seed in the analysis layer, see [paired gap](../analysis/scores.md#paired-gap).
- **The noise threshold** needs every grid setting, so it is analysis too, see [noise threshold](../analysis/scores.md#noise-threshold).

## Invariants

- A run of `baseline/uniform` has `gain == 0` and a run of `baseline/discerning` has `gain == gap`, exactly, on every seed and warm up. So their scenario scores are 0 and 1.
- `pooled_score` equals the gap-weighted mean of the run scores.
- The same log gives the same metrics on every machine, with no seed file and no engine.
- No metric reads a tape. The scorer is the only reader, and only through the store.
- `perfect ≥ discerning` on every seed, see [BP5](../baselines/tests.md#policies).

## Not decided

- `BOOTSTRAP_DRAWS` at 1000 is a convention, not a pilot knob. Raise it if the bars wobble between runs of the analysis at the seed counts the pilot picks. Decide once the pilot has set its seed count.
