# Scores

## Purpose

The maths over the run table. Scenario scores and headlines per result row, the marks the fixed baselines put on each bar, the flags, the gaps between two rows paired by seed, the public gap, spread, the switch kind each seed drew, and the noise threshold. Every pooled number goes through the harness's `pooled_score` and `bootstrap`, so a table here equals the log's own metrics. The design is in [scoring](../../design/scoring.md).

## Interface

```python
RETRY_FLAG = 0.1                       # retry share that flags a bar, pilot to confirm
RECOGNITION_FLAG = 0.25                # recognition hit share that flags a model, pilot to confirm

def load_recognition(path: Path) -> pd.DataFrame
# model, skin, lint_hits, canary_finished. The reply column is dropped on read and never returned

def scenario_scores(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey and scenario: the key's columns, scenario, trait, score, lo, hi, n, failed,
# retry_share, cut_off_share, notes_share, compute_share, complacent, hedge_rule, scout_rule, perfect, flags

def headlines(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey: the key's columns, headline, lo, hi, scenarios, weakest_scenario, weakest_trait,
# weakest_score, flags

GAP_COLUMNS = ("pair", "diff", "lo", "hi", "n_shared")   # every gap function returns these columns

def paired_gap(runs, a: ResultKey, b: ResultKey) -> pd.DataFrame            # one row per scenario, plus "headline"
def scenario_gap(runs, key: ResultKey, a: str, b: str, seeds: Sequence[int] | None = None) -> pd.DataFrame  # one row
def public_gap(runs, model: str, reasoning: str, skin: str) -> pd.DataFrame # one row per scenario, plus "headline"

def spread(runs) -> pd.DataFrame                 # per ResultKey and scenario: sd, p10, n
def sampling_share(runs) -> pd.DataFrame         # per ResultKey and scenario: within_sd, total_sd, share, seeds, epochs

def switch_kinds(runs) -> pd.DataFrame           # per scenario, seed_set, seed_index, engine_hash, game_rounds, inertia, own_scale: kind

def signal_points(config: ScenarioConfig) -> float

@dataclass(frozen=True)
class Threshold:
    snr: float | None                 # the signal to noise at the half way crossing
    lo: float | None
    hi: float | None
    snr_80: float | None              # the 80% crossing
    own_scale: float | None           # snr as an own_scale, for reading against the grid
    floor: float                      # the Complacent baseline's headline at the quietest setting
    floor_drift: float                # how far that headline moves across the grid, max minus min
    status: Literal["crossed", "off the noisy end", "off the quiet end"]
    uncrossed_draws: int

def noise_threshold(runs, key: ResultKey) -> Threshold
```

Every function here takes the run table after [`mean_over_epochs`](runs.md#mean-over-epochs), except `sampling_share`, which takes it as `load_runs` gives it.

## Behaviour

### Pooling

- **Every pooled score is `pooled_score(gains, gaps)`** from the harness, over the rows of one result row and scenario that did not error, see [pooling](../harness/scorer.md#pooling). Never a mean of run scores.
- **Every bar is `bootstrap(gains, gaps)`** at its defaults, `BOOTSTRAP_DRAWS` and `BOOTSTRAP_SEED`, so the bars equal the log's and are the same on every machine.
- **Rows are ordered by `seed_index`** before any draw, and scenarios are walked in `SCENARIOS` order whenever one rng serves several, so the bootstrap sees the same sequence as the metric did.

### Scenario scores

- **Group by `ResultKey` and `scenario`.** `score`, `lo`, `hi` as above. `n` is the rows scored, `failed` the rows with `gave_up`, as in the [scenario score metric](../harness/scorer.md#scenario-score).
- **`trait`** is `TRAITS[scenario]`.
- **`retry_share`** is `sum(retry_rounds) / sum(rounds)` and **`cut_off_share`** is `sum(cut_offs) / sum(rounds)`, as the [retry share metric](../harness/scorer.md#retry-share).
- **`notes_share`** is `sum(notes_rounds) / sum(rounds)` and **`compute_share`** is `sum(compute_rounds) / sum(rounds)`, as the [tool use share metric](../harness/scorer.md#tool-use-share).
- **The marks** are the fixed baselines' pooled scores on the same seeds: `complacent` is `pooled_score(complacent − uniform, gap)`, and the same for `hedge_rule`, `scout_rule` and `perfect`, each read from `Score.value`. The Perfect baseline is a mark and divides nothing, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).
- **A check, not a source.** When `log.results` holds the `scenario_score` metric and the log has one epoch, `score`, `lo` and `hi` must equal it to `1e-9`, else `scenario_scores` raises `ValueError` naming the log. This is how the layer knows it read the right numbers. At more than one epoch the check is skipped, see [verify before code](runs.md#verify-before-code).

### Flags

`flags` is a string of zero or more symbols, in this order.

| Symbol | Means | Rule |
|---|---|---|
| `†` | A run gave up | `failed > 0`. The legend gives the count |
| `‡` | Retries ran high | `retry_share > RETRY_FLAG`, see [defaults](#defaults) |
| `§` | The model recognised the prompt | The model's share of `recognition` rows with `lint_hits > 0`, over every skin probed, is above `RECOGNITION_FLAG`, see [recognition](../../pilot/provider-checks.md#recognition) |
| `¶` | The model finished the canary | The `recognition` table has a row for `model` with `canary_finished` true |

- **A flag never drops a row.** Every model stays scored on every seed, see the [retry rule](../../harness/prompts.md#retry-rule).
- **`§` and `¶` go on every score of that model**, in every table, as the pilot page says. With `recognition` as `None` neither is set.
- **`load_recognition` is the only reader of the recognition CSV.** It keeps `model`, `skin`, `lint_hits` and `canary_finished` and drops `reply` before returning, so no function in the layer can hold a reply, see [what never reaches a log or a prompt](../README.md#what-never-reaches-a-log-or-a-prompt). The CSV is private whenever a held-out skin was probed, and nothing but these four columns leaves it.
- **A headline's flags** are the union of its scenarios' flags.

### Headlines

- **The plain mean** of the result row's scenario scores, `scenarios` saying how many, as the [headline metric](../harness/scorer.md#headline). A full headline has eight.
- **Bars** resample seeds within every scenario with one rng seeded `BOOTSTRAP_SEED`, scenarios in `SCENARIOS` order, take the mean of the pooled scores, and report the 2.5th and 97.5th percentiles. Scenarios are never resampled, see [error bars](../../design/scoring.md#error-bars). At one epoch `lo` and `hi` equal the log's `headline` metric to `1e-9`.
- **Weakest** is the lowest scenario score, its trait and its value, ties to `SCENARIOS` order, as the [weakest trait metric](../harness/scorer.md#weakest-trait).

### Gaps

Every gap function returns `GAP_COLUMNS`: `pair` names the scenario or `headline`, `diff` is the difference of two pooled scores, `lo` and `hi` its interval, `n_shared` the seeds it used.

### Paired gap

Every model plays the same seeds, so a gap between two result rows is paired by seed and the world's luck cancels, see [error bars](../../design/scoring.md#error-bars).

- **`paired_gap(runs, a, b)`** requires `a.setting.seed_set == b.setting.seed_set`, and within every scenario the same `engine_hash` on both sides, else `ValueError` naming what differs. The skin and the other knobs may differ, as the skin sensitivity, inertia and warm up checks are gaps across them. It uses the `seed_index` values both rows scored, `n_shared` saying how many, ordered by `seed_index`.
- **`diff`** is `a`'s pooled score minus `b`'s on the shared seeds. **`lo`, `hi`**: `BOOTSTRAP_DRAWS` draws of one set of seed indices, applied to both, the 2.5th and 97.5th percentiles of the difference of the two pooled scores. The rng is seeded `BOOTSTRAP_SEED`.
- **The `headline` row** resamples within every scenario as the headline bar does, with the same indices for both rows, and differences the two means.
- **A row against itself** gives `diff == lo == hi == 0`.

### Scenario gap

The same pairing across two scenarios of one result row, for the twin timelines in [seeds](../../design/scoring.md#seeds).

- **`scenario_gap(runs, key, a, b, seeds)`** is `a`'s pooled score minus `b`'s on the seeds both scored, or on `seeds` when given, with one set of indices per draw. `pair` is `"<a> − <b>"`.
- **The pairs the pilot reads**, see [up against down](../../pilot/provider-checks.md#up-against-down): One shock against Down switch, Up switch against No change, Up switch then down switch against Up switch on the seeds whose Up switch kind is not `short`, Switch then shock against Down switch.

### Public gap

- **`public_gap(runs, model, reasoning, skin)`** takes the two result rows of that model and reasoning whose `Setting` differs only in `seed_set`, else `ValueError` naming what else differs or which set is missing, and reports public minus held-out per scenario and for the headline, see [the public gap](../../harness/contamination.md#the-public-gap).
- **There is no pairing.** The two seed sets are different worlds, so each set is resampled on its own with its own indices from one rng, and the interval is on the difference of the two draws. `n_shared` is the smaller seed count.

### Spread and sampling share

- **`spread`** is the SD of `run_score` over seeds, `ddof=1`, and its 10th percentile with linear interpolation, per result row and scenario, see [spread](../../design/scoring.md#spread). `n` is the seeds. One seed gives NA.
- **`sampling_share`** takes the table with one row per epoch. Per result row and scenario, `within_sd` is the root of the mean over seeds of the variance over epochs, `total_sd` is the SD of all rows, and `share` is `within_sd² / total_sd²`, see [repeats](../../pilot/provider-checks.md#repeats). A seed with one epoch is left out of `within_sd` and `seeds` says how many were used.

### Switch kinds

Which kind of switch each seed drew, so run scores can be split by it, see [up and down](../../pilot/engine-checks.md#up-and-down).

- **One timeline per distinct `(scenario, seed_set, seed_index, engine_hash, game_rounds, inertia, own_scale)`** in the table. The seed is `load_seeds(seed_set)[seed_index]`, so a held-out seed is read from the private seed file on the maintainer's machine and never from the table. The config is `scenario_config(scenario, rounds=game_rounds, inertia=..., own_scale=...)` with the row's knobs, and `engine_hash` of it must equal the row's, else `ValueError`.
- **`kind`** reads the first `Event` with `shape == "switch"`: `numbers["kind"]`, and `short` when `numbers["short"] == 1`. `none` when the scenario has no switch. The timeline is dropped as soon as the word is read, and nothing else from it reaches any table.
- **A kind per held-out seed is published** in the pilot's tables. It is one word per world and the engine is public, so it was weighed: it narrows a 64-bit seed by at most two bits and places nothing.
- **Nothing is cached to disk.** Timelines are rebuilt every call, as a cache would be a timeline on disk, see [timeline](../engine/timeline.md#interface).

### Noise threshold

The full study headline, see [noise threshold](../../design/scoring.md#noise-threshold). It needs one result row per setting of the [noise grid](../../pilot/engine-checks.md#noise-grid), all else equal.

- **The curve.** `noise_threshold(runs, key)` collects every result row with `key`'s model and reasoning whose `Setting` equals `key.setting` in every field but `own_scale`, and has `own_scale` set. Fewer than three settings raise `ValueError`.
- **The axis** is signal to noise, `snr = signal_points(config) / own_scale`, with `x = log(snr)`. `signal_points(config)` is the midpoint of `size_points` of the first `SwitchSpec` in `config.events`, read from `scenario_config("down_switch")`, so it is the switch size in level points the grid pins, see [pinning](../engine/timeline.md#pinning). `own_scale` is the weather's SD per round, see [config](../engine/config.md#fields), so the ratio is the [glossary's](../../glossary.md#scoring). A config with no `SwitchSpec` raises `ValueError`.
- **The floor** is the Complacent baseline's headline on the same logs: the plain mean over scenarios of the `complacent` mark, at the quietest setting. The design says it does not move with noise. `floor_drift` is how far it did move across the grid, and the table shows it beside the floor so a reader can judge, see [not decided](#not-decided).
- **The fit** is `h(x) = floor + (1 − floor) / (1 + exp(−k (x − x0)))` by `scipy.optimize.curve_fit` on the settings' headlines, with `k > 0` bounded and `x0` free, from a start of `k = 1` and `x0` the mean of `x`.
- **The threshold** is `snr = exp(x0)`, where the model sits half way between the floor and 1. `snr_80` is where `h = floor + 0.8 (1 − floor)`, `x0 + log(4) / k`. `own_scale` is `signal_points / snr`.
- **Status.** `crossed` when the headlines straddle the half way mark within the grid. `off the noisy end` when the headline is above it at every setting: the model reads every world on the grid, extend it to noisier settings. `off the quiet end` when below at every setting. Off the grid, `snr`, `lo`, `hi`, `snr_80` and `own_scale` are `None` and no fit is reported.
- **Bars.** `BOOTSTRAP_DRAWS` draws with one rng: resample seeds within every scenario at every setting, recompute the headlines, refit. `lo` and `hi` are the 2.5th and 97.5th percentiles of `exp(x0)` over the draws that crossed. `uncrossed_draws` counts the rest, and the table says so beside the bar.

## Defaults

| Name | Default | Why this number | Check |
|---|---|---|---|
| `RETRY_FLAG` | 0.1 | One round in ten needing a retry is a model that struggles with the tool, not a bad round | [Retry share that marks a bar](../../pilot/decisions.md#provider-checks) |
| `RECOGNITION_FLAG` | 0.25 | A model that names the test on a quarter of probes has a fair chance of knowing where it is on any run | [Recognition, share that marks a bar](../../pilot/decisions.md#provider-checks) |
| `signal_points` | midpoint of `size_points`, 8 at the engine defaults | The switch size the grid pins, see [config defaults](../engine/config.md#defaults) | [Switch size in level points on the noise grid](../../pilot/decisions.md#engine-checks) |

## Invariants

- A result row of `baseline/uniform` scores exactly 0 and one of `baseline/discerning` exactly 1 in every scenario, and `complacent` lies between them on every switch scenario, see [scorer invariants](../harness/scorer.md#invariants).
- `scenario_scores` and `headlines` equal the log's `scenario_score` and `headline` metrics wherever a one-epoch log has them.
- `paired_gap(runs, a, a)` is all zeros. `paired_gap(runs, a, b).diff == −paired_gap(runs, b, a).diff`.
- `noise_threshold` gives the same `Threshold` on every machine for the same logs.
- `switch_kinds` on public seeds agrees with `make_timeline` called by hand, and writes nothing.
- No function here returns, logs or raises with a word from a recognition reply.

## Pilot decides

- `RETRY_FLAG` and `RECOGNITION_FLAG`, see [defaults](#defaults).
- `signal_points`, through the engine's `size_points`, see [defaults](#defaults).

## Not decided

- Whether the public gap should be reported for the headline only, as the per-scenario rows on two different seed sets are noisy. Decide when the first held-out run exists.
- Whether `noise_threshold` should fit the floor too, as a third parameter, if `floor_drift` turns out large once the [noise grid](../../pilot/engine-checks.md#noise-grid) check has run. Decide then, and set the drift that counts as large.

## Verify before code

- **`scipy.optimize.curve_fit` with bounds** returns a deterministic fit for the same inputs. `noise_threshold` waits on it.
