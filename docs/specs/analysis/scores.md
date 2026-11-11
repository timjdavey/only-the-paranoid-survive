# Scores

## Purpose

The maths over the run table. Scenario scores and headlines per result row, the marks the fixed baselines put on each bar, the flags, the gaps between two rows paired by seed, the public gap, spread, the switch kind each seed drew, and the noise threshold. Every pooled number goes through the harness's `pooled_score`, and every bar through its `bootstrap` or `draws_of`, so a table here equals the log's own metrics. The design is in [scoring](../../design/scoring.md).

## Interface

```python
RETRY_FLAG = 0.1                       # retry share that flags a bar, pilot to confirm
RECOGNITION_FLAG = 0.25                # recognition hit share that flags a model, pilot to confirm

def load_recognition(path: Path) -> pd.DataFrame
# model, skin, probe, lint_hits, canary_finished. The reply column is dropped on read and never returned

def scenario_scores(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey and scenario: the key's columns, scenario, trait, score, lo, hi, n, failed,
# retry_share, cut_off_share, notes_share, compute_share, complacent, hedge_rule, scout_rule, perfect, flags

def headlines(runs: pd.DataFrame, *, recognition: pd.DataFrame | None = None) -> pd.DataFrame
# one row per ResultKey: the key's columns, headline, lo, hi, scenarios, weakest_scenario, weakest_trait,
# weakest_score, flags

GAP_COLUMNS = ("pair", "diff", "lo", "hi", "n_shared")   # every gap function returns these columns

def paired_gap(runs, a: ResultKey, b: ResultKey) -> pd.DataFrame            # one row per scenario, plus "headline"
def scenario_gap(runs, key: ResultKey, a: str, b: str, seeds: Sequence[int] | None = None) -> pd.DataFrame  # one row
def public_gap(runs, key: ResultKey) -> pd.DataFrame                        # one row per scenario, plus "headline"

def spread(runs) -> pd.DataFrame                 # per ResultKey and scenario: sd, p10, n
def sampling_share(runs) -> pd.DataFrame         # per ResultKey and scenario: within_sd, total_sd, share, seeds, epochs

def switch_kinds(runs) -> pd.DataFrame
# per scenario, seed_set, seed_index, engine_hash, game_rounds, inertia, own_scale: switch_kind

def signal_points(config: ScenarioConfig) -> float

@dataclass(frozen=True)
class Threshold:
    key: ResultKey                    # the result row asked for
    settings: int                     # how many noise settings the curve has
    snr: float | None                 # the signal to noise at the half way crossing
    lo: float | None
    hi: float | None
    snr_80: float | None              # the 80% crossing
    own_scale: float | None           # snr as an own_scale, for reading against the grid
    k: float | None                   # the fit's steepness
    complacent: float                 # the Complacent baseline's headline at the quietest setting
    complacent_drift: float           # how far that headline moves across the grid, max minus min
    status: Literal["crossed", "off the noisy end", "off the quiet end"]
    uncrossed_draws: int

def noise_threshold(runs, key: ResultKey) -> Threshold
```

Every function here takes the run table after [`mean_over_epochs`](runs.md#mean-over-epochs), except `sampling_share`, which takes it as `load_runs` gives it. Rows that errored are in none of them.

## Behaviour

### Pooling

- **Every pooled score is `pooled_score(gains, gaps)`** from the harness, over the rows of one result row and scenario, see [pooling](../harness/scorer.md#pooling). Never a mean of run scores.
- **A scenario's bar is `bootstrap(gains, gaps)`** at its defaults, `BOOTSTRAP_DRAWS` and `BOOTSTRAP_SEED`, so it equals the log's and is the same on every machine.
- **Every other bar is built from `draws_of`.** A headline, a gap and a threshold each combine several pooled scores draw by draw, and `bootstrap` returns two percentiles, not the draws. The harness's `draws_of(gains, gaps, rng, BOOTSTRAP_DRAWS)` returns the pooled score of every draw, the same draws `bootstrap` makes. The draws are combined, then the bar is their 2.5th and 97.5th percentiles by `np.percentile`.
- **Rows are ordered by `seed_index`** before any draw, and scenarios are walked in `SCENARIOS` order whenever one rng serves several, so the draws are the ones the metric made.
- **Pairing is two rngs seeded alike.** Where two sides must resample the same seeds, each side gets its own `default_rng(BOOTSTRAP_SEED)` and is walked in the same order. Both sides hold the same seeds, so the two rngs draw the same indices and draw `i` is the same resample on both.

### Scenario scores

- **Group by `ResultKey` and `scenario`.** `score`, `lo`, `hi` as above. `n` is the rows scored, `failed` the rows with `gave_up`, as in the [scenario score metric](../harness/scorer.md#scenario-score).
- **`trait`** is `TRAITS[scenario]`.
- **`retry_share`** is `sum(retry_rounds) / sum(rounds)` and **`cut_off_share`** is `sum(cut_offs) / sum(rounds)`, as the [retry share metric](../harness/scorer.md#retry-share).
- **`notes_share`** is `sum(notes_rounds) / sum(rounds)` and **`compute_share`** is `sum(compute_rounds) / sum(rounds)`, as the [tool use share metric](../harness/scorer.md#tool-use-share).
- **The marks** are the fixed baselines' pooled scores on the same seeds: `complacent` is `pooled_score(complacent − uniform, gap)`, and the same for `hedge_rule`, `scout_rule` and `perfect`, each read from `Score.value`. The Perfect baseline is a mark and divides nothing, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).
- **The log's own metric is a check, not a source.** `load_runs` has already held each log's numbers against it, see [metric check](runs.md#metric-check).

### Flags

`flags` is a string of zero or more symbols, in this order.

| Symbol | Means | Rule |
|---|---|---|
| `†` | A run gave up | `failed > 0`. The legend gives the count |
| `‡` | Retries ran high | `retry_share > RETRY_FLAG`, see [defaults](#defaults) |
| `§` | The model recognised the prompt | Of the model's `recognition` rows whose `probe` is `round_1` or `round_20`, over every skin probed, the share with `lint_hits > 0` is above `RECOGNITION_FLAG`, see [recognition](../../pilot/provider-checks.md#recognition) |
| `¶` | The model finished the canary | The `recognition` table has a row for `model` with `canary_finished` true |

- **A flag never drops a row.** Every model stays scored on every seed, see the [retry rule](../../harness/prompts.md#retry-rule).
- **`§` and `¶` go on every score of that model**, at every reasoning setting and in every table, as the pilot page says. With `recognition` as `None` neither is set.
- **`load_recognition` is the only reader of the recognition CSV.** It keeps `model`, `skin`, `probe`, `lint_hits` and `canary_finished` and drops `reply` before returning, so no function in the layer can hold a reply, see [what never reaches a log or a prompt](../README.md#what-never-reaches-a-log-or-a-prompt). The CSV is private whenever a held-out skin was probed, and nothing but these five columns leaves it.
- **`probe` is kept so the canary rows stay out of the `§` share.** A canary reply is never a hit, so counting it would thin every share by a third.
- **A headline's flags** are the union of its scenarios' flags.

### Headlines

- **The plain mean** of the result row's scenario scores, `scenarios` saying how many, as the [headline metric](../harness/scorer.md#headline). A full headline has eight.
- **Bars** take one rng seeded `BOOTSTRAP_SEED` and one block of `draws_of` per scenario, in `SCENARIOS` order. The mean across scenarios of each draw is that draw's headline. Scenarios are never resampled, see [error bars](../../design/scoring.md#error-bars). At one epoch `lo` and `hi` equal the log's `headline` metric to `1e-9`.
- **Weakest** is the lowest scenario score, its trait and its value, ties to `SCENARIOS` order, as the [weakest trait metric](../harness/scorer.md#weakest-trait).

### Gaps

Every gap function returns `GAP_COLUMNS`: `pair` names the scenario or `headline`, `diff` is the difference of two pooled scores, `lo` and `hi` its interval, `n_shared` the seeds it used. On a `headline` row `n_shared` is the fewest seeds any of its scenarios used.

### Paired gap

Every model plays the same seeds, so a gap between two result rows is paired by seed. Level luck cancels, and read noise mostly does, as `read_noise_z` is shared, see [error bars](../../design/scoring.md#error-bars).

- **`paired_gap(runs, a, b)`** requires `a.setting.seed_set == b.setting.seed_set`, and within every scenario the same `engine_hash` on both sides, else `ValueError` naming what differs. The skin and the other knobs may differ, as the skin sensitivity, inertia and warm up checks are gaps across them. It uses the `seed_index` values both rows scored, ordered by `seed_index`. A scenario with no shared seed has no row, and no shared seed at all raises `ValueError`.
- **`diff`** is `a`'s pooled score minus `b`'s on the shared seeds. **`lo`, `hi`** are the percentiles of `a`'s draws minus `b`'s, paired as [pooling](#pooling) says. Each scenario row starts both rngs afresh.
- **The `headline` row** walks both rngs over the scenarios both rows scored, as the headline bar does, and differences the two means draw by draw.
- **A row against itself** gives `diff == lo == hi == 0`.

### Scenario gap

The same pairing across two scenarios of one result row, for the twin timelines in [seeds](../../design/scoring.md#seeds).

- **`scenario_gap(runs, key, a, b, seeds)`** is `a`'s pooled score minus `b`'s on the seeds both scored, or on those of `seeds` both scored when given, paired the same way. `pair` is `"<a> − <b>"`.
- **The pairs the pilot reads**, see [up against down](../../pilot/provider-checks.md#up-against-down): One shock against Down switch, Up switch against No change, Up switch then down switch against Up switch on the seeds whose Up switch kind is not `rise_short`, Switch then shock against Down switch.

### Public gap

- **`public_gap(runs, key)`** pairs `key` with the one result row of its model and reasoning whose setting differs from `key.setting` in `seed_set` and nothing else, see [comparing settings](runs.md#comparing-settings). It reports public minus held-out per scenario and for the headline, whichever side `key` is, see [the public gap](../../harness/contamination.md#the-public-gap).
- **No such row raises `ValueError`.** It names the seed set that is missing, or the fields in which the nearest row on the other set also differs. Two such rows raise too, naming both.
- **There is no pairing.** The two seed sets are different worlds, so each is resampled on its own from one rng, the public block first. A scenario row starts its rng afresh. The `headline` row walks one rng over every public block in `SCENARIOS` order, then every held-out block. `n_shared` is the smaller seed count.

### Spread and sampling share

- **`spread`** is the SD of `run_score` over seeds, `ddof=1`, and its 10th percentile with linear interpolation, per result row and scenario, see [spread](../../design/scoring.md#spread). `n` is the seeds. One seed gives NA.
- **`sampling_share`** takes the table with one row per epoch. Per result row and scenario, `within_sd` is the root of the mean over seeds of the variance over epochs, `total_sd` is the SD of all rows, and `share` is `within_sd² / total_sd²`, see [repeats](../../pilot/provider-checks.md#repeats). Both are taken with `ddof=0`, so with equal epochs per seed the part within seeds and the part between them add up to the whole, and the share runs from 0 to 1. A `total_sd` of 0 gives NA, as there is no spread to share. A seed with one epoch is left out of `within_sd` and `seeds` says how many were used.

### Switch kinds

Which kind of switch each seed drew, so run scores can be split by it, see [up and down](../../pilot/engine-checks.md#up-and-down).

- **One timeline per distinct `(scenario, seed_set, seed_index, engine_hash, game_rounds, inertia, own_scale)`** in the table. The seed is `load_seeds(seed_set)[seed_index]`, so a held-out seed is read from the private seed file on the maintainer's machine and never from the table. The config is `scenario_config(scenario, rounds=game_rounds, inertia=..., own_scale=...)` with the row's knobs, and `engine_hash` of it must equal the row's, else `ValueError`.
- **`switch_kind`** reads the first `Event` with `shape == "switch"`. It is `rise_short` when `numbers["short"] == 1`, else `numbers["kind"]`, which is `fall`, `fall_and_rise` or `rise`. `none` when the scenario has no switch. They are the words the pilot cells write, see [words the columns use](../harness/pilot.md#words-the-columns-use). The timeline is dropped as soon as the word is read, and nothing else from it reaches any table.
- **The column is `switch_kind`, never `kind`**, which in the run table is the model's, see [one row per run](runs.md#one-row-per-run).
- **A switch kind per held-out seed is published** in the pilot's tables. It is one word per world and the engine is public, so it was weighed: it narrows a 64-bit seed by at most two bits and places nothing.
- **Nothing is cached to disk.** Timelines are rebuilt every call, as a cache would be a timeline on disk, see [timeline](../engine/timeline.md#interface).

### Noise threshold

The full study headline, see [noise threshold](../../design/scoring.md#noise-threshold). It needs one result row per setting of the [noise grid](../../pilot/engine-checks.md#noise-grid), all else equal.

- **The curve.** `noise_threshold(runs, key)` collects every result row with `key`'s model and reasoning whose setting equals `key.setting` in every field but `own_scale`, see [comparing settings](runs.md#comparing-settings), and has `own_scale` set. `settings` is how many. Fewer than three raise `ValueError`, as do two rows at one `own_scale`, and a setting that scored other scenarios than the rest.
- **The axis** is signal to noise, `snr = signal_points(config) / own_scale`, with `x = log(snr)`. `signal_points(config)` is the midpoint of `size_points` of the first `SwitchSpec` in `config.events`, read from `scenario_config("down_switch")`, so it is the switch size in level points the grid pins, see [pinning](../engine/timeline.md#pinning). `own_scale` is the weather's SD per round, see [config](../engine/config.md#fields), so the ratio is the [glossary's](../../glossary.md#scoring). A config with no `SwitchSpec` raises `ValueError`.
- **`complacent`** is the Complacent baseline's headline on the same logs: the plain mean over scenarios of the `complacent` mark, at the quietest setting. The design says it does not move with noise. `complacent_drift` is how far it did move across the grid, and the table shows it beside it so a reader can judge, see [not decided](#not-decided).
- **The half way mark** is `complacent + (1 − complacent) / 2`.
- **Status.** `crossed` when one setting's headline is at or above the half way mark and another's is below it. `off the noisy end` when every headline is at or above it: the model reads every world on the grid, extend it to noisier settings. `off the quiet end` when every one is below. Off the grid, `snr`, `lo`, `hi`, `snr_80`, `own_scale` and `k` are `None`, `uncrossed_draws` is 0 and no fit is run.
- **The fit** is `h(x) = complacent + (1 − complacent) / (1 + exp(−k (x − x0)))` by `scipy.optimize.curve_fit` on the settings' headlines. `k` is bounded, see [defaults](#defaults), and `x0` is free. The start is `k = 1` and `x0` the mean of `x`. **A fit fails** when `curve_fit` raises `RuntimeError` or returns `k` within `1e-6` of its lower bound, as a flat or falling draw comes back that way rather than raising, see [checked](#checked). A failed fit on the logs' own headlines raises `ValueError` naming the key.
- **The threshold** is `snr = exp(x0)`, where the model sits half way between the Complacent baseline's headline and 1. `snr_80` is where `h = complacent + 0.8 (1 − complacent)`, `exp(x0 + log(4) / k)`. `own_scale` is `signal_points / snr`.
- **Bars.** One rng seeded `BOOTSTRAP_SEED`, walked over the settings from the smallest `own_scale` up and over the scenarios in `SCENARIOS` order within each, one block of `draws_of` apiece. Each draw gives a headline per setting, the status test is run on them with `complacent` held at the logs' value, and a draw that crosses is fitted. `lo` and `hi` are the 2.5th and 97.5th percentiles of `exp(x0)` over those fits, `None` when there are none.
- **`uncrossed_draws`** counts the draws that did not cross and the ones whose fit failed. The table says so beside the bar.

## Defaults

| Name | Default | Why this number | Check |
|---|---|---|---|
| `RETRY_FLAG` | 0.1 | One round in ten needing a retry is a model that struggles with the tool, not a bad round | [Retry share that flags a bar](../../pilot/decisions.md#provider-checks) |
| `RECOGNITION_FLAG` | 0.25 | A model that names the test on a quarter of probes has a fair chance of knowing where it is on any run | [Recognition, share that flags a bar](../../pilot/decisions.md#provider-checks) |
| `signal_points` | midpoint of `size_points`, 8 at the engine defaults | The switch size the grid pins, see [config defaults](../engine/config.md#defaults) | [Switch size in level points on the noise grid](../../pilot/decisions.md#engine-checks) |
| The fit's bound on `k` | 0.01 to 50 | A `k` of 50 takes the curve from a tenth to nine tenths of its rise inside a 9% change in signal to noise, far inside one step of any grid. So a larger `k` says nothing more, and the bound keeps a draw that looks like a step from running off | None. A convention, not a pilot knob |

## Invariants

- A result row of `baseline/uniform` scores exactly 0 and one of `baseline/discerning` exactly 1 in every scenario, and `complacent` lies between them on every switch scenario, see [scorer invariants](../harness/scorer.md#invariants).
- `scenario_scores` and `headlines` equal the log's `scenario_score` and `headline` metrics wherever a one-epoch log has them.
- `paired_gap(runs, a, a)` is all zeros. `paired_gap(runs, a, b).diff == −paired_gap(runs, b, a).diff`.
- No function here draws resample indices of its own. Every draw is `bootstrap`'s or `draws_of`'s.
- `noise_threshold` gives the same `Threshold` on every machine for the same logs.
- `switch_kinds` on public seeds agrees with `make_timeline` called by hand, and writes nothing.
- No function here returns, logs or raises with a word from a recognition reply.

## Pilot decides

- `RETRY_FLAG` and `RECOGNITION_FLAG`, see [defaults](#defaults).
- `signal_points`, through the engine's `size_points`, see [defaults](#defaults).

## Not decided

- Whether the public gap should be reported for the headline only, as the per-scenario rows on two different seed sets are noisy. Decide when the first held-out run exists.
- Whether `noise_threshold` should fit the Complacent baseline's headline too, as a third parameter, if `complacent_drift` turns out large once the [noise grid](../../pilot/engine-checks.md#noise-grid) check has run. Decide then, and set the drift that counts as large.

## Checked

Run on 2026-11-11 with scipy 1.18.1 and numpy 2.5.4.

| Question | Answer |
|---|---|
| Is `curve_fit` with bounds deterministic | Yes. The fit above on seven points gave the same `popt` and `pcov`, bit for bit, in four fresh processes. With bounds it uses the `trf` method, which draws no random numbers |
| How does `curve_fit` fail on a draw it cannot fit | It does not raise or warn. On five equal headlines, and on five that fall as `x` grows, it returns `k` at its lower bound, 0.01, with a finite `pcov`. So a fit is failed when `k` lands on that bound, see [noise threshold](#noise-threshold) |
