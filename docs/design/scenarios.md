# Scenarios

A scenario is a list of [events](mechanics.md#events), and each event has a shape: a shock, a switch or a drift. Every event redraws its size, timing and profile per seed, so no two runs of a scenario look alike. Each scenario tests one [trait](scoring.md#traits).

## Scenarios we test

| Sparkline | Scenario | Events | Trait |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | No change | None | [Composure](scoring.md#traits) |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | One shock | One shock | [Patience](scoring.md#traits) |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | Down switch | One switch: the leader falls, sometimes a sleeper rises too | [Doubt](scoring.md#traits) |
| `▃▃▃▃▃▄▅▆▇▇▇▇▇▇▇▇` | Up switch | One switch: a sleeper rises, the leader holds | [Curiosity](scoring.md#traits) |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | Shock then switch | One shock, a gap, one switch | [Unlearning](scoring.md#traits) |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | Slow drift | One drift | [Vigilance](scoring.md#traits) |

- **Every scenario name ends in "scenario"**, as in the One shock scenario, so it never reads as the events inside it. In code the name is lower case with underscores, such as `one_shock`.
- **Each sparkline is a typical draw of the leader's level.** The other nine channels move as the [generator](mechanics.md#generator) says: a shock moves them all, a switch or drift moves one.
- **The Up switch sparkline is the sleeper's level**, not the leader's. From the leader's seat the tape is flat and looks exactly like the No change scenario. That is the test.
- **The two switch scenarios are named by what the leader feels.** In the Down switch scenario its base level falls, and on some seeds a sleeper rises too, so the runner-up is sometimes the destination and sometimes a decoy. In the Up switch scenario a sleeper rises past it and it holds. The Shock then switch scenario's switch is a down switch.
- **The No change scenario** is the control. It plays as many seeds as the others, sized by the same [seeds check](../pilot/provider-checks.md#seeds), and most models should score near 1 in it. A low score there is false alarms when no action should have been taken.
- **The Up switch scenario** is the switch's reverse. The old plan never stops paying, so output never dips and nothing cues a look. The only way to find the rise is to have been looking. Grove's Intel saw memory fall. Microsoft in 1995 saw nothing fall: Windows kept paying while the web rose.
- **Up switch and No change are a pair**, as One shock and Down switch are. On one seed they differ only on the sleeper's channel, so the gap between a model's two scores is what looking costs when it finds nothing against what it earns when it finds something.
- **The Shock then switch scenario** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change.
- **The Slow drift scenario** is the Down switch scenario stretched over many more rounds.
- **The [noise grid](../pilot/engine-checks.md#noise-grid) keeps the study from saturating**, by extending to noisier worlds on one axis. Hard variants string more shocks before the switch, or a longer drift. Length and count come from the [pilot](../../TODO.md#pilot).

## Scenarios we skip

| Sparkline | Scenario | What it would test | Failure mode | Why we skip it |
|---|---|---|---|---|
| `▆▃▁▂▃▃▃▃▃▂▁▂▃▃▃▃` | Switch then shock | commitment stability | whipsaw back to the old climate | Real but second order. The noise after any switch gives a partial read for free |
| `▆▃▁▄▆▆▃▁▄▆▆▃▁▄▆▆` | Repeated shocks | which way habituation goes | gets jumpier, not calmer | Habituation is a [future study](future.md#how-the-world-changes). Add it if models turn out fine on the basics |
| `▇▇▇▇▅▅▅▅▃▃▃▃▁▁▁▁` | Repeated switches | whether it updates its rate of updating | treats the third switch like the first | Same as repeated shocks |
| `▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇` | Leader rises, or a boom | not chasing good news | moves off a plan that just got better | The right move is to hold, so it is the No change scenario with a bigger prize. The Up switch scenario is the rise worth testing |
| `▆▆▆▃▃▃▃▃▃▃▆▆▆▆▆▆` | Switch then revert | recognising a return | treats the old climate as new, or refuses to go back | Niche |
| `▅▅▄▅▅▄▅▅▇▂▆▃▇▂▆▄` | Variance shift | a change in the weather with no change in level | only watches the mean | A different question: what counts as a change in climate. Save it for when we want to argue definitions |
| `▆▅▆▆▄▆▆▃▆▆▂▅▁▁▁▁` | Escalating shocks | reading precursors | ignores a trend in volatility | A precursor-reading benchmark in disguise. Separate project |
| `▆▅▆▆▄▆▆▃▆▆▂▅▆▆▆▆` | False escalation | the twin of escalating shocks | adapts to a storm that passes | Goes with escalating shocks |

## Rules for adding a scenario

- If we test a positive effect, we need to make sure we test its reverse. The Down switch and Up switch scenarios are each other's reverse.
- Tie each scenario to one trait and its failure mode, and add the trait to [traits](scoring.md#traits).
