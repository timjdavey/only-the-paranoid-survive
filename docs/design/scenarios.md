# Scenarios

## Shapes we test

| Shape | Scenario | What it tests | Failure mode |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | No change | jumpiness | false alarms |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | One shock | patience | overreaction |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | One switch | willingness to question | underreaction |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | Shock then switch | learned complacency | "dips always recover" |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | Slow drift | boiling frog | never triggers, as there's no sudden move to notice |

- **Every scenario name ends in "scenario"**, as in the One shock scenario, so it never reads as the [events](mechanics.md#events) inside it. In code the name is lower case with underscores, such as `one_shock`.
- **Each sparkline is a typical draw of the leader's level.** The other nine channels move as the [generator](mechanics.md#generator) says: a shock moves them all, a switch or drift moves one.
- **The No change scenario** is a floor. A handful of runs, not a real column. We expect high performance across the board.
- **The Shock then switch scenario** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change.
- **The Slow drift scenario** is the One switch scenario stretched over many more rounds.
- This study avoids becoming saturated by extending the game. More shocks then a switch; or more slow subtle drift.

## Each shape as a list of events

A scenario is a list of [events](mechanics.md#events). Every event redraws its size, timing and shape per seed, so no two runs of a shape look alike.

| Scenario | Events |
|---|---|
| No change | None |
| One shock | One shock |
| One switch | One switch |
| Shock then switch | One shock, a gap, one switch |
| Slow drift | One drift |
| Hard editions | More shocks before the switch, or a longer drift. Length and count come from the [pilot](../../TODO.md#pilot) |


## Shapes we skip

| Shape | Name | What it tests | Failure mode | Why we skip it |
|---|---|---|---|---|
| `▆▃▁▂▃▃▃▃▃▂▁▂▃▃▃▃` | switch then shock | commitment stability | whipsaw back to the old regime | Real but second order. The noise after any switch gives a partial read for free |
| `▆▃▁▄▆▆▃▁▄▆▆▃▁▄▆▆` | repeated shocks | which way habituation goes | gets jumpier, not calmer | Habituation is a follow-up study. Add it if models turn out fine on the basics |
| `▇▇▇▇▅▅▅▅▃▃▃▃▁▁▁▁` | repeated switches | whether it updates its rate of updating | treats the third switch like the first | Same as repeated shocks |
| `▆▆▆▃▃▃▃▃▃▃▆▆▆▆▆▆` | switch then revert | recognising a return | treats the old regime as new, or refuses to go back | Niche |
| `▅▅▄▅▅▄▅▅▇▂▆▃▇▂▆▄` | variance shift | a regime change with no level change | only watches the mean | A different question: what counts as a regime. Save it for when we want to argue definitions |
| `▆▅▆▆▄▆▆▃▆▆▂▅▁▁▁▁` | escalating shocks | reading precursors | ignores a trend in volatility | A precursor-reading benchmark in disguise. Separate project |
| `▆▅▆▆▄▆▆▃▆▆▂▅▆▆▆▆` | false escalation | the twin of escalating shocks | adapts to a storm that passes | Goes with escalating shocks |

## Rules for adding a shape

- If we test a positive effect, we need to make sure we test it's reverse.
- Tie each shape to a named failure mode.
