# Scenarios

## Shapes we test

| Shape | Name | What it tests | Failure mode |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | calm | jumpiness | false alarms |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | shock | patience | overreaction |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | switch | willingness to question | underreaction |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | shock then switch | learned complacency | "dips always recover" |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | drift | boiling frog | never triggers, as there's no sudden move to notice |

- **Calm** is a floor. A handful of runs, not a real column. We expect high performance across the board.
- **Shock then switch** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change.
- **Drift** is a version of switch but extended over a longer period.
- This study avoids becoming saturated by extending the game. More shocks then a switch; or more slow subtle drift.


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
