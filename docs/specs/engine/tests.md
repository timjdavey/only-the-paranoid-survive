# Tests

Every test the engine suite runs, in `tests/engine/`. They need no model, no network and no inspect, see [layout](../../harness/layout.md#four-layers). Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Config

| Id | Test | Page |
|---|---|---|
| C1 | Every key in `SCENARIOS` equals its config's `name`, the eight glossary code names are all present and nothing else, and assigning to `SCENARIOS` raises `TypeError` | [config](config.md#scenarios) |
| C2 | `ScenarioConfig()` with each bad value in the validation list raises `ValueError`, one case per clause, including `onset=(0, 5)`, a `size_sigmas` low of 0, a `hedge_margin_points` of 0, `short_share=0.5` on a `"draw"` switch, a `short_level` of `(0.0, 0.5)`, an undo as the first event and an undo after a `"fall"` switch | [config](config.md#fields) |
| C3 | `engine_hash` of the default config is 12 lowercase hex characters and equals a pinned string. Changing the pinned string is a reviewed change | [config](config.md#engine-hash) |
| C4 | `dataclasses.replace` on each field with a different valid value changes the hash. Replacing a field with its own value does not | [config](config.md#engine-hash) |
| C5 | Each `*_points` default equals its `*_sigmas` default times `own_scale` at the default config | [config](config.md#defaults) |
| C6 | `leader_base=(60, 70)` and `(60.0, 70.0)` give equal configs, equal hashes and equal tapes on seed 0 | [config](config.md#fields) |
| C7 | The canonical JSON of `one_shock` contains `"shape":"shock"` inside its one event, and `shock_then_switch` has one `shock` and one `switch` | [config](config.md#engine-hash) |

## Tape

| Id | Test | Page |
|---|---|---|
| T1 | `make_tape(c, s)` twice gives equal arrays, equal events and equal hash. A subprocess gives the same | [tape](tape.md#invariants) |
| T2 | Shapes: `(rounds, channels)` for `levels`, `base`, `weather`, `loadings`, `impulse`, `read_noise_z`, `(rounds,)` for `factor` | [tape](tape.md#invariants) |
| T3 | `levels` equals `base + weather + loadings × factor[:, None] + impulse` within `1e-9` | [tape](tape.md#invariants) |
| T4 | Ladder on 200 seeds: leader, runner-up and hedge distinct, `field` has `channels − 2` entries with the hedge, leader base above runner-up above every other, hedge lowest, every field channel at least `field_headroom` below the runner-up | [tape](tape.md#the-ladder) |
| T5 | Loadings on 200 seeds: every row 0 loading inside `loading`, except the hedge's inside `hedge_loading` | [tape](tape.md#loadings) |
| T6 | Weather SD: over 2000 No change seeds, the SD of `weather[t, :]` pooled across channels and seeds at each of rounds 1, 10 and 40 is within 5% of `own_scale`. The SD of `factor[t]` across seeds at the same rounds is within 10% of `factor_scale` | [tape](tape.md#weather-and-the-shared-factor) |
| T7 | Persistence: over the same seeds, the lag-1 correlation of `weather[:, c]` is within 0.05 of `persistence` | [tape](tape.md#weather-and-the-shared-factor) |
| T8 | Onset on 200 seeds lies inside `config.onset`, and is the same for `one_shock` and `down_switch` on each seed | [tape](tape.md#onset) |
| T9 | Twin tapes, One shock and Down switch: `levels[:onset−1]` equal exactly, and differ somewhere after | [tape](tape.md#twin-tapes) |
| T10 | Twin tapes, Shock then switch and One shock: `levels` equal before the switch's onset | [tape](tape.md#twin-tapes) |
| T11 | Twin tapes, Up switch and No change: `levels` equal on every channel but `sleeper`, and differ on the sleeper after onset | [tape](tape.md#twin-tapes) |
| T12 | Shock: `base` and `impulse` are untouched on every channel. `factor` differs from the No change tape's from onset on. The sharp profile's impulse halves every `half_life` rounds within `1e-9`. The slide profile reaches `−depth` at round `onset + half_life` and rises after | [tape](tape.md#shock) |
| T13 | Shock, hedge cap, 200 One shock seeds: at the trough, hedge `base + loading × impulse` is at least `hedge_margin_points` below the leader's, and `depth ≤ depth_drawn`. With `hedge_may_overtake` on and a config that allows it, at least `hedge_margin_points` above. With the default config and the knob on, `make_tape` raises `ValueError` on some seed in the first 50. On 200 Switch then shock seeds the same margin holds against the climate leader at the shock's onset, with that leader's loading at onset | [tape](tape.md#shock) |
| T14 | `one_channel_shock`: `factor` and `base` equal the No change tape's, `impulse` is non-zero on the leader only, and `discerning` plays the same bets as on the No change tape | [tape](tape.md#shock) |
| T15 | Switch, fall: after the ramp the leader's base is `size` below the base of the channel that was second at onset, within `1e-9`. The ramp is linear, no other base moves, the hedge is never the sleeper, `numbers["fall"]` equals the points moved | [tape](tape.md#switch) |
| T16 | Switch, rise, on seeds with `short` 0: after the ramp the sleeper's base is `rise` above every other channel's base, including the runner-up's and the fallen leader's. Its loading from onset equals `numbers["sleeper_loading"]` and is positive. No other loading changes | [tape](tape.md#switch) |
| T17 | Switch, `kind="draw"` over 1000 seeds: the share with a sleeper is within 0.05 of `riser_share` | [tape](tape.md#switch) |
| T18 | Drift: after `length` rounds the leader's base is `size` below the channel that was second at onset. The linear profile's steps are equal. The logistic profile has the same endpoints and is monotone | [tape](tape.md#drift) |
| T19 | Events past the last round: a config with `onset = (rounds, rounds)` and a drift makes a tape with one event and nothing out of bounds | [tape](tape.md#events) |
| T20 | No two alike: a config with two shocks whose ranges are single values raises `ValueError` after 100 tries | [tape](tape.md#no-two-alike) |
| T21 | Pinning: two pinned configs differing only in `own_scale` give equal `base`, `loadings`, `impulse` and events on each of 50 seeds of every scenario, One shock included | [tape](tape.md#pinning) |
| T22 | Pinning, **slow**: over 1000 Down switch seeds, the pooled output of `discerning` minus `complacent` at `own_scale` 2, 4 and 8 agrees within 5% | [tape](tape.md#pinning) |
| T23 | Nothing clipped: a config with a low ladder and a deep shock produces a level below 0, and `make_tape` does not raise | [tape](tape.md#invariants) |
| T24 | A leader that would end at or below 0 raises `ValueError` | [tape](tape.md#invariants) |
| T25 | Seeds `0` and `2**64 − 1` both make a tape | [tape](tape.md#seed-streams) |
| T26 | Gap: on 200 Shock then switch seeds, the switch's onset minus the shock's onset lies inside `gap`. The first event's `numbers["gap"]` is present and inside `gap` | [tape](tape.md#events) |
| T27 | A config with 4 channels and two `fall_and_rise` switches raises `ValueError` for an empty sleeper set | [tape](tape.md#draw-order) |
| T28 | Every array on a tape is read only: assigning to `tape.levels[0, 0]` raises `ValueError` | [tape](tape.md#interface) |
| T29 | `Event.numbers` has exactly the keys in the draw order table for its shape, `short` included on every switch, undo too, and `depth ≤ depth_drawn` on every One shock seed | [tape](tape.md#draw-order) |
| T30 | Short share: over 1000 Up switch seeds, the share with `short` 1 is within 0.05 of `short_share`. Every Up switch then down switch and Down switch seed has `short` 0 | [tape](tape.md#switch) |
| T31 | Short: on Up switch seeds with `short` 1, after the ramp the sleeper's base is `short_level` of the way from the runner-up's to the leader's within `1e-9`, strictly between them, and `climate_leader` is the leader in every round | [tape](tape.md#switch) |
| T32 | Undo, 200 Up switch then down switch seeds: `events[1].channel` is `events[0].sleeper`, `events[1].sleeper` is `None`, after the undo's ramp `base` and `loadings` equal the No change tape's within `1e-9`, the ramp is linear, and `numbers["fall"]` equals the points the sleeper moved | [tape](tape.md#switch) |
| T33 | Twin tapes, Switch then shock and Down switch: `levels` equal before the shock's onset, and differ somewhere after | [tape](tape.md#twin-tapes) |
| T34 | Twin tapes, Up switch then down switch and Up switch: on seeds where Up switch has `short` 0, `levels` equal before the undo's onset. On seeds where it has `short` 1, they differ on the sleeper only | [tape](tape.md#twin-tapes) |
| T35 | Twin tapes, Up switch then down switch and No change: `levels` equal from the end of the undo's ramp to the last round | [tape](tape.md#twin-tapes) |

## Game

| Id | Test | Page |
|---|---|---|
| G1 | Each row of the bets table raises `BetError` with the given `check`, at the defaults, and `str(error)` is `Bad tool call: {check}.`. `True` in a split fails `shape`, as do `10.0` and `"10"`. A split of `np.int64` passes. A split of 11 values fails `shape` before `sum`. A negative value fails `sign`, not `shape` | [game](game.md#bets) |
| G2 | A `BetError` leaves `round`, `done` and `len(record)` unchanged | [game](game.md#bets) |
| G3 | Inertia: with `inertia_cap = 20`, round 1 accepts any valid split, round 2 rejects a move of 21 with `check` `inertia` and accepts 20 | [game](game.md#bets) |
| G4 | Readings: with `read_noise_z` set to all ones on a hand-built tape, a bet of 4 reads `level + k/2`, 16 reads `level + k/4`, 100 reads `level + k/10`, each to one decimal | [game](game.md#readings) |
| G5 | Unfunded channels read `None`, and the row's readings are `None` exactly where bets are 0 | [game](game.md#readings) |
| G6 | Output equals the exact-level weighted sum rounded to one decimal, not the sum of the readings, on a tape where they differ | [game](game.md#readings) |
| G7 | A negative reading is possible: a low level and a large negative `read_noise_z` with a bet of 1 | [game](game.md#readings) |
| G8 | Playing a finished game raises `RuntimeError`, and `done` is true after `rounds` valid splits | [game](game.md#bets) |
| G9 | `to_csv` on a fixed two-round record with default names equals a pinned string, byte for byte, with one trailing newline per row and the header | [game](game.md#record) |
| G10 | `to_csv(names)` uses the names in order as `<name>_bet` and `<name>_level`. An empty record renders the header only. A name with a comma, a quote or a newline, or the wrong number of names, raises `ValueError`. A reading of `-0.0` renders as `0.0` | [game](game.md#record) |
| G11 | `unchanged_rounds` on bets A, A, B, B, A returns `[2, 4]` | [game](game.md#record) |
| G12 | `readings_of(c)` skips rounds where `c` had no bet and keeps round order | [game](game.md#record) |
| G13 | `Game(tape, record)` with rounds 1, 2, 4 raises `ValueError`, as does a record of `rounds + 1` rows. With rounds 1, 2, 3 it starts at round 4 | [game](game.md#starting-part-way) |
| G14 | `play(complacent, tape, max_rounds=5)` returns five rows. Passing that record back and playing to the end gives `rounds` rows, and the five-row record still has five rows | [game](game.md#play) |
| G15 | `play` with a policy that returns a bad split raises `BetError` | [game](game.md#play) |
| G16 | `play` gives a peeking policy the tape and a non-peeking policy `None`, checked with a recording stub | [game](game.md#play) |
| G17 | Determinism: `play(uniform, tape)` twice gives equal records | [game](game.md#invariants) |
| G18 | `game.view(False)` has the game's round, `start` matching the tape's ladder, the game's record and `tape = None`. `game.view(True).tape is tape` | [game](game.md#view) |
| G19 | `Game` on a hand-built tape whose `levels` has the wrong shape raises `ValueError` before any round is played | [game](game.md#starting-part-way) |
| G20 | `record.rows` cannot be assigned to or appended to directly, and `record.copy()` is equal but not the same object | [game](game.md#record) |

## Policies

| Id | Test | Page |
|---|---|---|
| P1 | Every baseline returns a valid split on every round of 50 seeds of every scenario, with `play` | [policies](policies.md#invariants) |
| P2 | `split_budget`: `[1] × 10` gives ten 10s. `[1, 1, 1]` with 100 gives `(34, 33, 33)`. All zeros and a negative raise `ValueError` | [policies](policies.md#split_budget) |
| P3 | `uniform` returns the same split for any view | [policies](policies.md#the-six-baselines) |
| P4 | `complacent` round 1 equals `discerning` round 1 on 50 seeds, and the two are equal on every round of a No change tape | [policies](policies.md#invariants) |
| P5 | `discerning` moves on every Down switch tape of 50 seeds, in the first round the sleeper's or runner-up's base passes the leader's, and never before onset | [policies](policies.md#the-six-baselines) |
| P6 | `perfect` output is at least `discerning` output on every seed of every scenario | [policies](policies.md#the-six-baselines) |
| P7 | Non-peeking policies give the same splits with `view.tape` as the tape and as `None` | [policies](policies.md#view) |
| P8 | Hedge rule on a hand-built record: holds through a fall with a tell, scouts for `scout_rounds` rounds after a fall with no tell, then moves to the best scouted channel and never to the hedge | [policies](policies.md#hedge-rule) |
| P9 | Hedge rule on an Up switch tape and an Up switch then down switch tape never moves | [policies](policies.md#hedge-rule) |
| P10 | Scout rule on a hand-built record: moves after exactly `n` rounds of a channel beating the pick, not after `n − 1`, and not when the hedge tells | [policies](policies.md#scout-rule) |
| P11 | `ScoutRule(s=12)` raises `ValueError` on its first view at the defaults, as `12 × 9 ≥ 100` | [policies](policies.md#scout-rule) |
| P12 | Baseline order, **slow**: over 1000 seeds, pooled output orders as in [baseline order](../../pilot/engine-checks.md#baseline-order) for Down switch, Up switch, No change, Switch then shock and Up switch then down switch, with Up switch split into seeds with `short` 0 and `short` 1. The No change case, and the short Up switch seeds for `complacent`, `discerning` and the hedge rule, allow them within 1% of each other | [policies](policies.md#the-six-baselines) |
| P13 | Uniform output, **slow**: over 1000 No change seeds, pooled, equals the mean level over all channels and rounds within 0.1% | [policies](policies.md#the-six-baselines) |
| P14 | Every exported policy has a `peeks` bool and is callable, `hedge_rule == HedgeRule()` and `scout_rule == ScoutRule()` | [policies](policies.md#interface) |
| P15 | A policy that tries to write to `view.tape.levels` raises `ValueError` | [policies](policies.md#invariants) |
| P16 | `discerning` never moves on 50 short Up switch seeds. On 50 Up switch then down switch seeds it moves to the sleeper once and back to `start.leader` once, and ends on `start.leader` | [policies](policies.md#the-six-baselines) |

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
