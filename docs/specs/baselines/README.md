# Baselines spec

The baselines layer holds every fixed [baseline](../../design/baselines.md) as a pure function from what it may see to a split, and the forecast rules that turn a forecast's quantiles into a split. It is the strategies with no game and no story: the engine says what a policy sees and what a valid split is, this layer says what each baseline does with it. It imports the engine and numpy only, and knows nothing about skins, inspect_ai or any model. Why each baseline is in the study lives in [baselines](../../design/baselines.md) and [scoring](../../design/scoring.md#why-these-two-baselines).

## Pages

| Page | What it specifies |
|---|---|
| [policies](policies.md) | `uniform`, `discerning`, `complacent`, `perfect`, and `POLICIES`, the names the harness plays |
| [rules](rules.md) | `HedgeRule` and `ScoutRule`, the two players that read the tell, with their parameters |
| [forecast](forecast.md) | `ForecastRule`, `QUANTILE_LEVELS`, the rules that turn quantiles into bets, `FORECAST_RULES` |
| [bayesian](bayesian.md) | `Bayesian`, the belief in the engine's family through a forecast rule, `Belief`, and the frontier's `HAZARDS` and `BAYESIAN_RULES` |
| [parked](parked.md) | The baselines that wait on a pilot check or a run: CUSUM, Barbell |
| [tests](tests.md) | Every test the baselines suite runs, with the page it checks |

## Exports

`paranoid.baselines` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#five-layers).

| Name | Kind | Page |
|---|---|---|
| `uniform`, `discerning`, `complacent`, `perfect` | The four fixed baselines, as instances | [policies](policies.md) |
| `POLICIES` | Read only `Mapping[str, Callable[..., Policy]]`, the seven `baseline/<name>` names to their classes | [policies](policies.md) |
| `HedgeRule`, `ScoutRule` | Frozen dataclasses with parameters, for the pilot sweeps | [rules](rules.md) |
| `hedge_rule`, `scout_rule` | `HedgeRule()` and `ScoutRule()` at the defaults | [rules](rules.md) |
| `ForecastRule`, `QUANTILE_LEVELS`, `ODDS_DRAWS` | The protocol, the quantile grid and the draw count | [forecast](forecast.md) |
| `TopPick`, `Odds`, `TopPickWithExploreBets` | The three forecast rules, as classes | [forecast](forecast.md) |
| `top_pick`, `odds`, `explore_1`, `explore_2`, `explore_5` | The five instances the Timestral ids name | [forecast](forecast.md) |
| `FORECAST_RULES` | Read only `Mapping[str, ForecastRule]`, Timestral rule ids to instances | [forecast](forecast.md) |
| `Bayesian`, `Belief` | The Bayesian baseline's class and the posterior it exposes | [bayesian](bayesian.md) |
| `bayesian` | `Bayesian()` at the defaults | [bayesian](bayesian.md) |
| `HAZARDS`, `BAYESIAN_RULES`, `LOOKAHEAD_DRAWS` | The frontier's family, and the lookahead's draw count | [bayesian](bayesian.md) |

## Names from the engine

The baselines layer imports these from `paranoid.engine`. Their behaviour is in the [engine spec](../engine/README.md#exports), and the engine's side of this boundary is [what the layers above read](../engine/README.md#what-the-layers-above-read).

| Name | What the baselines layer uses it for |
|---|---|
| `View`, `Start`, `Dials`, `Policy`, `Bets` | What every policy takes and returns, and what it is handed, see [view](../engine/view.md) |
| `Timeline`, `Record` | What a peeking policy reads, and what every policy reads, through the view |
| `split_budget` | Weights into a valid split: `uniform`, the hedge rule's scout split and `Odds`, see [`split_budget`](../engine/view.md#split_budget) |
| `play`, `make_timeline`, `SCENARIOS` | Whole runs for the test suite only, see [tests](tests.md) |

## What the layers above read

What each layer above takes from this one is listed on that layer's README, so every boundary is written on both sides, see [specs](../README.md#rules).

| Layer | Its list |
|---|---|
| skins | [Names from the baselines layer](../skins/README.md#names-from-the-baselines-layer): `uniform`, to play records in its tests |
| harness | [Names from the baselines layer](../harness/README.md#names-from-the-baselines-layer): `POLICIES` for the baseline provider and warm up, the policies, rules and `Bayesian` with `HAZARDS` and `BAYESIAN_RULES` for the pilot cells, and `FORECAST_RULES`, `ForecastRule` and `QUANTILE_LEVELS` for the Timestral provider |

## Modules

    src/paranoid/baselines/
      __init__.py    the exports above, nothing else
      policies.py    uniform, discerning, complacent, perfect
      rules.py       HedgeRule, ScoutRule, hedge_rule, scout_rule
      forecast.py    ForecastRule, QUANTILE_LEVELS, ODDS_DRAWS, the three rules, FORECAST_RULES
      bayesian.py    Bayesian, Belief, bayesian, HAZARDS, BAYESIAN_RULES, LOOKAHEAD_DRAWS
      names.py       POLICIES

- Nothing outside `__init__.py` is public. Tests import from `paranoid.baselines` only, plus `paranoid.engine` for timelines.
- The only imports are `paranoid.engine`, numpy and the standard library. `import-linter` enforces it, see [layout](../../harness/layout.md#five-layers).

## Conventions

- **Every policy is an instance of a frozen dataclass with `__call__` and `peeks` declared `ClassVar[bool]`.** A plain function with an attribute bolted on does not satisfy the engine's `Policy` protocol for a type checker. A `ClassVar` is not a field, so `peeks` is never a constructor argument and the harness's `-M` cast cannot reach it, see [baseline](../harness/providers.md#baseline). So the harness treats every entry in `POLICIES` alike.
- **A policy is pure.** Same view, same split. No state between calls. A rule with state recomputes it from the record each round, or caches by record length and gets the same answer.
- **Only the yardstick peeks.** `discerning` and `perfect` read the timeline. Every other policy has `peeks` false, works with `view.timeline = None` and never reads it, see [view](../engine/view.md#view) and [why these two baselines](../../design/scoring.md#why-these-two-baselines). A peeking baseline's bets follow the timeline, so a log of `baseline/discerning` on a held-out seed is as private as the seed, see [contamination](../../harness/contamination.md#public-and-held-out).
- **A baseline that bets badly is a bug.** Every policy returns a valid split for its view, or raises. Nothing here retries, see [play](../engine/game.md#play).
- **The layer writes no text.** Nothing here renders a prompt or a message. The skins layer renders, the harness logs.
- **Bets are written as `budget` on a channel** on these pages, meaning every point on it and 0 elsewhere.

## Invariants

- A policy with `peeks` false returns the same split whether `view.timeline` is the timeline or `None`.
- No policy edits the view, the record or the timeline. The timeline's arrays are read only, see [timeline](../engine/timeline.md#interface).
