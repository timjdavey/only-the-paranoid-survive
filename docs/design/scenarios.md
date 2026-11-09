# Scenarios

A scenario is a list of [events](mechanics.md#events), and each event has a shape: a shock, a switch or a drift. Every event redraws its size, timing and profile per seed, so no two runs of a scenario look alike. Each scenario tests one [trait](scoring.md#traits).

## Scenarios we test

| Sparkline | Scenario | Events | Trait |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | No change | None | [Composure](scoring.md#traits) |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | One shock | One shock | [Patience](scoring.md#traits) |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | One switch | One switch | [Doubt](scoring.md#traits) |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | Shock then switch | One shock, a gap, one switch | [Unlearning](scoring.md#traits) |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | Slow drift | One drift | [Vigilance](scoring.md#traits) |

- **Every scenario name ends in "scenario"**, as in the One shock scenario, so it never reads as the events inside it. In code the name is lower case with underscores, such as `one_shock`.
- **Each sparkline is a typical draw of the leader's level.** The other nine channels move as the [generator](mechanics.md#generator) says: a shock moves them all, a switch or drift moves one.
- **The No change scenario** is the control. It plays as many seeds as the others, sized by the same [seeds check](../pilot/checks.md#seeds), and most models should score near 1 in it. A low score there is false alarms when no action should have been taken.
- **The Shock then switch scenario** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change.
- **The Slow drift scenario** is the One switch scenario stretched over many more rounds.
- **The [noise grid](../pilot/checks.md#noise-grid) keeps the study from saturating**, by extending to noisier worlds on one axis. Hard variants string more shocks before the switch, or a longer drift. Length and count come from the [pilot](../../TODO.md#pilot).

## Scenarios we skip

| Sparkline | Scenario | What it would test | Failure mode | Why we skip it |
|---|---|---|---|---|
| `▆▃▁▂▃▃▃▃▃▂▁▂▃▃▃▃` | Switch then shock | commitment stability | whipsaw back to the old climate | Real but second order. The noise after any switch gives a partial read for free |
| `▆▃▁▄▆▆▃▁▄▆▆▃▁▄▆▆` | Repeated shocks | which way habituation goes | gets jumpier, not calmer | Habituation is a follow-up study. Add it if models turn out fine on the basics |
| `▇▇▇▇▅▅▅▅▃▃▃▃▁▁▁▁` | Repeated switches | whether it updates its rate of updating | treats the third switch like the first | Same as repeated shocks |
| `▆▆▆▃▃▃▃▃▃▃▆▆▆▆▆▆` | Switch then revert | recognising a return | treats the old climate as new, or refuses to go back | Niche |
| `▅▅▄▅▅▄▅▅▇▂▆▃▇▂▆▄` | Variance shift | a change in the weather with no change in level | only watches the mean | A different question: what counts as a change in climate. Save it for when we want to argue definitions |
| `▆▅▆▆▄▆▆▃▆▆▂▅▁▁▁▁` | Escalating shocks | reading precursors | ignores a trend in volatility | A precursor-reading benchmark in disguise. Separate project |
| `▆▅▆▆▄▆▆▃▆▆▂▅▆▆▆▆` | False escalation | the twin of escalating shocks | adapts to a storm that passes | Goes with escalating shocks |

## Rules for adding a scenario

- If we test a positive effect, we need to make sure we test its reverse.
- Tie each scenario to one trait and its failure mode, and add the trait to [traits](scoring.md#traits).
