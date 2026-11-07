# Scoring

## How we score

- **Each round the agent bets a fixed budget across channels**, see [interface](interface.md). Its bets are its belief: a small bet on a channel is a look, a large one is a switch.
- **A run scores output as a fraction of what the [oracle](baselines.md), which knows each round's mean levels, would earn on the same seed.** This sits between 0 and 1 and strips out luck in the world's levels.
- **A scenario score is the plain mean of its runs.** Every model plays the same seeds, see [below](#seeds). The gap reads directly as the scenario's failure mode: in calm it is jumpiness, in shock overreaction, in switch underreaction.
- **The headline is the geometric mean across [scenarios](scenarios.md).** A model must do well on every shape to score highly. One bad scenario drags the whole figure down.

## Seeds

- **A seed fixes the world.** It draws every channel's noise for every round up front, bet on or not, so two agents on one seed see the same world and differ only by what they do. The oracle runs on it too.
- **One fixed set of seeds per scenario, the same set for every model.** A model is compared with a rival on the same worlds, not on a different roll of the dice, so the gaps between models are tighter.
- **Each seed is played once.** A seed whose noise looks like a switch for a few rounds is one world among many, and the mean absorbs it. How many seeds, and whether a model's own sampling needs repeats on top, is for the [pilot](../pilot/README.md#seeds).

## Why a mean within and a geometric mean across

- **Seeds are one question asked many times**, so we want the expected value. A geometric mean over seeds would punish one unlucky world, which is noise, not a trait.
- **Scenarios are different questions** and we want an AND. The geometric mean makes one bad trait pull the headline down, where a plain mean would let a strong trait hide it.
- **Error bars.** A scenario score gets a standard error from its seeds. The headline gets a bootstrap: resample seeds, recompute the geometric mean. A gap between two models is paired by seed.

## Extension: inertia

- **A fixed budget is forgiving.** A model that never moves still earns most of the output, so being late costs less than it cost Kodak.
- **A cap on how far bets can move each round** would amplify the lateness signal. It is switched on only if the [pilot](../pilot/README.md#inertia) finds the base score too flat.
