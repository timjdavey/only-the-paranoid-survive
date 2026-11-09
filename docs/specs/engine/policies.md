# Policies

## Purpose

The six fixed baselines in [baselines](../../design/baselines.md), each a pure function from what it may see to a split. The harness wraps each in a provider so `--model baseline/complacent` plays like a model, see [inspect](../../harness/inspect.md#providers). The engine checks run them on thousands of tapes with no model, see [engine checks](../../pilot/engine-checks.md).

## Interface

```python
@dataclass(frozen=True)
class Start:                                # the climate on round 1, as the harness tells the agent nothing
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

uniform: Policy        # peeks = False
discerning: Policy     # peeks = True
complacent: Policy     # peeks = False
perfect: Policy        # peeks = True
def hedge_rule(look: int = 2, window: int = 3, fall_points: float = 8.0,
               tell_points: float = 4.0, scout_rounds: int = 2) -> Policy    # peeks = False
def scout_rule(s: int = 1, n: int = 3, tell_points: float = 4.0) -> Policy  # peeks = False
```

## Behaviour

### View

- **`start` is the ladder at round 1**: `tape.leader`, `tape.runner_up`, `tape.hedge`, `tape.field`. Every policy gets it, as the Complacent baseline is defined by the round 1 split and the hedge rule and Scout rule are reference players that read the tell, not learners. Handing them round 1 is the same gift the Complacent baseline gets, see [fixed baselines](../../design/baselines.md#fixed-baselines).
- **`record`** is the agent's own play, so a policy that reads only the record sees only what it bet on, at the roughness its bets bought.
- **`tape`** is set only when `peeks` is true. A policy with `peeks` false must work with `tape = None` and must never read it. Players may read their own record, only the yardstick reads the tape, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).
- **A policy is pure.** Same view, same split. No state between calls. A rule with state recomputes it from the record each round, or caches by record length and gets the same answer.

### `split_budget`

Turns weights into a valid split by largest remainder. Shares are `weight / sum × budget`. Each channel gets the floor of its share, then the leftover points go one each to the channels with the largest fractional parts, lowest index first on a tie. All weights zero or any weight negative raises `ValueError`. The result sums to `budget` and has one entry per weight. The Jev provider reuses it, see [providers](../../harness/providers.md#jev).

### The six baselines

Bets are written as `budget` on a channel, meaning every point on it and 0 elsewhere.

| Policy | Peeks | Split each round |
|---|---|---|
| `uniform` | No | `split_budget([1] × channels, budget)`. 10 each at the defaults |
| `discerning` | Yes | `budget` on `tape.climate_leader(round)`, the highest base level this round. Ties go to the lowest index |
| `complacent` | No | `budget` on `start.leader`, every round. Equals the Discerning baseline's round 1 split |
| `perfect` | Yes | `budget` on the channel with the highest `tape.levels[round−1]`. Ties go to the lowest index |
| `hedge_rule(...)` | No | `look` on the hedge, the rest on its pick. Below |
| `scout_rule(...)` | No | `s` on every channel but its pick, the rest on the pick. Below |

### Hedge rule

The simplest player that reads the tell. State: a `pick`, a `phase` of hold or scout, the round the pick was last set `moved_at`, and the round scouting began `scout_start`. All derived from the record by replaying the rounds below from round 1.

- **Round 1.** `pick = start.leader`, phase hold, `moved_at = 1`. Split: `look` on the hedge, `budget − look` on the pick.
- **Hold.** Each round, run the fall test on the pick's readings since `moved_at`. The recent readings are the last `window` of them. The earlier readings are all the ones before those, and there must be at least `window` of them or the test does not run.
  - **Fall** when `mean(recent) < mean(earlier) − fall_points`.
  - **Tell** when the hedge's mean over the same recent rounds is above its mean over the same earlier rounds by more than `tell_points`. The hedge rose while the pick fell, so it is a shock. Hold.
  - **Fall and no tell**: phase scout, `scout_start = round`.
- **Scout.** For `scout_rounds` rounds: `look` on the hedge and `budget − look` split by `split_budget` evenly over every other channel, the pick included.
- **Move.** On the round after the last scout round: `pick` becomes the channel, hedge excluded, with the highest mean reading over the scout rounds. Phase hold, `moved_at = round`. Bet the hold split with the new pick. The fall test then starts over on the new pick's readings.
- It never moves in the Up switch scenario, as the leader never falls, see [baseline order](../../pilot/engine-checks.md#baseline-order).

### Scout rule

The hedge rule that looks everywhere, all the time. State: `pick` and `moved_at`, derived as above.

- **Round 1.** `pick = start.leader`, `moved_at = 1`.
- **Every round.** `s` on each of the other `channels − 1` channels and `budget − s × (channels − 1)` on the pick. `s × (channels − 1)` must be below `budget`, else `ValueError` on construction.
- **Move test**, run before splitting once `round − moved_at ≥ n`:
  - **Candidates** are the channels, pick and hedge excluded, whose reading beat the pick's reading in each of the last `n` rounds.
  - **Tell** when the hedge's mean over the last `n` rounds is above its mean over every earlier round since `moved_at` by more than `tell_points`. With no earlier round there is no tell.
  - **Candidates and no tell**: `pick` becomes the candidate with the highest mean reading over the last `n` rounds, `moved_at = round`, and this round's split uses the new pick.
- It keeps scouting after a move, so it can move again.
- In noisy worlds it whipsaws. That is the point of it as a curve, see [fixed baselines](../../design/baselines.md#fixed-baselines).

### Parked

Named in [not yet](../../design/baselines.md#not-yet) and [Timestral](../../design/baselines.md#timestral). None are in this spec. Each will be a `Policy` here when it comes, with its own section.

| Policy | Waits for |
|---|---|
| Timestral policies, quantiles in and bets out | The Timestral provider in the harness spec, see [providers](../../harness/providers.md#timestral) |
| Bayesian | Timestral having run |
| CUSUM | The hedge rule having run |
| Barbell | [Up and down](../../pilot/engine-checks.md#up-and-down) |

## Invariants

- Every policy returns a valid split for its view: `channels` ints, none negative, summing to `budget`.
- A policy with `peeks` false returns the same split whether `view.tape` is the tape or `None`.
- `complacent` on round 1 equals `discerning` on round 1, on every tape.
- `discerning` and `complacent` are equal on every round of a No change tape.
- `uniform` ignores the view entirely.

## Tests

See [tests](tests.md#policies).

## Open

- `look`, `window`, `fall_points`, `tell_points` and `scout_rounds` for the hedge rule, from [the tell](../../pilot/engine-checks.md#the-tell) and [reading roughness](../../pilot/engine-checks.md#reading-roughness).
- `s` and `n` for the Scout rule, from [Streaks](../../pilot/engine-checks.md#streaks) and [Up and down](../../pilot/engine-checks.md#up-and-down).
- The thresholds are in level points so they survive [pinning](tape.md#pinning). Whether they should scale with read noise instead is for the pilot.
