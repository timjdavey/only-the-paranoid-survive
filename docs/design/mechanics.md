# Mechanics

How the game engine pays out, where each channel's level comes from, and what the agent gets to see. How the agent sends its split is on the [interface](interface.md) page. Words are in the [glossary](../glossary.md).

## Payout

- **Linear.** Output is the sum over channels of share times level. Point 70 on a channel pays the same as point 1.
- **So the Discerning baseline goes all in** on the channel with the highest base level. A split across channels only ever means doubt or an explore bet. See [scoring](scoring.md).
- **Output and levels are reported to one decimal place.**

## Generator

The generator turns a scenario and a seed into a **timeline**: the ground truth of the run, every channel's level in every round. Levels are not clipped, so one can go below 0 in a deep shock. Every run on a seed replays the same timeline, and anyone can regenerate a public seed's timeline from the engine. A timeline is never written down: a held-out seed's timeline is as secret as the seed, see [contamination](../harness/contamination.md#two-seed-sets).

### Each round

    level = base level + own weather + loading × shared factor

| Part | What it is | Set by |
|---|---|---|
| Base level | The channel's mean when nothing is happening | The ladder below, drawn per seed |
| Own weather | The channel's wobble. It has persistence, so a bad stretch fades rather than stops | Scale and persistence, per release |
| Shared factor | One hidden series every channel loads on. Good and bad weeks for everyone | Scale per release, persistence as own weather |
| Loading | How much the channel moves with the shared factor. Uneven, drawn per seed from about 0.3 to 1. One channel draws a negative loading and is the **hedge** | Range per release |

- **Persistence is why a bad month proves little.** At 0.8 a bad stretch is half gone after three rounds, so three poor rounds in a row are ordinary. With no persistence, three poor rounds are strong evidence and the only hard part is the scale.
- **The hedge rises when everything else falls**, like gold in a downturn. Its base level is low enough that it never pays more than the leader, even mid-shock. It is a clue, not a destination.
- **Base levels sit mid-range**, so a level rarely goes below 0. Nothing breaks when it does: the score is a share of a gap and the headline a plain mean, so a negative round is just a bad round. Clipping was only there for the geometric mean, which is gone, see [scoring](scoring.md#why-a-pool-within-and-a-plain-mean-across).
- **One seed, twin timelines.** The ladder, the weather, the loadings and the onset round are drawn from the seed before the scenario's events are applied. So seed *i* gives every scenario the same world, and the One shock and Down switch timelines match until the event begins, see [seeds](scoring.md#seeds).

### The ladder

- **One leader**, the channel the agent should be on at the start.
- **One runner-up**, a few sigmas below. The obvious fallback.
- **A field** of eight below that, the hedge lowest.
- **Drawn per seed** within ranges, so no two seeds share a ladder.

### Events

A scenario is a list of events. Each event has a shape, and redraws its own numbers per seed.

| Shape | What it edits | Who moves | Drawn per seed |
|---|---|---|---|
| Shock | An impulse into the shared factor that decays | Every channel by its loading, so most fall and the hedge rises | Depth in sigmas, onset round, half-life, profile: sharp fall and slow climb, or slow slide and quick rebound |
| Switch | A base level | The leader falls below the runner-up, a **sleeper** in the field rises past every other channel, or both. The sleeper's loading is redrawn so it stops moving with its old group. Where the scenario says so, a sleeper rises short of the leader instead, or an earlier switch is undone | How far below the runner-up the leader ends and how far above the rest the sleeper ends, both in sigmas, onset, ramp of 1 to 5 rounds, which channel falls, which sleeper rises, whether a rise stops short and where, and the direction where the scenario leaves it open |
| Drift | A base level, slowly | As a switch, over many more rounds | How far below the runner-up the leader ends, in sigmas, length, profile: linear or logistic |

- **Why a shock and a switch look different.** A shock moves every channel at once, each by its loading, and lifts the hedge. A switch moves one channel and leaves the factor alone. An explore bet on any unfunded channel tells them apart. An explore bet on the hedge tells them apart fastest.
- **Why a switch comes in three kinds.** When only the leader falls, the destination is the runner-up and the test is spotting the fall. When the leader falls and a sleeper rises, the runner-up is a decoy and the agent has to explore to find the new best. Sizes are measured from the runner-up, so a fall always changes who pays best and a riser always ends on top, unless the scenario has it stop short. When only a sleeper rises, nothing in the agent's record moves and the test is whether it was exploring at all. The [Down switch scenario](scenarios.md#scenarios-we-test) draws the first two per seed, so a model cannot learn that a fall always comes with a riser, or never does. The Up switch scenario pins the third.
- **The old plan keeps paying.** A switch leaves the leader well above zero. Staying put costs a little every round, not everything at once. That is Grove's case, not Blockbuster's.

### Stringing events

- **A minimum gap** between events, set per scenario. Events may still overlap, so a shock can land mid-drift.
- **No two alike.** Each event redraws its numbers and lands on different weather, and a second switch hits a different channel unless the scenario says it undoes the first, as in the Up switch then down switch scenario. A timeline is rejected if consecutive events of the same kind differ in fewer than two draws.
- **A hard variant strings more, or stretches.** More shocks before the switch, a longer drift, or a sleeper's rise spread over many rounds, which is the Up drift we [skip](scenarios.md#scenarios-we-skip). Length and count come from the pilot, see [TODO](../../TODO.md#pilot).

### Difficulty

- **Signal to noise is the axis.** The size of a switch in level points over the weather's SD per round. With a high ratio one reading settles whether a dip is a shock or a switch. With a low one it takes many rounds.
- **Three dials move it**, all set per release and picked in the [engine checks](../pilot/engine-checks.md#weather): own-weather scale, persistence and shared-factor scale. Every scenario shares them, so twin timelines keep the same weather. The own-weather scale is the axis the [noise grid](../pilot/engine-checks.md#noise-grid) turns. Persistence never moves within a release, as it changes what a bad stretch means.
- **On the grid, events are pinned in level points.** By default an event's size is drawn in sigmas, so a noisier world would also get a bigger switch and the prize would grow with the noise. On the grid the switch keeps its size in level points and only the weather grows, so the gain the Discerning baseline makes over the Complacent baseline is the same at every setting. A rise is pinned the same way, as the sleeper's end level above the leader's.
- **A harder release extends the grid** to lower signal to noise. It does not start a new chart, see [noise threshold](scoring.md#noise-threshold).

### Hard-variant knobs

Off by default. Each one closes a tell a model could learn.

| Knob | What it does |
|---|---|
| Hedge may overtake | In a deep shock the hedge pays more than the leader for a few rounds, so holding costs real output |
| One-channel shock | A shock that hits the leader only, as an impulse on its level that leaves its base level alone, so the climate does not move and an explore bet on the field says nothing about scope |

## What the agent sees

- **Only the channels it funded.** A share of 0 shows a blank in the record, not a 0.
- **A small share gives a rough reading, a large share a clean one.** Read noise shrinks as spend rises, the way customers from a small spend are a small count. The skin explains it, so there is no rule to tell the agent.
- **Read noise is normal with SD k ÷ √bet**, so a bet of 4 is twice as rough as a bet of 16. Readings are not clipped either, so a rough reading of a low channel can be negative. The pilot sets k, see [reading roughness](../pilot/engine-checks.md#reading-roughness).
- **Why.** An explore bet costs something, so paranoia has a price. You know a market by being in it.
- **Output is paid at the true levels, on purpose**, while each reading carries read noise. A business knows its revenue to the penny but only roughly which channel drove it.
  - **It adds little beyond the readings.** Summing the readings the way output is summed already gives output to within an SD of k ÷ 10, whatever the split. So output is worth one clean reading of the agent's own mix, and nothing about any one channel.
  - **It can't name the shape.** A dip in output says the mix fell, not why. Uneven hidden loadings, the hedge and sleepers mean a dip's size varies per seed, so telling a shock from a switch still takes an explore bet, see [events](#events).
  - **It can't see a rise.** A sleeper rising on a channel with a bet of 0 changes nothing the agent sees. The Up switch scenario is invisible without an explore bet.
  - **It can't sharpen a small explore bet.** With 99 on the leader and 1 on the hedge, output minus the leader's reading gives the hedge with an SD of about 10k, against k for the explore bet itself.
  - **This is why the weather scale, not read noise, is the grid's dial.**

## Defaults

- **Every number on this page is a field on `ScenarioConfig`** in the engine, with a default, so the engine is built from this page alone. A hash of the config goes in every log, see [layout](../harness/layout.md).
- **A run is 40 rounds by default.** The pilot moves this and the other defaults, see [decisions](../pilot/decisions.md).
- **A run is as short as it can be without ending before the hedge rule and the Scout rule have moved.** The [game length](../pilot/engine-checks.md#game-length-and-switch-round) check finds that length. Tighter error bars come from seeds, never from rounds, see [rejected](#rejected).
- **A release freezes them.** The defaults, the noise grid and the held-out seeds together are one release, see [contamination](../harness/contamination.md#who-can-see-them). Releases share the signal to noise axis, so scores from different releases sit on one chart.

## Rejected

| Option | Why not |
|---|---|
| Concave payout | The Perfect baseline splits too, so a split stops reading as belief. The agent has to be told the curve and do the maths, and a model bad at the maths looks like a model full of doubt |
| A sigma per channel | With a fixed budget that does not compound and a linear payout, sigma never changes which channel is best. It adds risk maths the score never rewards |
| Every channel visible | An explore bet is free, so a calm agent and a paranoid one only differ by jumpiness. A forecaster then wins by reading series, which is a different study |
| A hand-written table of means plus independent noise | Streaks cannot happen by chance, so three bad rounds prove too much. Every repeat of a shock is identical. No market-wide weeks, so an explore bet never says "everyone is down" |
| Two or three factors, with events on loadings | Most realistic, but scenarios become emergent and hard to match to the sparkline, baselines need a factor filter, and it is easy to build a world no model can read. A hard variant once one factor saturates |
| Shocks that hit one channel only | An explore bet cannot tell a shock from a switch, so paying to see loses its point. Kept as a hard-variant knob |
| A longer run to tighten the error bars | Once a model has moved, each extra round pays it and the Discerning baseline the same. So the gap between a model that moved in 3 rounds and one that took 8 shrinks as the run grows, and the error bar shrinks with it, and the two are no easier to tell apart. Only a model that never moves falls further behind. Cost grows at least as fast as the run, and input tokens with the square of its length, as every round resends the record. Doubling the seeds narrows every bar for twice the cost, see [spread](scoring.md#spread) |
| Output summed from the noisy readings | It only adds one noise term with an SD of k ÷ 10, which changes little, see [what the agent sees](#what-the-agent-sees). And it breaks the skin, since no business estimates its own revenue |
| A noise setting drawn per seed | It hides one number from a model that can already train across the whole public grid, so it stops nothing, see [learning the game](../harness/contamination.md#what-it-does-not-stop). And it breaks the axis: the [noise threshold](scoring.md#noise-threshold) is read off fixed settings, releases join by sharing two of them, and [luck on offer](../pilot/engine-checks.md#luck-on-offer) is checked per setting |
