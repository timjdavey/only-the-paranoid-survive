# Alternatives

**The five games we weighed, and why the budget split won.**

In brief, the chosen game: each round the agent splits a fixed budget across ten units, five kinds on two sides, sees yield on the ones it funded above a threshold, and is scored on output. It starts from the record, 200 rounds of past play, and the split the record ends on is the standing split. The world wears weather, good and bad stretches that fade, so a bad month is ordinary. Partway through, one of the units the standing split funds slowly falls, and an ignored unit on the same side rises past it. Full rules are in [mechanics.md](mechanics.md).

## What any design must keep

1. **A record the agent starts from**, with a standing split that still pays after the change.
2. **Bad luck that comes in streaks**, so a bad stretch is a real explanation for poor results.
3. **A no-change run**: every game is also played on the same luck with nothing changed, and holds a dip that starts like the change and then recovers, to tempt a false alarm.
4. **Graded change sizes**, from loud to faint.
5. **Every move a logged action**, so doubt is read from what the agent does.
6. **A reference bot we can build**: a scripted player that learns from the same rounds as the agent and values information.
7. **No hint of change** in the prompt or the story.

## Why the coin flip game was dropped

The old game was one even money bet a round: pick A, B or C, stake a share of a bankroll, win or lose it. We simulated an oracle that knows the exact new levels, start and ramp, follows the standing split, and asks how often its odds that the split has slipped reach 3 to 1 by round 40. It is an upper bound on any real player. 4,000 games a cell.

| Evidence a round | 3 points | 5 | 8 | 12 | 15 |
|---|---|---|---|---|---|
| Coin flip, 1 trial | 0% | 1% | 10% | 32% | 45% |
| Coin flip, 20 trials | 37% | 70% | 89% | 98% | 99% |
| Coin flip, 100 trials | 86% | 97% | 100% | 100% | 100% |
| Budget split, three-kind world, N = 400 | 99% | 100% | 100% | 100% | 100% |
| Budget split, three-kind world, N = 25 | 44% | 75% | 92% | 98% | 100% |

At one trial a round even the oracle mostly misses the loudest change and never sees 3 points. Batching fixes that, and in the budget split the batch is a setting, N, the volume a whole budget buys. The budget rows were run on an older three-kind world with coin flip noise, and are to be rerun in [next step 1](../../TODO.md#next-steps) with weather in. Weather with memory will pull every row down, which is what it is for.

Power wasn't the only problem:

- **The bet has no story.** "Win or lose your stake at even money" has no reading in any skin.
- **The stake mixed two skills.** Sizing a bet on a growing bankroll is a maths test, and it blurred with doubt. See [Fixed or compounding budget](#fixed-or-compounding-budget).
- **A weekly condition was a tell.** The old game showed a flag every round that the notes never used, which invites a careful agent to test it early. Side is now a tag on a unit instead. See [Why ten units](decisions.md#why-ten-units-in-five-kinds-by-two-sides).

## The five designs

| Design | Action | Feedback | An experiment | Main cost |
|---|---|---|---|---|
| **Budget split** | Shares of a fixed budget across ten units | Yield per funded unit | A share above the threshold on a unit the standing split leaves out | A trickle may look cheap |
| Inventory ordering | Units to stock each week, given a forecast | Sales, capped at stock | Stock more than the forecast | Demand above stock is never seen |
| Pricing by segment | A price for each segment | Sales at that price | Try another price | A curve, not a level, so a hard reference bot |
| Supplier split | Orders split across suppliers, with a fee to move | Defects per supplier | A small order elsewhere | Tests lock-in as well |
| Coin flip with batches | One option and a stake | Wins in a batch of flips | A small stake off the standing option | Kelly and ruin stay |

**Budget split.** The chosen game. Every trait reads as a share, and the evidence a round buys is a setting. Its risk, a cheap trickle on every unit, is closed by the threshold, below.

**Inventory ordering on a demand forecast.** Familiar, but when demand beats stock the agent sees only that it sold out. Evidence is cut off exactly when the world gets better. Show full demand instead and every model sees the same evidence whatever it does, so there is nothing to test and the split between looking and committing, which the traits lean on, is gone.

**Pricing by segment.** Close to real work, but the change moves a demand curve rather than a level, so the reference bot is much harder to write and check. Models also reason about price response less well than about rates, and on a continuous price it is hard to say which round counts as the switch.

**Supplier split with switching costs.** A good story for lock-in, which the game leaves out on purpose ([Why no lock-in](decisions.md#why-no-lock-in)). A fee mixes the price of switching into every trait, and it turns the reference bot into a planning problem over future fees.

**The coin flip game repaired with batches.** The smallest change. It fixes power, but a test and a hedge still need stake cut-offs the agent never knew about, and it keeps Kelly and a cap against ruin. It stays the fallback if the reference bot for the budget split proves too hard to build.

Pricing and the supplier split are candidates for a second game, once the proof of concept shows the core measure works. See [Future work](future.md).

## Why the budget split won

1. **The story needs no translation.** Splitting a budget across units is what an operator does every week, in every skin.
2. **Batching fixes power.** Evidence a round is N, a dial on the generator, not a count of calls to the model.
3. **A share replaces the stake.** How much the agent puts on a unit shows how sure it is, with no cut-off it was never told about.
4. **The fixed budget keeps evidence a function of share alone.** A lucky or unlucky past doesn't change what next round can show.

## Why cheap probes aren't a loophole

The budget split's one weakness was that a 1% trickle on every unit watched the whole game for almost nothing. Two rules close it.

- **The threshold.** A share under 3% buys nothing and reports nothing, and the agent is told so. The standing split funds four units, so every other unit is dark until the agent pays to look. The unit that rises sits under the threshold at the standing split, so the rise is never heard for free. See [Why attention is scarce](decisions.md#why-attention-is-scarce).
- **Precision scales with spend above it.** At N = 150, 3% buys 6 of volume a round and 25% buys 43. A look at the threshold says something moved within some rounds. Telling whether C0 now beats B0 by 3 points takes a real share and real rounds.
- **The reference bot sets the right amount of looking**, so a model that looks more pays for it as a gap.
- **The no-change run charges for it**, in output forgone, and its yoked dip tempts exactly the look the change run rewards.
- **The table of rounds to 3 to 1 odds**, by share and amplitude, is produced in [next step 1](../../TODO.md#next-steps) from the generator itself, with weather in.

## Fixed or compounding budget

| | Fixed budget | Compounding budget |
|---|---|---|
| What is scored | Output, added over rounds | Final budget, through log growth |
| Right sizing | Expected output under saturation | Kelly, with a cap against ruin |
| Evidence a round | Set by share alone | Shrinks after bad luck |
| Removing luck | Expected output per round | Expected log growth |
| A bad run | Costs that round | Costs every round after |

**Decision: fixed.** It drops Kelly and ruin, keeps evidence equal across runs on a seed, and makes the score a plain count. Compounding stays a generator option, switched off, for the [extension](future.md#how-the-agent-can-act) that asks whether late mistakes should cost more.

**Sources.** Kelly 1956, "A New Interpretation of Information Rate" (Bell System Technical Journal 35(4): 917 to 926, [doi:10.1002/j.1538-7305.1956.tb03809.x](https://doi.org/10.1002/j.1538-7305.1956.tb03809.x)), sizes a bet by the edge. Baker and McHale 2013 (Decision Analysis 10(3): 189 to 199, [doi:10.1287/deca.2013.0271](https://doi.org/10.1287/deca.2013.0271)) show that betting on an estimated edge as if it were known overcommits.
