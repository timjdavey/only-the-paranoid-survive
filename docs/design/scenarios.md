# Scenarios

A scenario is a list of [events](mechanics.md#events), and each event has a shape: a shock, a switch or a drift. Every event redraws its size, timing and profile per seed, so no two runs of a scenario look alike. Each scenario tests one [trait](scoring.md#traits).

## Scenarios we test

| Sparkline | Scenario | Events | Trait |
|---|---|---|---|
| `▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆` | No change | None | [Composure](scoring.md#traits) |
| `▆▆▆▆▃▁▂▄▅▆▆▆▆▆▆▆` | One shock | One shock | [Patience](scoring.md#traits) |
| `▆▆▆▆▃▁▂▃▃▃▃▃▃▃▃▃` | Down switch | One switch: the leader falls, sometimes a sleeper rises too | [Doubt](scoring.md#traits) |
| `▃▃▃▃▃▄▅▆▇▇▇▇▇▇▇▇` | Up switch | One switch: a sleeper rises, the leader holds. On most seeds the sleeper rises past the leader, on some it stops short | [Curiosity](scoring.md#traits) |
| `▆▃▁▂▄▆▆▆▆▃▁▂▃▃▃▃` | Shock then switch | One shock, a gap, one switch | [Unlearning](scoring.md#traits) |
| `▆▆▆▆▆▅▅▅▄▄▄▃▃▃▃▃` | Slow drift | One drift | [Vigilance](scoring.md#traits) |
| `▆▆▆▆▃▃▃▃▃▁▂▃▃▃▃▃` | Switch then shock | One switch, drawn as the Down switch scenario draws it, a gap, one shock | [Conviction](scoring.md#traits) |
| `▃▃▃▃▄▅▆▇▇▇▇▆▅▄▃▃` | Up switch then down switch | One switch where a sleeper rises past the leader, a gap, one switch where the same sleeper falls back to its old level | [Recall](scoring.md#traits) |

- **Every scenario name ends in "scenario"**, as in the One shock scenario, so it never reads as the events inside it. In code the name is lower case with underscores, such as `one_shock`.
- **Each sparkline is a typical draw of the leader's level.** The other nine channels move as the [generator](mechanics.md#generator) says: a shock moves them all, a switch or drift moves one.
- **The Up switch sparkline is the sleeper's level**, not the leader's. From the leader's seat the tape is flat and looks exactly like the No change scenario. That is the test. The Up switch then down switch sparkline shows the sleeper too.
- **The two switch scenarios are named by what the leader feels.** In the Down switch scenario its base level falls, and on some seeds a sleeper rises too, so the runner-up is sometimes the destination and sometimes a decoy. In the Up switch scenario a sleeper rises and it holds. On most seeds the sleeper rises past it, and on some it stops short, so a rising channel is sometimes worth the move and sometimes not. The Shock then switch scenario's switch is a down switch.
- **The No change scenario** is the control. It plays as many seeds as the others, sized by the same [seeds check](../pilot/provider-checks.md#seeds), and most models should score near 1 in it. A low score there is false alarms when no action should have been taken.
- **The Up switch scenario** is the switch's reverse. The old plan never stops paying, so output never dips and nothing cues a look. The only way to find the rise is to have been looking. Grove's Intel saw memory fall. Microsoft in 1995 saw nothing fall: Windows kept paying while the web rose.
- **On some Up switch seeds the sleeper stops short.** It lands above the runner-up, so a looker sees a real move, but below the leader, so the right call is to stay. The Down switch scenario draws its decoy the same way, so a model cannot learn that a rising channel always wins, any more than it can learn that a fall always comes with a riser. The short share and the end level are [pilot knobs](../pilot/decisions.md#engine-checks).
- **Up switch and No change are a pair**, as One shock and Down switch are. On one seed they differ only on the sleeper's channel, so the gap between a model's two scores is what looking costs when it finds nothing against what it earns when it finds something. On a seed where the sleeper stops short, the gap is what a look costs when it finds something not worth acting on.
- **Conviction and Recall are each other's reverse.** Both test a plan the agent has just chosen. In the Switch then shock scenario going back is wrong, in the Up switch then down switch scenario it is right. Patience and Doubt ask the same of the plan the agent started with.
- **The Shock then switch scenario** is Grove's thesis. A model that rightly held through the shock has learnt "dips recover", and is primed to miss the real change.
- **The Slow drift scenario** is the Down switch scenario stretched over many more rounds.
- **The Switch then shock scenario** is Grove's bad quarters after the move. The agent has moved to the new best, and a shock dips it along with everything else. The Discerning baseline holds the new best through the shock and the Complacent baseline is still on the old leader, so a model that whipsaws back lands between them. A model that never moved at the switch lands near the Complacent mark too, and never gets to show Conviction, so read this score against the Down switch score on the same seed: the tapes match until the shock, and the gap between the two is what the whipsaw cost. The hedge rises in the shock, so the hedge rule holds. The sparkline shows the leader, and the destination channel dips with it. Gallistel 2014's "take it back" button and Bazaar's "revision, not detection" are the prior, see [people](../prior/people.md#gallistel-et-al-2014-step-hold-and-take-it-back).
- **The Up switch then down switch scenario** is Hopin: a rise that was real for a while, then undone. The leader is best again at the end, so the Complacent baseline scores well, and a model that found the sleeper but stays on it scores *below* one that never looked. Pair it with the Up switch scenario on the same seed: on seeds where the Up switch sleeper rises past, the tapes match until the fall, so the gap between the two scores is what the revert cost. Set-shifting found models go back to old tool groups readily, so the number to watch may be how fast, not whether, see [worlds that change](../prior/worlds-that-change.md#set-shifting-2026-tool-groups-that-stop-working).
- **The [noise grid](../pilot/engine-checks.md#noise-grid) keeps the study from saturating**, by extending to noisier worlds on one axis. Hard variants string more shocks before the switch, or a longer drift. Length and count come from the [pilot](../../TODO.md#pilot).

## Scenarios we skip

| Sparkline | Scenario | What it would test | Failure mode | Why we skip it |
|---|---|---|---|---|
| `▆▃▁▄▆▆▃▁▄▆▆▃▁▄▆▆` | Repeated shocks | which way habituation goes | gets jumpier, not calmer | Habituation is a [future study](future.md#how-the-world-changes). Add it if models turn out fine on the basics |
| `▇▇▇▇▅▅▅▅▃▃▃▃▁▁▁▁` | Repeated switches | whether it updates its rate of updating | treats the third switch like the first | Same as repeated shocks |
| `▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇` | Leader rises | not chasing good news | moves off a plan that just got better | A lasting rise on the leader is the No change scenario with a bigger prize. A rise elsewhere is the Up switch scenario |
| `▆▆▆▆▇█▇▇▇▆▆▆▆▆▆▆` | One boom | not chasing good news that passes | reads the fade as a decline, or chases a channel the boom lifted | A shock with its sign flipped: every channel rises by its loading, then it passes. With 100 on the leader there is nothing to over-invest in, and at the fade every channel falls together, so the only wrong move is a look, which the No change scenario already prices. It becomes a test once the boom is deep enough for a high-loading channel to pass the leader for a while, so a looker is tempted to chase weather. That is a [hard-variant knob](mechanics.md#hard-variant-knobs), like the hedge overtaking |
| `▃▃▃▃▃▃▄▄▄▅▅▅▆▆▇▇` | Up drift | looking long enough for a slow rise to add up | one look shows nothing, so the looking stops | The Up switch scenario stretched over many rounds. It says nothing new until models look at all, so it is a [hard variant](mechanics.md#stringing-events) of the Up switch scenario. Promote it if the Up switch run scores split into found and not found |
| `▆▆▆▃▃▃▃▃▃▃▆▆▆▆▆▆` | Down switch then revert | recognising a return the agent cannot see | never looks back at the channel it left | The Up switch then down switch scenario tests the return the agent can see. This one needs a look to notice, so it muddles Recall with Curiosity |
| `▅▅▄▅▅▄▅▅▇▂▆▃▇▂▆▄` | Variance shift | a change in the weather with no change in level | only watches the mean | A different question: what counts as a change in climate. Save it for when we want to argue definitions |
| `▆▅▆▆▄▆▆▃▆▆▂▅▁▁▁▁` | Escalating shocks | reading precursors | ignores a trend in volatility | A precursor-reading benchmark in disguise. Separate project |
| `▆▅▆▆▄▆▆▃▆▆▂▅▆▆▆▆` | False escalation | the twin of escalating shocks | adapts to a storm that passes | Goes with escalating shocks |

## Rules for adding a scenario

- If we test a positive effect, we need to make sure we test its reverse. The Down switch and Up switch scenarios are each other's reverse.
- Tie each scenario to one trait, write the question its score answers, and name its failure mode. Add the trait to [traits](scoring.md#traits).
