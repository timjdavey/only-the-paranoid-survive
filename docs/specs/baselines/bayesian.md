# Bayesian

## Purpose

`Bayesian` is the baseline that knows how the world works and reads only its own record. It keeps a belief over each channel's base level in the engine's own family, turns the belief into quantiles on `QUANTILE_LEVELS`, and hands them to a [forecast rule](forecast.md), so `Bayesian(rule="odds")` is the Timestral odds row with a belief in place of a forecaster. Its prior and rule are set by the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier), which sweeps a fixed family of both on timelines. It is a player with a mark on every bar, never the yardstick, see [the Bayesian frontier](../../design/baselines.md#the-bayesian-frontier).

## Interface

```python
HAZARDS = (0.005, 0.01, 0.025, 0.05, 0.1)            # the frontier's hazards, pilot to confirm
BAYESIAN_RULES = ("top-pick", "odds", "explore-1", "explore-2", "explore-5", "lookahead")
LOOKAHEAD_DRAWS = 100

@dataclass(frozen=True)
class Belief:                                # the posterior for next round, one entry per channel
    mean: np.ndarray                         # predictive mean of next round's level
    sd: np.ndarray                           # predictive SD of next round's level
    changed: np.ndarray                      # chance the base level has jumped since round 1
    quantiles: np.ndarray                    # (channels, len(QUANTILE_LEVELS)), ascending along the last axis

@dataclass(frozen=True)
class Bayesian:                              # peeks: ClassVar[bool] = False
    hazard: float = 0.025                    # chance per round that a channel's base level jumps
    rule: str = "odds"                       # one of BAYESIAN_RULES
    draws: int = ODDS_DRAWS                  # samples behind the quantiles
    lookahead_draws: int = LOOKAHEAD_DRAWS   # simulated next rounds per candidate, rule "lookahead" only
    def belief(self, view: View) -> Belief

bayesian: Policy    # Bayesian() at the defaults
```

- **Handed round 1 and the dials.** It reads `view.start` for each channel's role and `view.dials` for the weather, read noise, ladder ranges and run length, see [view](../engine/view.md#view). It never reads `view.timeline`.
- **State is derived, never kept.** Each call replays the record from round 1, so the same view gives the same split, see [conventions](README.md#conventions).

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

- **Round 1** has one run, `r = 0`, with `b` from the role prior and `w ~ N(0, σ_w²)`, independent.
- **Each round**, for every run: the predict step, `b` unchanged, `w ← ρ w`, the covariance as the weather equation says. Then, when the channel had a reading this round, the likelihood of `y` under the run's predictive `N(b + w, var(b + w) + read_noise_k² / bet)`, and the Kalman update. With no reading the likelihood is 1 and there is no update.
- **A new run** `r = 0` starts every round: `b` from the jump prior, `w` the old runs' mixture of `w` collapsed to one Gaussian, no covariance between them. It takes the round's reading like any run.
- **Weights.** Run `r` grows to `r + 1` with weight `(1 − hazard) × weight_r × likelihood_r`. The new run has weight `hazard × likelihood_new`. Normalise over every run.
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

`belief(view)` runs the filter over the record and returns next round's predictive per channel.

- **The predictive of a run** is the predict step applied to its posterior with no reading, read as `b + w`. The channel's predictive is the mixture of its runs by weight. `mean` and `sd` are the mixture's.
- **`changed`** is `1 − weight` of the run that began on round 1. A channel with no reading on any round has `changed == 1 − (1 − hazard)^(round − 1)` exactly, as every likelihood is 1.
- **`quantiles`** are `draws` samples from the mixture per channel, drawn with `default_rng(0)` as `Odds` does, sorted, read at `QUANTILE_LEVELS` by linear interpolation. No row is `NaN`: every channel has a prior, so a channel never explored is forecast from its prior and the hazard, which is what makes the odds rule explore it once enough rounds have passed.

### Rules

- **Round 1** is `budget` on `start.leader` whatever the rule, as the hedge rule is handed round 1, see [rules](rules.md#hedge-rule).
- **The five forecast rules.** For `rule` in `FORECAST_RULES`, the split is `FORECAST_RULES[rule](belief(view).quantiles, view.budget)`, see [the rules](forecast.md#the-rules).
- **`lookahead`** is one-step value of information over the five:
  - The candidates are the five rules' splits on this round's quantiles, in `FORECAST_RULES` order, equal splits kept once.
  - For each candidate, `lookahead_draws` simulated next rounds with `default_rng(1)`: next round's level per channel from the predictive, a reading on each channel the candidate funds with read noise at its bet, the filter run one more round on a copy of the belief, and `best`, the highest predictive mean over channels after that.
  - Its value is `sum(bet_c / budget × mean_c)` this round plus `(dials.rounds − view.round) × mean of best` over the draws.
  - The split is the candidate with the highest value, the first on a tie. On the last round the second term is 0, so it exploits.
- **Construction checks** `0 < hazard < 1`, `rule in BAYESIAN_RULES`, `draws ≥ 1` and `lookahead_draws ≥ 1`, else `ValueError`. An explore rule's own check on `explore × (channels − 1) < budget` runs when it is called, see [forecast](forecast.md#the-rules).

## Defaults

Every number is **pilot to confirm** by the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier).

| Name | Default | Why |
|---|---|---|
| `hazard` | 0.025 | About one jump per channel per run at 40 rounds, the order of what the scenarios hold |
| `rule` | `odds` | Explores in proportion to its own doubt, so it needs no explore size |
| `HAZARDS` | 0.005 to 0.1 | A factor of 2 to 2.5 apart, from one jump in 200 rounds to one in 10 |
| `draws` | `ODDS_DRAWS` | As `Odds`, a convention |
| `lookahead_draws` | 100 | Enough to rank five candidates, cheap enough for a thousand seeds. A convention |

## Invariants

- `bayesian` and every `Bayesian(hazard, rule)` over `HAZARDS` and `BAYESIAN_RULES` returns a valid split for every view: `channels` ints, none negative, summing to `budget`.
- Called twice on one view it gives equal splits and equal quantiles. Every quantile row is finite and ascending.
- `0 ≤ changed ≤ 1` on every channel, and a channel never explored has `changed == 1 − (1 − hazard)^(round − 1)`.
- `Bayesian(hazard=1e-9, rule="top-pick")` plays every round of a No change timeline as the Complacent baseline does.
- The layer still imports nothing outside `paranoid.engine`, numpy and the standard library.

## Pilot decides

- `hazard`, `rule` and whether `HAZARDS` is wide enough, see [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier).

## Not decided

- **Output as an observation.** Output is exact and a linear sum of levels, so it is a noiseless reading of the agent's own mix. It couples the channels, so the belief leaves it out. Decide once the frontier shows how far the best player sits below the Discerning baseline.
- **Modelling the tell.** A belief with the shared factor and the hedge's loading would tell a shock from a switch. It needs a loading per channel, which is drawn per seed. Decide once the frontier's One shock scores are read.
- **The jump prior's centre.** The ladder prior, as here, or a Normal round the old base. Decide when the first frontier runs.
- **Pruning run lengths** for runs longer than 40 rounds, if a hard variant needs them.
- **The weather bound.** Whether to use the loading range's midpoint instead of 1, which would narrow the belief and raise false alarms on high-loading channels.
