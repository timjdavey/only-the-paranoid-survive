# Tests

Every test the forecasters suite runs, in `tests/forecasters/`. Ids start `F` for forecasters, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect: every `FP` test plays a fake `Forecaster`, and `PARANOID_CACHE` points at a temporary folder throughout. Tests marked **timestral** load the real model, so they need the extra and the weights. They are skipped by default, run with `uv run pytest -m timestral`.

- **The fake** is a class with a `key` and a `__call__` that records its inputs and returns quantiles built from the last finite reading of each column, so a test can say which channel it forecasts highest.

## Policy

| Id | Test | Page |
|---|---|---|
| FP1 | `top-pick` with a fake through `play` on Down switch seed 0: round 1's bets are `uniform`'s and the fake is not called for it. The first call's `readings` has shape `(1, channels)` with no `NaN`. The second call's has `NaN` on nine channels in its last row. `bets` is `None` on every call | [the arrays](policy.md#the-arrays) |
| FP2 | A policy with `with_bets` true and a fake: `bets` on each call equals the record's bets as float64, the same shape as `readings` | [the arrays](policy.md#the-arrays) |
| FP3 | On a view after a five round `complacent` warm up record: the fake gets arrays of shape `(5, 1)`, `forecast(view).quantiles` has nine `NaN` rows and one finite, `explore-1` puts 1 on each of the nine and `top-pick` puts `budget` on the one | [the arrays](policy.md#the-arrays) |
| FP4 | A fake that returns its quantiles reversed gives the same bets as one that returns them ascending. A fake that returns 20 columns, one row too few, or a `NaN` raises `ValueError` | [the arrays](policy.md#the-arrays) |
| FP5 | `forecast` twice on one view calls the fake once and gives equal `cache_key`s and equal quantiles. The file is `<PARANOID_CACHE>/forecasts/<cache_key>.npy`. A fake with another `key`, `with_bets` flipped, and one reading changed by 0.1 each give a different `cache_key` | [the cache](policy.md#the-cache) |
| FP6 | `play` twice with one policy gives equal records, and the second play never calls the fake | [invariants](policy.md#invariants) |
| FP7 | `forecast` is `None` and `rounded_out` is 0 on an empty record. `forecast(view).quantiles` is read only. A call leaves the record equal to a copy taken before, and gives the same split with `view.timeline` as the timeline and as `None` | [the policy](policy.md#the-policy) |
| FP8 | A fake that puts one channel far above the rest: `rounded_out` is 9 for `odds`, as the other nine get 0 with finite rows, and 0 for `top-pick` and `explore-1` on the same view. It is an `int`, never a `bool` | [rounded out](policy.md#rounded-out) |
| FP9 | `TIMESTRAL_POLICIES` has exactly the seven glossary ids, in the table's order, and assigning to it raises `TypeError`. `odds-alone` and `odds-bet-aware` have `FORECAST_RULES["odds"]` and `Timestral(joint=False)`, with `with_bets` false and true. Every other id has `FORECAST_RULES[id]`, `with_bets` false and `timestral`. Each has a `peeks` of false that is not in `dataclasses.fields` | [the policies](policy.md#the-policies) |
| FP10 | Each of the seven with a fake swapped in returns a valid split on every round of One shock, Down switch and Up switch seed 0, with `play` | [README](README.md#invariants) |

## Timestral

| Id | Test | Page |
|---|---|---|
| FT1 | In a subprocess, importing `paranoid.forecasters` adds neither `torch` nor `timestral` to `sys.modules` | [loading](timestral.md#loading) |
| FT2 | With both packages made unfindable, `require_timestral()` and `Timestral()(readings, None)` each raise `ImportError` naming `uv sync --extra timestral` | [loading](timestral.md#loading) |
| FT3 | `Timestral(joint=True)` called with `bets` raises `ValueError`, with no extra installed. `timestral == Timestral()`. `key` differs between `joint` true and false, between two models and between two revisions | [two shapes](timestral.md#two-shapes) |
| FT4 | **timestral** The real forecaster, both shapes, on the ten readings of `play(uniform, make_timeline(SCENARIOS["one_shock"], 0), max_rounds=10)`: shape `(channels, 21)`, finite, every row ascending, and the same input twice is equal | [checked](timestral.md#checked) |
| FT5 | **timestral** The gap test, both shapes: the same ten readings then thirty `NaN` rows. The spread, last quantile minus first, is wider after thirty blanks than after one on every channel | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| FT6 | **timestral** `Timestral(joint=False)` with the bet rows of a split that puts 55 on one channel gives a forecast that differs from the one with `bets` as `None` | [two shapes](timestral.md#two-shapes) |
| FT7 | **timestral** `play(TIMESTRAL_POLICIES["top-pick"], make_timeline(SCENARIOS["one_shock"], 0))` returns `rounds` rows of valid splits, and a second play gives an equal record | [README](README.md#invariants) |
