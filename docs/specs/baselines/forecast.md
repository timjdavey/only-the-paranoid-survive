# Forecast

## Purpose

A [forecast rule](../../glossary.md#the-study) turns a forecast of next round's levels, as quantiles per channel, into a split. A forecast policy calls one each round, see [policy](../forecasters/policy.md), and the Bayesian baseline does too, see [bayesian](bayesian.md). The rules have no model in them, so they are tested on hand-written quantiles. Why each is in the study is in [Timestral](../../design/baselines.md#timestral).

## Interface

```python
QUANTILE_LEVELS: tuple[float, ...]   # 21 levels, ascending: 0.01, 0.05, then 0.10 to 0.90 in steps of 0.05, then 0.95, 0.99
MEDIAN_INDEX = 10                    # QUANTILE_LEVELS[MEDIAN_INDEX] == 0.5
ODDS_DRAWS = 1000

class ForecastRule(Protocol):
    def __call__(self, quantiles: np.ndarray, budget: int) -> Bets: ...
    # quantiles (channels, len(QUANTILE_LEVELS)), ascending along the last axis, ties allowed. A row of NaN is a channel with no reading yet

@dataclass(frozen=True)
class TopPick: ...                            # budget on the highest median

@dataclass(frozen=True)
class TopPickWithExploreBets:
    explore: int                                 # on every channel but the top pick

@dataclass(frozen=True)
class Odds:
    draws: int = ODDS_DRAWS

top_pick: ForecastRule     # TopPick()
odds: ForecastRule         # Odds()
explore_1, explore_2, explore_5: ForecastRule          # TopPickWithExploreBets(1), (2), (5)

FORECAST_RULES: Mapping[str, ForecastRule]   # "top-pick", "odds", "explore-1", "explore-2", "explore-5"
```

- **The ids are the Timestral ids** in the [glossary](../../glossary.md#the-study) after `timestral/`, bar `odds-alone` and `odds-bet-aware`, which are `odds` with a different input. The forecasters layer maps them, see [the policies](../forecasters/policy.md#the-policies).
- **Every rule is a frozen dataclass with `__call__`**, like a policy, see [conventions](README.md#conventions). A rule is pure: same quantiles, same split.

## Behaviour

### The rules

| Rule | Bets |
|---|---|
| `TopPick` | `budget` on the channel with the highest median, `quantiles[:, MEDIAN_INDEX]`. Ties go to the lowest index |
| `TopPickWithExploreBets(explore)` | `explore` on every channel but the top pick, `budget − explore × (channels − 1)` on it. 91, 82 or 55 on the pick at the defaults for `explore_1`, `explore_2`, `explore_5` |
| `Odds(draws)` | `split_budget(p, budget)` where `p[c]` is the share of `draws` draws in which channel `c` is highest, lowest index on a tie. The draws are one `default_rng(0).random((draws, channels))`, a level per draw and channel, each read off that channel's quantile function by `np.interp` over `QUANTILE_LEVELS`. So the same quantiles give the same split on every call. The levels are not evenly spaced, and `np.interp` takes them as they are. A draw below 0.01 or above 0.99 takes the end quantile, as `np.interp` does |

- **A channel with no reading yet** has a `NaN` row. `TopPick` and `TopPickWithExploreBets` treat its median as lowest, and `Odds` gives it no draws. So `TopPick` and `Odds` give it 0, as `split_budget` never hands a leftover point to a weight of 0, and `TopPickWithExploreBets` gives it `explore`, which is how a dark channel gets read. `NaN` rows are masked before any argmax, as `np.argmax` returns the first `NaN`.
- **Every channel `NaN`** raises `ValueError`. There is nothing to forecast from, and the caller should have bet `uniform` instead, as a forecast policy does on an empty record, see [the policy](../forecasters/policy.md#the-policy).
- **`explore × (channels − 1)` must be below `budget`**, else `ValueError` when the rule is called, as `channels` is the array's.
- **A bad array** raises `ValueError`: not two dimensions, the last axis not `len(QUANTILE_LEVELS)`, a row that is neither all finite nor all `NaN`, or a finite row that falls anywhere. Equal neighbours pass. The rules never sort. Crossed quantiles are the forecaster's to fix, so a forecast policy sorts each row before it calls a rule, see [the arrays](../forecasters/policy.md#the-arrays).
- **Construction checks** `explore ≥ 1` for `TopPickWithExploreBets` and `draws ≥ 1` for `Odds`, else `ValueError`.
- **The draws are drawn once.** `Odds` asks for the same seed and shape on every call, so a private `fixed_draws(seed, draws, channels, normals)` keeps the arrays: one `rng.random((draws, channels))`, then `normals` arrays of `rng.standard_normal((draws, channels))`, from `default_rng(seed)`, all read only. The Bayesian baseline's belief and lookahead read theirs the same way, see [the cache](bayesian.md#the-cache).
- **A tiny share rounds to 0.** `Odds` can give a channel a bet of 0 and so a blank reading next round. The pilot watches how often, see [Timestral checks](../../pilot/provider-checks.md#timestral-checks).

## Defaults

| Constant | Value | Why |
|---|---|---|
| `QUANTILE_LEVELS` | 0.01, 0.05, 0.10 to 0.90 in steps of 0.05, 0.95, 0.99 | The 21 levels Timestral reports, read from its [model card](https://huggingface.co/mistralai/Timestral-209M) on 2026-11-10, and checked on the loaded model on 2026-11-11, see [checked](../forecasters/timestral.md#checked). A checkpoint with other levels raises on load |
| `MEDIAN_INDEX` | 10 | Where 0.5 sits in the list above. Rules read the median through it, never through a bare 10 |
| `ODDS_DRAWS` | 1000 | Enough that the share is within a point or two of the true odds. A convention, not a pilot knob |

## Invariants

- Every rule returns a valid split for any quantile array with at least one finite row: `channels` ints, none negative, summing to `budget`.
- A rule never edits the array it is given.
- `Odds` called twice on equal arrays gives equal splits.
- `FORECAST_RULES["explore-2"]` is `explore_2`, and so on for the five ids.
