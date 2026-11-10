# Engine checks

The first half of the pilot, a short run before the full study to settle the knobs.

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
  - **Hit rate.** On One shock, how often the hedge rule's reading of the hedge rises above its average before the shock while the shock is on.
  - **False tell rate.** On Down switch, how often the hedge reading rises anyway after onset, so the hedge rule holds when it should move.
  - **Field moving together.** On No change, how often every channel but the hedge moves more than one weather SD the same way in one round. Too often and calm weeks look like shocks.
- **Decide.** A scale where the tell is right on about nine shocks in ten and false on under one switch in ten. If no scale does both, the [loading range](../design/mechanics.md#each-round) is wrong, not the weather.

### Luck on offer

- **Question.** How much weather luck no reader could see sits on top of the gap the score divides.
- **Run.** The Perfect, Discerning and Uniform baselines on Down switch timelines, at every setting the noise grid tries.
- **Measure.** (Perfect − Discerning) ÷ (Discerning − Uniform), pooled over seeds.
- **Decide.** It stays under about 0.5 at every setting. Above that, luck rivals the prize and a lucky run lands well above 1. A setting where it fails comes off the grid.

### Timeline sanity

- **Question.** Do the timelines do what the design pages say.
- **Run.** Timelines for every scenario on a thousand seeds, at every setting the noise grid tries.
- **Measure.**
  - **Below zero.** The share of channel rounds with a level below 0 at the noisiest setting. Levels are not clipped, see [generator](../design/mechanics.md#generator).
  - **Pinning.** The Discerning baseline's output minus the Complacent baseline's, in level points, at each setting. It should be the same across the grid, see [difficulty](../design/mechanics.md#difficulty).
  - **Twin timelines.** The One shock and Down switch timelines of one seed are identical until onset, and the Up switch and No change timelines are identical on every channel but the sleeper. The Switch then shock timeline matches Down switch until the shock, and the Up switch then down switch timeline matches Up switch until the fall, on seeds where the Up switch sleeper does not stop short. These are tests in the engine suite, not decisions.
  - **Sparklines.** The leader's median level in each round of each scenario, plotted beside its sparkline in [scenarios](../design/scenarios.md#scenarios-we-test).
- **Decide.** If levels below 0 are common, the base ladder moves up. If pinning drifts, events are not pinned in level points. A sparkline that does not look like the leader's median levels is redrawn.

## Noise grid

Noise is the difficulty knob, and [signal to noise](../design/mechanics.md#difficulty) is its axis: the switch size in level points over the weather's SD per round. The full study plays a fixed grid of settings and reads the [noise threshold](../design/scoring.md#noise-threshold) off it.

- **Question.** Which settings make the grid.
- **Run.** The fixed [baselines](../design/baselines.md) in the One shock and Down switch scenarios, with events pinned in level points, at five or so settings of the own-weather scale. Persistence and the shared-factor scale hold at the values [Streaks](#streaks) and [The tell](#the-tell) chose.
- **Measure.** The hedge rule baseline's scenario scores at each setting, and whether the [baseline order](#baseline-order) holds throughout. The Scout rule baseline's curve is measured beside it, on Up switch timelines too, but the grid is set from the hedge rule alone. Timestral's curve on the grid is a [provider check](provider-checks.md#timestral-checks).
- **Decide.** A grid of three to five settings on which the hedge rule's curve runs from near 1 down to near the Complacent baseline, so the grid spans a full curve before any model plays. The proof of concept setting is one point on it. The grid is set from baselines alone, never from how flat the model scores look.

## Game length and switch round

- **Question.** How many rounds a run lasts, and in which round the shock or switch hits.
- **Run.** The fixed baselines in the One shock and Down switch scenarios, at a few game lengths and switch rounds. Then the two-event scenarios, Shock then switch, Switch then shock and Up switch then down switch, which need room for both events.
- **Measure.** How far the Discerning baseline pulls ahead of the Complacent baseline after the switch, and how many rounds that takes. In the two-event scenarios, the same for each event's window.
- **Decide.** Enough calm rounds before the change to set a habit, and enough rounds after it for the Discerning baseline to pull clear of the Complacent baseline. In the two-event scenarios, enough rounds between the events and after the second for both to show. Longer runs cost more, see [cost per run](provider-checks.md#cost-per-run).

## Reading roughness

A small bet gives a rough reading and a large bet a clean one, see [what the agent sees](../design/mechanics.md#what-the-agent-sees). That rewards an explore bet, and is how it works in the real world.

- **Question.** How fast the read noise shrinks as the bet grows.
- **Run.** The hedge rule baseline with 1, 2 and 5 points on the hedge, and the Scout rule baseline with 1, 2 and 5 points on every other channel, at a few strengths of read noise.
- **Measure.** Whether a bigger explore bet buys a better read of the switch, and how much an explore bet costs in output. The Scout rule shows the same for a rise, which is where an explore bet's size bites hardest, see [Up and down](#up-and-down).
- **Output is exact,** so the agent always knows its own mix's level. Read noise only prices explore bets on single channels, see [what the agent sees](../design/mechanics.md#what-the-agent-sees).
- **Decide.** One strength, where an explore bet is worth its cost but no explore bet tells the whole story. A [provider check](provider-checks.md#timestral-checks) confirms it with Timestral top pick with explore bets.

## Up and down

A switch comes in three kinds, see [events](../design/mechanics.md#events): the leader falls, the leader falls and a sleeper rises, or only a sleeper rises. The first two are drawn per seed in the Down switch scenario, the third is the Up switch scenario.

- **Question.** How a rise compares with a fall for the baselines, how often the Down switch scenario draws a sleeper, and whether an explore bet can read a rise.
- **Run.** A thousand Down switch and Up switch timelines, plus No change timelines, at the proof of concept setting, with the Discerning, Complacent, hedge rule and Scout rule baselines. The Scout rule plays at `s` of 1, 2 and 5.
- **Measure.**
  - **Sleeper share.** How many Down switch timelines draw a sleeper.
  - **Prize on offer.** The Discerning baseline's output minus the Complacent baseline's, in level points, on fall-only, fall-with-riser and rise-only timelines.
  - **Reading a rise.** The Scout rule's scenario score on Up switch at each `s`, and the round it moves. Its false moves and its cost in output on No change.
  - **Short seeds.** The Scout rule's moves on the Up switch seeds where the sleeper stops short, which is the price of moving on a near tie.
- **Decide.** The sleeper share and the rise size in level points, so the three kinds put a comparable prize on offer. And whether a one-point explore bet reads the rise at the read noise [reading roughness](#reading-roughness) chose. If the Scout rule at `s` of 1 cannot find the sleeper by the end of the run, read noise is too high for the Up switch scenario to be fair, and reading roughness is revisited. And the short share of Up switch seeds, and the sleeper's end level on them, as a band between the runner-up and the leader, so that a looker sees a real move and the Scout rule does not move on a near tie.

## Bayesian frontier

Picks the Bayesian baseline's prior and rule, and says how much of the gap to the Discerning baseline no reader can close. The design is in [the Bayesian frontier](../design/baselines.md#the-bayesian-frontier) and the player in the [bayesian spec](../specs/baselines/bayesian.md).

- **Question.** Which hazard and forecast rule make the best reader of the engine's family, and how far below the Discerning baseline the best one sits.
- **Run.** Every `Bayesian(hazard, rule)` with `hazard` in `HAZARDS` and `rule` in `BAYESIAN_RULES`, 30 players, on 1000 public seeds of every scenario at the proof of concept setting, with the Uniform, Discerning, Complacent, hedge rule and Scout rule baselines on the same seeds.
- **Measure.**
  - Pooled scenario score per player and scenario, and each player's headline.
  - The two planes: No change against Down switch, and No change against Up switch, one point per player, the hedge rule, Scout rule and Complacent baselines drawn in them, and the upper envelope.
  - The best headline on seeds 0 to 499, and that player's headline and scenario scores on seeds 500 to 999, so the pick carries no lucky-draw bonus.
  - Irreducible lag: one minus that player's Down switch score on seeds 500 to 999.
- **Decide.** The `hazard` and `rule` of the best player become the Bayesian baseline's defaults. The irreducible lag is reported beside every Down switch bar. Whether the Bayesian baseline joins the scorer's marks is decided here too, see the [scorer](../specs/harness/scorer.md#not-decided). If no player beats the hedge rule on Down switch, the family is too narrow and `HAZARDS` or the rules widen, which is a spec change, not a knob.

## Baseline order

- **Question.** Do the fixed baselines land in the order we expect.
- **Run.** Every [fixed baseline](../design/baselines.md#fixed-baselines) in every scenario.
- **Measure.** Their scores, against these orders:
  - **Down switch scenario:** Perfect > Discerning > hedge rule > Complacent > Uniform.
  - **Up switch scenario:** Perfect > Discerning > Scout rule > Complacent ≥ hedge rule > Uniform. The hedge rule has no reason to move here, so it sits with the Complacent baseline minus its explore bet, less any false alarm on weather. On the seeds where the sleeper stops short, Complacent ≈ Discerning ≈ hedge rule ≥ Scout rule, and report how far the Scout rule falls below.
  - **No change scenario:** Complacent ≈ Discerning ≈ hedge rule, and report any player that lands above the Discerning baseline, which means it chased weather and won.
  - **Switch then shock scenario:** as Down switch. The hedge rises in the shock, so the hedge rule holds the new best.
  - **Up switch then down switch scenario:** as Up switch. The Scout rule keeps scouting after a move, so it sees the sleeper fall and the leader hold.
  - **The Bayesian baseline at its defaults:** report where it lands in every order above. On Down switch it should sit between the Discerning baseline and the hedge rule, as it reads the same evidence with a calibrated prior, and on No change at or near the Complacent baseline.
- **Decide.** If the order breaks, the [noise](#noise-grid) is likely too high or a baseline is wrong. Fix it before any model runs. Where Timestral lands is a [provider check](provider-checks.md#timestral-checks).
