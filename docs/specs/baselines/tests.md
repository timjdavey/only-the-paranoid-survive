# Tests

Every test the baselines suite runs, in `tests/baselines/`. Ids start `B` for baselines, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, see [layout](../../harness/layout.md#five-layers). Timelines and whole runs come from `paranoid.engine`, with `play` and `make_timeline` on public seeds. Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Policies

| Id | Test | Page |
|---|---|---|
| BP1 | Every entry in `POLICIES`, built at its defaults, returns a valid split on every round of 50 seeds of every scenario, with `play` | [policies](policies.md#invariants) |
| BP2 | `uniform` returns the same split for any view | [policies](policies.md#the-four-fixed-baselines) |
| BP3 | `complacent` round 1 equals `discerning` round 1 on 50 seeds, and the two are equal on every round of a No change timeline | [policies](policies.md#invariants) |
| BP4 | `discerning` moves on every Down switch timeline of 50 seeds, in the first round the sleeper's or runner-up's base passes the leader's, and never before onset | [policies](policies.md#the-four-fixed-baselines) |
| BP5 | `perfect` output is at least `discerning` output on every seed of every scenario | [policies](policies.md#the-four-fixed-baselines) |
| BP6 | Non-peeking policies give the same splits with `view.timeline` as the timeline and as `None` | [README](README.md#invariants) |
| BP7 | Baseline order, **slow**: over 1000 seeds of every scenario, pooled output has `perfect ≥ discerning ≥ complacent`, with `discerning` above `complacent` on Down switch, and `uniform` below every other entry in `POLICIES`. That much holds whatever the knobs. Where the hedge rule and Scout rule land depends on the knobs, so it is the pilot's [baseline order](../../pilot/engine-checks.md#baseline-order) check and not a test | [policies](policies.md#the-four-fixed-baselines) |
| BP8 | Uniform output, **slow**: over 1000 No change seeds, pooled, equals the mean level over all channels and rounds within 0.1% | [policies](policies.md#the-four-fixed-baselines) |
| BP9 | Every exported policy has a `peeks` bool that is not in `dataclasses.fields`, and is callable | [README](README.md#conventions) |
| BP10 | `discerning` never moves on 50 short Up switch seeds. On 50 Up switch then down switch seeds it moves to the sleeper once and back to `start.leader` once, and ends on `start.leader` | [policies](policies.md#the-four-fixed-baselines) |
| BP11 | `POLICIES` has exactly the six glossary keys, assigning to it raises `TypeError`, `POLICIES[name]()` equals the exported instance of the same name for all six, and `POLICIES["hedge_rule"](nope=1)` and `POLICIES["uniform"](explore=1)` raise `TypeError` | [policies](policies.md#policies) |
| BP12 | In a subprocess that imports `paranoid.baselines` and nothing else, `sys.modules` holds no top-level package outside `paranoid`, numpy and the standard library | [README](README.md#modules) |

## Rules

| Id | Test | Page |
|---|---|---|
| BR1 | Hedge rule on a hand-built record: holds through a fall with a tell, scouts for `scout_rounds` rounds after a fall with no tell, then moves to the best scouted channel and never to the hedge | [rules](rules.md#hedge-rule) |
| BR2 | Hedge rule on 50 Up switch seeds and 50 Up switch then down switch seeds: it ends on `start.leader` on every seed and scouts on at most 10 of each 50, as every scout there is a false alarm on weather | [rules](rules.md#hedge-rule) |
| BR3 | Scout rule on a hand-built record: moves after exactly `n` rounds of a channel beating the pick, not after `n − 1`, and not when the hedge tells | [rules](rules.md#scout-rule) |
| BR4 | `ScoutRule(s=12)` raises `ValueError` on its first view at the defaults, as `12 × 9 ≥ 100` | [rules](rules.md#scout-rule) |
| BR5 | `HedgeRule(explore=0)`, `HedgeRule(window=0)`, `HedgeRule(scout_rounds=0)`, `HedgeRule(fall_points=0.0)`, `ScoutRule(s=0)`, `ScoutRule(n=0)` and `ScoutRule(tell_points=float("nan"))` each raise `ValueError` on construction. `HedgeRule(explore=100)` and `HedgeRule(explore=95)` raise `ValueError` on the first view at the defaults, as `100 − 95 < 9` | [rules](rules.md#hedge-rule) |
| BR6 | Scout rule on 50 Up switch then down switch seeds: on at least 40 it ends on `start.leader` having moved at least twice, to the sleeper after the rise and back after the undo | [rules](rules.md#scout-rule) |
| BR7 | Hedge rule and Scout rule played with `play` from a five round `complacent` warm up record on 20 Down switch seeds: every split is valid, the hedge rule does not scout before round `6 + 2 × window` and the Scout rule does not move before round `6 + n`, as the hedge has no reading until round 6 | [rules](rules.md#behaviour) |
| BR8 | Hedge rule on 50 One shock seeds: it never scouts on at least 40 and ends on `start.leader` on at least 45, the timeline version of BR1 | [rules](rules.md#hedge-rule) |
| BR9 | Hedge rule and Scout rule called twice on one view give equal splits, and the split for a record's first `k` rows is the same whether or not a longer record was played through the rule first | [README](README.md#conventions) |

## Forecast

| Id | Test | Page |
|---|---|---|
| BF1 | On hand-built quantiles: `top_pick` puts 100 on the highest median, `explore_2` puts 2 on the rest and 82 on it, `odds` on two channels with equal quantiles gives `50, 50` within 3, and a `NaN` channel gets 0 from `top_pick` and `odds` and `explore` from `explore_2` | [forecast](forecast.md#the-rules) |
| BF2 | `QUANTILE_LEVELS` has 21 ascending values, `QUANTILE_LEVELS[10] == 0.5`, and `FORECAST_RULES` has the five ids mapping to the five instances | [forecast](forecast.md#interface) |
| BF3 | `odds` twice on one array gives equal splits, and the array is unchanged after | [forecast](forecast.md#invariants) |
| BF4 | An all-`NaN` array, a one-dimensional array, an array with 20 columns, a row with one `NaN` among finite values and a finite row in descending order each raise `ValueError` from every rule. `TopPickWithExploreBets(12)` raises `ValueError` on ten channels | [forecast](forecast.md#the-rules) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| BH1 | For any public seed and scenario, every entry in `POLICIES` at its defaults returns valid splits on every round through `play` |
| BH2 | For any `(channels, 21)` array of ascending rows with at least one finite row, every rule in `FORECAST_RULES` returns a valid split |

## Pilot decides

- The pilot's [Baseline order](../../pilot/engine-checks.md#baseline-order) runs every entry in `POLICIES` on every scenario at every grid setting and records the full order. BP7 keeps only the part no knob can change.

## Not decided

- The tolerances in BR2, BR6 and BR8 are first guesses. Tighten them once the suite runs.
