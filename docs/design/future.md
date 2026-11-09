# Future work

## How the world changes

- **Habituation.** Repeated shocks, and repeated switches. Does an agent get calmer with each shock or jumpier, and does it treat the third switch like the first? See [scenarios we skip](scenarios.md#scenarios-we-skip).
- **Changes that recur.** In Gama et al.'s survey of concept drift (ACM Computing Surveys 46(4): 44, 2014, [doi:10.1145/2523813](https://doi.org/10.1145/2523813)), the Down switch scenario is sudden drift and the Slow drift scenario is incremental. A change that reverses once is the Up switch then down switch scenario, which is what Hopin and Peloton bet on. A boom that passes, and a climate that comes and goes more than once, are the gap, see [scenarios we skip](scenarios.md#scenarios-we-skip).
- **Size and ramp.** Each switch draws its size and a ramp of 1 to 5 rounds per seed, see [events](mechanics.md#events). Holding one fixed and stepping the other shows where each model starts to miss.
- **Changes to structure, not level.** A loading that flips, so a channel stops moving with the shared factor. Weather that widens with no level change, the Variance shift scenario we skip. A reading credited to the wrong channel. An agent that only watches levels can't see any of them. Two or three factors is already a [hard variant](mechanics.md#rejected) once one saturates.
- **A change that reacts to the agent (relexivity).** Like a trading edge that fades once everyone copies it. The headline rules it out, see [limits](limits.md). As a study, a timid agent would score well, and the Discerning baseline would have to plan ahead, as the climate would depend on the agent's play.
- **Add additional information sources.** A skin could show something like ambient temperature beside a manufacturing plant.
- **What a round stands for.** "Week" says slow and "minute" says fast, so the skin's word sets a model's prior on how often the world moves. Same engine and seeds, with only the word changed.

## What the agent knows before it starts

- **A longer calm before the change.** A longer run of success should make anyone slower to doubt. The pilot sets one [game length and switch round](../pilot/engine-checks.md#game-length-and-switch-round). Stepping the calm stretch shows how each model's lateness grows with it.
- **A record someone else played.** The record starts empty, see [tools](interface.md#tools), and the [warm-up cell](../../TODO.md#pilot) pre-fills it once. Varying its length, and how often it looks, shows whether a model copies the habits of a past it only read.
- **An inherited plan.** A written plan beside the record, in a voice from flat to "this split has served the client for four years". It shows what a confident author costs. See [ideas we parked](../prior/README.md#ideas-we-parked).
- **Several short runs in a row.** Fresh seeds each time, with the world changing in only a few. It is Epoch's [EBR-bench](../prior/themes.md) set-up, with a lesson that can go stale between runs.

## How the agent can act

- **Channels that pay later.** Every channel pays in the round it is bet on. A channel that builds a stock and pays out rounds later, like brand, asks whether an agent allows for lag before judging a dip.
- **A price on switching.** A one-off fee, rejected for the headline as it leaks into every trait, see [interface](interface.md#rejected). A look stays cheap, so an agent should look as soon as it doubts. But the dearer the switch, the more evidence it should wait for. Does its switching follow the price while its looking doesn't? The headline's only lever here is the [inertia](scoring.md#extension-inertia) cap.
- **A look that isn't a bet.** A `look(channel)` tool that reads one channel for a fee. Today a small bet is the look, so a split can mean doubt or a look and the log can't tell which. A tool would split them, at the risk of hinting a look is worth taking.
- **A compounding budget.** Output feeds the next round's budget, so late mistakes cost more. Rejected for the headline, as it tests bet sizing and one ruined seed swamps the pool, see [interface](interface.md#rejected).
- **Ask how sure it is.** Each round, before it bets, ask how likely its plan is out of date, and leave the answer out of later prompts. Rejected for the headline as it tells the agent what the question is. As a study, it shows whether an agent can suspect and still not act, the way Kodak built the first digital camera and sat on it.

## Whether it holds outside our game

- **One real task with a stale handoff note.** A coding task whose notes say the payments client is on v1 and the mocks match, when the repo has moved on and the old path still passes but does worse. Two or three models, a few runs each, transcripts read by hand, and the ranking compared with the game's. The most direct check on "a game, not a job" in [limits](limits.md).
- **Stakes in the story.** Skins with low and high stakes on the same engine and seeds. A controlled form of [skin sensitivity](scoring.md#spread).
- **A second game.** A controller with feedback ([interface](interface.md#rejected)), pricing by segment, or a supplier split. Tests whether the skill carries over, or a model is just good at this one game.
- **A human baseline.** So a score could read as "catches what a typical person catches". [Limits](limits.md) says why the headline doesn't need one.
- **Other benchmarks.** The "What we'd check" column in [themes](../prior/themes.md) lists them.
