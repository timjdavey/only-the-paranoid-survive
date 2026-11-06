# Scenarios

**The shapes of change we put each model through, and the ones we chose to leave out.**

A shape is how a unit's level moves over a run. Single shapes test whether a model spots a change and acts on it. Compound shapes test what the model learnt from the last event. That is closest to Grove's point: the response that was right last time is what blinds you to the next change.

## How to read a shape

- Each shape is a sparkline of one unit's level over a run. Time runs left to right, height is the level.
- In most shapes `▆` is the old level and `▃` the new one. The brief drops below `▃` are dips.
- Every shape is 16 characters wide, so they line up and can be compared by eye.
- Twins match at the start. Shock and switch are identical for their first 7 characters, then part.

## Shapes we test

| Shape | Name | What it tests | Failure mode |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | calm | jumpiness | false alarms |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | shock | patience | overreaction |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | switch | willingness to question | underreaction |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | shock then switch | learned complacency | "dips always recover" |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | drift | boiling frog | never triggers, as there's no sudden move to notice |

- **Calm** is a sanity floor. A handful of runs, not a real column.
- **Shock and switch are the benchmark.** One catches overreaction, the other underreaction. The rest refine them.
- **Shock then switch** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change. If we keep only one history effect, it's this one.
- **Drift** is the only shape that isn't a version of shock or switch. It's cheap and catches a detector that only fires on sudden moves. First to cut if we need to be ruthless.

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

- **Every shape that should trigger a change needs a twin** that looks the same for the first few rounds and shouldn't. Shock is the twin of switch. Without twins we only test one side of the tradeoff, and a maximally paranoid model wins.
- **Tie each shape to a named failure mode.** A shape with no hypothesis about what it catches is just noise in the headline.
- **Build shapes from a grammar, then hand-pick.** The generator can compose any sequence of primitives (calm, shock, switch, drift, variance shift). Up to length three that's well over a hundred shapes, so we choose a dozen at most, not all.

## Why the pairing is new

- Switch alone is well studied, in the change-point literature and in work on LLM belief revision.
- Those studies rarely pair it with a matching shock, so they reward jumpiness. The pairing is the new part, not the switch.

## How shapes feed the score

- **Headline:** the geometric mean of the shock score and the switch score. "How well it holds, times how well it moves."
- **Diagnostics:** shock then switch and drift are reported beside it, by name, not folded in. That keeps the headline easy to read, and lets us say "model X is fine on singles but anchors badly".
- Full detail on [measures](measures.md).
