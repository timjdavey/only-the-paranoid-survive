# Scores

## Purpose

The maths over the run table. Scenario scores and headlines per result row, the marks the fixed baselines put on each bar, the flags, the gaps between two rows paired by seed, the public gap, spread, the switch kind each seed drew, and the noise threshold. Every pooled number goes through the harness's `pooled_score` and `bootstrap`, so a table here equals the log's own metrics. The design is in [scoring](../../design/scoring.md).

## Interface

```python
RETRY_FLAG = 0.1                       # retry share that flags a bar, pilot to confirm

def scenario_scores(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey and scenario: the key's fields, scenario, trait, score, lo, hi, n, failed,
# retry_share, cut_off_share, complacent, hedge_rule, scout_rule, perfect, flags

def headlines(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey: the key's fields, headline, lo, hi, scenarios, weakest_scenario, weakest_trait,
# weakest_score, flags

@dataclass(frozen=True)
class Gap:
    diff: float
    lo: float
    hi: float
    n_shared: int

def paired_gap(runs, a: ResultKey, b: ResultKey) -> pd.DataFrame            # one row per scenario, plus "headline"
def scenario_gap(runs, key: ResultKey, a: str, b: str, seeds: Sequence[int] | None = None) -> Gap
def public_gap(runs, model: str, reasoning: str, skin: str) -> pd.DataFrame # one row per scenario, plus "headline"

def spread(runs) -> pd.DataFrame                 # per ResultKey and scenario: sd, p10, n
def sampling_share(epoch_runs) -> pd.DataFrame   # per ResultKey and scenario: within_sd, total_sd, share, seeds, epochs

def switch_kinds(runs) -> pd.DataFrame           # per scenario, seed_set, seed_index, engine_hash, own_scale: kind

def signal_points(config: ScenarioConfig) -> float

@dataclass(frozen=True)
class Threshold:
    snr: float | None                 # the signal to noise at the half way crossing
    lo: float | None
    hi: float | None
    snr_80: float | None              # the 80% crossing
    own_scale: float | None           # snr as an own_scale, for reading against the grid
    floor: float                      # the Complacent baseline's headline
    status: Literal["crossed", "off the noisy end", "off the quiet end"]
    uncrossed_draws: int

def noise_threshold(runs, key_without_scale: ResultKey) -> Threshold
```

## Behaviour

### Pooling

- **Every pooled score is `pooled_score(gains, gaps)`** from the harness, over the rows of one result row and scenario that did not error, see [pooling](../harness/scorer.md#pooling). Never a mean of run scores.
- **Every bar is `bootstrap(gains, gaps)`** at its defaults, `BOOTSTRAP_DRAWS` and `BOOTSTRAP_SEED`, so the bars equal the log's and are the same on every machine.
- **Rows are ordered by `seed_index`** before any draw, so the bootstrap sees the same sequence as the metric did.

### Scenario scores

- **Group by `ResultKey` and `scenario`.** `score`, `lo`, `hi` as above. `n` is the rows scored, `failed` the rows with `gave_up`, as in the [scenario score metric](../harness/scorer.md#scenario-score).
- **`trait`** is `TRAITS[scenario]`.
- **`retry_share`** is `sum(retry_rounds) / sum(rounds)` and **`cut_off_share`** is `sum(cut_offs) / sum(rounds)`, as the [retry share metric](../harness/scorer.md#retry-share).
- **The marks** are the fixed baselines' pooled scores on the same seeds: `complacent` is `pooled_score(complacent − uniform, gap)`, and the same for `hedge_rule`, `scout_rule` and `perfect`, each read from `Score.value`. The Perfect baseline is a mark and divides nothing, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).
- **A check, not a source.** When `log.results` holds the `scenario_score` metric, `score`, `lo` and `hi` must equal it to `1e-9`, else `scenario_scores` raises `ValueError` naming the log. This is how the layer knows it read the right numbers.

### Flags

`flags` is a string of zero or more symbols, in this order.

| Symbol | Means | Rule |
|---|---|---|
| `†` | A run gave up | `failed > 0`. The legend gives the count |
| `‡` | Retries ran high | `retry_share > RETRY_FLAG`, see [defaults](#defaults) |
| `¶` | The model finished the canary | The `recognition` table has a row for `model` with `canary_finished` true, see [recognition](../../pilot/provider-checks.md#recognition) |

- **A flag never drops a row.** Every model stays scored on every seed, see the [retry rule](../../harness/prompts.md#retry-rule).
- **`¶` goes on every score of that model**, in every table, as the pilot page says. With `recognition` as `None` it is never set.
- **A headline's flags** are the union of its scenarios' flags.

### Headlines

- **The plain mean** of the result row's scenario scores, `scenarios` saying how many, as the [headline metric](../harness/scorer.md#headline). A full headline has eight.
- **Bars** resample seeds within every scenario with one rng seeded `BOOTSTRAP_SEED`, take the mean of the pooled scores, and report the 2.5th and 97.5th percentiles. Scenarios are never resampled, see [error bars](../../design/scoring.md#error-bars).
- **Weakest** is the lowest scenario score, its trait and its value, ties to `SCENARIOS` order, as the [weakest trait metric](../harness/scorer.md#weakest-trait).

### Paired gap

Every model plays the same seeds, so a gap between two result rows is paired by seed and the world's luck cancels, see [error bars](../../design/scoring.md#error-bars).

- **`paired_gap(runs, a, b)`** requires `a.seed_set == b.seed_set` and `a.engine_hash == b.engine_hash`, else `ValueError`. It uses the `seed_index` values both rows scored, `n_shared` saying how many, ordered by `seed_index`.
- **`diff`** is `a`'s pooled score minus `b`'s on the shared seeds. **`lo`, `hi`**: `BOOTSTRAP_DRAWS` draws of one set of seed indices, applied to both, the 2.5th and 97.5th percentiles of the difference of the two pooled scores. The rng is seeded `BOOTSTRAP_SEED`.
- **The `headline` row** resamples within every scenario as the headline bar does, with the same indices for both rows, and differences the two means.
- **A row against itself** gives `diff == lo == hi == 0`.

### Scenario gap

The same pairing across two scenarios of one result row, for the twin tapes in [seeds](../../design/scoring.md#seeds).

- **`scenario_gap(runs, key, a, b, seeds)`** is `a`'s pooled score minus `b`'s on the seeds both scored, or on `seeds` when given, with one set of indices per draw.
- **The pairs the pilot reads**, see [up against down](../../pilot/provider-checks.md#up-against-down): One shock against Down switch, Up switch against No change, Up switch then down switch against Up switch on the seeds whose Up switch kind is not `short`, Switch then shock against Down switch.

### Public gap

- **`public_gap(runs, model, reasoning, skin)`** takes the two result rows that differ only in `seed_set`, else `ValueError` naming what else differs, and reports public minus held-out per scenario and for the headline, see [the public gap](../../harness/contamination.md#the-public-gap).
- **There is no pairing.** The two seed sets are different worlds, so each set is resampled on its own with its own indices from one rng, and the interval is on the difference of the two draws.

### Spread and sampling share

- **`spread`** is the SD of `run_score` over seeds, `ddof=1`, and its 10th percentile with linear interpolation, per result row and scenario, see [spread](../../design/scoring.md#spread). `n` is the seeds. One seed gives NA.
- **`sampling_share`** takes an `epochs="all"` table. Per result row and scenario, `within_sd` is the root of the mean over seeds of the variance over epochs, `total_sd` is the SD of all rows, and `share` is `within_sd² / total_sd²`, see [repeats](../../pilot/provider-checks.md#repeats). A seed with one epoch is left out of `within_sd` and `seeds` says how many were used.

### Switch kinds

Which kind of switch each seed drew, so run scores can be split by it, see [up and down](../../pilot/engine-checks.md#up-and-down).

- **One tape per distinct `(scenario, seed_set, seed_index, engine_hash, own_scale)`** in the table. The seed is `load_seeds(seed_set)[seed_index]`, so a held-out seed is read from the private seed file on the maintainer's machine and never from the table. The config is `scenario_config(scenario, rounds=..., own_scale=...)` with the row's knobs, and `engine_hash` of it must equal the row's, else `ValueError`.
- **`kind`** reads the first `Event` with `shape == "switch"`: `numbers["kind"]`, and `short` when `numbers["short"] == 1`. `none` when the scenario has no switch. The tape is dropped as soon as the word is read, and nothing else from it reaches any table.
- **Nothing is cached to disk.** Tapes are rebuilt every call, as a cache would be a tape on disk, see [tape](../engine/tape.md#interface).

### Noise threshold

The full study headline, see [noise threshold](../../design/scoring.md#noise-threshold). It needs one result row per setting of the [noise grid](../../pilot/engine-checks.md#noise-grid), all else equal.

- **The curve.** `noise_threshold(runs, key)` takes a `ResultKey` with `own_scale` as `None` and collects every result row that equals it in all other fields and has `own_scale` set. Fewer than three settings raise `ValueError`.
- **The axis** is signal to noise, `snr = signal_points(config) / own_scale`, with `x = log(snr)`. `signal_points(config)` is the midpoint of `size_points` of the first `SwitchSpec` in `config.events`, read from `scenario_config("down_switch")`, so it is the switch size in level points the grid pins, see [pinning](../engine/tape.md#pinning). A config with no `SwitchSpec` raises `ValueError`.
- **The floor** is the Complacent baseline's headline on the same logs: the plain mean over scenarios of the `complacent` mark, at the quietest setting. It does not move with noise, as the design says, and a test checks it within `0.02` across settings.
- **The fit** is `h(x) = floor + (1 − floor) / (1 + exp(−k (x − x0)))` by `scipy.optimize.curve_fit` on the settings' headlines, with `k > 0` bounded and `x0` free, from a start of `k = 1` and `x0` the mean of `x`.
- **The threshold** is `snr = exp(x0)`, where the model sits half way between the floor and 1. `snr_80` is where `h = floor + 0.8 (1 − floor)`, `x0 + log(4) / k`. `own_scale` is `signal_points / snr`.
- **Status.** `crossed` when the headlines straddle the half way mark within the grid. `off the noisy end` when the headline is above it at every setting: the model reads every world on the grid, extend it to noisier settings. `off the quiet end` when below at every setting. Off the grid, `snr`, `lo`, `hi`, `snr_80` and `own_scale` are `None` and no fit is reported.
- **Bars.** `BOOTSTRAP_DRAWS` draws with one rng: resample seeds within every scenario at every setting, recompute the headlines, refit. `lo` and `hi` are the 2.5th and 97.5th percentiles of `exp(x0)` over the draws that crossed. `uncrossed_draws` counts the rest, and the table says so beside the bar.

## Defaults

| Name | Default | Why this number | Check |
|---|---|---|---|
| `RETRY_FLAG` | 0.1 | One round in ten needing a retry is a model that struggles with the tool, not a bad round | [Retry share that marks a bar](../../pilot/decisions.md#provider-checks) |
| `signal_points` | midpoint of `size_points`, 8 at the engine defaults | The switch size the grid pins, see [config defaults](../engine/config.md#defaults) | [Switch size in level points on the noise grid](../../pilot/decisions.md#engine-checks) |

## Invariants

- A result row of `baseline/uniform` scores exactly 0 and one of `baseline/discerning` exactly 1 in every scenario, and `complacent` lies between them on every switch scenario, see [scorer invariants](../harness/scorer.md#invariants).
- `scenario_scores` equals the log's `scenario_score` metric wherever the log has one.
- `paired_gap(runs, a, a)` is all zeros. `paired_gap(runs, a, b).diff == −paired_gap(runs, b, a).diff`.
- `noise_threshold` gives the same `Threshold` on every machine for the same logs.
- `switch_kinds` on public seeds agrees with `make_tape` called by hand, and writes nothing.

## Pilot decides

- `RETRY_FLAG`, see [defaults](#defaults).
- `signal_points`, through the engine's `size_points`, see [defaults](#defaults).

## Not decided

- Whether the public gap should be reported for the headline only, as the per-scenario rows on two different seed sets are noisy. Decide when the first held-out run exists.
- Whether `noise_threshold` should fit the floor too, as a third parameter, if the Complacent baseline's headline turns out to move with noise after all. Decide when the [noise grid](../../pilot/engine-checks.md#noise-grid) check has run.

## Verify before code

- **`scipy.optimize.curve_fit` with bounds** returns a deterministic fit for the same inputs. `noise_threshold` waits on it.
