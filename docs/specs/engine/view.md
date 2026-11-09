# View

## Purpose

The contract a policy is written to: `View`, what a policy may see this round, `Policy`, what a policy is, and `split_budget`, the one way weights become a valid split. The engine builds the view and plays whatever a policy returns. The strategies themselves live in the [baselines spec](../baselines/README.md), so a new baseline never touches the engine.

## Interface

```python
@dataclass(frozen=True)
class Start:                                # the ladder on round 1. Handed to the baselines, never to a model
    leader: int
    runner_up: int
    hedge: int
    field: tuple[int, ...]

@dataclass(frozen=True)
class View:
    round: int                              # the round about to be played, from 1
    channels: int
    budget: int
    start: Start
    record: Record                          # every round before this one
    tape: Tape | None                       # the tape for peeking policies, else None

class Policy(Protocol):
    peeks: bool                             # True if it may read the tape
    def __call__(self, view: View) -> Bets: ...

def split_budget(weights: Sequence[float], budget: int) -> Bets
```

- **`Policy` is a `Protocol`.** Anything with a `peeks` bool and a `__call__` from a view to bets satisfies it. The baselines layer makes each one a frozen dataclass instance, see [conventions](../baselines/README.md#conventions). A plain function with an attribute bolted on does not satisfy it for a type checker.
- **A `View` is built by `Game.view(peeks)`**, see [game](game.md#view). Nothing else builds one.
- **A `View` is never serialised**, for the same reason as a tape, see [tape](tape.md#interface).

## Behaviour

### View

- **`start` is the ladder at round 1**: `tape.leader`, `tape.runner_up`, `tape.hedge`, `tape.field`. Every policy gets it, as the Complacent baseline is defined by the round 1 split and the hedge rule and Scout rule are reference players that read the tell, not learners. Handing them round 1 is the same gift the Complacent baseline gets, see [fixed baselines](../../design/baselines.md#fixed-baselines).
- **No model gets `start`.** A model finds the leader in its first rounds and never learns which channel is the hedge. So the hedge rule and Scout rule curves are an upper bound on what a player that reads the tell could earn, and [baselines](../../design/baselines.md#fixed-baselines) says so.
- **`record`** is the agent's own play, so a policy that reads only the record sees only what it bet on, at the roughness its bets bought. Policies read it through `readings_of`, see [record](game.md#record).
- **`tape`** is set only when `peeks` is true. A policy with `peeks` false must work with `tape = None` and must never read it. Players may read their own record, only the yardstick reads the tape, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).

### `split_budget`

Turns weights into a valid split by largest remainder. Shares are `weight / sum × budget`. Each channel gets the floor of its share, then the leftover points go one each to the channels with the largest fractional parts, lowest index first on a tie. All weights zero or any weight negative raises `ValueError`. The result sums to `budget` and has one entry per weight. The baselines layer and the Jev provider both use it, see [names from the engine](../baselines/README.md#names-from-the-engine) and [Jev](../harness/providers.md#jev).

## Invariants

- `game.view(peeks).tape is game.tape` when `peeks` is true, else `None`.
- A view's `start` equals the tape's ladder on every round.
- The tape a view carries is read only. A policy that writes to it gets `ValueError`, see [tape](tape.md#interface).
- `split_budget` returns `len(weights)` non-negative ints summing to `budget`, for any weights with a positive sum.
