# Tape

## Purpose

`make_tape(config, seed)` turns a scenario and a seed into a tape: the true level of every channel in every round, plus everything drawn on the way. Every run on a seed replays the same tape. The design is in [generator](../../design/mechanics.md#generator).

## Interface

```python
@dataclass(frozen=True)
class Event:
    shape: Literal["shock", "switch", "drift"]
    onset: int                              # first round it edits, from 1
    channel: int | None                     # the channel whose base level moved. None for a shock through the factor
    sleeper: int | None                     # the channel that rose, if one did
    numbers: Mapping[str, float | int | str]  # every per-seed draw by name, see Draw order below

@dataclass(frozen=True)
class Tape:
    config: ScenarioConfig
    seed: int
    engine_hash: str
    levels: np.ndarray        # (rounds, channels), float. base + weather + loadings × factor
    base: np.ndarray          # (rounds, channels). The climate, after events
    weather: np.ndarray       # (rounds, channels). Own weather
    factor: np.ndarray        # (rounds,). The shared factor, shock impulses included
    loadings: np.ndarray      # (rounds, channels). Per round, as a switch redraws the sleeper's
    read_noise_z: np.ndarray  # (rounds, channels). Standard normals, see game.md
    leader: int
    runner_up: int
    field: tuple[int, ...]    # the other channels, hedge included, as in the glossary
    hedge: int
    sleeper: int | None
    events: tuple[Event, ...]

    def climate_leader(self, round: int) -> int   # argmax of base in that round, lowest index on a tie

def make_tape(config: ScenarioConfig, seed: int) -> Tape
```

## Behaviour

### Seed streams

- **One `SeedSequence(seed)`, spawned into seven children, in this order:** `ladder`, `loadings`, `weather`, `factor`, `onset`, `read_noise`, `events`. Each child makes its own `numpy.random.default_rng`. The `events` child is spawned once more into one child per event in `config.events`.
- **The first six streams never see the event list.** They draw the same numbers for every scenario on a seed, which is what makes [twin tapes](#twin-tapes).
- **Every draw consumes its stream in the order written on this page.** Changing the order changes every tape, so it bumps `GENERATOR_VERSION`, see [config](config.md#engine-hash).
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

Events are applied in order. Each event has its own stream. Each later event's onset is the previous event's onset plus a uniform from its `gap`. An event is recorded even when its onset is past the last round, and anything it would edit past the last round is cut.

The channel that falls is the **climate leader at onset**, `climate_leader(onset)`, so a second switch after a first lands on the new leader.

#### Draw order

The draws each shape makes, in order, and the key each gets in `Event.numbers`.

| Shape | Draws, in order |
|---|---|
| Shock | `profile` (if `"draw"`, sharp or slide at even odds), `depth` (from `depth_sigmas` × `own_scale`, or `depth_points`), `half_life` |
| Switch | `kind` (if `"draw"`, fall and rise with chance `riser_share`, else fall), `size`, `rise`, `ramp`, `sleeper` (uniform over the field minus the hedge minus any channel an earlier event moved), `sleeper_loading` (uniform from `loading`) |
| Drift | `profile` (if `"draw"`, linear or logistic at even odds), `size`, `length` |

Every draw is made even when the kind does not use it, so a `fall` and a `fall_and_rise` consume the stream alike.

#### Shock

An impulse `s` into the shared factor, `factor[t] += s[t]`. Every channel moves by its loading, so most fall and the hedge rises.

- **Sharp.** `s[onset] = −depth`, then `s[t] = s[t−1] × 2^(−1 / half_life)`.
- **Slide.** Falls in a straight line over `half_life + 1` rounds, `s[onset + j] = −depth × (j + 1) / (half_life + 1)` for `j` from 0 to `half_life`, then rebounds with half-life `ceil(half_life / 2)`.
- **Hedge and leader at the trough.** Let the trough be `−depth`. With `hedge_may_overtake` off, `depth` is capped so that the hedge's `base + loading × trough` sits at least one sigma below the leader's. With it on, `depth` is raised so the hedge sits at least one sigma above. The drawn and the final depth both go in `numbers`, as `depth_drawn` and `depth`.
- **`one_channel_shock`.** The impulse is added to the leader's `base` instead of the factor, with no loading, and the cap above does not apply.

#### Switch

Edits `base`, and the sleeper's `loadings`. Let `f(t) = min(1, (t − onset + 1) / ramp)` for `t ≥ onset`.

- **Fall.** `base[t, leader] −= size × f(t)`.
- **Rise.** The sleeper's base moves in a straight line over the same ramp from its old base to a target, then holds. The target is the leader's base at the end of the ramp, after any fall, plus `rise`. From `onset` on, `loadings[t, sleeper] = sleeper_loading`.
- **`fall_and_rise`** does both. **`rise`** leaves the leader alone. **`fall`** leaves every other channel alone, and `sleeper` on the event is `None`.
- `Tape.sleeper` is the last sleeper any event made, or `None`.

#### Drift

Edits the leader's `base` over `length` rounds. Let `j = t − onset` from 0.

- **Linear.** `base[t, leader] −= size × min(1, (j + 1) / length)`.
- **Logistic.** The same endpoints on an S-curve: `g(x) = 1 / (1 + exp(−(8 / length) × (x − length / 2)))`, `base[t, leader] −= size × (g(j + 1) − g(0)) / (g(length) − g(0))` until `j + 1 = length`, then the full `size`.

#### No two alike

Consecutive events of the same shape must differ in at least two draws. An int or string draw differs when not equal. A float draw differs when the two are at least a tenth of the range's width apart. If they do not, the later event redraws everything from its own stream. After 100 tries `make_tape` raises `ValueError`. See [stringing events](../../design/mechanics.md#stringing-events).

### Pinning

With `pin_in_level_points` true, every size that has a points range uses it and ignores the sigmas range: the runner-up gap, shock depth, switch size and rise, drift size. Nothing else changes. So two configs that differ only in `own_scale` draw the same ladder and the same events, and only the weather grows, see [difficulty](../../design/mechanics.md#difficulty).

### Twin tapes

What one seed guarantees across scenarios whose configs differ only in `events`.

- The order, ladder, loadings, weather, factor before impulses, onset draw and `read_noise_z` are identical.
- One shock and Down switch `levels` are identical before the onset round.
- Shock then switch and One shock `levels` are identical before the switch's onset.
- Up switch and No change `levels` are identical on every channel but the sleeper.

## Invariants

- `levels == base + weather + loadings × factor[:, None]`, to floating point.
- `levels`, `base`, `weather`, `loadings`, `read_noise_z` have shape `(rounds, channels)`. `factor` has shape `(rounds,)`.
- No array is clipped. A level can be below 0.
- Exactly one leader, runner-up and hedge, all different, and `field` has `channels − 2` entries including the hedge.
- At round 1, `base[0, leader] > base[0, runner_up] > base[0, c]` for every other channel, and the hedge's base is the lowest.
- Every loading is positive except the hedge's, which is negative, until a switch redraws the sleeper's, which is positive.
- A switch or drift leaves the leader's base above 0 on every seed. If a draw would not, `make_tape` raises `ValueError`, as the config is wrong.
- With `hedge_may_overtake` off, the hedge's `base + loading × factor_impulse` never exceeds the leader's. Weather is not counted, see [shock](#shock).
- Same config and seed give equal arrays and equal `engine_hash` on every call and every machine.

## Tests

See [tests](tests.md#tape).

## Open

- Every range and scale in [config defaults](config.md#defaults) is pilot to confirm.
- Whether a drift should sometimes carry a riser, as a switch does. It does not here. Revisit after [Up and down](../../pilot/engine-checks.md#up-and-down).
- Whether the cut at the last round for a long drift leaves the Slow drift scenario enough rounds at the new level. [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) decides.
