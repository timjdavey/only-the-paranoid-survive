# Parked

## Purpose

The baselines named in [not yet](../../design/baselines.md#not-yet), with what is known of each one's shape and what it waits for. None is in the code yet. Each becomes a `Policy` with its own page here when it comes, and a row in [`POLICIES`](policies.md#policies). The Timestral rules were parked here until the layer existed and are now on [forecast](forecast.md), and the Bayesian baseline is now on [bayesian](bayesian.md).

## Behaviour

### CUSUM

- **Shape.** A `Policy` with `peeks` false, the textbook change detector: sum how much each reading of the pick favours a change, move when the sum crosses a line. A `threshold` and a `drift` parameter, swept from hasty to patient, draw the trade between delay and false alarms.
- **Waits for** the [Bayesian frontier](../../pilot/engine-checks.md#bayesian-frontier) having run. The frontier draws the delay against false alarm trade already, with the prior in place of the line, so CUSUM comes only if the pilot wants the one-channel textbook curve beside it.

### Barbell

- **Shape.** A `Policy` with `peeks` false: `budget` split between `start.leader` and `start.runner_up`, with a switch rule like the hedge rule's fall test on the leader. A cheap win when only the leader falls, a decoy when a sleeper rises, and blind in the Up switch scenario as it never explores past the runner-up.
- **Waits for** [Up and down](../../pilot/engine-checks.md#up-and-down) showing how often a sleeper rises.

