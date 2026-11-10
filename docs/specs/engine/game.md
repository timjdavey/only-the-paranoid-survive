# Game

## Purpose

`Game` plays one run against a timeline: it takes a split each round, checks it, appends a row of readings and output to the record, and returns that row. `Record` is the agent's own play so far, the thing the skins layer renders into the prompt, see [render](../skins/render.md#record). `play` runs a policy to the end with no model in the loop. The design is in [interface](../../design/interface.md) and [what the agent sees](../../design/mechanics.md#what-the-agent-sees).

## Interface

```python
Bets = tuple[int, ...]                      # one whole number per channel, summing to the budget

class BetError(ValueError):
    check: str                              # the check that failed: shape, sign, sum or inertia

@dataclass(frozen=True)
class Row:
    round: int
    bets: Bets
    readings: tuple[float | None, ...]      # one per channel, None where the bet was 0, one decimal
    output: float                           # one decimal

class Record:
    rows: Sequence[Row]                     # read only view. append is the one writer
    def __len__(self) -> int
    def append(self, row: Row) -> None
    def copy(self) -> Record
    def last_bets(self) -> Bets | None
    def readings_of(self, channel: int) -> list[tuple[int, float]]   # (round, reading) for rounds with a bet
    def unchanged_rounds(self) -> list[int]                           # rounds whose bets equal the round before

class Game:
    timeline: Timeline
    record: Record                          # the game's own copy
    round: int                              # the round about to be played, from 1
    done: bool                              # round > timeline.config.rounds
    def __init__(self, timeline: Timeline, record: Record | None = None)
    def view(self, peeks: bool) -> View     # what a policy may see this round, see view.md
    def play(self, bets: Sequence[int]) -> Row     # the row it appended

def play(policy: Policy, timeline: Timeline, *, max_rounds: int | None = None, record: Record | None = None) -> Record
```

## Behaviour

### Bets

`Game.play` checks the split in this order and raises `BetError` at the first failure, with `check` naming it.

| `check` | Fails when |
|---|---|
| `shape` | Not exactly `channels` values, or any value is not a whole number |
| `sign` | Any value is negative |
| `sum` | The values do not add up to `budget` |
| `inertia` | `inertia_cap` is set, the record is not empty, and some bet differs from the round before by more than the cap |

- **The message is generic.** `str(error)` is `Bad tool call: {check}.`, for logs and tests. The engine writes no text for the agent. The harness answers every `BetError` with the skin's `bad_call`, see [submit](../harness/solver.md#submit).
- **A whole number** is any `numbers.Integral` that is not a `bool`. So `np.int64` passes, as the Jev and Timestral providers produce it, and `True`, `10.0` and `"10"` fail. A negative int passes `shape` and fails `sign`.
- **A round advances only on a valid split.** A `BetError` leaves `round`, `record` and the timeline untouched, so the same round can be tried again. The engine never counts retries, the harness does, see [retry rule](../../harness/prompts.md#retry-rule).
- **Playing a finished game** raises `RuntimeError`.
- **Bets are stored as a tuple of `int`**, whatever sequence was passed in, and `play` returns the row it appended, so `game.play(bets) == game.record.rows[-1]`.

### Readings

For round `r` (row `r − 1`) and channel `c` with bet `b`:

- **A funded channel reads** `levels[r−1, c] + read_noise_k / sqrt(b) × read_noise_z[r−1, c]`, rounded to one decimal place with Python's `round`. So a bet of 4 is twice as rough as a bet of 16, and a bet of 100 reads with SD `k / 10`.
- **An unfunded channel reads `None`.** Never 0, never blank-as-zero.
- **Readings are not clipped.** A rough reading of a low channel can be negative.
- **Output** is `sum(b_c / budget × levels[r−1, c])` over every channel, from the ground truth with no read noise, rounded to one decimal place. See [why output is exact](../../design/mechanics.md#what-the-agent-sees).
- **The row the record keeps holds the rounded values**, the ones the agent saw. The timeline keeps the ground truth.
- **The score sums the rounded outputs in the record.** The rounding error is at most `0.05 × rounds` points a run, 2 points at the defaults against a gap of hundreds, and the agent and the scorer then agree on every number. The scorer never recomputes from the timeline.

### Record

- **A record is the rows in round order**, 1 to `len(record)`, with no gaps. `Game(timeline, record)` raises `ValueError` if the rows are not 1, 2, 3… in order, if there are more rows than `timeline.config.rounds`, or if a row's bets or readings do not fit the timeline's `channels` and `budget`.
- **`rows` is a read only view.** `append` is the only way to add a row and nothing removes or edits one. `copy()` returns a new record with the same rows.
- **A record renders nothing.** The skins layer turns it into the CSV the agent reads, column words and decimals included, see [render](../skins/render.md#record). So no engine word reaches a model.
- **`unchanged_rounds`** returns every round from 2 on whose bets equal the previous round's. The harness reports them as rounds the agent left the plan alone, see [interface](../../design/interface.md#how-the-agent-plays).
- **`readings_of(c)`** returns `(round, reading)` pairs for the rounds where `c` had a bet, in round order. Policies read the record through it.
- **A record carries no timeline and no ground truth.** Nothing on it lets a reader recover a level it did not bet on. It is the one engine object that leaves the engine, see [conventions](README.md#conventions).

### Starting part way

- **`Game(timeline, record)`** copies the record and starts at round `len(record) + 1`. The caller's record is never changed, so one warm-up record can seed many games. This is how the warm-up cell starts with a record a baseline played, see [TODO](../../../TODO.md#pilot).
- **`Game(timeline)`** also checks that every array on the timeline has the shape `timeline.config` says, and raises `ValueError` if not, so a hand-built timeline fails at once and not mid-game.
- **The record's bets need not come from this timeline.** The engine does not check that the readings match the timeline. The harness is responsible for pairing a warm-up record with its timeline.

### `view`

- **`game.view(peeks)`** builds the `View` for the round about to be played: `round`, `channels`, `budget`, `start` from the timeline's ladder, the game's record, and `timeline` when `peeks` is true, else `None`. See [view](view.md#view).
- The baseline provider in the harness plays a [baselines layer](../baselines/README.md) policy round by round through the solver, so it calls `view` and `play` itself, see [baseline](../harness/providers.md#baseline). `play` below is the same loop with no solver.

### `play`

- **`play(policy, timeline)`** builds `Game(timeline, record)`, then until the game is done or `max_rounds` rounds have been played: calls `policy(game.view(policy.peeks))` and plays the bets. It returns the game's record.
- **`max_rounds`** caps how many rounds this call plays, counted from where the record left off. `None` plays to the end. So `play(complacent, timeline, max_rounds=5)` is a five-round warm-up record.
- **A `BetError` from a policy propagates.** A baseline that bets badly is a bug, not an agent to retry, see [conventions](../baselines/README.md#conventions).

## Invariants

- Same timeline, same sequence of splits, same record, on every call within one environment.
- `len(game.record)` equals the number of valid splits played plus the rows it started with.
- Every row's readings are `None` exactly where its bets are 0.
- Every row's output equals the exact-level sum rounded to one decimal, never the sum of the readings.
- A record passed to `Game` or `play` has the same rows afterwards.
- The engine never imports anything outside numpy and the standard library.

## Pilot decides

- `read_noise_k` is pilot to confirm, see [reading roughness](../../pilot/engine-checks.md#reading-roughness).
- Whether `inertia_cap` is ever switched on, see [inertia](../../pilot/provider-checks.md#inertia).
