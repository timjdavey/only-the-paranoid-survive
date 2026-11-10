# Timeline

## Purpose

`make_timeline(config, seed)` turns a scenario and a seed into a timeline: the ground truth, every channel's level in every round, plus everything drawn on the way. Every run on a seed replays the same timeline. The design is in [generator](../../design/mechanics.md#generator).

## Interface

```python
@dataclass(frozen=True)
class Event:
    shape: Literal["shock", "switch", "drift"]
    onset: int                              # first round it edits, from 1
    channel: int | None                     # the channel whose base or impulse moved. None for a shock through the factor
    sleeper: int | None                     # the channel that rose, if one did
    numbers: Mapping[str, float | int | str]  # every per-seed draw by name, see Draw order below

@dataclass(frozen=True)
class Timeline:
    config: ScenarioConfig
    seed: int
    engine_hash: str
    levels: np.ndarray        # (rounds, channels), float. base + weather + loadings × factor + impulse
    base: np.ndarray          # (rounds, channels). The climate, after events
    weather: np.ndarray       # (rounds, channels). Own weather
    factor: np.ndarray        # (rounds,). The shared factor, shock impulses included
    loadings: np.ndarray      # (rounds, channels). Per round, as a switch redraws the sleeper's
    impulse: np.ndarray       # (rounds, channels). A one-channel shock. All zeros otherwise
    read_noise_z: np.ndarray  # (rounds, channels). Standard normals, see game.md
    leader: int
    runner_up: int
    field: tuple[int, ...]    # the other channels, hedge included, as in the glossary
    hedge: int
    sleeper: int | None
    events: tuple[Event, ...]

    def climate_leader(self, round: int) -> int   # argmax of base in that round, lowest index on a tie

def make_timeline(config: ScenarioConfig, seed: int) -> Timeline
```

- **Every array is read only.** `make_timeline` calls `setflags(write=False)` on each, so a peeking policy or a test cannot edit the ground truth by accident.
- **A timeline is never written to disk or into a log.** It is regenerated from `config` and `seed`, and `engine_hash` says which engine made it. A held-out seed's timeline is as secret as the seed, see [contamination](../../harness/contamination.md#public-and-held-out). The harness logs the hash and, for a held-out seed, its position in the list, never `seed` or any array.

## Behaviour

### Seed streams

- **One `SeedSequence(seed)`, spawned into seven children, in this order:** `ladder`, `loadings`, `weather`, `factor`, `onset`, `read_noise`, `events`. Each child makes its own `numpy.random.default_rng`. The `events` child is spawned once more into one child per event in `config.events`.
- **The first six streams never see the event list.** They draw the same numbers for every scenario on a seed, which is what makes [twin timelines](#twin-timelines).
- **Every draw consumes its stream in the order written on this page.** Changing the order changes every timeline, so it bumps `GENERATOR_VERSION`, see [config](config.md#engine-hash).
- **`seed` is any non-negative int up to 2^64 − 1.** Public seeds are small, held-out seeds are random 64-bit, see [contamination](../../harness/contamination.md#two-seed-sets).

### The ladder

From the `ladder` stream, in level points.

1. **Order.** `rng.permutation(channels)`. The first is the leader, the second the runner-up, the last the hedge, the rest are the field with the hedge.
2. **Leader.** Uniform from `leader_base`.
3. **Runner-up.** Leader minus a gap. The gap is uniform from `runner_up_gap_sigmas` times `own_scale`, or from `runner_up_gap_points` when [pinned](#pinning).
4. **Field.** For each field channel but the hedge, in order, uniform from `field_base` low to the smaller of `field_base` high and the runner-up minus `field_headroom`. If that top is below the low, raise `ValueError`.
5. **Hedge.** Uniform from `hedge_base`.

The ladder fills row 0 of `base`, and every later row starts as a copy of it. Events edit it from there.

### Loadings

From the `loadings` stream. One uniform from `loading` per channel in index order, then the hedge's is overwritten with a uniform from `hedge_loading`. This fills row 0 of `loadings` and every later row copies it until a switch redraws one.

### Weather and the shared factor

- **Own weather**, from the `weather` stream. `eps = rng.standard_normal((rounds, channels))`. Then per channel `z[0] = eps[0]` and `z[t] = p · z[t−1] + sqrt(1 − p²) · eps[t]` with `p = persistence`. `weather = own_scale × z`.
- **So `own_scale` is the SD per round at every round**, not the innovation SD. A bad stretch at `p = 0.8` is half gone after three rounds, see [each round](../../design/mechanics.md#each-round).
- **The shared factor**, from the `factor` stream, is the same recursion on one series, `eps = rng.standard_normal(rounds)`, scaled by `factor_scale`. Shock impulses are added to it afterwards, see [shock](#shock).

### Onset

From the `onset` stream, one `u = rng.random()`. The first event's onset is `low + floor(u × (high − low + 1))` from `config.onset`. With no events the draw is still made, so the stream order holds.

### Read noise

From the `read_noise` stream, `read_noise_z = rng.standard_normal((rounds, channels))`. Drawn for every channel in every round, bet on or not, so two agents on one seed meet the same roughness. [game](game.md#readings) scales it by the bet.

### Events

Events are applied in order. Each event has its own stream. The first event's onset is the [onset](#onset) draw. Each later event's onset is the previous event's onset plus its `gap` draw. An event is recorded even when its onset is past the last round, and anything it would edit past the last round is cut.

The channel that falls is the **climate leader at onset**, `climate_leader(onset)`, so a second switch after a first lands on the new leader. An [undo](#switch) is the one exception: it moves the earlier sleeper back, wherever that sleeper ranks.

#### Draw order

The draws each shape makes from its own stream, in order, and the key each gets in `Event.numbers`. Every draw is made even when the event does not use it, so the first event draws `gap` and ignores it, and a `fall` and a `fall_and_rise` consume the stream alike.

| Shape | Draws, in order | Derived keys, not draws |
|---|---|---|
| Shock | `gap`, `profile` (if `"draw"`, sharp or slide at even odds), `depth_drawn` (from `depth_sigmas` × `own_scale`, or `depth_points`), `half_life` | `depth`, after the [cap](#shock). `tries`, see [no two alike](#no-two-alike) |
| Switch | `gap`, `kind` (if `"draw"`, fall and rise with chance `riser_share`, else fall), `size`, `rise`, `ramp`, `sleeper` (uniform over the field minus the hedge minus any channel an earlier event moved), `sleeper_loading` (uniform from `loading`), `short` (1 with chance `short_share`, else 0), `short_level` (uniform from `short_level`) | `fall`, the points the leader's base moves, or the earlier sleeper's in an undo. `target`, the sleeper's end base, or the base an undo restores. `tries` |
| Drift | `gap`, `profile` (if `"draw"`, linear or logistic at even odds), `size`, `length` | `fall`, as a switch. `tries` |

- **`Event.numbers` holds exactly the keys in both columns**, nothing else, so a log's columns are stable.
- **An empty sleeper set raises `ValueError`.** With four channels and two switches the second has no channel to raise. The config is wrong, not the seed.

#### Shock

An impulse `s` that decays. By default it goes into the shared factor, `factor[t] += s[t]`, so every channel moves by its loading, most fall and the hedge rises.

- **Sharp.** `s[onset] = −depth`, then `s[t] = s[t−1] × 2^(−1 / half_life)`.
- **Slide.** Falls in a straight line over `half_life + 1` rounds, `s[onset + j] = −depth × (j + 1) / (half_life + 1)` for `j` from 0 to `half_life`, then rebounds from the trough with half-life `ceil(half_life / 2)`, `s[t] = s[t−1] × 2^(−1 / ceil(half_life / 2))`.
- **Hedge and leader at the trough.** Let the trough be `−depth`, `h` the hedge and `l` the climate leader at onset, with `base` and `loadings` read from row `onset − 1`. After a switch, `l` is the new leader, and may be a sleeper with a redrawn loading, as in the Switch then shock scenario. The hedge at the trough is `base[h] + loadings[h] × trough` and the leader is `base[l] + loadings[l] × trough`. With `hedge_may_overtake` off, `depth` is the smaller of `depth_drawn` and the depth at which the hedge sits exactly `hedge_margin_points` below the leader. With it on, `depth` is the larger of `depth_drawn` and the depth at which the hedge sits exactly `hedge_margin_points` above the leader. If that depth is above `depth_points` high, `make_timeline` raises `ValueError`, as the ladder and loadings do not allow the knob, see [config](config.md#not-decided).
- **`one_channel_shock`.** The impulse goes into `impulse[t, l]` instead of the factor, with no loading. `base` and `factor` are untouched, so the climate does not move and the Discerning baseline holds. The cap above does not apply. `Event.channel` is `l`.

#### Switch

Edits `base`, and the sleeper's `loadings`. Let `l` be the climate leader at onset, `r` the channel with the highest base at onset other than `l`, and `f(t) = min(1, (t − onset + 1) / ramp)` for `t ≥ onset`.

- **Fall.** The leader's base ends `size` below `r`'s. `fall = base[onset−1, l] − base[onset−1, r] + size`, and `base[t, l] −= fall × f(t)`. So a fall changes who pays best on every seed, see [events](../../design/mechanics.md#events).
- **Rise.** The sleeper's base moves in a straight line over the same ramp from its old base to `target`, then holds. `target` is the highest base of every channel but the sleeper at the end of the ramp, after any fall, plus `rise`. So the sleeper ends above the runner-up as well as the fallen leader, and the runner-up is a decoy. From `onset` on, `loadings[t, sleeper] = sleeper_loading`.
- **Short.** When `short` is 1, `target` is instead `base[e, q] + short_level × (base[e, l] − base[e, q])`, where `e` is the row at the end of the ramp and `q` the channel with the highest base at `e` other than `l` and the sleeper. So the sleeper ends above the runner-up and below the leader, and the climate leader never changes. Validation lets `short` be 1 only when `kind` is `"rise"`, see [config](config.md#fields).
- **`fall_and_rise`** does both. **`rise`** leaves the leader alone. **`fall`** leaves every other channel alone, and `sleeper` on the event is `None`.
- **Undo.** Let `s` be the sleeper of the most recent earlier switch. Its base moves in a straight line over this event's ramp, from `base[onset−1, s]` back to `base[0, s]`, then holds. From `onset` on, `loadings[t, s] = loadings[0, s]`. Row 0 holds its values from before it rose, as no event moves a channel before it is a sleeper. No other channel moves. `Event.channel` is `s`, `Event.sleeper` is `None`, `fall` is the points `s` moved and `target` is `base[0, s]`. It ignores the `kind`, `size`, `rise`, `sleeper`, `sleeper_loading`, `short` and `short_level` draws.
- `Timeline.sleeper` is the last sleeper any event made, or `None`.

#### Drift

Edits the leader's `base` over `length` rounds, with `fall` defined as for a [switch](#switch). Let `j = t − onset` from 0.

- **Linear.** `base[t, l] −= fall × min(1, (j + 1) / length)`.
- **Logistic.** The same endpoints on an S-curve: `g(x) = 1 / (1 + exp(−(8 / length) × (x − length / 2)))`, `base[t, l] −= fall × (g(j + 1) − g(0)) / (g(length) − g(0))` until `j + 1 = length`, then the full `fall`.

#### No two alike

Consecutive events of the same shape must differ in at least two of the shape's draws, `gap` excluded. An int or string draw differs when not equal. A float draw differs when the two are at least a tenth of the range's width apart, so a fixed range never differs. If they do not, the later event redraws every one of its draws, `gap` included, from where its stream left off. `numbers["tries"]` is how many times the event was drawn, 1 when the first draw was kept, so a log says how often the rule bit. After 100 tries `make_timeline` raises `ValueError`. See [stringing events](../../design/mechanics.md#stringing-events).

### Pinning

With `pin_in_level_points` true, every size that has a points range uses it and ignores the sigmas range: the runner-up gap, shock depth, switch size and rise, drift size. `hedge_margin_points` is already in points. Nothing else changes. So two configs that differ only in `own_scale` draw the same ladder and the same events, and only the weather grows, see [difficulty](../../design/mechanics.md#difficulty).

### Twin timelines

What one seed guarantees across scenarios whose configs differ only in `events`.

- The order, ladder, loadings, weather, factor before impulses, onset draw and `read_noise_z` are identical.
- One shock and Down switch `levels` are identical before the onset round.
- Shock then switch and One shock `levels` are identical before the switch's onset.
- Up switch and No change `levels` are identical on every channel but the sleeper.
- Switch then shock and Down switch `levels` are identical before the shock's onset.
- Up switch then down switch and Up switch `levels` are identical before the undo's onset, on seeds where the Up switch draws `short` as 0. On a short seed they differ on the sleeper from the first onset, as Up switch then down switch never stops short.
- Up switch then down switch and No change `base` and `loadings`, and so `levels`, are identical once the undo's ramp is complete.

## Invariants

- `levels == base + weather + loadings × factor[:, None] + impulse`, to floating point.
- `levels`, `base`, `weather`, `loadings`, `impulse`, `read_noise_z` have shape `(rounds, channels)`. `factor` has shape `(rounds,)`. All are read only.
- `impulse` is all zeros unless `one_channel_shock` is on.
- No array is clipped. A level can be below 0.
- Exactly one leader, runner-up and hedge, all different, and `field` has `channels − 2` entries including the hedge.
- At round 1, `base[0, leader] > base[0, runner_up] > base[0, c]` for every other channel, and the hedge's base is the lowest.
- Every loading is positive except the hedge's, which is negative, until a switch redraws the sleeper's, which is positive.
- After a fall or drift completes, the fallen channel's base is `size` below the channel that was second at onset. After a rise completes, the sleeper's base is `rise` above every other channel's, unless it is short, when it lies strictly between the runner-up's and the leader's.
- After an undo completes, the undone sleeper's base and loading equal their row 0 values. In the Up switch then down switch scenario that makes `base` and `loadings` equal the No change timeline's.
- A switch or drift leaves the leader's base above 0 on every seed. If a draw would not, `make_timeline` raises `ValueError`, as the config is wrong.
- With `hedge_may_overtake` off, the hedge's `base + loading × trough` is at least `hedge_margin_points` below the leader's. Weather is not counted, see [shock](#shock).
- Same config and seed give equal arrays and equal `engine_hash` on every call within one environment. Across numpy versions or CPUs, `allclose` at `1e-9`, see [config](config.md#engine-hash).

## Pilot decides

- Every range and scale in [config defaults](config.md#defaults).
- Whether the cut at the last round for a long drift leaves the Slow drift scenario enough rounds at the new level. [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) decides.
- Whether the Switch then shock scenario's shock, which lands 20 to 32, leaves enough rounds after it to recover before round 40. [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) decides, as it does for the other two-event scenarios.
- How often the shock cap bites at the defaults. [The tell](../../pilot/engine-checks.md#the-tell) reports the share of seeds where `depth < depth_drawn`.

## Not decided

- Whether a drift should sometimes carry a riser, as a switch does. It does not here. Decide after [Up and down](../../pilot/engine-checks.md#up-and-down) has run.
