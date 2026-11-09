# Mechanics

How the game engine pays out, where each channel's level comes from, and what the agent gets to see. How the agent sends its split is on the [interface](interface.md) page. Words are in the [glossary](../glossary.md).

## Payout

- **Linear.** Output is the sum over channels of share times level. Point 70 on a channel pays the same as point 1.
- **So the oracle goes all in** on the channel with the highest level. A split across channels only ever means doubt or a look. See [scoring](scoring.md).
- **Output and levels are reported to one decimal place.**

## Generator

The generator turns a scenario and a seed into a **tape**: the true level of every channel in every round. Levels run 0 to 100. Every run on a seed replays the same tape, and the tapes of public seeds are published with the engine. Held-out seeds' tapes are not, see [contamination](../harness/contamination.md#two-seed-sets).

### Each round

    level = base level + own weather + loading × shared factor, clipped to 0 to 100

| Part | What it is | Set by |
|---|---|---|
| Base level | The channel's mean when nothing is happening | The ladder below, drawn per seed |
| Own weather | The channel's wobble. It has persistence, so a bad stretch fades rather than stops | Scale and persistence, per scenario |
| Shared factor | One hidden series every channel loads on. Good and bad weeks for everyone | Scale per scenario, persistence as own weather |
| Loading | How much the channel moves with the shared factor. Uneven, drawn per seed from about 0.3 to 1. One channel draws a negative loading and is the **hedge** | Range per edition |

- **Persistence is why a bad month proves little.** At 0.8 a bad stretch is half gone after three rounds, so three poor rounds in a row are ordinary. With no persistence, three poor rounds are strong evidence and the only hard part is the scale.
- **The hedge rises when everything else falls**, like gold in a downturn. Its base level is low enough that it never pays more than the leader, even mid-shock. It is a clue, not a destination.
- **Base levels sit mid-range**, so clipping at 0 or 100 is rare.

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
| Switch | A base level | The leader falls. Sometimes a **sleeper** in the field also rises past the leader's old level, and its loading is redrawn so it stops moving with its old group | Size in sigmas, onset, ramp of 1 to 5 rounds, which channel falls, whether a sleeper rises and which |
| Drift | A base level, slowly | As a switch, over many more rounds | Slope in sigmas per round, length, profile: linear or logistic |

- **Why a shock and a switch look different.** A shock moves every channel at once, each by its loading, and lifts the hedge. A switch moves one channel and leaves the factor alone. A look at any unfunded channel tells them apart. A look at the hedge tells them apart fastest.
- **Why a switch sometimes has a riser.** When only the leader falls, the destination is the runner-up and the test is spotting the fall. When a sleeper rises, the runner-up is a decoy and the agent has to look to find the new best. Mixing the two per seed means a model cannot learn that a fall always comes with a riser, or never does.
- **The old plan keeps paying.** A switch leaves the leader well above zero. Staying put costs a little every round, not everything at once. That is Grove's case, not Blockbuster's.

### Stringing events

- **A minimum gap** between events, set per scenario. Events may still overlap, so a shock can land mid-drift.
- **No two alike.** Each event redraws its numbers and lands on different weather, and a second switch hits a different channel. A tape is rejected if consecutive events of the same kind differ in fewer than two draws.
- **A hard variant strings more.** More shocks before the switch, or a longer drift. Length and count come from the pilot, see [TODO](../../TODO.md#pilot).

### Difficulty

Three dials, all set per scenario: own-weather scale, persistence and shared-factor scale. With low noise one reading settles whether a dip is a shock or a switch. With high noise it takes many rounds. Raise a dial to keep the test from saturating.

### Hard-variant knobs

Off by default. Each one closes a tell a model could learn.

| Knob | What it does |
|---|---|
| Hedge may overtake | In a deep shock the hedge pays more than the leader for a few rounds, so holding costs real output |
| One-channel shock | A shock that hits the leader only, so a look at the field says nothing about scope |

## What the agent sees

- **Only the channels it funded.** A share of 0 shows a blank in the record, not a 0.
- **A small share gives a rough reading, a large share a clean one.** Read noise shrinks as spend rises, the way customers from a small spend are a small count. The skin explains it, so there is no rule to tell the agent.
- **Read noise is normal with SD k ÷ √bet**, so a bet of 4 is twice as rough as a bet of 16. The pilot sets k, see [reading roughness](../pilot/checks.md#reading-roughness).
- **Why.** A look costs something, so paranoia has a price. You know a market by being in it.

## Defaults

- **Every number on this page is a field on `ScenarioConfig`** in the engine, with a default, so the engine is built from this page alone. A hash of the config goes in every log, see [layout](../harness/layout.md).
- **A run is 40 rounds by default.** The pilot moves this and the other defaults, see [decisions](../pilot/decisions.md).

## Rejected

| Option | Why not |
|---|---|
| Concave payout | The oracle splits too, so a split stops reading as belief. The agent has to be told the curve and do the maths, and a model bad at the maths looks like a model full of doubt |
| A sigma per channel | With a fixed budget that does not compound and a linear payout, sigma never changes which channel is best. It adds risk maths the score never rewards |
| Every channel visible | A look is free, so a calm agent and a paranoid one only differ by jumpiness. A forecaster then wins by reading series, which is a different study |
| A hand-written table of means plus independent noise | Streaks cannot happen by chance, so three bad rounds prove too much. Every repeat of a shock is identical. No market-wide weeks, so a look never says "everyone is down" |
| Two or three factors, with events on loadings | Most realistic, but scenarios become emergent and hard to match to the sparkline, baselines need a factor filter, and it is easy to build a world no model can read. A hard variant once one factor saturates |
| Shocks that hit one channel only | A look cannot tell a shock from a switch, so paying to see loses its point. Kept as a hard-variant knob |
