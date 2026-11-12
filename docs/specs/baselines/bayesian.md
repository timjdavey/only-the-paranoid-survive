# Bayesian

## Purpose

`Bayesian` is the baseline that knows how the world works and reads only its own record. It keeps a belief over each channel's base level in the engine's own family, turns the belief into quantiles on `QUANTILE_LEVELS`, and hands them to a [forecast rule](forecast.md), so `Bayesian(rule="odds")` is the Timestral odds row with a belief in place of a forecaster. Its prior and rule are set by the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier), which plays a few of a fixed family of both on timelines. It is a player with a mark on every bar, never the yardstick, see [the Bayesian frontier](../../design/baselines.md#the-bayesian-frontier).

## Interface

```python
HAZARDS = (0.005, 0.01, 0.025, 0.05, 0.1)            # the frontier's hazards, pilot to confirm
BAYESIAN_RULES = ("top-pick", "odds", "explore-1", "explore-2", "explore-5", "lookahead")
LOOKAHEAD_DRAWS = 100

@dataclass(frozen=True, eq=False)
class Belief:                                # the belief for view.round, one entry per channel. Read only arrays, compared by identity
    mean: np.ndarray                         # predictive mean of next round's level
    sd: np.ndarray                           # predictive SD of next round's level
    changed: np.ndarray                      # chance the base level has jumped since round 1
    quantiles: np.ndarray                    # (channels, len(QUANTILE_LEVELS)), ascending along the last axis

@dataclass(frozen=True)
class Bayesian:                              # peeks: ClassVar[bool] = False
    hazard: float = 0.01                     # chance per round that a channel's base level jumps
    rule: str = "odds"                       # one of BAYESIAN_RULES
    draws: int = ODDS_DRAWS                  # samples behind the quantiles
    lookahead_draws: int = LOOKAHEAD_DRAWS   # simulated next rounds per candidate, rule "lookahead" only
    def belief(self, view: View) -> Belief

bayesian: Policy    # Bayesian() at the defaults
```

- **Handed round 1 and the dials.** It reads `view.start` for each channel's role and `view.dials` for the weather, read noise, ladder ranges and run length, see [view](../engine/view.md#view). It never reads `view.timeline`.
- **State is derived, never kept.** Each call's state is the record replayed from round 1, so the same view gives the same split, see [conventions](README.md#conventions). [The cache](#the-cache) saves the work and changes no number.

## Behaviour

### The family

One channel, independent of every other. Round `t`, a bet `bet` on it:

    weather   w_t = ρ w_{t−1} + e_t,  e_t ~ N(0, σ_w² (1 − ρ²)),  σ_w² = own_scale² + factor_scale²
    base      b_t = b_{t−1} with chance 1 − hazard, else b_t ~ jump prior
    reading   y_t = b_t + w_t + v_t,  v_t ~ N(0, read_noise_k² / bet),  only when bet > 0

- **`ρ` is `dials.persistence`** and the other three numbers are the dials of the same names.
- **The weather SD is a bound.** A channel's weather is own weather plus loading times the shared factor, and loadings are drawn per seed and not handed, so the belief uses the largest SD any loading of 1 could give. The hedge's loading is smaller still, so the bound holds for every channel.
- **The shared factor and the hedge are not modelled.** The belief reads a shock as a possible switch, and the One shock score is the price of that. Modelling the tell is [not decided](#not-decided).

### The filter

Per channel, a run-length filter after Adams and MacKay 2007, with a Kalman state per run length: the mean of `(b, w)` and its 2 by 2 covariance. Run length `r` means the base has held for `r` rounds.

- **Round 1** has one run, `r = 0`, with `b` from the role prior and `w ~ N(0, σ_w²)`, independent. No jump comes before round 1.
- **Round `t`'s reading.** For every run, when the channel had a reading on round `t`: the likelihood of `y` under the run's predictive `N(b + w, var(b + w) + read_noise_k² / bet)`, then the Kalman update. With no reading the likelihood is 1 and there is no update. Each run's weight is multiplied by its likelihood, then the weights are normalised.
- **Into round `t + 1`.** Every run takes the predict step, `b` unchanged, `w ← ρ w`, the covariance as the weather equation says, and grows to `r + 1` with its weight times `1 − hazard`. A new run `r = 0` starts with weight `hazard`: `b` from the jump prior, `w` the old runs' mixture of predicted `w` collapsed to one Gaussian, no covariance between them.
- **So the state for round `t`** has had `t − 1` chances to jump, the jump into round `t` included. The belief is the state for `view.round`, before its reading, see [the belief](#the-belief).
- **Weights are kept in logs**, so a long run of unlikely readings never underflows to 0.
- **No pruning.** At 40 rounds there are at most 40 runs a channel. Pruning for longer runs is [not decided](#not-decided).

### Priors

Every prior is a Normal from a `Range` `(lo, hi)` on the dials: mean `(lo + hi) / 2`, SD `(hi − lo) / 4`, with the SD at least 1 level point.

| Prior | Range | Note |
|---|---|---|
| `start.leader` | `dials.leader_base` | |
| `start.runner_up` | `dials.leader_base` less `dials.runner_up_gap_points` | Mean is the leader's mean minus the gap's, variance is the two variances summed |
| `start.field`, hedge excluded | `dials.field_base` | |
| `start.hedge` | `dials.hedge_base` | |
| Jump prior, any channel | `dials.hedge_base` low to `dials.leader_base` high | After a jump the base could be anywhere on the ladder |

### The belief

`belief(view)` runs the filter over the record and returns the predictive for `view.round`, the round about to be played, per channel.

- **The predictive of a run** is its `b + w` in the state for `view.round`. The channel's predictive is the mixture of its runs by weight. `mean` and `sd` are the mixture's.
- **`changed`** is `1 − weight` of the run that began on round 1. A channel with no reading on any round has `changed == 1 − (1 − hazard)^(view.round − 1)` exactly, as every likelihood is 1. Its `mean` is `(1 − changed) × its role's prior mean + changed × the jump prior's mean`, as every run's weather mean is 0 and every jump draws from the jump prior.
- **`quantiles`** are `draws` samples from the mixture per channel, read at `QUANTILE_LEVELS` by `np.quantile`'s linear method, which sorts and interpolates. With `rng = default_rng(0)`: one `rng.random((draws, channels))` picks each sample's run by the cumulative weights, then one `rng.standard_normal((draws, channels))` places it in that run's Normal. No row is `NaN`: every channel has a prior, so a channel never explored is forecast from its prior and the hazard, which is what makes the odds rule explore it once enough rounds have passed.

### Rules

- **Round 1** is `budget` on `start.leader` whatever the rule, as the hedge rule is handed round 1, see [rules](rules.md#hedge-rule).
- **The five forecast rules.** For `rule` in `FORECAST_RULES`, the split is `FORECAST_RULES[rule](belief(view).quantiles, view.budget)`, see [the rules](forecast.md#the-rules).
- **`lookahead`** is one-step value of information over the five:
  - The candidates are the five rules' splits on this round's quantiles, in `FORECAST_RULES` order, equal splits kept once.
  - For each candidate, `lookahead_draws` simulated next rounds: this round's level per channel from the predictive, a reading on each channel the candidate funds with read noise at its bet, the filter run one more round on a copy of the state, and `best`, the highest mean over channels of the predictive for `view.round + 1`.
  - **The draws are shared**, so the comparison between candidates is paired. With `rng = default_rng(1)`, three arrays of shape `(lookahead_draws, channels)`, in order: `rng.random` picks the run, `rng.standard_normal` places the level in it, and `rng.standard_normal` is the read noise `z`. A funded channel reads `level + read_noise_k / sqrt(bet) × z`, not rounded.
  - Its value is `sum(bet_c / budget × mean_c)` this round plus `(dials.rounds − view.round) × mean of best` over the draws.
  - The split is the candidate with the highest value, the first on a tie. On the last round the second term is 0, so it exploits.
  - A candidate rule that raises, such as an explore rule too big for the view, raises out of the lookahead too.
- **Not the Complacent baseline at a hazard near 0.** The belief forecasts weather, which persists. So a leader with a low base in a bad spell can forecast below an unread runner-up, and a top pick moves off it. Only on a timeline with no weather and no read noise does it hold as the Complacent baseline does.
- **Construction checks** `0 < hazard < 1`, `rule in BAYESIAN_RULES`, `draws ≥ 1` and `lookahead_draws ≥ 1`, else `ValueError`. An explore rule's own check on `explore × (channels − 1) < budget` runs when it is called, see [forecast](forecast.md#the-rules).

### The cache

A run of 40 rounds would replay 780 rounds in all, so the filter's states are cached. Private to `filter.py`, and no policy's split depends on it.

- **Keyed by the family and the record's rows.** The state for a record is the state for all its rows but the last, taken through that last row. `play` adds one row a call, so each call runs the filter for one round.
- **Never by the record's length**, which would hand one timeline's state to another, see [conventions](README.md#conventions).
- **A hit equals a replay to the bit.** The filter is a fold over the rows, so a cached state taken one row on runs the same sums in the same order as a replay from round 1.
- **The family is built once** for each `start`, `dials`, channel count and hazard, and is compared by identity, as it holds arrays.
- **The last `STATE_CACHE` states are kept**, 128. A state is six arrays of one float per channel and run, so under 20 KB at 40 rounds. Every cached array is read only.
- **The fixed draws are drawn once.** The belief's two arrays and the lookahead's three come from a seed and a shape that never change, so [`fixed_draws`](forecast.md#the-rules) hands back the same read only arrays on every call.

## Defaults

Every number is **pilot to confirm** by the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier).

| Name | Default | Why |
|---|---|---|
| `hazard` | 0.01 | The best headline of the five hazards the pilot played, see [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier). About four jumps a run over the ten channels at 40 rounds |
| `rule` | `odds` | Explores in proportion to its own doubt, so it needs no explore size |
| `HAZARDS` | 0.005 to 0.1 | A factor of 2 to 2.5 apart, from one jump in 200 rounds to one in 10 |
| `draws` | `ODDS_DRAWS` | As `Odds`, a convention |
| `lookahead_draws` | 100 | Enough to rank five candidates, cheap enough for a thousand seeds. A convention |

## Invariants

- `bayesian` and every `Bayesian(hazard, rule)` over `HAZARDS` and `BAYESIAN_RULES` returns a valid split for every view: `channels` ints, none negative, summing to `budget`.
- Called twice on one view it gives equal splits and equal quantiles. Every quantile row is finite and ascending.
- A split and a belief are the same to the bit with the cache warm, cold or cleared between calls.
- `0 ≤ changed ≤ 1` on every channel.
- The layer still imports nothing outside `paranoid.engine`, numpy and the standard library.

## Pilot decides

- `hazard`, `rule` and whether `HAZARDS` is wide enough, see [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier).

## Not decided

- **Modelling the tell.** A belief with the shared factor and the hedge's loading would tell a shock from a switch. It needs a loading per channel, which is drawn per seed. Decide once the frontier's One shock scores are read.
- **The jump prior's centre.** The ladder prior, as here, or a Normal round the old base. Decide when the first frontier runs.
- **Pruning run lengths** for runs longer than 40 rounds, if a hard variant needs them.
- **The weather bound.** Whether to use the loading range's midpoint instead of 1, which would narrow the belief and raise false alarms on high-loading channels.
