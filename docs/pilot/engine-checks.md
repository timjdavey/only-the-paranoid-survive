# Engine checks

The first half of the pilot, a short run before the full study to settle the knobs. What each check's cell runs and writes, exactly, is the [harness pilot spec](../specs/harness/pilot.md#engine-cells), and what its table shows is the [analysis pilot spec](../specs/analysis/pilot.md#sections).

- **These run on timelines and the fixed baselines.** No model and no network, so thousands of seeds cost nothing.
- **Run them first.** The [provider checks](provider-checks.md) need a model and cost tokens, so they wait until these pass.
- **Every knob here is set from baselines**, never from how a model scores.

## Weather

The three weather dials are set per release, see [difficulty](../design/mechanics.md#difficulty). The own-weather scale is the axis of the [noise grid](#noise-grid). These checks pick the other two, persistence and the shared-factor scale, and check the timelines they make.

- **Streaks and The tell run first**, at a starting own-weather scale. The noise grid then picks the proof of concept setting around it.
- **Luck on offer and Timeline sanity** check every setting the noise grid tries.

### Streaks

Picks persistence, and the Scout rule's streak `n`.

- **Question.** How long a bad stretch lasts by chance, against how fast a real switch shows.
- **Run.** A thousand No change and Down switch timelines at persistence 0, 0.5, 0.8 and 0.9.
- **Measure.**
  - On the No change timelines, the longest run of rounds where the leader's level sits below the runner-up's.
  - On the Down switch timelines, the rounds from onset until the leader sits below the runner-up and stays there.
  - On the No change timelines, the longest run of rounds where some field channel's one-point reading beats the leader's, which is what the [Scout rule baseline](../design/baselines.md#fixed-baselines) acts on.
- **Decide.** A value where a three round streak of the leader below the runner-up is ordinary on No change, say in one timeline in five, but the switch still separates within a handful of rounds. Then `n`: a streak of a field reading above the leader's that is rare on No change, say in one timeline in twenty.

### The tell

Picks the shared-factor scale. The tell is the hedge rising while the field falls, which marks a shock rather than a switch.

- **Question.** How often the hedge tells a shock from a switch.
- **Run.** The hedge rule baseline on One shock and Down switch timelines, plus No change timelines, at a few shared-factor scales.
- **Measure.**
  - **Hit rate.** On One shock, of the seeds where the hedge rule's fall test fires after onset, the share where the tell stops it every time. The hedge rose while the leader fell, so the rule held through the shock.
  - **False tell rate.** On Down switch, the same share: the fall was real, the hedge reading rose anyway, and the tell stopped the rule every time, so it holds when it should move.
  - **Never fired.** The share of seeds where the fall test never fires after onset, on each. A shock too shallow to see is no test of the tell, and a switch the rule never sees is a miss of another kind.
  - **Field moving together.** On No change, how often every channel but the hedge moves more than one weather SD the same way in one round. Too often and calm weeks look like shocks.
- **Decide.** A scale where the tell is right on about nine shocks in ten and false on under one switch in ten. If no scale does both, the [loading range](../design/mechanics.md#each-round) is wrong, not the weather, and the range is redrawn and this check run again. That is where the loading range is decided.
- **Then the hedge rule's thresholds.** At the chosen scale, the hedge rule again over a small grid of `window`, `fall_points` and `tell_points`, see [rules](../specs/baselines/rules.md#defaults). Keep the set with the highest hit rate whose false tell rate stays under one in ten.

### Luck on offer

- **Question.** How much weather luck no reader could see sits on top of the gap the score divides.
- **Run.** The Perfect, Discerning and Uniform baselines on Down switch timelines, at every setting the noise grid tries.
- **Measure.** (Perfect − Discerning) ÷ (Discerning − Uniform), pooled over seeds.
- **Decide.** It stays under about 0.5 at every setting. Above that, luck rivals the [reachable gain](#reachable-gain) and a lucky run lands well above 1. A setting where it fails comes off the grid.

### Timeline sanity

- **Question.** Do the timelines do what the design pages say.
- **Run.** Timelines for every scenario on a thousand seeds, at every setting the noise grid tries. On each, the Scout rule plays with one point on every other channel and never moves off the leader, so every channel gets its roughest reading every round.
- **Measure.**
  - **Below zero.** At every setting, the share of channel rounds with a level below 0, and the share of runs where that Scout rule gets a reading below 0. Neither is clipped, and a reading below 0 is a real loss, as a bet is paid its reading. The default ladder is set so that none shows, see [each round](../design/mechanics.md#each-round).
  - **Pinning.** The Discerning baseline's output minus the Complacent baseline's, in level points, at each setting. It should be the same across the grid, see [difficulty](../design/mechanics.md#difficulty).
  - **Twin timelines.** The One shock and Down switch timelines of one seed are identical until onset, and the Up switch and No change timelines are identical on every channel but the sleeper. The Switch then shock timeline matches Down switch until the shock, and the Up switch then down switch timeline matches Up switch until the fall, on seeds where the Up switch sleeper does not stop short. These are tests in the engine suite, not decisions.
  - **Sparklines.** The leader's median level in each round of each scenario, plotted beside its sparkline in [scenarios](../design/scenarios.md#scenarios-we-test).
- **Decide.** If any run shows a reading below 0 at the proof of concept setting, the base ladder moves up, which is where the ladder ranges are decided. It moves up too if a noisier setting shows one in more than one run in a hundred. If pinning drifts, events are not pinned in level points. A sparkline that does not look like the leader's median levels is redrawn.

## Noise grid

Noise is the difficulty knob, and [signal to noise](../design/mechanics.md#difficulty) is its axis: the switch size in level points over the weather's SD per round. The full study plays a fixed grid of settings and reads the [noise threshold](../design/scoring.md#noise-threshold) off it.

- **Question.** Which settings make the grid.
- **Run.** The fixed [baselines](../design/baselines.md) in the One shock and Down switch scenarios, with events pinned in level points, at five or so settings of the own-weather scale. Persistence and the shared-factor scale hold at the values [Streaks](#streaks) and [The tell](#the-tell) chose.
- **Measure.** The hedge rule baseline's scenario scores at each setting, and whether the [baseline order](#baseline-order) holds throughout. The Scout rule baseline's curve is measured beside it, on Up switch timelines too, but the grid is set from the hedge rule alone. Timestral's curve on the grid is a [provider check](provider-checks.md#timestral-checks).
- **Decide.** A grid of three to five settings on which the hedge rule's curve runs from near 1 down to near the Complacent baseline, so the grid spans a full curve before any model plays. The proof of concept setting is one point on it. The grid is set from baselines alone, never from how flat the model scores look.
- **And the switch size the grid pins.** `size_points` is the signal in signal to noise, so it is fixed here with the grid: the range at which the hedge rule's curve crosses half way inside the grid, not at an end. The grid's settings mean nothing without it, see [noise threshold](../specs/analysis/scores.md#noise-threshold). The size it pins must leave the Down switch scenario at or above the [reachable gain](#reachable-gain) floor.

## Game length and switch round

- **Question.** How many rounds a run lasts, and in which round the shock or switch hits.
- **Run.** The fixed baselines in the One shock, Down switch and Up switch scenarios, at a few game lengths and switch rounds. Then the Slow drift scenario, whose fall can outlast the run, and the two-event scenarios, Shock then switch, Switch then shock and Up switch then down switch, which need room for both events. The [Stayer](../glossary.md#scoring) plays beside them in Up switch then down switch.
- **Measure.**
  - How far the Discerning baseline pulls ahead of the Complacent baseline after the switch, and how many rounds that takes: the rounds from onset until its output since onset is ahead and stays ahead. In the two-event scenarios, the same for each event's window.
  - **Unmoved at the end.** The round the hedge rule and the Scout rule first move, and the share of seeds where each never does. The hedge rule is counted where the leader falls, the Scout rule wherever the Discerning baseline moves. A share that does not fall as the run grows means the rule is missing the change, and length is not the cause.
  - **Rounds to spare.** The rounds left after the last event ends: a drift at its end level, a switch's ramp done, and a shock with an eighth of its depth left.
  - **Reachable gain and Bayesian gain percentage**, as [reachable gain](#reachable-gain) measures them, at every length, onset and gap.
  - **The squeeze.** The hedge rule's scenario score at each length. It climbs towards 1 as the run grows, though the rule plays no better, which is how much a longer run hides the rounds a player was late.
- **Decide.** The shortest run that passes all three:
  - Enough calm rounds before the change to set a habit.
  - Enough rounds after it for the Discerning baseline to pull clear of the Complacent baseline, which means the [reachable gain](#reachable-gain) pass lines hold. In the two-event scenarios, enough rounds between the events and after the second for both to show.
  - The hedge rule and the Scout rule are each unmoved at the end on fewer than one seed in twenty, or on no fewer in a longer run, and every event ends with rounds to spare.
- **One length for every scenario, if one passes.** If only the Slow drift and two-event scenarios need more, they get their own `rounds`, and the engine spec gains a rule that a longer timeline on a seed starts with the shorter one, so twin timelines still match.
- **Events per run and the gap between them** are decided here too. `gap` is the shortest range that leaves the first event rounds to spare before the second begins. Two events is the most a run of this length holds, so a hard variant with more waits for a longer run.
- **Never longer than that.** A longer run does not tighten an error bar, see [rejected](../design/mechanics.md#rejected), and it costs more, see [cost per run](provider-checks.md#cost-per-run).

## Reading roughness

A small bet gives a rough reading and a large bet a clean one, see [what the agent sees](../design/mechanics.md#what-the-agent-sees). That rewards an explore bet, and is how it works in the real world.

- **Question.** How fast the read noise shrinks as the bet grows.
- **Run.** The hedge rule baseline with 1, 2 and 5 points on the hedge and 1, 2 and 3 scout rounds, and the Scout rule baseline with 1, 2 and 5 points on every other channel, at a few strengths of read noise.
- **Measure.** Whether a bigger explore bet buys a better read of the switch, and how much an explore bet costs in output: the Complacent baseline's output minus the rule's on No change, which is the [explore cost](../glossary.md#scoring) in level points. The Scout rule shows the same for a rise, which is where an explore bet's size bites hardest, see [Up and down](#up-and-down).
- **Read noise is paid as well as seen.** A larger k adds luck to every output, with an SD of k ÷ 10 a round whatever the split. On a full bet that is well under the weather, so read noise mostly prices explore bets, see [what the agent sees](../design/mechanics.md#what-the-agent-sees).
- **Decide.** One strength, where an explore bet is worth its cost but no explore bet tells the whole story. And at that strength the hedge rule's `explore` and `scout_rounds`: the cheapest pair that still moves to the best channel as often as a larger one. A [provider check](provider-checks.md#timestral-checks) confirms it with Timestral top pick with explore bets.
- **Then Timeline sanity again**, at the chosen strength. A stronger read noise puts far more readings below 0 than rougher weather does, so the ladder is checked against the strength the study will play, see [Timeline sanity](#timeline-sanity).

## Up and down

A switch comes in three kinds, see [events](../design/mechanics.md#events): the leader falls, the leader falls and a sleeper rises, or only a sleeper rises. The first two are drawn per seed in the Down switch scenario, the third is the Up switch scenario.

- **Question.** How a rise compares with a fall for the baselines, how often the Down switch scenario draws a sleeper, and whether an explore bet can read a rise.
- **Run.** A thousand Down switch and Up switch timelines, plus No change timelines, at the proof of concept setting, with the Uniform, Discerning, Complacent, hedge rule and Scout rule baselines. The Scout rule plays at `s` of 1, 2 and 5. The rise size is swept at three ranges, as it sets the Up switch scenario's reachable gain.
- **Measure.**
  - **Sleeper share.** How many Down switch timelines draw a sleeper.
  - **Reachable gain.** The Discerning baseline's output minus the Complacent baseline's in level points, and as a share of the gap to the Uniform baseline, on fall-only, fall-with-riser and rise-only timelines at each rise size.
  - **Reading a rise.** The Scout rule's scenario score on Up switch at each `s`, and the round it moves. Its false moves and its cost in output on No change.
  - **Short seeds.** The Scout rule's moves on the Up switch seeds where the sleeper stops short, which is the price of moving on a near tie.
- **Decide.** The sleeper share and the rise size in level points, so the three kinds offer a comparable reachable gain, and the Up switch scenario clears the [reachable gain](#reachable-gain) floor. And whether a one-point explore bet reads the rise at the read noise [reading roughness](#reading-roughness) chose. If the Scout rule at `s` of 1 cannot find the sleeper by the end of the run, read noise is too high for the Up switch scenario to be fair, and reading roughness is revisited. And the Scout rule's `s`, from its Up switch score and its No change cost at each. And the short share of Up switch seeds, and the sleeper's end level on them, as a band between the runner-up and the leader, so that an explore bet sees a real move and the Scout rule does not move on a near tie.

## Bayesian frontier

Picks the Bayesian baseline's prior and rule, and says how much of the gap to the Discerning baseline no reader can close. The design is in [the Bayesian frontier](../design/baselines.md#the-bayesian-frontier) and the player in the [bayesian spec](../specs/baselines/bayesian.md).

- **Question.** Which hazard and forecast rule make the best reader of the engine's family, and how far below the Discerning baseline the best one sits.
- **Run.** Three players of the family's thirty: `Bayesian(hazard, rule)` at the two ends of `HAZARDS` and at the default, all three at the `odds` rule. Ten public seeds of every scenario at the proof of concept setting, with the Uniform, Discerning, Complacent, hedge rule and Scout rule baselines on the same seeds.
- **A coarse read, on purpose.** Thirty players on a thousand seeds is 240,000 runs and hours of one core, and every knob the pilot moves would run them again. Three players on ten seeds take seconds, so the frontier is read after every knob move. Five seeds pick and five report, so trust a pick only when the players sit well apart. Which three and how many seeds are two constants in the cell, see the [pilot spec](../specs/harness/pilot.md#bayesian-frontier).
- **Measure.**
  - Pooled scenario score per player and scenario, and each player's headline.
  - The two planes: No change against Down switch, and No change against Up switch, one point per player, the hedge rule, Scout rule and Complacent baselines drawn in them, and the upper envelope.
  - The best headline on the lower half of the seeds, and that player's headline and scenario scores on the upper half, so the pick carries no lucky-draw bonus.
  - Irreducible lag: one minus that player's Down switch score on the upper half.
- **Decide.** The `hazard` of the best player becomes the Bayesian baseline's default, and its `rule` stays `odds`, the one rule the cell plays. The irreducible lag is reported beside every Down switch bar. Whether the Bayesian baseline joins the scorer's marks is decided here too, see the [scorer](../specs/harness/scorer.md#not-decided). If no player beats the hedge rule on Down switch, the cell plays more of the family first. If none of the thirty does, the family is too narrow and `HAZARDS` or the rules widen, which is a spec change, not a knob.

## Baseline order

- **Question.** Do the fixed baselines land in the order we expect.
- **Run.** Every [fixed baseline](../design/baselines.md#fixed-baselines) in every scenario.
- **Measure.** Their scores, against these orders:
  - **Down switch scenario:** Perfect > Discerning > hedge rule > Complacent > Uniform.
  - **Up switch scenario:** Perfect > Discerning > Scout rule > Complacent ≥ hedge rule > Uniform. The order is of pooled scores. The leader never falls here, so the hedge rule sits with the Complacent baseline minus its explore bet, less any false alarm on weather. On a seed where a false alarm finds the sleeper it lands above, see [rules](../specs/baselines/rules.md#hedge-rule). On the seeds where the sleeper stops short, Complacent ≈ Discerning ≈ hedge rule ≥ Scout rule, and report how far the Scout rule falls below.
  - **No change scenario:** Complacent ≈ Discerning ≈ hedge rule, and report any player that lands above the Discerning baseline, which means it chased weather and won.
  - **Switch then shock scenario:** as Down switch. The hedge rises in the shock, so the hedge rule holds the new best.
  - **Up switch then down switch scenario:** as Up switch. The Scout rule keeps scouting after a move, so it sees the sleeper fall and the leader hold.
  - **The Bayesian baseline at its defaults:** report where it lands in every order above. On Down switch it should sit between the Discerning baseline and the hedge rule, as it reads the same evidence with a calibrated prior, and on No change at or near the Complacent baseline.
- **Decide.** If the order breaks, the [noise](#noise-grid) is likely too high or a baseline is wrong. Fix it before any model runs. Where Timestral lands is a [provider check](provider-checks.md#timestral-checks).

## Reachable gain

Says whether moving is worth enough for a score to tell a player that reads a change from one that never moves. At the first defaults it is not: never moving scored 0.84 on the headline and the Bayesian baseline 0.93, see [TODO](../../TODO.md). The words are in the [glossary](../glossary.md#scoring).

- **Question.** In every scenario with a switch or drift, is moving worth enough points, and can a [blind baseline](../glossary.md#the-study) earn most of them.
- **Run.** Nothing of its own. It reads the [baseline order](#baseline-order) run, which plays every fixed baseline in every scenario, and the Stayer in Up switch then down switch.
- **Measure.** Pooled over seeds, in the six scenarios with a switch or drift:
  - **Reachable gain.** The Discerning baseline's score minus the Complacent baseline's.
  - **Bayesian gain.** The Bayesian baseline's score minus the Complacent baseline's.
  - **Bayesian gain percentage.** The Bayesian gain over the reachable gain.
  - **Explore cost.** One minus each blind baseline's No change score, so the price of exploring sits beside the gain it buys.
  - **In the Up switch then down switch scenario** the Stayer stands in for the Complacent baseline in all three gains. The Complacent baseline never leaves the leader, which is the right call once the change undoes itself, so it is no yardstick there. Also report the share of seeds on which the Bayesian baseline moves off the leader at all.
- **Decide.** No model plays until these hold in all six scenarios:
  - A reachable gain of at least 0.3.
  - A Bayesian gain percentage of at least 50%.
  - In the Up switch then down switch scenario, the Bayesian baseline moves on at least half the seeds. Under half, the rise is not worth moving for, so Recall is never tested.
- **If a line fails**, move one knob at a time in this order, and rerun the check that owns it:

  | Order | Knob | Owning check | What it costs |
  |---|---|---|---|
  | 1 | `onset` earlier, `gap` | [Game length](#game-length-and-switch-round) | Fewer calm rounds to set a habit |
  | 2 | `size_sigmas`, `rise_sigmas`, the drift's size | [Noise grid](#noise-grid), [Up and down](#up-and-down), [Game length](#game-length-and-switch-round) | A louder change, so the noise grid must stretch to noisier settings |
  | 3 | `rounds` longer | [Game length](#game-length-and-switch-round) | Tokens, and [the squeeze](#game-length-and-switch-round) |
  | 4 | `field_base` higher | [Up and down](#up-and-down) | A smaller gap, so luck weighs more |

- **A scenario that passes at no setting** needs a design change, not a knob.
