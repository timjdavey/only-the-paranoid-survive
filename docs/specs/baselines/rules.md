# Rules

## Purpose

The two baselines with parameters: the hedge rule, the simplest player that reads the [tell](../../glossary.md#the-world), and the Scout rule, the hedge rule that looks everywhere all the time. Both read only their own record, so they are players with a mark on every bar, never the yardstick, see [fixed baselines](../../design/baselines.md#fixed-baselines). Their parameters are what the pilot sweeps, see [pilot decides](#pilot-decides).

## Interface

```python
@dataclass(frozen=True)
class HedgeRule:                            # peeks = False
    look: int = 2
    window: int = 3
    fall_points: float = 8.0
    tell_points: float = 4.0
    scout_rounds: int = 2

@dataclass(frozen=True)
class ScoutRule:                            # peeks = False
    s: int = 1
    n: int = 3
    tell_points: float = 4.0

hedge_rule: Policy     # HedgeRule() at the defaults
scout_rule: Policy     # ScoutRule() at the defaults
```

- **Both are handed round 1** through `view.start`: they start on the leader and know which channel is the hedge, the same gift the Complacent baseline gets. No model gets either, so their curves are an upper bound on what a player that reads the tell could earn, see [view](../engine/view.md#view) and [the baselines are handed round 1](../../design/baselines.md#fixed-baselines).
- **State is derived, never kept.** Each call replays the rounds below from round 1 over the record, so the same view gives the same split, see [conventions](README.md#conventions).

## Behaviour

### Hedge rule

`look` on the hedge, the rest on its pick. State: a `pick`, a `phase` of hold or scout, the round the pick was last set `moved_at`, and the round scouting began `scout_start`.

- **Round 1.** `pick = start.leader`, phase hold, `moved_at = 1`. Split: `look` on the hedge, `budget − look` on the pick.
- **Hold.** Each round, run the fall test on the pick's readings since `moved_at`. The recent readings are the last `window` of them. The earlier readings are all the ones before those, and there must be at least `window` of them or the test does not run.
  - **Fall** when `mean(recent) < mean(earlier) − fall_points`.
  - **Tell** when the hedge's mean over the same recent rounds is above its mean over the same earlier rounds by more than `tell_points`. The hedge rose while the pick fell, so it is a shock. Hold.
  - **Fall and no tell**: phase scout, `scout_start = round`.
- **Scout.** For `scout_rounds` rounds: `look` on the hedge and `budget − look` split by `split_budget` evenly over every other channel, the pick included.
- **Move.** On the round after the last scout round: `pick` becomes the channel, hedge excluded, with the highest mean reading over the scout rounds. Phase hold, `moved_at = round`. Bet the hold split with the new pick. The fall test then starts over on the new pick's readings.
- It never moves in the Up switch or Up switch then down switch scenarios, as the leader never falls, see [baseline order](../../pilot/engine-checks.md#baseline-order).
- `look ≥ 1`, else `ValueError` on construction. `look < budget`, else `ValueError` when the first view arrives.

### Scout rule

`s` on every channel but its pick, the rest on the pick. State: `pick` and `moved_at`, derived as above.

- **Round 1.** `pick = start.leader`, `moved_at = 1`.
- **Every round.** `s` on each of the other `channels − 1` channels and `budget − s × (channels − 1)` on the pick. `s × (channels − 1)` must be below `budget`, else `ValueError` when the first view arrives, as `channels` is not known on construction.
- **Move test**, run before splitting once `round − moved_at ≥ n`:
  - **Candidates** are the channels, pick and hedge excluded, whose reading beat the pick's reading in each of the last `n` rounds.
  - **Tell** when the hedge's mean over the last `n` rounds is above its mean over every earlier round since `moved_at` by more than `tell_points`. With no earlier round there is no tell.
  - **Candidates and no tell**: `pick` becomes the candidate with the highest mean reading over the last `n` rounds, `moved_at = round`, and this round's split uses the new pick.
- It keeps scouting after a move, so it can move again. In the Up switch then down switch scenario that is how it goes back to the leader once the sleeper falls.
- In noisy worlds it whipsaws. That is the point of it as a curve, see [fixed baselines](../../design/baselines.md#fixed-baselines).

## Defaults

Every number is **pilot to confirm**.

| Parameter | Default | Why | Settled by |
|---|---|---|---|
| `look` | 2 | Reads the hedge less roughly than one point, for 2 of the 100 points | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `window` | 3 | Three rounds is the streak that is ordinary by chance on No change, so the fall test needs a real drop | [Streaks](../../pilot/engine-checks.md#streaks) |
| `fall_points` | 8.0 | Two weather SDs at the default `own_scale` of 4, well inside a switch's size | [The tell](../../pilot/engine-checks.md#the-tell) |
| `tell_points` | 4.0 | One weather SD at the default `own_scale`. The hedge's rise in a shock is its loading times the depth, and should clear this | [The tell](../../pilot/engine-checks.md#the-tell) |
| `scout_rounds` | 2 | Two rounds of a spread look reads each channel twice before the move | [Reading roughness](../../pilot/engine-checks.md#reading-roughness) |
| `s` | 1 | The cheapest look, 9 of the 100 points off the pick each round | [Up and down](../../pilot/engine-checks.md#up-and-down) |
| `n` | 3 | A streak of a field reading above the leader's that is rare on No change | [Streaks](../../pilot/engine-checks.md#streaks) |

## Invariants

- `hedge_rule == HedgeRule()` and `scout_rule == ScoutRule()`.
- The hedge rule never bets on the hedge beyond `look`, and never picks it.
- The Scout rule's split always has `s` on every channel but the pick.

## Pilot decides

- `look`, `window`, `fall_points`, `tell_points` and `scout_rounds` for the hedge rule, from [the tell](../../pilot/engine-checks.md#the-tell) and [reading roughness](../../pilot/engine-checks.md#reading-roughness).
- `s` and `n` for the Scout rule, from [Streaks](../../pilot/engine-checks.md#streaks) and [Up and down](../../pilot/engine-checks.md#up-and-down).

## Not decided

- The thresholds are in level points so they survive [pinning](../engine/tape.md#pinning). Whether they should scale with read noise instead. Decide when [reading roughness](../../pilot/engine-checks.md#reading-roughness) has run.
