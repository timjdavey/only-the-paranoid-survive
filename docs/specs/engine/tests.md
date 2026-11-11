# Tests

Every test the engine suite runs, in `tests/engine/`. Ids start `E` for the engine, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, and they import `paranoid.engine` alone, see [layout](../../harness/layout.md#five-layers). Where a test needs a policy it builds a stub in the test file, see [stub policies](#stub-policies), and a test that needs a real baseline lives in the [baselines suite](../baselines/tests.md). Tests marked **slow** run a thousand seeds and are skipped by default, run with `-m slow`. Where a check uses a tolerance it is given, so the test can be written from this page alone.

## Config

| Id | Test | Page |
|---|---|---|
| EC1 | Every key in `SCENARIOS` equals its config's `name`, the eight glossary code names are all present in the scenario table's order and nothing else, and assigning to `SCENARIOS` raises `TypeError` | [config](config.md#scenarios) |
| EC2 | `ScenarioConfig()` with each bad value in the validation list raises `ValueError`, one case per clause, including `onset=(1, 5)`, a `runner_up_gap_points` low of 0, an infinite `own_scale`, an unknown `kind`, a `size_sigmas` low of 0, a `hedge_margin_points` of 0, `short_share=0.5` on a `"draw"` switch, a `short_level` of `(0.0, 0.5)`, an undo as the first event and an undo after a `"fall"` switch | [config](config.md#fields) |
| EC3 | `engine_hash(SCENARIOS["no_change"])` is 12 lowercase hex characters and equals a pinned string. Changing the pinned string is a reviewed change | [config](config.md#engine-hash) |
| EC4 | `dataclasses.replace` on each field with a different valid value changes the hash. Replacing a field with its own value does not | [config](config.md#engine-hash) |
| EC5 | Each `*_points` default equals its `*_sigmas` default times `own_scale` at the default config | [config](config.md#defaults) |
| EC6 | `leader_base=(90, 100)` and `(90.0, 100.0)` give equal configs, equal hashes and equal timelines on seed 0 | [config](config.md#fields) |
| EC7 | The test rebuilds the canonical JSON of `one_shock` from the recipe on the config page, and its SHA-256 starts with `engine_hash`. It contains `"shape":"shock"` inside its one event, and `shock_then_switch`'s has one `shock` and one `switch` | [config](config.md#engine-hash) |
| EC8 | `replace(SCENARIOS[name], own_scale=8.0, pin_in_level_points=True)` builds for every scenario. The same with `pin_in_level_points=False` raises `ValueError`, as does a pinned config with `runner_up_gap_points=(8.0, 30.0)` | [config](config.md#fields) |
| EC9 | A `Range` entry that is not a real number, an `IntRange` entry or `int` field that is not a whole number, and a `bool` in either, raise `TypeError`. `own_scale=4` and `own_scale=4.0` give equal configs and equal hashes | [config](config.md#fields) |

## Timeline

| Id | Test | Page |
|---|---|---|
| ET1 | `make_timeline(c, s)` twice gives equal arrays, equal events and equal hash. A subprocess gives the same | [timeline](timeline.md#invariants) |
| ET2 | Shapes: `(rounds, channels)` for `levels`, `base`, `weather`, `loadings`, `impulse`, `read_noise_z`, `(rounds,)` for `factor` | [timeline](timeline.md#invariants) |
| ET3 | `levels` equals `base + weather + loadings × factor[:, None] + impulse` within `1e-9` | [timeline](timeline.md#invariants) |
| ET4 | Ladder on 200 seeds: leader, runner-up and hedge distinct, `field` has `channels − 2` entries with the hedge, leader base above runner-up above every other, hedge lowest, every field channel at least `field_headroom` below the runner-up | [timeline](timeline.md#the-ladder) |
| ET5 | Loadings on 200 seeds: every row 0 loading inside `loading`, except the hedge's inside `hedge_loading` | [timeline](timeline.md#loadings) |
| ET6 | Weather SD, **slow**: over 2000 No change seeds, the SD of `weather[t, :]` pooled across channels and seeds at each of rounds 1, 10 and 40 is within 5% of `own_scale`. The SD of `factor[t]` across seeds at the same rounds is within 10% of `factor_scale` | [timeline](timeline.md#weather-and-the-shared-factor) |
| ET7 | Persistence, **slow**: over the same seeds, the correlation across seeds between `weather[t, c]` and `weather[t + 1, c]`, pooled across channels, at each of rounds 1, 10 and 39 is within 0.05 of `persistence`. It is measured across seeds and never along one series, as a 40 round series reads about 0.09 low | [timeline](timeline.md#weather-and-the-shared-factor) |
| ET8 | Onset on 200 seeds lies inside `config.onset`, and is the same for `one_shock` and `down_switch` on each seed | [timeline](timeline.md#onset) |
| ET9 | Twin timelines, One shock and Down switch: `levels[:onset−1]` equal exactly, and differ somewhere after | [timeline](timeline.md#twin-timelines) |
| ET10 | Twin timelines, Shock then switch and One shock: `levels` equal before the switch's onset | [timeline](timeline.md#twin-timelines) |
| ET11 | Twin timelines, Up switch and No change: `levels` equal on every channel but `sleeper`, and differ on the sleeper after onset | [timeline](timeline.md#twin-timelines) |
| ET12 | Shock: `base` and `impulse` are untouched on every channel. `factor` differs from the No change timeline's from onset on. The sharp profile's impulse halves every `half_life` rounds within `1e-9`. The slide profile reaches `−depth` at round `onset + half_life` and rises after | [timeline](timeline.md#shock) |
| ET13 | Shock, hedge cap, 200 One shock seeds: at the trough, which is `−numbers["depth"]`, hedge `base + loading × trough` is at least `hedge_margin_points` below the leader's, and `depth ≤ depth_drawn`. With `hedge_may_overtake` on and `events=(ShockSpec(depth_sigmas=(4.0, 25.0), depth_points=(16.0, 100.0)),)`, which the default ladder and loadings allow on every seed as they never need more than 90 points, at least `hedge_margin_points` above. With the default config and the knob on, `make_timeline` raises `ValueError` on some seed in the first 50. On 200 Switch then shock seeds the same margin holds against the climate leader at the shock's onset, with that leader's loading at onset | [timeline](timeline.md#shock) |
| ET14 | `one_channel_shock`: `factor` and `base` equal the No change timeline's, `impulse` is non-zero on the leader only, and `climate_leader(round)` is the same channel as on the No change timeline in every round. That the Discerning baseline then plays the same bets is [BP13](../baselines/tests.md#policies) | [timeline](timeline.md#shock) |
| ET15 | Switch, fall: after the ramp the leader's base is `size` below the base of the channel that was second at onset, within `1e-9`. The ramp is linear, no other base moves, the hedge is never the sleeper, `numbers["fall"]` equals the points moved | [timeline](timeline.md#switch) |
| ET16 | Switch, rise, on seeds with `short` 0: after the ramp the sleeper's base is `rise` above the highest other channel's base within `1e-9`, so above the runner-up's and the fallen leader's. Its loading from onset equals `numbers["sleeper_loading"]` and is positive. No other loading changes | [timeline](timeline.md#switch) |
| ET17 | Switch, `kind="draw"`, **slow**: over 1000 seeds, the share with a sleeper is within 0.05 of `riser_share` | [timeline](timeline.md#switch) |
| ET18 | Drift, with `length=(10, 15)` so it ends by round 40: after `length` rounds the leader's base is `size` below the channel that was second at onset, within `1e-9`. The linear profile's steps are equal. The logistic profile has the same endpoints and is monotone | [timeline](timeline.md#drift) |
| ET19 | Events past the last round: a config with `onset = (rounds, rounds)`, a drift then a shock, makes a timeline with two events, the shock's onset past `rounds`, every array the right shape, and the drift's first step on the last round | [timeline](timeline.md#events) |
| ET20 | No two alike: a config with two shocks whose ranges are single values raises `ValueError` after 100 tries | [timeline](timeline.md#no-two-alike) |
| ET21 | Pinning: two pinned configs differing only in `own_scale` give equal `base`, `loadings`, `impulse` and events on each of 50 seeds of every scenario, One shock included | [timeline](timeline.md#pinning) |
| ET23 | Nothing clipped: a config with a low ladder and a deep shock produces a level below 0, and `make_timeline` does not raise | [timeline](timeline.md#invariants) |
| ET24 | A leader that would end at or below 0 raises `ValueError` | [timeline](timeline.md#invariants) |
| ET25 | Seeds `0` and `2**64 − 1` both make a timeline | [timeline](timeline.md#seed-streams) |
| ET26 | Gap: on 200 Shock then switch seeds, the switch's onset minus the shock's onset lies inside `gap`. The first event's `numbers["gap"]` is present and inside `gap` | [timeline](timeline.md#events) |
| ET27 | A config with 4 channels and two `fall_and_rise` switches raises `ValueError` for an empty sleeper set | [timeline](timeline.md#draw-order) |
| ET28 | Every array on a timeline is read only: assigning to `timeline.levels[0, 0]` raises `ValueError` | [timeline](timeline.md#interface) |
| ET29 | `Event.numbers` has exactly the keys in the draw order table for its shape, `short` included on every switch, undo too, `tries` on every event, and `depth ≤ depth_drawn` on every One shock seed | [timeline](timeline.md#draw-order) |
| ET30 | Short share, **slow**: over 1000 Up switch seeds, the share with `short` 1 is within 0.05 of `short_share`. Every Up switch then down switch and Down switch seed has `short` 0 | [timeline](timeline.md#switch) |
| ET31 | Short: on Up switch seeds with `short` 1, after the ramp the sleeper's base is `short_level` of the way from the runner-up's to the leader's within `1e-9`, strictly between them, and `climate_leader` is the leader in every round | [timeline](timeline.md#switch) |
| ET32 | Undo, 200 Up switch then down switch seeds: `events[1].channel` is `events[0].sleeper`, `events[1].sleeper` is `None`, after the undo's ramp `base` and `loadings` equal the No change timeline's within `1e-9`, the ramp is linear, and `numbers["fall"]` equals the points the sleeper moved | [timeline](timeline.md#switch) |
| ET33 | Twin timelines, Switch then shock and Down switch: `levels` equal before the shock's onset, and differ somewhere after | [timeline](timeline.md#twin-timelines) |
| ET34 | Twin timelines, Up switch then down switch and Up switch: on seeds where Up switch has `short` 0, `levels` equal before the undo's onset. On seeds where it has `short` 1, they differ on the sleeper only | [timeline](timeline.md#twin-timelines) |
| ET35 | Twin timelines, Up switch then down switch and No change: `levels` equal from the end of the undo's ramp to the last round | [timeline](timeline.md#twin-timelines) |
| ET36 | No two alike, redraw: a config with two `ShockSpec()` events on 200 seeds. Consecutive shocks always differ in at least two draws, `gap` excluded. Every first event has `numbers["tries"] == 1`, and at least one second event has `tries > 1` | [timeline](timeline.md#no-two-alike) |
| ET37 | `inertia_cap`: a config with it set has a different hash from one without, and the same arrays and events on 20 seeds | [config](config.md#fields) |

## Game

| Id | Test | Page |
|---|---|---|
| EG1 | Each row of the bets table raises `BetError` with the given `check`, at the defaults, and `str(error)` is `Bad tool call: {check}.`. `True` in a split fails `shape`, as do `10.0` and `"10"`. A split of `np.int64` passes. A split of 11 values fails `shape` before `sum`. A negative value fails `sign`, not `shape` | [game](game.md#bets) |
| EG2 | A `BetError` leaves `round`, `done` and `len(record)` unchanged | [game](game.md#bets) |
| EG3 | Inertia: with `inertia_cap = 20`, round 1 accepts any valid split, round 2 rejects a move of 21 with `check` `inertia` and accepts 20 | [game](game.md#bets) |
| EG4 | Readings: with `read_noise_z` set to all ones on a hand-built timeline, round 1 splits 4, 16 and 80 and reads `level + k/2`, `level + k/4` and `level + k/sqrt(80)`, and round 2 puts 100 on one channel and reads `level + k/10`, each to one decimal | [game](game.md#readings) |
| EG5 | Unfunded channels read `None`, and the row's readings are `None` exactly where bets are 0 | [game](game.md#readings) |
| EG6 | `row.output` equals the row's bets times its rounded readings, added up and divided by the budget, on an all in row and a split row, and differs from the level-weighted sum on a timeline with read noise | [game](game.md#readings) |
| EG7 | A negative reading is possible: a low level and a large negative `read_noise_z` with a bet of 1 | [game](game.md#readings) |
| EG8 | Playing a finished game raises `RuntimeError`, and `done` is true after `rounds` valid splits | [game](game.md#bets) |
| EG9 | Bets passed as a list, a numpy array and a tuple of `np.int64` are all stored as a `tuple` of Python `int`, and `game.play(bets)` is `game.record.rows[-1]` | [game](game.md#bets) |
| EG11 | `unchanged_rounds` on bets A, A, B, B, A returns `[2, 4]` | [game](game.md#record) |
| EG12 | `readings_of(c)` skips rounds where `c` had no bet and keeps round order | [game](game.md#record) |
| EG13 | `Game(timeline, record)` with rounds 1, 2, 4 raises `ValueError`, as does a record of `rounds + 1` rows. With rounds 1, 2, 3 it starts at round 4 | [game](game.md#starting-part-way) |
| EG14 | `play(on_first, timeline, max_rounds=5)` returns five rows. Passing that record back and playing to the end gives `rounds` rows, and the five-row record still has five rows | [game](game.md#play) |
| EG15 | `play` with a policy that returns a bad split raises `BetError` | [game](game.md#play) |
| EG16 | `play` gives a peeking policy the timeline and a non-peeking policy `None`, checked with a recording stub | [game](game.md#play) |
| EG17 | Determinism: `play(even, timeline)` twice gives equal records | [game](game.md#invariants) |
| EG18 | `game.view(False)` has the game's round, `start` matching the timeline's ladder, the game's record and `timeline = None`. `game.view(True).timeline is timeline` | [game](game.md#view) |
| EG19 | `Game` on a hand-built timeline whose `levels` has the wrong shape raises `ValueError` before any round is played | [game](game.md#starting-part-way) |
| EG20 | `record.rows` cannot be assigned to or appended to directly, and `record.copy()` is equal but not the same object | [game](game.md#record) |

- EG10 moved to the skins suite with the CSV, see [KR9 and KR10](../skins/tests.md#render). The number stays free so no reference goes stale.
- ET22 moved to the baselines suite as [BP14](../baselines/tests.md#policies), as it plays the Discerning and Complacent baselines. Its number stays free too.

## View

| Id | Test | Page |
|---|---|---|
| EV1 | `split_budget`: `[1] × 10` gives ten 10s. `[1, 1, 1]` with 100 gives `(34, 33, 33)`. All zeros and a negative raise `ValueError` | [view](view.md#split_budget) |
| EV2 | A policy that tries to write to `view.timeline.levels` raises `ValueError` | [view](view.md#invariants) |
| EV3 | On every round of 20 seeds of every scenario, `view.dials` equals the nine fields of the same names on the timeline's config, and `Dials` has no other field | [view](view.md#view) |

- EP1 to EP18 moved to the baselines suite with the policies, see [baselines tests](../baselines/tests.md). The letter stays retired so no reference goes stale.

## Stub policies

The engine suite may not import the baselines layer, so the two tests that only need some policy use these, defined in `tests/engine/conftest.py`. Each is a frozen dataclass with `peeks: ClassVar[bool] = False`, as the [`Policy`](view.md#interface) protocol asks.

| Stub | Split each round |
|---|---|
| `on_first` | `budget` on channel 0 |
| `even` | `split_budget([1] × channels, budget)` |

- **They test `play`, never a baseline.** Any valid policy serves EG14 and EG17, so the stubs are as plain as a policy can be. A test that needs what a real baseline does is a baselines test.

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| EH1 | For any seed and scenario, ET2, ET3 and ET4 hold |
| EH2 | For any valid split, `Game.play` accepts it and the row's `None`s match its zeros |
| EH3 | For any finite non-negative weights with a positive sum, `split_budget` sums to the budget and is non-negative, see [view](view.md#split_budget). A weight that is not finite raises `ValueError` |

## Pilot decides

- [Timeline sanity](../../pilot/engine-checks.md#timeline-sanity) in the pilot runs the pinning test [BP14](../baselines/tests.md#policies) at every grid setting and records the numbers. Baseline order is the pilot's, with the part no knob can change in [BP7](../baselines/tests.md#policies).

## Not decided

- Tolerances in ET6, ET7 and ET17 are first guesses. Tighten them once the suite runs.
