# Tests

Every test the engine suite runs, in `tests/engine/`. Ids start `E` for the engine, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, see [layout](../../harness/layout.md#five-layers). Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Config

| Id | Test | Page |
|---|---|---|
| EC1 | Every key in `SCENARIOS` equals its config's `name`, the eight glossary code names are all present and nothing else, and assigning to `SCENARIOS` raises `TypeError` | [config](config.md#scenarios) |
| EC2 | `ScenarioConfig()` with each bad value in the validation list raises `ValueError`, one case per clause, including `onset=(0, 5)`, a `size_sigmas` low of 0, a `hedge_margin_points` of 0, `short_share=0.5` on a `"draw"` switch, a `short_level` of `(0.0, 0.5)`, an undo as the first event and an undo after a `"fall"` switch | [config](config.md#fields) |
| EC3 | `engine_hash` of the default config is 12 lowercase hex characters and equals a pinned string. Changing the pinned string is a reviewed change | [config](config.md#engine-hash) |
| EC4 | `dataclasses.replace` on each field with a different valid value changes the hash. Replacing a field with its own value does not | [config](config.md#engine-hash) |
| EC5 | Each `*_points` default equals its `*_sigmas` default times `own_scale` at the default config | [config](config.md#defaults) |
| EC6 | `leader_base=(60, 70)` and `(60.0, 70.0)` give equal configs, equal hashes and equal tapes on seed 0 | [config](config.md#fields) |
| EC7 | The canonical JSON of `one_shock` contains `"shape":"shock"` inside its one event, and `shock_then_switch` has one `shock` and one `switch` | [config](config.md#engine-hash) |

## Tape

| Id | Test | Page |
|---|---|---|
| ET1 | `make_tape(c, s)` twice gives equal arrays, equal events and equal hash. A subprocess gives the same | [tape](tape.md#invariants) |
| ET2 | Shapes: `(rounds, channels)` for `levels`, `base`, `weather`, `loadings`, `impulse`, `read_noise_z`, `(rounds,)` for `factor` | [tape](tape.md#invariants) |
| ET3 | `levels` equals `base + weather + loadings × factor[:, None] + impulse` within `1e-9` | [tape](tape.md#invariants) |
| ET4 | Ladder on 200 seeds: leader, runner-up and hedge distinct, `field` has `channels − 2` entries with the hedge, leader base above runner-up above every other, hedge lowest, every field channel at least `field_headroom` below the runner-up | [tape](tape.md#the-ladder) |
| ET5 | Loadings on 200 seeds: every row 0 loading inside `loading`, except the hedge's inside `hedge_loading` | [tape](tape.md#loadings) |
| ET6 | Weather SD: over 2000 No change seeds, the SD of `weather[t, :]` pooled across channels and seeds at each of rounds 1, 10 and 40 is within 5% of `own_scale`. The SD of `factor[t]` across seeds at the same rounds is within 10% of `factor_scale` | [tape](tape.md#weather-and-the-shared-factor) |
| ET7 | Persistence: over the same seeds, the lag-1 correlation of `weather[:, c]` is within 0.05 of `persistence` | [tape](tape.md#weather-and-the-shared-factor) |
| ET8 | Onset on 200 seeds lies inside `config.onset`, and is the same for `one_shock` and `down_switch` on each seed | [tape](tape.md#onset) |
| ET9 | Twin tapes, One shock and Down switch: `levels[:onset−1]` equal exactly, and differ somewhere after | [tape](tape.md#twin-tapes) |
| ET10 | Twin tapes, Shock then switch and One shock: `levels` equal before the switch's onset | [tape](tape.md#twin-tapes) |
| ET11 | Twin tapes, Up switch and No change: `levels` equal on every channel but `sleeper`, and differ on the sleeper after onset | [tape](tape.md#twin-tapes) |
| ET12 | Shock: `base` and `impulse` are untouched on every channel. `factor` differs from the No change tape's from onset on. The sharp profile's impulse halves every `half_life` rounds within `1e-9`. The slide profile reaches `−depth` at round `onset + half_life` and rises after | [tape](tape.md#shock) |
| ET13 | Shock, hedge cap, 200 One shock seeds: at the trough, hedge `base + loading × impulse` is at least `hedge_margin_points` below the leader's, and `depth ≤ depth_drawn`. With `hedge_may_overtake` on and a config that allows it, at least `hedge_margin_points` above. With the default config and the knob on, `make_tape` raises `ValueError` on some seed in the first 50. On 200 Switch then shock seeds the same margin holds against the climate leader at the shock's onset, with that leader's loading at onset | [tape](tape.md#shock) |
| ET14 | `one_channel_shock`: `factor` and `base` equal the No change tape's, `impulse` is non-zero on the leader only, and `discerning` plays the same bets as on the No change tape | [tape](tape.md#shock) |
| ET15 | Switch, fall: after the ramp the leader's base is `size` below the base of the channel that was second at onset, within `1e-9`. The ramp is linear, no other base moves, the hedge is never the sleeper, `numbers["fall"]` equals the points moved | [tape](tape.md#switch) |
| ET16 | Switch, rise, on seeds with `short` 0: after the ramp the sleeper's base is `rise` above every other channel's base, including the runner-up's and the fallen leader's. Its loading from onset equals `numbers["sleeper_loading"]` and is positive. No other loading changes | [tape](tape.md#switch) |
| ET17 | Switch, `kind="draw"` over 1000 seeds: the share with a sleeper is within 0.05 of `riser_share` | [tape](tape.md#switch) |
| ET18 | Drift: after `length` rounds the leader's base is `size` below the channel that was second at onset. The linear profile's steps are equal. The logistic profile has the same endpoints and is monotone | [tape](tape.md#drift) |
| ET19 | Events past the last round: a config with `onset = (rounds, rounds)` and a drift makes a tape with one event and nothing out of bounds | [tape](tape.md#events) |
| ET20 | No two alike: a config with two shocks whose ranges are single values raises `ValueError` after 100 tries | [tape](tape.md#no-two-alike) |
| ET21 | Pinning: two pinned configs differing only in `own_scale` give equal `base`, `loadings`, `impulse` and events on each of 50 seeds of every scenario, One shock included | [tape](tape.md#pinning) |
| ET22 | Pinning, **slow**: over 1000 Down switch seeds, the pooled output of `discerning` minus `complacent` at `own_scale` 2, 4 and 8 agrees within 5% | [tape](tape.md#pinning) |
| ET23 | Nothing clipped: a config with a low ladder and a deep shock produces a level below 0, and `make_tape` does not raise | [tape](tape.md#invariants) |
| ET24 | A leader that would end at or below 0 raises `ValueError` | [tape](tape.md#invariants) |
| ET25 | Seeds `0` and `2**64 − 1` both make a tape | [tape](tape.md#seed-streams) |
| ET26 | Gap: on 200 Shock then switch seeds, the switch's onset minus the shock's onset lies inside `gap`. The first event's `numbers["gap"]` is present and inside `gap` | [tape](tape.md#events) |
| ET27 | A config with 4 channels and two `fall_and_rise` switches raises `ValueError` for an empty sleeper set | [tape](tape.md#draw-order) |
| ET28 | Every array on a tape is read only: assigning to `tape.levels[0, 0]` raises `ValueError` | [tape](tape.md#interface) |
| ET29 | `Event.numbers` has exactly the keys in the draw order table for its shape, `short` included on every switch, undo too, `tries` on every event, and `depth ≤ depth_drawn` on every One shock seed | [tape](tape.md#draw-order) |
| ET30 | Short share: over 1000 Up switch seeds, the share with `short` 1 is within 0.05 of `short_share`. Every Up switch then down switch and Down switch seed has `short` 0 | [tape](tape.md#switch) |
| ET31 | Short: on Up switch seeds with `short` 1, after the ramp the sleeper's base is `short_level` of the way from the runner-up's to the leader's within `1e-9`, strictly between them, and `climate_leader` is the leader in every round | [tape](tape.md#switch) |
| ET32 | Undo, 200 Up switch then down switch seeds: `events[1].channel` is `events[0].sleeper`, `events[1].sleeper` is `None`, after the undo's ramp `base` and `loadings` equal the No change tape's within `1e-9`, the ramp is linear, and `numbers["fall"]` equals the points the sleeper moved | [tape](tape.md#switch) |
| ET33 | Twin tapes, Switch then shock and Down switch: `levels` equal before the shock's onset, and differ somewhere after | [tape](tape.md#twin-tapes) |
| ET34 | Twin tapes, Up switch then down switch and Up switch: on seeds where Up switch has `short` 0, `levels` equal before the undo's onset. On seeds where it has `short` 1, they differ on the sleeper only | [tape](tape.md#twin-tapes) |
| ET35 | Twin tapes, Up switch then down switch and No change: `levels` equal from the end of the undo's ramp to the last round | [tape](tape.md#twin-tapes) |
| ET36 | No two alike, redraw: a config with two `ShockSpec()` events on 200 seeds. Consecutive shocks always differ in at least two draws, `gap` excluded. Every first event has `numbers["tries"] == 1`, and at least one second event has `tries > 1` | [tape](tape.md#no-two-alike) |

## Game

| Id | Test | Page |
|---|---|---|
| EG1 | Each row of the bets table raises `BetError` with the given `check`, at the defaults, and `str(error)` is `Bad tool call: {check}.`. `True` in a split fails `shape`, as do `10.0` and `"10"`. A split of `np.int64` passes. A split of 11 values fails `shape` before `sum`. A negative value fails `sign`, not `shape` | [game](game.md#bets) |
| EG2 | A `BetError` leaves `round`, `done` and `len(record)` unchanged | [game](game.md#bets) |
| EG3 | Inertia: with `inertia_cap = 20`, round 1 accepts any valid split, round 2 rejects a move of 21 with `check` `inertia` and accepts 20 | [game](game.md#bets) |
| EG4 | Readings: with `read_noise_z` set to all ones on a hand-built tape, a bet of 4 reads `level + k/2`, 16 reads `level + k/4`, 100 reads `level + k/10`, each to one decimal | [game](game.md#readings) |
| EG5 | Unfunded channels read `None`, and the row's readings are `None` exactly where bets are 0 | [game](game.md#readings) |
| EG6 | Output equals the exact-level weighted sum rounded to one decimal, not the sum of the readings, on a tape where they differ | [game](game.md#readings) |
| EG7 | A negative reading is possible: a low level and a large negative `read_noise_z` with a bet of 1 | [game](game.md#readings) |
| EG8 | Playing a finished game raises `RuntimeError`, and `done` is true after `rounds` valid splits | [game](game.md#bets) |
| EG9 | Bets passed as a list, a numpy array and a tuple of `np.int64` are all stored as a `tuple` of Python `int`, and `game.play(bets)` is `game.record.rows[-1]` | [game](game.md#bets) |
| EG11 | `unchanged_rounds` on bets A, A, B, B, A returns `[2, 4]` | [game](game.md#record) |
| EG12 | `readings_of(c)` skips rounds where `c` had no bet and keeps round order | [game](game.md#record) |
| EG13 | `Game(tape, record)` with rounds 1, 2, 4 raises `ValueError`, as does a record of `rounds + 1` rows. With rounds 1, 2, 3 it starts at round 4 | [game](game.md#starting-part-way) |
| EG14 | `play(complacent, tape, max_rounds=5)` returns five rows. Passing that record back and playing to the end gives `rounds` rows, and the five-row record still has five rows | [game](game.md#play) |
| EG15 | `play` with a policy that returns a bad split raises `BetError` | [game](game.md#play) |
| EG16 | `play` gives a peeking policy the tape and a non-peeking policy `None`, checked with a recording stub | [game](game.md#play) |
| EG17 | Determinism: `play(uniform, tape)` twice gives equal records | [game](game.md#invariants) |
| EG18 | `game.view(False)` has the game's round, `start` matching the tape's ladder, the game's record and `tape = None`. `game.view(True).tape is tape` | [game](game.md#view) |
| EG19 | `Game` on a hand-built tape whose `levels` has the wrong shape raises `ValueError` before any round is played | [game](game.md#starting-part-way) |
| EG20 | `record.rows` cannot be assigned to or appended to directly, and `record.copy()` is equal but not the same object | [game](game.md#record) |

- EG10 moved to the skins suite with the CSV, see [KR9 and KR10](../skins/tests.md#render). The number stays free so no reference goes stale.

## View

| Id | Test | Page |
|---|---|---|
| EV1 | `split_budget`: `[1] × 10` gives ten 10s. `[1, 1, 1]` with 100 gives `(34, 33, 33)`. All zeros and a negative raise `ValueError` | [view](view.md#split_budget) |
| EV2 | A policy that tries to write to `view.tape.levels` raises `ValueError` | [view](view.md#invariants) |

- EP1 to EP18 moved to the baselines suite with the policies, see [baselines tests](../baselines/tests.md). The letter stays retired so no reference goes stale.

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| EH1 | For any seed and scenario, ET2, ET3 and ET4 hold |
| EH2 | For any valid split, `Game.play` accepts it and the row's `None`s match its zeros |
| EH3 | For any weights with a positive sum, `split_budget` sums to the budget and is non-negative, see [view](view.md#split_budget) |

## Pilot decides

- ET22 doubles as [Tape sanity](../../pilot/engine-checks.md#tape-sanity) in the pilot, which runs it at every grid setting and records the numbers. Baseline order is [BP7](../baselines/tests.md#policies).

## Not decided

- Tolerances in ET6, ET7, ET17 and ET22 are first guesses. Tighten them once the suite runs.
