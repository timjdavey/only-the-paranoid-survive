# Pilot decisions

One row per check in [engine checks](engine-checks.md) and [provider checks](provider-checks.md), and per knob the [generator](../design/mechanics.md#generator) leaves to the pilot. Fill a row when its run is done. Tables and plots are in [results](results.md).

## Engine checks

| Check | Decision | Date | Log |
|---|---|---|---|
| [Streaks](engine-checks.md#streaks), persistence | | | |
| [The tell](engine-checks.md#the-tell), shared-factor scale | | | |
| [Luck on offer](engine-checks.md#luck-on-offer) | | | |
| [Tape sanity](engine-checks.md#tape-sanity) | | | |
| [Noise grid](engine-checks.md#noise-grid), own-weather scale | | | |
| [Game length and switch round](engine-checks.md#game-length-and-switch-round) | | | |
| [Reading roughness](engine-checks.md#reading-roughness) | | | |
| [Baseline order](engine-checks.md#baseline-order) | | | |
| Events per run and minimum gap | | | |
| Switch size in level points on the noise grid | | | |
| Loading range and ladder ranges | | | |

## Provider checks

| Check | Decision | Date | Log |
|---|---|---|---|
| [Seeds](provider-checks.md#seeds) | | | |
| [Repeats](provider-checks.md#repeats) | | | |
| [Timestral checks](provider-checks.md#timestral-checks) | | | |
| [Notepad and compute](provider-checks.md#notepad-and-compute) | | | |
| [Rolling conversation](provider-checks.md#rolling-conversation) | | | |
| [Inertia](provider-checks.md#inertia) | | | |
| [Cost per run](provider-checks.md#cost-per-run) | | | |
| Warm up: empty record or pre-filled | | | |
| Retry share that marks a bar, see [retry rule](../harness/prompts.md#retry-rule) | | | |

- **A decision is a number or a yes or no**, plus one line on why if the run surprised us.
- **Once a row is filled it is frozen.** Changing it means a new pilot and a new row.
