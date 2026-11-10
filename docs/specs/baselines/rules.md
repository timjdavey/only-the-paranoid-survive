# Rules

## Purpose

The two baselines with parameters: the hedge rule, the simplest player that reads the [tell](../../glossary.md#the-world), and the Scout rule, the hedge rule that explores everywhere all the time. Both read only their own record, so they are players with a mark on every bar, never the yardstick, see [fixed baselines](../../design/baselines.md#fixed-baselines). Their parameters are what the pilot sweeps, see [pilot decides](#pilot-decides).

## Interface

```python
@dataclass(frozen=True)
class HedgeRule:                            # peeks: ClassVar[bool] = False
    explore: int = 2
    window: int = 3
    fall_points: float = 8.0
    tell_points: float = 4.0
    scout_rounds: int = 2

@dataclass(frozen=True)
class ScoutRule:                            # peeks: ClassVar[bool] = False
    s: int = 1
    n: int = 3
    tell_points: float = 4.0

hedge_rule: Policy     # HedgeRule() at the defaults
scout_rule: Policy     # ScoutRule() at the defaults
```

- **Both are handed round 1** through `view.start`: they start on the leader and know which channel is the hedge, the same gift the Complacent baseline gets. No model gets either, so their curves are an upper bound on what a player that reads the tell could earn, see [view](../engine/view.md#view) and [the baselines are handed round 1](../../design/baselines.md#fixed-baselines).
- **State is derived, never kept.** Each call replays the rounds below from round 1 over the record, so the same view gives the same split, see [conventions](README.md#conventions).
- **The record may not be the rule's own.** The scorer plays every baseline from the agent's warm up record, which another baseline wrote, see [scoring one run](../harness/scorer.md#scoring-one-run). So the replay reads readings, never bets, and a round where a channel a test needs has no reading drops out of that test. The hedge rule's fall and tell tests count only the rounds since `moved_at` where both the pick and the hedge read. A Scout rule channel without a reading in one of the last `n` rounds is no candidate, and a missing hedge reading in those rounds means no move. Once the rule's own bets fund the channels, every round counts.

## Behaviour

### Hedge rule

`explore` on the hedge, the rest on its pick. State: a `pick`, a `phase` of hold or scout, the round the pick was last set `moved_at`, and the round scouting began `scout_start`.

- **Round 1.** `pick = start.leader`, phase hold, `moved_at = 1`. Split: `explore` on the hedge, `budget − explore` on the pick.
- **Hold.** Each round, run the fall test on the pick's readings since `moved_at`. The recent readings are the last `window` of them. The earlier readings are all the ones before those, and there must be at least `window` of them or the test does not run.
  - **Fall** when `mean(recent) < mean(earlier) − fall_points`.
  - **Tell** when the hedge's mean over the same recent rounds is above its mean over the same earlier rounds by more than `tell_points`. The hedge rose while the pick fell, so it is a shock. Hold.
  - **Fall and no tell**: phase scout, `scout_start = round`.
- **Scout.** For `scout_rounds` rounds: `explore` on the hedge and `budget − explore` split by `split_budget` evenly over every other channel, the pick included.
- **Move.** On the round after the last scout round: `pick` becomes the channel, hedge excluded, with the highest mean reading over the scout rounds, lowest index on a tie. The old pick can win, after a false alarm. Phase hold, `moved_at = round`. Bet the hold split with the new pick. The fall test then starts over on the new pick's readings.
- It has no reason to move in the Up switch or Up switch then down switch scenarios, as the leader never falls. Any scout there is a false alarm on weather, which costs it the scout rounds, so it sits at or a little below the Complacent baseline, see [baseline order](../../pilot/engine-checks.md#baseline-order).
- **Construction checks** `explore ≥ 1`, `window ≥ 1`, `scout_rounds ≥ 1`, and `fall_points` and `tell_points` finite and above 0, else `ValueError`. **The first view checks** `explore < budget` and `budget − explore ≥ channels − 1`, so every scouted channel gets a reading, else `ValueError`, as `budget` and `channels` are the view's.

### Scout rule

`s` on every channel but its pick, the rest on the pick. State: `pick` and `moved_at`, derived as above.

- **Round 1.** `pick = start.leader`, `moved_at = 1`.
- **Every round.** `s` on each of the other `channels − 1` channels and `budget − s × (channels − 1)` on the pick.
- **Construction checks** `s ≥ 1`, `n ≥ 1` and `tell_points` finite and above 0, else `ValueError`. **The first view checks** `s × (channels − 1) < budget`, else `ValueError`, as `channels` is not known on construction.
- **Move test**, run before splitting once `round − moved_at ≥ n`:
  - **Candidates** are the channels, pick and hedge excluded, whose reading beat the pick's reading in each of the last `n` rounds.
  - **Tell** when the hedge's mean over the last `n` rounds is above its mean over every earlier round since `moved_at` by more than `tell_points`. With no earlier round there is no tell.
  - **Candidates and no tell**: `pick` becomes the candidate with the highest mean reading over the last `n` rounds, lowest index on a tie, `moved_at = round`, and this round's split uses the new pick.
- It keeps scouting after a move, so it can move again. In the Up switch then down switch scenario that is how it goes back to the leader once the sleeper falls.
- In noisy worlds it whipsaws. That is the point of it as a curve, see [fixed baselines](../../design/baselines.md#fixed-baselines).

## Defaults

Every number is **pilot to confirm**.

| Parameter | Default | Why | Settled by |
|---|---|---|---|
| `explore` | 2 | Reads the hedge less roughly than one point, for 2 of the 100 points | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `window` | 3 | Three rounds is the streak that is ordinary by chance on No change, so the fall test needs a real drop | [Streaks](../../pilot/engine-checks.md#streaks) |
| `fall_points` | 8.0 | Two weather SDs at the default `own_scale` of 4, well inside a switch's size | [The tell](../../pilot/engine-checks.md#the-tell) |
| `tell_points` | 4.0 | One weather SD at the default `own_scale`. The hedge's rise in a shock is its loading times the depth, and should clear this | [The tell](../../pilot/engine-checks.md#the-tell) |
| `scout_rounds` | 2 | Two rounds of a spread explore bet reads each channel twice before the move | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `s` | 1 | The cheapest explore bet, 9 of the 100 points off the pick each round | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `n` | 3 | A streak of a field reading above the leader's that is rare on No change | [Streaks](../../pilot/engine-checks.md#streaks) |

## Invariants

- The hedge rule never bets on the hedge beyond `explore`, and never picks it.
- The Scout rule's split always has `s` on every channel but the pick.

## Pilot decides

- `explore` and `scout_rounds` from [reading roughness](../../pilot/engine-checks.md#reading-roughness), `window` from [Streaks](../../pilot/engine-checks.md#streaks), and `fall_points` and `tell_points` from [the tell](../../pilot/engine-checks.md#the-tell), which also tries `window` beside them, as the [defaults](#defaults) table says.
- `s` from [Up and down](../../pilot/engine-checks.md#up-and-down) and `n` from [Streaks](../../pilot/engine-checks.md#streaks).

## Not decided

- The thresholds are in level points so they survive [pinning](../engine/timeline.md#pinning). Whether they should scale with read noise instead. Decide when [reading roughness](../../pilot/engine-checks.md#reading-roughness) has run.
