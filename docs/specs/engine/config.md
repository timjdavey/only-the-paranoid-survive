# Config

## Purpose

`ScenarioConfig` holds every number the engine uses, so a scenario is data and the engine is built from [mechanics](../../design/mechanics.md) alone. The six scenarios are six configs. A hash of the config goes into every tape and every log.

## Interface

```python
Range = tuple[float, float]      # inclusive low, inclusive high, drawn uniform per seed
IntRange = tuple[int, int]       # inclusive low, inclusive high, drawn uniform per seed

@dataclass(frozen=True)
class ShockSpec:
    gap: IntRange = (8, 12)                 # rounds after the previous event's onset. Drawn and ignored for the first event
    depth_sigmas: Range = (4.0, 8.0)        # impulse into the shared factor, in sigmas. Capped per seed, see tape
    depth_points: Range = (16.0, 32.0)      # the same, in level points, used when pinned
    half_life: IntRange = (2, 4)            # rounds for the impulse to halve
    profile: Literal["sharp", "slide", "draw"] = "draw"

@dataclass(frozen=True)
class SwitchSpec:
    gap: IntRange = (8, 12)
    kind: Literal["fall", "fall_and_rise", "rise", "draw"] = "draw"
    riser_share: float = 0.5                # chance "draw" gives fall_and_rise rather than fall
    size_sigmas: Range = (1.0, 3.0)         # how far below the runner-up's base the leader's base ends
    size_points: Range = (4.0, 12.0)
    rise_sigmas: Range = (1.0, 3.0)         # how far above every other channel's base the sleeper's base ends
    rise_points: Range = (4.0, 12.0)
    ramp: IntRange = (1, 5)                 # rounds the move is spread over, linear

@dataclass(frozen=True)
class DriftSpec:
    gap: IntRange = (8, 12)
    size_sigmas: Range = (1.0, 3.0)         # how far below the runner-up's base the leader's base ends
    size_points: Range = (4.0, 12.0)
    length: IntRange = (15, 25)             # rounds the fall is spread over
    profile: Literal["linear", "logistic", "draw"] = "draw"

EventSpec = ShockSpec | SwitchSpec | DriftSpec

@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    # shape
    channels: int = 10
    rounds: int = 40
    budget: int = 100
    # ladder, in level points unless the name says sigmas
    leader_base: Range = (60.0, 70.0)
    runner_up_gap_sigmas: Range = (2.0, 4.0)
    runner_up_gap_points: Range = (8.0, 16.0)
    field_base: Range = (30.0, 55.0)
    field_headroom: float = 4.0             # a field channel lands at least this far below the runner-up
    hedge_base: Range = (20.0, 28.0)
    # weather
    own_scale: float = 4.0                  # sigma: the SD per round of own weather
    persistence: float = 0.8
    factor_scale: float = 3.0               # the SD per round of the shared factor
    loading: Range = (0.3, 1.0)
    hedge_loading: Range = (-0.6, -0.3)
    # what the agent sees
    read_noise_k: float = 8.0               # reading SD is k / sqrt(bet)
    # events
    events: tuple[EventSpec, ...] = ()
    onset: IntRange = (12, 20)              # the first event's onset round
    pin_in_level_points: bool = False
    hedge_margin_points: float = 4.0        # at a shock's trough the hedge sits at least this far from the leader, see tape
    # hard-variant knobs
    hedge_may_overtake: bool = False
    one_channel_shock: bool = False
    inertia_cap: int | None = None

SCENARIOS: Mapping[str, ScenarioConfig]     # read only
GENERATOR_VERSION: int                      # bumped when make_tape changes for the same config
def engine_hash(config: ScenarioConfig) -> str
```

## Behaviour

### Fields

- **Every number in [mechanics](../../design/mechanics.md) is a field.** Nothing is hard coded in `tape.py` or `game.py`. If a rule needs a number, it gets a field here first.
- **A `Range` is drawn uniform per seed**, low and high inclusive. An `IntRange` is drawn uniform over the whole numbers from low to high inclusive. A range with low equal to high is a fixed value.
- **Ranges are stored as floats and `IntRange`s as ints.** `__post_init__` casts each entry, so `leader_base=(60, 70)` and `(60.0, 70.0)` are one config with one hash. A `Range` entry that is not a real number, or an `IntRange` entry that is not a whole number, raises `TypeError`.
- **Sizes come in pairs**, one in sigmas and one in level points. The engine reads the sigmas pair unless `pin_in_level_points` is true, then it reads the points pair and ignores the sigmas pair. See [difficulty](../../design/mechanics.md#difficulty) for why. The pairs are set so that at the default `own_scale` they agree.
- **A switch or drift `size` is measured from the runner-up**, not from where the leader was. The leader's base ends `size` below the runner-up's base, so a fall changes who pays best on every seed. The points the leader actually moves are the gap to the runner-up plus `size`, see [switch](tape.md#switch).
- **`own_scale` is the weather's SD per round**, not the SD of the innovation. [tape](tape.md) says how the AR(1) is scaled to make that so. It is the axis of the [noise grid](../../pilot/engine-checks.md#noise-grid).
- **`persistence` never moves within a release**, see [difficulty](../../design/mechanics.md#difficulty). The engine does not enforce this, the release process does.
- **`hedge_margin_points`** is in level points, so it survives [pinning](tape.md#pinning). It bounds the shock depth, see [shock](tape.md#shock).
- **`inertia_cap`** is off by default. When set, no bet may move more than this many points from the round before, see [game](game.md#bets) and [inertia](../../design/scoring.md#extension-inertia).
- **Validation on construction.** `__post_init__` raises `ValueError` if any of these hold:
  - `channels < 4`, `rounds < 1`, `budget < channels`.
  - Any range has low above high.
  - `persistence` is outside `[0, 1)`. `own_scale`, `factor_scale`, `read_noise_k`, `field_headroom` or `hedge_margin_points` is not positive.
  - `loading` has a low at or below 0. `hedge_loading` has a high at or above 0.
  - `onset` low is below 1 or `onset` high is above `rounds`.
  - `hedge_base` high is not below `field_base` low.
  - `field_base` low is above `leader_base` low minus the larger of `runner_up_gap_points` high and `runner_up_gap_sigmas` high × `own_scale`, minus `field_headroom`.
  - In any event spec: `riser_share` is outside `[0, 1]`, `gap`, `ramp`, `half_life` or `length` has a low below 1, or any `*_sigmas` or `*_points` range has a low at or below 0.

### Scenarios

`SCENARIOS` maps each code name from the [glossary](../../glossary.md#how-the-world-changes) to a config. Each is the defaults above plus its events. It is a `types.MappingProxyType`, so a caller cannot replace a scenario under a name that is already in a log.

| Code name | `events` | Note |
|---|---|---|
| `no_change` | `()` | The control |
| `one_shock` | `(ShockSpec(),)` | |
| `down_switch` | `(SwitchSpec(kind="draw"),)` | Per seed, fall or fall and rise, see [events](../../design/mechanics.md#events) |
| `up_switch` | `(SwitchSpec(kind="rise"),)` | The leader holds |
| `shock_then_switch` | `(ShockSpec(), SwitchSpec(kind="draw"))` | The switch is a down switch, `gap` rounds after the shock's onset |
| `slow_drift` | `(DriftSpec(),)` | |

- **`name` equals the key.** `SCENARIOS["one_shock"].name == "one_shock"`.
- **The first event lands at `onset`**, which every scenario shares. So twin tapes share their onset round, see [tape](tape.md#twin-tapes). Later events land `gap` rounds after the previous event's onset.
- **A hard variant is a new config**, not a flag: more events in the tuple, or a longer `length`. It gets its own key when it exists, see [scenarios](../../design/scenarios.md#scenarios-we-test).

### Engine hash

- **`engine_hash(config)`** is the first 12 hex characters of the SHA-256 of a canonical JSON string. The string is `dataclasses.asdict(config)` with sorted keys, no whitespace, floats as `repr`, plus two additions: each event dict gets a key `"shape"` with `"shock"`, `"switch"` or `"drift"`, and the top level gets `"generator_version": GENERATOR_VERSION`. The `shape` key is there so two spec types that ever share a field set cannot collide.
- **Same config, same hash**, across Python versions and machines. Two configs that differ in any field, including `name`, differ in hash.
- **`GENERATOR_VERSION` is bumped** whenever `make_tape` changes what it produces for a config it already accepted. Adding a field with a default that reproduces the old tapes does not bump it, as the hash changes anyway.
- **The hash does not cover numpy.** numpy does not promise that `Generator` streams or `exp` are bit-stable across versions and CPU paths. So `pyproject.toml` pins numpy to one minor version, the harness logs the numpy version beside the hash, and bit equality is promised within one environment only, see [tape invariants](tape.md#invariants).
- **The hash is on every tape and in every log**, see [tape](tape.md) and [running](../../harness/running.md#commands).

## Defaults

Proposed starting values. Every one is **pilot to confirm**. The check column says which run settles it, and the decision lands in [decisions](../../pilot/decisions.md).

| Field | Default | Why this number | Check |
|---|---|---|---|
| `channels`, `budget` | 10, 100 | [interface](../../design/interface.md#how-the-agent-plays) | Fixed by design |
| `rounds` | 40 | [defaults](../../design/mechanics.md#defaults) | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `leader_base` | 60 to 70 | Mid-range, so a deep shock stays above 0 | [Tape sanity](../../pilot/engine-checks.md#tape-sanity) |
| `runner_up_gap_sigmas` | 2 to 4 | "A few sigmas below", see [the ladder](../../design/mechanics.md#the-ladder) | [Streaks](../../pilot/engine-checks.md#streaks) |
| `field_base`, `field_headroom` | 30 to 55, 4 | Below the runner-up, with room so no field channel is a near twin of it | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `hedge_base` | 20 to 28 | Lowest, and low enough that the shock cap rarely bites | [The tell](../../pilot/engine-checks.md#the-tell) |
| `own_scale` | 4 | A switch lands 4 to 12 points below the runner-up, so one reading rarely settles it | [Noise grid](../../pilot/engine-checks.md#noise-grid) |
| `persistence` | 0.8 | A bad stretch half gone after three rounds, see [each round](../../design/mechanics.md#each-round) | [Streaks](../../pilot/engine-checks.md#streaks) |
| `factor_scale` | 3 | Shared weeks visible but smaller than own weather | [The tell](../../pilot/engine-checks.md#the-tell) |
| `loading`, `hedge_loading` | 0.3 to 1, −0.6 to −0.3 | "About 0.3 to 1", one negative, see [each round](../../design/mechanics.md#each-round) | [The tell](../../pilot/engine-checks.md#the-tell) |
| `read_noise_k` | 8 | A 1 point look has SD 8, a 16 point look SD 2, the full budget SD 0.8 | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `onset` | 12 to 20 | Enough calm to set a habit, enough left to pull clear | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `hedge_margin_points` | 4 | One sigma at the default `own_scale`, in points so it survives pinning | [The tell](../../pilot/engine-checks.md#the-tell) |
| `ShockSpec.depth_sigmas` | 4 to 8 | Through a loading of 0.65 the leader dips 2.6 to 5.2 sigmas. The cap cuts the deepest draws on seeds with a high hedge and strong loadings, so the final depth is in `Event.numbers` | [The tell](../../pilot/engine-checks.md#the-tell) |
| `ShockSpec.half_life` | 2 to 4 | The shock is mostly gone in about ten rounds | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `SwitchSpec.size_sigmas` | 1 to 3 | The leader ends clearly below the runner-up on every seed. With the gap it moves 12 to 28 points | Switch size row in [decisions](../../pilot/decisions.md#engine-checks) |
| `SwitchSpec.rise_sigmas` | 1 to 3 | A sleeper clearly best once risen, but not a giveaway | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.riser_share` | 0.5 | Half the Down switch tapes draw a sleeper | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.ramp` | 1 to 5 | [events](../../design/mechanics.md#events) | Fixed by design |
| `DriftSpec.size_sigmas`, `length` | 1 to 3, 15 to 25 | The Down switch stretched: with the gap, about 0.5 to 1.9 points a round | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `gap` | 8 to 12 | Room for a habit to re-form after a shock | Events per run row in [decisions](../../pilot/decisions.md#engine-checks) |
| `*_points` pairs | sigmas × 4 | Agree with the sigmas pair at `own_scale` 4 | [Noise grid](../../pilot/engine-checks.md#noise-grid) |

## Open

- The [noise grid](../../pilot/engine-checks.md#noise-grid) is a list of `own_scale` values with `pin_in_level_points` on. Where that list lives, `configs/` or a constant in the harness, is a harness spec question.
- Whether `inertia_cap` belongs here or on the harness task. It is here because it changes what a valid bet is, which is an engine rule.
- `hedge_may_overtake` needs a config whose ladder and loadings let the hedge pass the leader within `depth_points`. At the defaults most seeds cannot, so the knob's config is for the pilot, see [shock](tape.md#shock).
