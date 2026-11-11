# Tests

Every test the baselines suite runs, in `tests/baselines/`. Ids start `B` for baselines, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, see [layout](../../harness/layout.md#five-layers). Timelines and whole runs come from `paranoid.engine`, with `play` and `make_timeline` on small whole-number seeds. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Three sizes

| Size | What | Where it runs |
|---|---|---|
| Hand-built | A view built with `Game(timeline, record).view(peeks)` from rows written by hand, or a timeline with scripted levels and no read noise. Tests the rule with no luck in it | Every run, CI included |
| Short runs | Whole runs through `play`. 50 seeds for the four fixed baselines, which take milliseconds. 2 or 3 named seeds for the hedge rule, the Scout rule and the Bayesian baseline | Every run, CI included |
| Sweeps | A thousand seeds, marked **sweep** | By hand with `uv run pytest -m sweep`. The default run and CI skip them |

- **A named seed** is one picked on the real code and written into the row with what the baseline does on it. A row about a share of seeds can't be checked on three, so it names its seeds instead. The shares are the pilot's to measure, see [pilot decides](#pilot-decides).
- **A named seed that stops holding** after a change to the engine or a rule is a finding, not a flake: the draws are fixed by the seed. Re-pick it only when the change was meant to move it, and say so in the PR.

## Policies

| Id | Test | Page |
|---|---|---|
| BP1 | Every entry in `POLICIES`, built at its defaults, returns a valid split on every round with `play`: the four fixed baselines on 50 seeds of every scenario, the hedge rule, the Scout rule and the Bayesian baseline on seeds 0, 1 and 2 of every scenario | [policies](policies.md#invariants) |
| BP2 | `uniform` returns the same split for any view | [policies](policies.md#the-four-fixed-baselines) |
| BP3 | `complacent` round 1 equals `discerning` round 1 on 50 seeds, and the two are equal on every round of a No change timeline | [policies](policies.md#invariants) |
| BP4 | `discerning` moves on every Down switch timeline of 50 seeds, in the first round the sleeper's or runner-up's base passes the leader's, and never before onset | [policies](policies.md#the-four-fixed-baselines) |
| BP5 | The levels `perfect` bets on sum to at least the levels `discerning` bets on, read from `timeline.levels`, on every seed of every scenario | [policies](policies.md#the-four-fixed-baselines) |
| BP6 | Non-peeking policies give the same splits with `view.timeline` as the timeline and as `None` | [README](README.md#invariants) |
| BP7 | Baseline order, **sweep**: over 1000 seeds of every scenario, pooled output has `perfect ≥ discerning ≥ complacent`, with `discerning` above `complacent` on Down switch, and `uniform` below every other entry in `POLICIES` but `bayesian`. That much holds whatever the knobs. Where the hedge rule and Scout rule land depends on the knobs, so it is the pilot's [baseline order](../../pilot/engine-checks.md#baseline-order) check and not a test. The Bayesian baseline's place is the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier)'s | [policies](policies.md#the-four-fixed-baselines) |
| BP8 | Uniform output, **sweep**: over 1000 No change seeds, pooled, equals the mean level over all channels and rounds within 0.1%, as read noise averages out over 400,000 readings | [policies](policies.md#the-four-fixed-baselines) |
| BP9 | Every exported policy has a `peeks` bool that is not in `dataclasses.fields`, and is callable | [README](README.md#conventions) |
| BP10 | `discerning` never moves on 50 short Up switch seeds. On 50 Up switch then down switch seeds it moves to the sleeper once and back to `start.leader` once, and ends on `start.leader` | [policies](policies.md#the-four-fixed-baselines) |
| BP11 | `POLICIES` has exactly the seven glossary keys, assigning to it raises `TypeError`, `POLICIES[name]()` equals the exported instance of the same name for all seven, and `POLICIES["hedge_rule"](nope=1)` and `POLICIES["uniform"](explore=1)` raise `TypeError` | [policies](policies.md#policies) |
| BP12 | In a subprocess that imports `paranoid.baselines` and nothing else, `sys.modules` holds no top-level package outside `paranoid`, numpy and the standard library | [README](README.md#modules) |
| BP13 | On 20 seeds of a One shock config with `one_channel_shock` on, `discerning` plays the same bets in every round as on the No change timeline of the same seed, as the climate does not move. The engine's half is [ET14](../engine/tests.md#timeline) | [policies](policies.md#the-four-fixed-baselines) |
| BP14 | Pinning, **sweep**: over 1000 Down switch seeds, the pooled output of `discerning` minus `complacent` at `own_scale` 2, 4 and 8, each pinned in level points, agrees within 5%. Moved from the engine suite, where it was ET22 | [pinning](../engine/timeline.md#pinning) |

## Rules

| Id | Test | Page |
|---|---|---|
| BR1 | Hedge rule on a hand-built record: holds through a fall with a tell, scouts for `scout_rounds` rounds after a fall with no tell, then moves to the best scouted channel and never to the hedge | [rules](rules.md#hedge-rule) |
| BR2 | Hedge rule on named seeds of the Up switch scenarios. On Up switch seeds 0 and 1 and Up switch then down switch seeds 0 and 1 it never scouts and ends on `start.leader`. On Up switch seed 12 a false alarm after the rise finds the sleeper, and it ends on it | [rules](rules.md#hedge-rule) |
| BR3 | Scout rule on a hand-built record: moves after exactly `n` rounds of a channel beating the pick, not after `n − 1`, and not when the hedge tells | [rules](rules.md#scout-rule) |
| BR4 | `ScoutRule(s=12)` raises `ValueError` on its first view at the defaults, as `12 × 9 ≥ 100` | [rules](rules.md#scout-rule) |
| BR5 | `HedgeRule(explore=0)`, `HedgeRule(window=0)`, `HedgeRule(scout_rounds=0)`, `HedgeRule(fall_points=0.0)`, `ScoutRule(s=0)`, `ScoutRule(n=0)` and `ScoutRule(tell_points=float("nan"))` each raise `ValueError` on construction. `HedgeRule(explore=100)` and `HedgeRule(explore=95)` raise `ValueError` on the first view at the defaults, as `100 − 95 < 9` | [rules](rules.md#hedge-rule) |
| BR6 | Scout rule on Up switch then down switch seeds 0, 2 and 3: it ends on `start.leader` having moved at least twice, to the sleeper after the rise and back after the undo | [rules](rules.md#scout-rule) |
| BR7 | Hedge rule and Scout rule played with `play` from a five round `complacent` warm up record on Down switch seeds 0, 1 and 2: every split is valid, the hedge rule does not scout before round `6 + 2 × window`, 12 at the defaults, and the Scout rule does not move before round `6 + n`, 9 at the defaults, as the hedge has no reading until round 6 | [rules](rules.md#behaviour) |
| BR8 | Hedge rule on One shock seeds 4, 5 and 7: it never scouts and ends on `start.leader`, the timeline version of BR1 | [rules](rules.md#hedge-rule) |
| BR9 | Hedge rule and Scout rule called twice on one view give equal splits, and the split for a record's first `k` rows is the same whether or not a longer record was played through the rule first | [README](README.md#conventions) |

## Forecast

| Id | Test | Page |
|---|---|---|
| BF1 | On hand-built quantiles: `top_pick` puts 100 on the highest median, `explore_2` puts 2 on the rest and 82 on it, `odds` on two channels with equal, strictly ascending quantiles gives `50, 50` within 5, and a `NaN` channel gets 0 from `top_pick` and `odds` and `explore` from `explore_2` | [forecast](forecast.md#the-rules) |
| BF2 | `QUANTILE_LEVELS` has 21 ascending values from 0.01 to 0.99, with 0.05, 0.10 and 0.95 among them, `MEDIAN_INDEX == 10` and `QUANTILE_LEVELS[MEDIAN_INDEX] == 0.5`, and `FORECAST_RULES` has the five ids mapping to the five instances | [forecast](forecast.md#interface) |
| BF3 | `odds` twice on one array gives equal splits, and the array is unchanged after | [forecast](forecast.md#invariants) |
| BF4 | An all-`NaN` array, a one-dimensional array, an array with 20 columns, a row with one `NaN` among finite values, a row with an infinity and a finite row in descending order each raise `ValueError` from every rule, and a row with equal neighbours does not. `TopPickWithExploreBets(12)` raises `ValueError` on ten channels. `TopPickWithExploreBets(0)` and `Odds(draws=0)` raise `ValueError` on construction | [forecast](forecast.md#the-rules) |

## Bayesian

| Id | Test | Page |
|---|---|---|
| BB1 | On a hand-built record of 20 rounds with `budget` on channel 0 and readings within 1 of 90: `belief(view).mean[0]` is within 1 of 90, and `changed[0]` is below the prior `1 − (1 − hazard)^20`, as flat readings argue against a jump | [bayesian](bayesian.md#the-belief) |
| BB2 | The same record with the readings 20 lower from round 15 on: `changed[0]` is above 0.9 on the view for round 18, and `mean[0]` is within 3 of 70 on the view for round 21 | [bayesian](bayesian.md#the-filter) |
| BB3 | A channel with no reading on any round of a 30 round record has `changed` equal to `1 − (1 − hazard)^30` within `1e-9`, and `mean` equal to `(1 − changed) × its role's prior mean + changed × the jump prior's mean` within `1e-6` | [bayesian](bayesian.md#the-belief) |
| BB4 | `bayesian` called twice on one view gives equal splits and equal quantiles, every quantile row is finite and ascending, and the view's record is unchanged | [bayesian](bayesian.md#invariants) |
| BB5 | `Bayesian(hazard=1e-9, rule="top-pick")` through `play` gives a record equal to `play(complacent, timeline)` on a No change timeline with its weather, shared factor and read noise set to 0, and on two named No change seeds | [bayesian](bayesian.md#rules) |
| BB6 | `Bayesian(hazard=0.0)`, `Bayesian(hazard=1.0)`, `Bayesian(rule="nope")`, `Bayesian(draws=0)` and `Bayesian(lookahead_draws=0)` each raise `ValueError` on construction. `Bayesian(rule="explore-5")` with `budget` 40 and ten channels raises `ValueError` on its first view after round 1 | [bayesian](bayesian.md#rules) |
| BB7 | `Bayesian(rule="lookahead")` on a hand-built record returns a split equal to one of the five forecast rules' splits on `belief(view).quantiles`, and on a view with `round == dials.rounds` returns the `top-pick` split | [bayesian](bayesian.md#rules) |
| BB8 | `bayesian` through `play`: on two named Down switch seeds its output is above the Complacent baseline's, and on two named One shock seeds it ends on `start.leader` | [bayesian](bayesian.md#the-family) |
| BB9 | `HAZARDS` has five ascending values in `(0, 1)`, `BAYESIAN_RULES` is the five `FORECAST_RULES` ids then `"lookahead"`, and every `Bayesian(hazard, rule)` over both, 30 players, returns valid splits on every round of Down switch seed 0 and One shock seed 0, with `play` | [bayesian](bayesian.md#interface) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| BH1 | For any seed and scenario, every entry in `POLICIES` at its defaults but `bayesian` returns valid splits on every round through `play`. BP1 and BB9 run the Bayesian baseline |
| BH2 | For any `(channels, 21)` array of ascending rows with at least one finite row, every rule in `FORECAST_RULES` returns a valid split |
| BH3 | For any seed, scenario and record of valid rows on its timeline, `bayesian.belief(view).quantiles` has shape `(channels, 21)`, is finite and ascending along the last axis, and `changed` lies in `[0, 1]` |

## Pilot decides

- The pilot's [Baseline order](../../pilot/engine-checks.md#baseline-order) runs every entry in `POLICIES` on every scenario at every grid setting and records the full order. BP7 keeps only the part no knob can change.
- The pilot's [Timeline sanity](../../pilot/engine-checks.md#timeline-sanity) runs BP14 at every grid setting and records the numbers.
- **The shares the named seeds stand in for.** How often the hedge rule false alarms on weather and how often the tell stops a scout are [The tell](../../pilot/engine-checks.md#the-tell)'s. How often the Scout rule follows the sleeper there and back is [Up and down](../../pilot/engine-checks.md#up-and-down)'s. How often the Bayesian baseline beats the Complacent baseline, and holds through a shock, is the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier)'s.

## Not decided

- The tolerance in BP14 is a first guess. Tighten it once the sweep has run.
