# Parked

## Purpose

The baselines named in [not yet](../../design/baselines.md#not-yet), with what is known of each one's shape and what it waits for. None is in the code yet. Each becomes a `Policy` with its own page here when it comes, and a row in [`POLICIES`](policies.md#policies). The Timestral rules were parked here until the layer existed and are now on [forecast](forecast.md).

## Behaviour

### Bayesian

- **Shape.** A `Policy` with `peeks` false that keeps a belief over each channel's level from its own readings, in the engine's family, turns the belief into quantiles on `QUANTILE_LEVELS`, and hands them to a `ForecastRule`. So `Bayesian(rule=odds)` and `Bayesian(rule=top_pick)` are the Timestral rows with a belief in place of a forecaster, see [forecast](forecast.md).
- **Why a player, never the yardstick.** It bets on past readings only, so there is no loop, but what it could know depends on what it looked at, see [why these two baselines](../../design/scoring.md#why-these-two-baselines).
- **Waits for** Timestral having run, as the hazard prior is a dial we would have to pre-register, see [Timestral checks](../../pilot/provider-checks.md#timestral-checks).

### CUSUM

- **Shape.** A `Policy` with `peeks` false, the textbook change detector: sum how much each reading of the pick favours a change, move when the sum crosses a line. A `threshold` and a `drift` parameter, swept from hasty to patient, draw the trade between delay and false alarms.
- **Waits for** the hedge rule having run, so the two can be read side by side on the [noise grid](../../pilot/engine-checks.md#noise-grid).

### Barbell

- **Shape.** A `Policy` with `peeks` false: `budget` split between `start.leader` and `start.runner_up`, with a switch rule like the hedge rule's fall test on the leader. A cheap win when only the leader falls, a decoy when a sleeper rises, and blind in the Up switch scenario as it never looks past the runner-up.
- **Waits for** [Up and down](../../pilot/engine-checks.md#up-and-down) showing how often a sleeper rises.

### Fixed split

- **Not planned.** Incumbent plus a fixed split that never acts pays for a look it never uses, so it sits below the Complacent baseline. With a switch rule it is the hedge rule or `TopPickWithLooks`, see [not yet](../../design/baselines.md#not-yet).

## Not decided

- Whether the Bayesian baseline's quantiles should come from a closed form or from samples. Decide when it is written, after Timestral has run.
