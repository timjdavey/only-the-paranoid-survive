# Tests

Every test the engine suite runs, in `tests/engine/`. They need no model, no network and no inspect, see [layout](../../harness/layout.md#four-layers). Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Config

| Id | Test | Page |
|---|---|---|
| C1 | Every key in `SCENARIOS` equals its config's `name`, and the six glossary code names are all present and nothing else | [config](config.md#scenarios) |
| C2 | `ScenarioConfig()` with each bad value in the validation list raises `ValueError`, one case per clause | [config](config.md#fields) |
| C3 | `engine_hash` of the default config is 12 lowercase hex characters and equals a pinned string. Changing the pinned string is a reviewed change | [config](config.md#engine-hash) |
| C4 | `dataclasses.replace` on each field with a different valid value changes the hash. Replacing a field with its own value does not | [config](config.md#engine-hash) |
| C5 | Each `*_points` default equals its `*_sigmas` default times `own_scale` at the default config | [config](config.md#defaults) |

## Tape

| Id | Test | Page |
|---|---|---|
| T1 | `make_tape(c, s)` twice gives equal arrays, equal events and equal hash. A subprocess gives the same | [tape](tape.md#invariants) |
| T2 | Shapes: `(rounds, channels)` for `levels`, `base`, `weather`, `loadings`, `read_noise_z`, `(rounds,)` for `factor` | [tape](tape.md#invariants) |
| T3 | `levels` equals `base + weather + loadings × factor[:, None]` within `1e-9` | [tape](tape.md#invariants) |
| T4 | Ladder on 200 seeds: leader, runner-up and hedge distinct, `field` has `channels − 2` entries with the hedge, leader base above runner-up above every other, hedge lowest, every field channel at least `field_headroom` below the runner-up | [tape](tape.md#the-ladder) |
| T5 | Loadings on 200 seeds: every row 0 loading inside `loading`, except the hedge's inside `hedge_loading` | [tape](tape.md#loadings) |
| T6 | Weather SD: over 2000 No change seeds, the SD of `weather[t, c]` across seeds at each of rounds 1, 10 and 40 is within 5% of `own_scale`. The same for `factor` and `factor_scale` | [tape](tape.md#weather-and-the-shared-factor) |
| T7 | Persistence: over the same seeds, the lag-1 correlation of `weather[:, c]` is within 0.05 of `persistence` | [tape](tape.md#weather-and-the-shared-factor) |
| T8 | Onset on 200 seeds lies inside `config.onset`, and is the same for `one_shock` and `down_switch` on each seed | [tape](tape.md#onset) |
| T9 | Twin tapes, One shock and Down switch: `levels[:onset−1]` equal exactly, and differ somewhere after | [tape](tape.md#twin-tapes) |
| T10 | Twin tapes, Shock then switch and One shock: `levels` equal before the switch's onset | [tape](tape.md#twin-tapes) |
| T11 | Twin tapes, Up switch and No change: `levels` equal on every channel but `sleeper`, and differ on the sleeper after onset | [tape](tape.md#twin-tapes) |
| T12 | Shock: `base` is untouched on every channel. `factor` differs from the No change tape's from onset on. The sharp profile's impulse halves every `half_life` rounds within `1e-9` | [tape](tape.md#shock) |
| T13 | Shock, hedge cap, 200 One shock seeds: at the trough, hedge `base + loading × impulse` is at least one sigma below the leader's. With `hedge_may_overtake` on, at least one sigma above | [tape](tape.md#shock) |
| T14 | `one_channel_shock`: `factor` equals the No change tape's, and only the leader's `base` moves | [tape](tape.md#shock) |
| T15 | Switch, fall: the leader's base ends `size` lower, the ramp is linear, no other base moves, the hedge is never the sleeper | [tape](tape.md#switch) |
| T16 | Switch, rise: the sleeper's base ends `rise` above the leader's base at the end of the ramp. Its loading changes from onset and is positive. No other loading changes | [tape](tape.md#switch) |
| T17 | Switch, `kind="draw"` over 1000 seeds: the share with a sleeper is within 0.05 of `riser_share` | [tape](tape.md#switch) |
| T18 | Drift: the leader's base ends `size` lower after `length` rounds. The linear profile's steps are equal. The logistic profile has the same endpoints and is monotone | [tape](tape.md#drift) |
| T19 | Events past the last round: a config with `onset = (rounds, rounds)` and a drift makes a tape with one event and nothing out of bounds | [tape](tape.md#events) |
| T20 | No two alike: a config with two shocks whose ranges are single values raises `ValueError` after 100 tries | [tape](tape.md#no-two-alike) |
| T21 | Pinning: two pinned configs differing only in `own_scale` give equal `base`, `loadings` and events on each of 50 seeds | [tape](tape.md#pinning) |
| T22 | Pinning, **slow**: over 1000 Down switch seeds, the pooled output of `discerning` minus `complacent` at `own_scale` 2, 4 and 8 agrees within 5% | [tape](tape.md#pinning) |
| T23 | Nothing clipped: a config with a low ladder and a deep shock produces a level below 0, and `make_tape` does not raise | [tape](tape.md#invariants) |
| T24 | A leader that would end at or below 0 raises `ValueError` | [tape](tape.md#invariants) |
| T25 | Seeds `0` and `2**64 − 1` both make a tape | [tape](tape.md#seed-streams) |

## Game

| Id | Test | Page |
|---|---|---|
| G1 | Each row of the bets table raises `BetError` with exactly the given `message`, at the defaults. `True` in a split fails the shape check. A split of 11 values fails shape before sum | [game](game.md#bets) |
| G2 | A `BetError` leaves `round`, `done` and `len(record)` unchanged | [game](game.md#bets) |
| G3 | Inertia: with `inertia_cap = 20`, round 1 accepts any valid split, round 2 rejects a move of 21 and accepts 20 | [game](game.md#bets) |
| G4 | Readings: with `read_noise_z` set to all ones on a hand-built tape, a bet of 4 reads `level + k/2`, 16 reads `level + k/4`, 100 reads `level + k/10`, each to one decimal | [game](game.md#readings) |
| G5 | Unfunded channels read `None`, and the row's readings are `None` exactly where bets are 0 | [game](game.md#readings) |
| G6 | Output equals the exact-level weighted sum rounded to one decimal, not the sum of the readings, on a tape where they differ | [game](game.md#readings) |
| G7 | A negative reading is possible: a low level and a large negative `read_noise_z` with a bet of 1 | [game](game.md#readings) |
| G8 | Playing a finished game raises `RuntimeError`, and `done` is true after `rounds` valid splits | [game](game.md#bets) |
| G9 | `to_csv` on a fixed two-round record with default names equals a pinned string, byte for byte, with one trailing newline per row and the header | [game](game.md#record) |
| G10 | `to_csv(names)` uses the names in order as `<name>_bet` and `<name>_level`. An empty record renders the header only | [game](game.md#record) |
| G11 | `unchanged_rounds` on bets A, A, B, B, A returns `[2, 4]` | [game](game.md#record) |
| G12 | `readings_of(c)` skips rounds where `c` had no bet and keeps round order | [game](game.md#record) |
| G13 | `Game(tape, record)` with rounds 1, 2, 4 raises `ValueError`. With rounds 1, 2, 3 starts at round 4 | [game](game.md#starting-part-way) |
| G14 | `play(complacent, tape, rounds=5)` returns five rows. Passing that record back and playing to the end gives `rounds` rows | [game](game.md#play) |
| G15 | `play` with a policy that returns a bad split raises `BetError` | [game](game.md#play) |
| G16 | `play` gives a peeking policy the tape and a non-peeking policy `None`, checked with a recording stub | [game](game.md#play) |
| G17 | Determinism: `play(uniform, tape)` twice gives equal records | [game](game.md#invariants) |

## Policies

| Id | Test | Page |
|---|---|---|
| P1 | Every baseline returns a valid split on every round of 50 seeds of every scenario, with `play` | [policies](policies.md#invariants) |
| P2 | `split_budget`: `[1] × 10` gives ten 10s. `[1, 1, 1]` with 100 gives `(34, 33, 33)`. All zeros and a negative raise `ValueError` | [policies](policies.md#split_budget) |
| P3 | `uniform` returns the same split for any view | [policies](policies.md#the-six-baselines) |
| P4 | `complacent` round 1 equals `discerning` round 1 on 50 seeds, and the two are equal on every round of a No change tape | [policies](policies.md#invariants) |
| P5 | `discerning` moves on a Down switch tape in the first round the sleeper's or runner-up's base passes the leader's, and never before onset | [policies](policies.md#the-six-baselines) |
| P6 | `perfect` output is at least `discerning` output on every seed of every scenario | [policies](policies.md#the-six-baselines) |
| P7 | Non-peeking policies give the same splits with `view.tape` as the tape and as `None` | [policies](policies.md#view) |
| P8 | Hedge rule on a hand-built record: holds through a fall with a tell, scouts for `scout_rounds` rounds after a fall with no tell, then moves to the best scouted channel and never to the hedge | [policies](policies.md#hedge-rule) |
| P9 | Hedge rule on an Up switch tape never moves | [policies](policies.md#hedge-rule) |
| P10 | Scout rule on a hand-built record: moves after exactly `n` rounds of a channel beating the pick, not after `n − 1`, and not when the hedge tells | [policies](policies.md#scout-rule) |
| P11 | Scout rule with `s × (channels − 1) ≥ budget` raises `ValueError` | [policies](policies.md#scout-rule) |
| P12 | Baseline order, **slow**: over 1000 seeds, pooled output orders as in [baseline order](../../pilot/engine-checks.md#baseline-order) for Down switch, Up switch and No change. The No change case allows `complacent`, `discerning` and the hedge rule within 1% of each other | [policies](policies.md#the-six-baselines) |
| P13 | Uniform output, **slow**: over 1000 No change seeds, pooled, equals the mean level over all channels and rounds within 0.1% | [policies](policies.md#the-six-baselines) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| H1 | For any seed and scenario, T2, T3 and T4 hold |
| H2 | For any valid split, `Game.play` accepts it and the row's `None`s match its zeros |
| H3 | For any weights with a positive sum, `split_budget` sums to the budget and is non-negative |

## Open

- Tolerances in T6, T7, T17 and T22 are first guesses. Tighten them once the suite runs.
- T22 and P12 double as [Tape sanity](../../pilot/engine-checks.md#tape-sanity) and [Baseline order](../../pilot/engine-checks.md#baseline-order) in the pilot, but the pilot runs them at every grid setting and records the numbers.
