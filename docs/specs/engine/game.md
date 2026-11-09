# Game

## Purpose

`Game` plays one run against a tape: it takes a split each round, checks it, returns the readings and output, and appends a row to the record. `Record` is the agent's own play so far, the thing the harness renders into the prompt. `play` runs a policy to the end with no model in the loop. The design is in [interface](../../design/interface.md) and [what the agent sees](../../design/mechanics.md#what-the-agent-sees).

## Interface

```python
Bets = tuple[int, ...]                      # one whole number per channel, summing to the budget

class BetError(ValueError):
    check: str                              # the check that failed: shape, sign, sum or inertia

@dataclass(frozen=True)
class Reading:
    round: int
    readings: tuple[float | None, ...]      # one per channel, None where the bet was 0, one decimal
    output: float                           # one decimal

@dataclass(frozen=True)
class Row:
    round: int
    bets: Bets
    readings: tuple[float | None, ...]      # what the agent saw, as in Reading.readings
    output: float

class Record:
    rows: Sequence[Row]                     # read only view. append is the one writer
    def __len__(self) -> int
    def append(self, row: Row) -> None
    def copy(self) -> Record
    def last_bets(self) -> Bets | None
    def readings_of(self, channel: int) -> list[tuple[int, float]]   # (round, reading) for rounds with a bet
    def unchanged_rounds(self) -> list[int]                           # rounds whose bets equal the round before
    def to_csv(self, names: Sequence[str] | None = None) -> str

class Game:
    tape: Tape
    record: Record                          # the game's own copy
    round: int                              # the round about to be played, from 1
    done: bool                              # round > tape.config.rounds
    def __init__(self, tape: Tape, record: Record | None = None)
    def view(self, peeks: bool) -> View     # what a policy may see this round, see policies.md
    def play(self, bets: Sequence[int]) -> Reading

def play(policy: Policy, tape: Tape, *, max_rounds: int | None = None, record: Record | None = None) -> Record
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

- **The message is generic.** `str(error)` is `Bad tool call: {check}.`, for logs and tests. The engine writes no text for the agent. The harness answers every `BetError` with the skin's `bad_call`, see [tool text](../../harness/prompts.md#tool-text).
- **A whole number** is any `numbers.Integral` that is not a `bool`. So `np.int64` passes, as the Jev and Timestral providers produce it, and `True`, `10.0` and `"10"` fail. A negative int passes `shape` and fails `sign`.
- **A round advances only on a valid split.** A `BetError` leaves `round`, `record` and the tape untouched, so the same round can be tried again. The engine never counts retries, the harness does, see [retry rule](../../harness/prompts.md#retry-rule).
- **Playing a finished game** raises `RuntimeError`.
- **Bets are stored as a tuple of `int`**, whatever sequence was passed in.

### Readings

For round `r` (row `r − 1`) and channel `c` with bet `b`:

- **A funded channel reads** `levels[r−1, c] + read_noise_k / sqrt(b) × read_noise_z[r−1, c]`, rounded to one decimal place with Python's `round`. So a bet of 4 is twice as rough as a bet of 16, and a bet of 100 reads with SD `k / 10`.
- **An unfunded channel reads `None`.** Never 0, never blank-as-zero.
- **Readings are not clipped.** A rough reading of a low channel can be negative.
- **Output** is `sum(b_c / budget × levels[r−1, c])` over every channel, from the true levels with no read noise, rounded to one decimal place. See [why output is exact](../../design/mechanics.md#what-the-agent-sees).
- **The row the record keeps holds the rounded values**, the ones the agent saw. The tape keeps the truth.
- **The score sums the rounded outputs in the record.** The rounding error is at most `0.05 × rounds` points a run, 2 points at the defaults against a gap of hundreds, and the agent and the scorer then agree on every number. The scorer never recomputes from the tape.

### Record

- **A record is the rows in round order**, 1 to `len(record)`, with no gaps. `Game(tape, record)` raises `ValueError` if the rows are not 1, 2, 3… in order, if there are more rows than `tape.config.rounds`, or if a row's bets or readings do not fit the tape's `channels` and `budget`.
- **`rows` is a read only view.** `append` is the only way to add a row and nothing removes or edits one. `copy()` returns a new record with the same rows.
- **`to_csv`** renders the shape in [user message](../../harness/prompts.md#user-message):

      round,<name>_bet × channels,<name>_level × channels,output

  - Names default to `c0`, `c1`, … `c{channels−1}`. The skins layer passes the skin's channel names in channel index order.
  - A name that contains `,`, `"`, `\n` or `\r`, or the wrong number of names, raises `ValueError`. The CSV is the agent's prompt, so no name may add a column or a row to it.
  - Bets are written as ints, readings and output with exactly one decimal, a `None` reading as an empty field. A value that rounds to zero from below is written `0.0`, never `-0.0`.
  - Rows end with `\n`, including the last. An empty record renders the header line only.
  - Example, two channels for brevity: `round,c0_bet,c1_bet,c0_level,c1_level,output\n1,100,0,61.2,,61.2\n`.
- **`unchanged_rounds`** returns every round from 2 on whose bets equal the previous round's. The harness reports them as rounds the agent left the plan alone, see [interface](../../design/interface.md#how-the-agent-plays).
- **`readings_of(c)`** returns `(round, reading)` pairs for the rounds where `c` had a bet, in round order. Policies read the record through it.
- **A record carries no tape and no truth.** Nothing on it lets a reader recover a level it did not bet on. It is the one engine object the harness may render or log.

### Starting part way

- **`Game(tape, record)`** copies the record and starts at round `len(record) + 1`. The caller's record is never changed, so one warm-up record can seed many games. This is how the warm-up cell starts with a record a baseline played, see [TODO](../../../TODO.md#pilot).
- **`Game(tape)`** also checks that every array on the tape has the shape `tape.config` says, and raises `ValueError` if not, so a hand-built tape fails at once and not mid-game.
- **The record's bets need not come from this tape.** The engine does not check that the readings match the tape. The harness is responsible for pairing a warm-up record with its tape.

### `view`

- **`game.view(peeks)`** builds the `View` for the round about to be played: `round`, `channels`, `budget`, `start` from the tape's ladder, the game's record, and `tape` when `peeks` is true, else `None`. See [policies](policies.md#view).
- The baseline provider in the harness plays a policy round by round through the solver, so it calls `view` and `play` itself. `play` below is the same loop with no solver.

### `play`

- **`play(policy, tape)`** builds `Game(tape, record)`, then until the game is done or `max_rounds` rounds have been played: calls `policy(game.view(policy.peeks))` and plays the bets. It returns the game's record.
- **`max_rounds`** caps how many rounds this call plays, counted from where the record left off. `None` plays to the end. So `play(complacent, tape, max_rounds=5)` is a five-round warm-up record.
- **A `BetError` from a policy propagates.** A baseline that bets badly is a bug, not an agent to retry.

## Invariants

- Same tape, same sequence of splits, same record, on every call within one environment.
- `len(game.record)` equals the number of valid splits played plus the rows it started with.
- Every row's readings are `None` exactly where its bets are 0.
- Every row's output equals the exact-level sum rounded to one decimal, never the sum of the readings.
- `record.to_csv().count("\n") == len(record) + 1`.
- A record passed to `Game` or `play` has the same rows afterwards.
- The engine never imports anything outside numpy and the standard library.

## Tests

See [tests](tests.md#game).

## Open

- `read_noise_k` is pilot to confirm, see [reading roughness](../../pilot/engine-checks.md#reading-roughness).
- Whether `inertia_cap` is ever switched on, see [inertia](../../pilot/provider-checks.md#inertia).
