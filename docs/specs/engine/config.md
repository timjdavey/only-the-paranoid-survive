# Config

## Purpose

`ScenarioConfig` holds every number the engine uses, so a scenario is data and the engine is built from [mechanics](../../design/mechanics.md) alone. The eight scenarios are eight configs. A hash of the config goes into every timeline and every log.

## Interface

```python
Range = tuple[float, float]      # inclusive low, inclusive high, drawn uniform per seed
IntRange = tuple[int, int]       # inclusive low, inclusive high, drawn uniform per seed

@dataclass(frozen=True)
class ShockSpec:
    gap: IntRange = (8, 12)                 # rounds after the previous event's onset. Drawn and ignored for the first event
    depth_sigmas: Range = (4.0, 8.0)        # impulse into the shared factor, in sigmas. Capped per seed, see timeline
    depth_points: Range = (16.0, 32.0)      # the same, in level points, used when pinned
    half_life: IntRange = (2, 4)            # rounds for the impulse to halve
    profile: Literal["sharp", "slide", "draw"] = "draw"
    # shape knobs, all off by default, see timeline.md#storm
    recovery: Range = (1.0, 1.0)            # each channel's multiplier on the rebound's half-life
    leader_last_share: float = 0.0          # chance the leader gets the slowest multiplier
    pop_share: float = 0.0                  # chance a field channel pops to the margin under the leader at the trough
    leader_stays_ahead: bool = False        # before weather, the leader stays the margin above every channel in a storm
    leader_loading: Range | None = None     # the loading the leader meets a storm with. None is its own

@dataclass(frozen=True)
class SwitchSpec:
    gap: IntRange = (8, 12)
    kind: Literal["fall", "fall_and_rise", "rise", "undo", "draw"] = "draw"
    riser_share: float = 0.5                # chance "draw" gives fall_and_rise rather than fall
    size_sigmas: Range = (1.0, 3.0)         # how far below the runner-up's base the leader's base ends
    size_points: Range = (4.0, 12.0)
    rise_sigmas: Range = (3.0, 6.0)         # how far above every other channel's base the sleeper's base ends
    rise_points: Range = (12.0, 24.0)
    ramp: IntRange = (1, 5)                 # rounds the move is spread over, linear
    short_share: float = 0.0                # chance a "rise" stops short of the leader
    short_level: Range = (0.25, 0.75)       # where a short rise ends, as a share of the gap from runner-up to leader
    storm: ShockSpec | None = None          # a shape knob: the fall arrives in this storm, see timeline.md#storm

@dataclass(frozen=True)
class DriftSpec:
    gap: IntRange = (8, 12)
    size_sigmas: Range = (2.0, 4.0)         # how far below the runner-up's base the leader's base ends
    size_points: Range = (8.0, 16.0)
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
    leader_base: Range = (90.0, 100.0)
    runner_up_gap_sigmas: Range = (2.0, 4.0)
    runner_up_gap_points: Range = (8.0, 16.0)
    field_base: Range = (60.0, 85.0)
    field_headroom: float = 4.0             # a field channel lands at least this far below the runner-up
    hedge_base: Range = (50.0, 58.0)
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
    onset: IntRange = (8, 12)               # the first event's onset round
    pin_in_level_points: bool = False
    hedge_margin_points: float = 4.0        # at a shock's trough the hedge sits at least this far from the leader, see timeline
    # hard-variant knobs
    hedge_may_overtake: bool = False
    one_channel_shock: bool = False
    inertia_cap: int | None = None

SCENARIOS: Mapping[str, ScenarioConfig]     # read only, in the scenario table's order
GENERATOR_VERSION: int                      # 1. Bumped when make_timeline changes for the same config
def engine_hash(config: ScenarioConfig) -> str
```

## Behaviour

### Fields

- **Every number in [mechanics](../../design/mechanics.md) is a field.** Nothing is hard coded in `timeline.py` or `game.py`. If a rule needs a number, it gets a field here first.
- **A `Range` is drawn uniform per seed**, low and high inclusive. An `IntRange` is drawn uniform over the whole numbers from low to high inclusive. A range with low equal to high is a fixed value.
- **Every field is stored as its declared type.** `__post_init__`, on the config and on each event spec, casts each `Range` entry and `float` field to `float`, each `IntRange` entry and `int` field to `int`, and `events` to a tuple. So `leader_base=(90, 100)` and `(90.0, 100.0)` are one config with one hash, as are `own_scale=4` and `4.0`.
- **A value of the wrong type raises `TypeError`.** A whole number is a `numbers.Integral` that is not a `bool`, as for [bets](game.md#bets), so `channels=10.0` and `gap=(8.5, 12)` raise. A real number is a `numbers.Real` that is not a `bool`. A `bool` field takes a `bool` only, `name` a `str` only, and `events` holds event specs only. A range is a pair.
- **A `float` field or `Range` entry that is not finite raises `ValueError`**, as JSON cannot hash it.
- **Sizes come in pairs**, one in sigmas and one in level points. The engine reads the sigmas pair unless `pin_in_level_points` is true, then it reads the points pair and ignores the sigmas pair. See [difficulty](../../design/mechanics.md#difficulty) for why. The pairs are set so that at the default `own_scale` they agree.
- **A switch or drift `size` is measured from the runner-up**, not from where the leader was. The leader's base ends `size` below the runner-up's base, so a fall changes who pays best on every seed. The points the leader actually moves are the gap to the runner-up plus `size`, see [switch](timeline.md#switch).
- **`own_scale` is the weather's SD per round**, not the SD of the innovation. [timeline](timeline.md) says how the AR(1) is scaled to make that so. It is the axis of the [noise grid](../../pilot/engine-checks.md#noise-grid).
- **`persistence` never moves within a release**, see [difficulty](../../design/mechanics.md#difficulty). The engine does not enforce this, the release process does.
- **A short rise and an undo** are the two switch moves the [Up switch](../../design/scenarios.md#scenarios-we-test) scenarios need, see [switch](timeline.md#switch). `short_level` is a share, not a size, so it has no sigmas or points pair and [pinning](timeline.md#pinning) leaves it alone.
- **`hedge_margin_points`** is in level points, so it survives [pinning](timeline.md#pinning). It bounds the shock depth, see [shock](timeline.md#shock).
- **The shape knobs** are the five storm fields on `ShockSpec` and `storm` on `SwitchSpec`. They are off by default, and off draws the timelines from before they existed, see [storm](timeline.md#storm). `recovery` is a multiplier and `leader_loading` a loading, not sizes, so neither has a sigmas or points pair. `leader_loading` is a `Range` or `None` and `storm` is a `ShockSpec` or `None`, and anything else raises `TypeError`. The values tried with them on live in `shapes/src/worlds.py` until a pilot moves them into the scenarios.
- **`inertia_cap`** is off by default. When set, no bet may move more than this many points from the round before, see [game](game.md#bets) and [inertia](../../design/scoring.md#extension-inertia). `make_timeline` never reads it, so a config with the cap cleared draws the same arrays, which the [scorer](../harness/scorer.md) relies on. It lives on the config and not on the harness task, as it changes what a valid bet is, which is an engine rule. The task's `inertia` arg sets it, see the [task spec](../harness/task.md#scenarios-and-config).
- **Validation on construction.** `__post_init__` raises `ValueError` if any of these hold:
  - `channels < 4`, `rounds < 1`, `budget < channels`.
  - Any range has low above high.
  - `persistence` is outside `[0, 1)`. `own_scale`, `factor_scale`, `read_noise_k`, `field_headroom` or `hedge_margin_points` is not positive.
  - `loading` has a low at or below 0. `hedge_loading` has a high at or above 0.
  - `runner_up_gap_sigmas` or `runner_up_gap_points` has a low at or below 0, so the runner-up is always strictly below the leader.
  - `onset` low is below 2 or `onset` high is above `rounds`. Round 1 is never edited, so the ladder holds on round 1 and an [undo](timeline.md#switch) can read row 0 as the base from before the rise.
  - `inertia_cap` is set and below 0.
  - `hedge_base` high is not below `field_base` low.
  - `field_base` low is above `leader_base` low minus the widest runner-up gap the config can draw, minus `field_headroom`. The widest gap is `runner_up_gap_points` high when `pin_in_level_points` is true, and `runner_up_gap_sigmas` high × `own_scale` when it is not, as only the pair the engine reads can break the ladder, see [pinning](timeline.md#pinning). So the noise grid's settings all build: pinned at `own_scale` 8 the check is 90 − 16 − 4 = 70, above the field's low of 60. Unpinned at 8 it is 90 − 32 − 4 = 54 and raises, which is right, as that ladder could put a field channel above the runner-up.
  - In any event spec: `riser_share` or `short_share` is outside `[0, 1]`, `gap`, `ramp`, `half_life` or `length` has a low below 1, any `*_sigmas` or `*_points` range has a low at or below 0, or `kind` or `profile` is not one of its words.
  - A `SwitchSpec` has `short_share` above 0 and a `kind` other than `"rise"`, or a `short_level` low at or below 0 or high at or above 1.
  - A `SwitchSpec` with `kind="undo"` is the first event, or the most recent `SwitchSpec` before it does not have `kind` `"rise"` or `"fall_and_rise"`.
  - A `ShockSpec` has a `recovery` or `leader_loading` low at or below 0, or `leader_last_share` or `pop_share` outside `[0, 1]`.
  - A `SwitchSpec` has a `storm` and a `kind` of `"rise"` or `"undo"`. A storm comes with a fall.
  - Any shape knob is on, a storm included, with `one_channel_shock` or `hedge_may_overtake` on. Their rules for the impulse and the cap do not combine.

### Scenarios

`SCENARIOS` maps each code name from the [glossary](../../glossary.md#how-the-world-changes) to a config. Each is the defaults above plus its events. It is a `types.MappingProxyType`, so a caller cannot replace a scenario under a name that is already in a log. Its keys are in the order of the table below, which the harness and analysis use as `SCENARIOS` order.

| Code name | `events` | Note |
|---|---|---|
| `no_change` | `()` | The control |
| `one_shock` | `(ShockSpec(),)` | |
| `down_switch` | `(SwitchSpec(kind="draw"),)` | Per seed, fall or fall and rise, see [events](../../design/mechanics.md#events) |
| `up_switch` | `(SwitchSpec(kind="rise", short_share=0.25),)` | The leader holds. On a quarter of seeds the sleeper stops short |
| `shock_then_switch` | `(ShockSpec(), SwitchSpec(kind="draw"))` | The switch is a down switch, `gap` rounds after the shock's onset |
| `slow_drift` | `(DriftSpec(),)` | |
| `switch_then_shock` | `(SwitchSpec(kind="draw"), ShockSpec())` | The switch is drawn as in `down_switch`, and the shock lands `gap` rounds after it |
| `up_switch_then_down_switch` | `(SwitchSpec(kind="rise"), SwitchSpec(kind="undo"))` | The sleeper always rises past the leader, then the undo puts it back |

- **`name` equals the key.** `SCENARIOS["one_shock"].name == "one_shock"`.
- **The first event lands at `onset`**, which every scenario shares. So twin timelines share their onset round, see [timeline](timeline.md#twin-timelines). Later events land `gap` rounds after the previous event's onset.
- **A hard variant is a new config**, not a flag: more events in the tuple, a longer `length`, or a longer `ramp`. It gets its own key when it exists, see [scenarios](../../design/scenarios.md#scenarios-we-test).

### Engine hash

- **`engine_hash(config)`** is the first 12 hex characters of the SHA-256 of a canonical JSON string, encoded as UTF-8. The string is `dataclasses.asdict(config)` with two additions: each event dict gets a key `"shape"` with `"shock"`, `"switch"` or `"drift"`, and the top level gets `"generator_version": GENERATOR_VERSION`. The `shape` key is there so two spec types that ever share a field set cannot collide.
- **The recipe is `json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)`.** `allow_nan` changes no string, as validation has already refused a value that is not finite. Floats come out as `repr`, tuples as lists and `None` as `null`. [EC7](tests.md#config) rebuilds the string from this line.
- **`GENERATOR_VERSION` starts at 1.**
- **Same config, same hash**, across Python versions and machines. Two configs that differ in any field, including `name`, differ in hash.
- **`GENERATOR_VERSION` is bumped** whenever `make_timeline` changes what it produces for a config it already accepted. Adding a field with a default that reproduces the old timelines does not bump it, as the hash changes anyway.
- **The hash does not cover numpy.** numpy does not promise that `Generator` streams or `exp` are bit-stable across versions and CPU paths. So `pyproject.toml` pins numpy to one minor version, the harness logs the numpy version beside the hash, and bit equality is promised within one environment only, see [timeline invariants](timeline.md#invariants).
- **The hash is on every timeline and in every log**, see [timeline](timeline.md) and [running](../../harness/running.md#commands).

## Defaults

Proposed starting values. Every one is **pilot to confirm**. The check column says which run settles it, and the decision lands in [decisions](../../pilot/decisions.md).

| Field | Default | Why this number | Check |
|---|---|---|---|
| `channels`, `budget` | 10, 100 | 100 so a bet is a percentage, ten so the Uniform baseline is 10 on every channel, see [interface](../../design/interface.md#how-the-agent-plays) | Fixed by design |
| `rounds` | 40 | [defaults](../../design/mechanics.md#defaults) | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `leader_base` | 90 to 100 | High enough that no reading realistically falls below 0, see [each round](../../design/mechanics.md#each-round) | [Timeline sanity](../../pilot/engine-checks.md#timeline-sanity) |
| `runner_up_gap_sigmas` | 2 to 4 | "A few sigmas below", see [the ladder](../../design/mechanics.md#the-ladder) | [Streaks](../../pilot/engine-checks.md#streaks) |
| `field_base`, `field_headroom` | 60 to 85, 4 | Below the runner-up, with room so no field channel is a near twin of it | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `hedge_base` | 50 to 58 | Lowest, and low enough that the shock cap rarely bites | [The tell](../../pilot/engine-checks.md#the-tell) |
| `own_scale` | 4 | A switch lands 4 to 12 points below the runner-up, so one reading rarely settles it | [Noise grid](../../pilot/engine-checks.md#noise-grid) |
| `persistence` | 0.8 | A bad stretch half gone after three rounds, see [each round](../../design/mechanics.md#each-round) | [Streaks](../../pilot/engine-checks.md#streaks) |
| `factor_scale` | 3 | Shared weeks visible but smaller than own weather | [The tell](../../pilot/engine-checks.md#the-tell) |
| `loading`, `hedge_loading` | 0.3 to 1, −0.6 to −0.3 | "About 0.3 to 1", one negative, see [each round](../../design/mechanics.md#each-round) | [The tell](../../pilot/engine-checks.md#the-tell) |
| `read_noise_k` | 8 | A 1 point explore bet has SD 8, a 16 point explore bet SD 2, the full budget SD 0.8 | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `onset` | 8 to 12 | Seven calm rounds at least to set a habit, and enough left to pull clear | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `hedge_margin_points` | 4 | One sigma at the default `own_scale`, in points so it survives pinning | [The tell](../../pilot/engine-checks.md#the-tell) |
| `ShockSpec.depth_sigmas` | 4 to 8 | Through a loading of 0.65 the leader dips 2.6 to 5.2 sigmas. The cap cuts the deepest draws on seeds with a high hedge and strong loadings, so the final depth is in `Event.numbers` | [The tell](../../pilot/engine-checks.md#the-tell) |
| `ShockSpec.half_life` | 2 to 4 | The shock is mostly gone in about ten rounds | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `SwitchSpec.size_sigmas` | 1 to 3 | The leader ends clearly below the runner-up on every seed. With the gap it moves 12 to 28 points | [Noise grid](../../pilot/engine-checks.md#noise-grid) |
| `SwitchSpec.rise_sigmas` | 3 to 6 | The smallest rise the pilot swept that lifts the Up switch scenario over the [reachable gain](../../pilot/engine-checks.md#reachable-gain) floor | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.riser_share` | 0.5 | Half the Down switch timelines draw a sleeper | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.short_share` | 0 on the spec, 0.25 in `up_switch` | "On most seeds the sleeper rises past the leader, on some it stops short", see [scenarios](../../design/scenarios.md#scenarios-we-test) | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.short_level` | 0.25 to 0.75 | Clear of the runner-up, so an explore bet sees a real move, and clear of the leader, so the Scout rule does not move on a near tie | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `SwitchSpec.ramp` | 1 to 5 | [events](../../design/mechanics.md#events) | Fixed by design |
| `DriftSpec.size_sigmas`, `length` | 2 to 4, 15 to 25 | The Down switch stretched and a sigma deeper, so the slow fall is worth leaving: with the gap, about 0.6 to 2.1 points a round | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `gap` | 8 to 12 | Room for a habit to re-form after a shock | [Game length](../../pilot/engine-checks.md#game-length-and-switch-round) |
| `ShockSpec.recovery` | 1 to 1, off | Off until a pilot runs it. `shapes/` tries 0.5 to 1.5 | The next pilot |
| `ShockSpec.leader_last_share` | 0, off | Off until a pilot runs it. `shapes/` tries 0.5 | The next pilot |
| `ShockSpec.pop_share` | 0, off | Off until a pilot runs it. `shapes/` tries 0.5 | The next pilot |
| `ShockSpec.leader_stays_ahead` | false, off | Off until a pilot runs it. `shapes/` tries it on | The next pilot |
| `ShockSpec.leader_loading` | `None`, off | Off until a pilot runs it. `shapes/` tries 0.8 to 1.2, so the leader falls about as far as the storm is deep | The next pilot |
| `SwitchSpec.storm` | `None`, off | Off until a pilot runs it. `shapes/` puts the scenario's shock on every fall | The next pilot |
| `*_points` pairs | sigmas × 4 | Agree with the sigmas pair at `own_scale` 4 | [Noise grid](../../pilot/engine-checks.md#noise-grid) |

## Pilot decides

- Every default above. The [noise grid](../../pilot/engine-checks.md#noise-grid) is a list of `own_scale` values with `pin_in_level_points` on. It lives in `configs/grid.toml`, and the harness applies one setting per eval, see the [task spec](../harness/task.md#scenarios-and-config).
- **Every default that sets how much moving earns** must also clear the [reachable gain](../../pilot/engine-checks.md#reachable-gain) check: `rounds`, `onset`, `gap`, the event sizes, the drift's `length` and `field_base`.

## Not decided

- `hedge_may_overtake` needs a config whose ladder and loadings let the hedge pass the leader within `depth_points`. At the defaults most seeds cannot, so the knob's config is for the pilot, see [shock](timeline.md#shock). Build it when [the tell](../../pilot/engine-checks.md#the-tell) runs.
