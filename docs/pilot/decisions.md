# Pilot decisions

One row per check in [engine checks](engine-checks.md) and [provider checks](provider-checks.md), and per knob the [generator](../design/mechanics.md#generator) leaves to the pilot. Every row names the check whose Decide line settles it, so no number is filled without a run behind it. Fill a row when its run is done. Tables and plots are in [results](results.md).

## Engine checks

| Check | Decision | Date | Log |
|---|---|---|---|
| [Streaks](engine-checks.md#streaks), persistence and the Scout rule's `n` | | | |
| [The tell](engine-checks.md#the-tell), shared-factor scale, and the hedge rule's `window`, `fall_points` and `tell_points` | | | |
| [Luck on offer](engine-checks.md#luck-on-offer) | | | |
| [Timeline sanity](engine-checks.md#timeline-sanity) | | | |
| [Noise grid](engine-checks.md#noise-grid), own-weather scale | | | |
| [Game length and switch round](engine-checks.md#game-length-and-switch-round) | | | |
| [Reading roughness](engine-checks.md#reading-roughness), read noise, and the hedge rule's `explore` and `scout_rounds` | | | |
| [Baseline order](engine-checks.md#baseline-order) | | | |
| [Bayesian frontier](engine-checks.md#bayesian-frontier), `hazard` and `rule` | | | |
| [Bayesian frontier](engine-checks.md#bayesian-frontier), irreducible lag, and whether the Bayesian baseline joins the marks | | | |
| [Game length and switch round](engine-checks.md#game-length-and-switch-round), events per run and the `gap` between them | | | |
| [Noise grid](engine-checks.md#noise-grid), switch size in level points | | | |
| [Up and down](engine-checks.md#up-and-down), sleeper share, rise size in level points and the Scout rule's `s` | | | |
| [Up and down](engine-checks.md#up-and-down), short share of Up switch seeds and the sleeper's end level on them as a share of the gap between runner-up and leader | | | |
| [The tell](engine-checks.md#the-tell), loading range, and [Timeline sanity](engine-checks.md#timeline-sanity), ladder ranges | | | |
| [Reachable gain](engine-checks.md#reachable-gain), reachable gain and Bayesian gain percentage per scenario at the chosen knobs, and the knob that moved to clear them | | | |

## Provider checks

| Check | Decision | Date | Log |
|---|---|---|---|
| [Seeds](provider-checks.md#seeds), the count, and the row and scenario with the widest spread that set it | | | |
| [Repeats](provider-checks.md#repeats) | | | |
| [Recognition](provider-checks.md#recognition), share that flags a bar | | | |
| [Channel order](provider-checks.md#channel-order), whether `submit` keeps its list | | | |
| [Up against down](provider-checks.md#up-against-down) | | | |
| [Jev checks](provider-checks.md#jev-checks) | | | |
| [Timestral checks](provider-checks.md#timestral-checks) | | | |
| [Bare harness](provider-checks.md#bare-harness), bare gap per model and `notes_cap` | | | |
| [Tool choice](provider-checks.md#tool-choice), gap per model | | | |
| [Rolling conversation](provider-checks.md#rolling-conversation), gap per model | | | |
| [Inertia](provider-checks.md#inertia) | | | |
| [Cost per run](provider-checks.md#cost-per-run) | | | |
| [Warm up](provider-checks.md#warm-up) | | | |
| [Cost per run](provider-checks.md#cost-per-run), retry share that flags a bar, see [retry rule](../harness/prompts.md#retry-rule) | | | |

- **A decision is a number or a yes or no**, plus one line on why if the run surprised us.
- **Once a row is filled it is frozen.** Changing it means a new pilot and a new row.
