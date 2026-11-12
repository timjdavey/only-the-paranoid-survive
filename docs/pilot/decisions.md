# Pilot decisions

One row per check in [engine checks](engine-checks.md) and [provider checks](provider-checks.md), and per knob the [generator](../design/mechanics.md#generator) leaves to the pilot. Every row names the check whose Decide line settles it, so no number is filled without a run behind it. Fill a row when its run is done. Tables and plots are in [results](results.md).

## Engine checks

| Check | Decision | Date | Log |
|---|---|---|---|
| [Streaks](engine-checks.md#streaks), persistence | 0.8, kept. A three round streak shows on 0.10 of No change timelines at 0.8 and at 0.9, so no value reaches one in five. The switch separates in a median of 8 rounds, up from 3 before onset moved: more rounds follow the switch, so weather has longer to cross back. The Discerning baseline still pulls clear in a median of 1 round, see [length](results.md#length) | 2026-11-12 | [streaks](results.md#streaks) |
| [The tell](engine-checks.md#the-tell), shared-factor scale, and the hedge rule's `window`, `fall_points` and `tell_points` | Scale 3, kept. `window` 3, `fall_points` 8 and `tell_points` 4, kept. The field moves together on no No change seed at 3 and on 0.015 at 4.5. The tell is false on 0.002 of switches. The hit rate is 0.37 and does not move with the scale, so the check no longer asks for nine in ten. The default set has the best score at scale 3, 0.937 | 2026-11-12 | [tell](results.md#tell) |
| [Luck on offer](engine-checks.md#luck-on-offer) | Yes. At most 0.11, at setting 8 | 2026-11-12 | [luck](results.md#luck) |
| [Timeline sanity](engine-checks.md#timeline-sanity) | Yes. No level falls below 0 at any setting. A reading below 0 shows on 0.001 of runs at setting 8 and on none below it. Pinning holds: on Down switch the Discerning baseline leads by 503.6 points at setting 2 and 501.9 at 8. Three sparklines in [scenarios](../design/scenarios.md#scenarios-we-test) were redrawn to the earlier onset | 2026-11-12 | [sanity](results.md#sanity) |
| [Noise grid](engine-checks.md#noise-grid), own-weather scale | 2, 3, 4, 6 and 8, kept, with 4 the proof of concept setting. The grid does not span a full curve: the hedge rule's Down switch score falls from 0.91 to 0.82 across it and never comes half way to the Complacent baseline's 0.40. No knob fixes that, see [TODO](../../TODO.md#pilot) | 2026-11-12 | [scores](results.md#scores) |
| [Game length and switch round](engine-checks.md#game-length-and-switch-round) | 40 rounds, kept. Onset 8 to 12, was 12 to 20. At 30 rounds Slow drift's reachable gain is 0.17. At an onset of 12 to 20 three scenarios stay under the floor, even at the new sizes | 2026-11-12 | [length](results.md#length) |
| [Reading roughness](engine-checks.md#reading-roughness), read noise, and the hedge rule's `explore` and `scout_rounds` | k of 8, kept. `explore` 1 and `scout_rounds` 1, both were 2. At every k the hedge rule's Down switch output falls as its explore bet grows, and it moves on 0.99 of seeds at every pair. So no strength makes a bigger explore bet pay, and the cheapest pair is the best | 2026-11-12 | [roughness](results.md#roughness) |
| [Baseline order](engine-checks.md#baseline-order) | Yes, every line holds. Three lines were reworded first, as no knob could make them hold: ≈ and ≥ now allow 0.05, the Stayer is the yardstick in Up switch then down switch, and the hedge rule sits beside the Complacent baseline on Up switch | 2026-11-12 | [orders](results.md#orders) |
| [Bayesian frontier](engine-checks.md#bayesian-frontier), `hazard` and `rule` | 0.01, was 0.025, and `odds`. Its headline is 0.937 on the picking half and 0.944 on the reporting half. Three players on ten seeds could not tell 0.005 from 0.025, so the cell now plays all five hazards on a hundred seeds | 2026-11-12 | [pick](results.md#pick) |
| [Bayesian frontier](engine-checks.md#bayesian-frontier), irreducible lag, and whether the Bayesian baseline joins the marks | 0.057. Yes: it is the best blind baseline in every scenario, level with the hedge rule on No change. Joining the scorer's marks is not built yet, see [TODO](../../TODO.md#pilot) | 2026-11-12 | [pick](results.md#pick), [outputs](results.md#outputs) |
| [Game length and switch round](engine-checks.md#game-length-and-switch-round), events per run and the `gap` between them | Two events, and a gap of 8 to 12, kept. At 6 to 8 the Scout rule never moves on 0.10 of Up switch then down switch seeds. At 12 to 16 Shock then switch's reachable gain is 0.31, on the floor | 2026-11-12 | [length](results.md#length) |
| [Noise grid](engine-checks.md#noise-grid), switch size in level points | 4 to 12, kept. Down switch's reachable gain is 0.60. The hedge rule's curve crosses half way at no size the grid can pin, see the own-weather scale row | 2026-11-12 | [scores](results.md#scores) |
| [Up and down](engine-checks.md#up-and-down), sleeper share, rise size in level points and the Scout rule's `s` and `n` | Sleeper share 0.5, kept. Rise 12 to 24 points, 3 to 6 sigmas, was 4 to 12. `s` 1 and `n` 3, kept. The three kinds' reachable gains are 0.38 for a fall, 0.40 for a rise and 0.72 for both. An `n` of 5 gains 0.005 on No change and loses 0.03 to 0.05 on every switch | 2026-11-12 | [kinds](results.md#kinds) |
| [Up and down](engine-checks.md#up-and-down), short share of Up switch seeds and the sleeper's end level on them as a share of the gap between runner-up and leader | 0.25, and 0.25 to 0.75, kept. On the short seeds the Scout rule scores 0.89, the same as on No change, so a near tie costs it nothing past its explore bets | 2026-11-12 | [kinds](results.md#kinds) |
| [The tell](engine-checks.md#the-tell), loading range, and [Timeline sanity](engine-checks.md#timeline-sanity), ladder ranges | Loading 0.3 to 1.0 and the ladder ranges, kept. Scale 3 passes the tell's lines, so the range is not redrawn, and no run at the proof of concept setting shows a reading below 0. The shock cap bites on 0.14 of shocks | 2026-11-12 | [tell](results.md#tell), [sanity](results.md#sanity) |
| [Reachable gain](engine-checks.md#reachable-gain), reachable gain and Bayesian gain percentage per scenario at the chosen knobs, and the knob that moved to clear them | Down switch 0.60 and 90%. Up switch 0.33 and 80%. Shock then switch 0.39 and 83%. Slow drift 0.31 and 79%. Switch then shock 0.61 and 89%. Up switch then down switch 0.48 and 80%, with the Bayesian baseline moving on 0.86 of seeds. Three knobs moved: onset to 8 to 12, the rise to 3 to 6 sigmas, and the drift's size to 2 to 4 sigmas, was 1 to 3 | 2026-11-12 | [gains](results.md#gains), [lines](results.md#lines) |

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
