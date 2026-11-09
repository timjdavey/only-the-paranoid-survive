# Tests

Every test the baselines suite runs, in `tests/baselines/`. Ids start `B` for baselines, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, see [layout](../../harness/layout.md#five-layers). Tapes and whole runs come from `paranoid.engine`, with `play` and `make_tape` on public seeds. Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Policies

| Id | Test | Page |
|---|---|---|
| BP1 | Every entry in `POLICIES`, built at its defaults, returns a valid split on every round of 50 seeds of every scenario, with `play` | [policies](policies.md#invariants) |
| BP2 | `uniform` returns the same split for any view | [policies](policies.md#the-four-fixed-baselines) |
| BP3 | `complacent` round 1 equals `discerning` round 1 on 50 seeds, and the two are equal on every round of a No change tape | [policies](policies.md#invariants) |
| BP4 | `discerning` moves on every Down switch tape of 50 seeds, in the first round the sleeper's or runner-up's base passes the leader's, and never before onset | [policies](policies.md#the-four-fixed-baselines) |
| BP5 | `perfect` output is at least `discerning` output on every seed of every scenario | [policies](policies.md#the-four-fixed-baselines) |
| BP6 | Non-peeking policies give the same splits with `view.tape` as the tape and as `None` | [README](README.md#invariants) |
| BP7 | Baseline order, **slow**: over 1000 seeds, pooled output orders as in [baseline order](../../pilot/engine-checks.md#baseline-order) for Down switch, Up switch, No change, Switch then shock and Up switch then down switch, with Up switch split into seeds with `short` 0 and `short` 1. The No change case, and the short Up switch seeds for `complacent`, `discerning` and the hedge rule, allow them within 1% of each other | [policies](policies.md#the-four-fixed-baselines) |
| BP8 | Uniform output, **slow**: over 1000 No change seeds, pooled, equals the mean level over all channels and rounds within 0.1% | [policies](policies.md#the-four-fixed-baselines) |
| BP9 | Every exported policy has a `peeks` bool and is callable, `hedge_rule == HedgeRule()` and `scout_rule == ScoutRule()` | [README](README.md#conventions) |
| BP10 | `discerning` never moves on 50 short Up switch seeds. On 50 Up switch then down switch seeds it moves to the sleeper once and back to `start.leader` once, and ends on `start.leader` | [policies](policies.md#the-four-fixed-baselines) |
| BP11 | `POLICIES` has exactly the six glossary keys, four instances and two classes, assigning to it raises `TypeError`, `POLICIES["hedge_rule"]() == hedge_rule`, and `POLICIES["hedge_rule"](nope=1)` raises `TypeError` | [policies](policies.md#policies) |
| BP12 | In a subprocess that imports `paranoid.baselines` and nothing else, `sys.modules` holds no top-level package outside `paranoid`, numpy and the standard library | [README](README.md#modules) |

## Rules

| Id | Test | Page |
|---|---|---|
| BR1 | Hedge rule on a hand-built record: holds through a fall with a tell, scouts for `scout_rounds` rounds after a fall with no tell, then moves to the best scouted channel and never to the hedge | [rules](rules.md#hedge-rule) |
| BR2 | Hedge rule on an Up switch tape and an Up switch then down switch tape never moves | [rules](rules.md#hedge-rule) |
| BR3 | Scout rule on a hand-built record: moves after exactly `n` rounds of a channel beating the pick, not after `n − 1`, and not when the hedge tells | [rules](rules.md#scout-rule) |
| BR4 | `ScoutRule(s=12)` raises `ValueError` on its first view at the defaults, as `12 × 9 ≥ 100` | [rules](rules.md#scout-rule) |
| BR5 | `HedgeRule(look=0)` raises `ValueError` on construction. `HedgeRule(look=100)` raises `ValueError` on its first view at the defaults | [rules](rules.md#hedge-rule) |
| BR6 | Scout rule on 50 Up switch then down switch seeds: on at least 40 it ends on `start.leader` having moved at least twice, to the sleeper after the rise and back after the undo | [rules](rules.md#scout-rule) |

## Forecast

| Id | Test | Page |
|---|---|---|
| BF1 | On hand-built quantiles: `top_pick` puts 100 on the highest median, `look_2` puts 2 on the rest and 82 on it, `odds` on two channels with equal quantiles gives `50, 50` within 3, and a `NaN` channel gets 0 from every rule | [forecast](forecast.md#the-rules) |
| BF2 | `QUANTILE_LEVELS` has 21 ascending values, `QUANTILE_LEVELS[10] == 0.5`, and `FORECAST_RULES` has the five ids mapping to the five instances | [forecast](forecast.md#interface) |
| BF3 | `odds` twice on one array gives equal splits, and the array is unchanged after | [forecast](forecast.md#invariants) |
| BF4 | An all-`NaN` array, a one-dimensional array and an array with 20 columns each raise `ValueError` from every rule. `TopPickWithLooks(12)` raises `ValueError` on ten channels | [forecast](forecast.md#the-rules) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| BH1 | For any public seed and scenario, every entry in `POLICIES` at its defaults returns valid splits on every round through `play` |
| BH2 | For any `(channels, 21)` array of ascending rows with at least one finite row, every rule in `FORECAST_RULES` returns a valid split |

## Pilot decides

- BP7 doubles as [Baseline order](../../pilot/engine-checks.md#baseline-order) in the pilot, which runs it at every grid setting and records the numbers.

## Not decided

- The tolerance in BR6 is a first guess. Tighten it once the suite runs.
