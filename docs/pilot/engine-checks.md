# Engine checks

The first half of the pilot, a short run before the full study to settle the knobs.

- **These run on tapes and the fixed baselines.** No model and no network, so thousands of seeds cost nothing.
- **Run them first.** The [provider checks](provider-checks.md) need a model and cost tokens, so they wait until these pass.
- **Every knob here is set from baselines**, never from how a model scores.

## Weather

The three weather dials are set per release, see [difficulty](../design/mechanics.md#difficulty). The own-weather scale is the axis of the [noise grid](#noise-grid). These checks pick the other two, persistence and the shared-factor scale, and check the tapes they make.

- **Streaks and The tell run first**, at a starting own-weather scale. The noise grid then picks the proof of concept setting around it.
- **Luck on offer and Tape sanity** check every setting the noise grid tries.

### Streaks

Picks persistence.

- **Question.** How long a bad stretch lasts by chance, against how fast a real switch shows.
- **Run.** A thousand No change and One switch tapes at persistence 0, 0.5, 0.8 and 0.9.
- **Measure.**
  - On the No change tapes, the longest run of rounds where the leader's level sits below the runner-up's.
  - On the One switch tapes, the rounds from onset until the leader sits below the runner-up and stays there.
- **Decide.** A value where a three round streak of the leader below the runner-up is ordinary on No change, say in one tape in five, but the switch still separates within a handful of rounds.

### The tell

Picks the shared-factor scale. The tell is the hedge rising while the field falls, which marks a shock rather than a switch.

- **Question.** How often the hedge tells a shock from a switch.
- **Run.** The hedge rule baseline on One shock and One switch tapes, plus No change tapes, at a few shared-factor scales.
- **Measure.**
  - **Hit rate.** On One shock, how often the hedge rule's reading of the hedge rises above its average before the shock while the shock is on.
  - **False tell rate.** On One switch, how often the hedge reading rises anyway after onset, so the hedge rule holds when it should move.
  - **Field moving together.** On No change, how often every channel but the hedge moves more than one weather SD the same way in one round. Too often and calm weeks look like shocks.
- **Decide.** A scale where the tell is right on about nine shocks in ten and false on under one switch in ten. If no scale does both, the [loading range](../design/mechanics.md#each-round) is wrong, not the weather.

### Luck on offer

- **Question.** How much weather luck no reader could see sits on top of the gap the score divides.
- **Run.** The Perfect, Discerning and Uniform baselines on One switch tapes, at every setting the noise grid tries.
- **Measure.** (Perfect − Discerning) ÷ (Discerning − Uniform), pooled over seeds.
- **Decide.** It stays under about 0.5 at every setting. Above that, luck rivals the prize and a lucky run lands well above 1. A setting where it fails comes off the grid.

### Tape sanity

- **Question.** Do the tapes do what the design pages say.
- **Run.** Tapes for every scenario on a thousand seeds, at every setting the noise grid tries.
- **Measure.**
  - **Below zero.** The share of channel rounds with a level below 0 at the noisiest setting. Levels are not clipped, see [generator](../design/mechanics.md#generator).
  - **Pinning.** The Discerning baseline's output minus the Complacent baseline's, in level points, at each setting. It should be the same across the grid, see [difficulty](../design/mechanics.md#difficulty).
  - **Twin tapes.** The One shock and One switch tapes of one seed are identical until onset. This is a test in the engine suite, not a decision.
  - **Sparklines.** The median tape of the leader in each scenario, plotted beside its sparkline in [scenarios](../design/scenarios.md#scenarios-we-test).
- **Decide.** If levels below 0 are common, the base ladder moves up. If pinning drifts, events are not pinned in level points. A sparkline that does not look like its median tape is redrawn.

## Noise grid

Noise is the difficulty knob, and [signal to noise](../design/mechanics.md#difficulty) is its axis: the switch size in level points over the weather's SD per round. The full study plays a fixed grid of settings and reads the [noise threshold](../design/scoring.md#noise-threshold) off it.

- **Question.** Which settings make the grid.
- **Run.** The fixed [baselines](../design/baselines.md) in the One shock and One switch scenarios, with events pinned in level points, at five or so settings of the own-weather scale. Persistence and the shared-factor scale hold at the values [Streaks](#streaks) and [The tell](#the-tell) chose.
- **Measure.** The hedge rule baseline's scenario scores at each setting, and whether the [baseline order](#baseline-order) holds throughout. Timestral's curve on the grid is a [provider check](provider-checks.md#timestral-checks).
- **Decide.** A grid of three to five settings on which the hedge rule's curve runs from near 1 down to near the Complacent baseline, so the grid spans a full curve before any model plays. The proof of concept setting is one point on it. The grid is set from baselines alone, never from how flat the model scores look.

## Game length and switch round

- **Question.** How many rounds a run lasts, and in which round the shock or switch hits.
- **Run.** The fixed baselines in the One shock and One switch scenarios, at a few game lengths and switch rounds.
- **Measure.** How far the Discerning baseline pulls ahead of the Complacent baseline after the switch, and how many rounds that takes.
- **Decide.** Enough calm rounds before the change to set a habit, and enough rounds after it for the Discerning baseline to pull clear of the Complacent baseline. Longer runs cost more, see [cost per run](provider-checks.md#cost-per-run).

## Reading roughness

A small bet gives a rough reading and a large bet a clean one, see [what the agent sees](../design/mechanics.md#what-the-agent-sees). That rewards a look, and is how it works in the real world.

- **Question.** How fast the read noise shrinks as the bet grows.
- **Run.** The hedge rule baseline with 1, 2 and 5 points on the hedge, at a few strengths of read noise.
- **Measure.** Whether a bigger look buys a better read of the switch, and how much a look costs in output.
- **Decide.** One strength, where a look is worth its cost but no look tells the whole story. A [provider check](provider-checks.md#timestral-checks) confirms it with Timestral top pick with looks.

## Baseline order

- **Question.** Do the fixed baselines land in the order we expect.
- **Run.** Every [fixed baseline](../design/baselines.md#fixed-baselines) in the One switch and No change scenarios.
- **Measure.** Their scores, against these orders:
  - **One switch scenario:** Perfect > Discerning > hedge rule > Complacent > Uniform.
  - **No change scenario:** Complacent ≈ Discerning ≈ hedge rule, and report any player that lands above the Discerning baseline, which means it chased weather and won.
- **Decide.** If the order breaks, the [noise](#noise-grid) is likely too high or a baseline is wrong. Fix it before any model runs. Where Timestral lands is a [provider check](provider-checks.md#timestral-checks).
