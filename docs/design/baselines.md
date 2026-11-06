# Baselines

**The scripted players every score is read against. None uses a model, and all of them play every seed.**

## In brief

Each round the agent splits a fixed budget across ten units and sees what each one yields. A unit's yield rises with its share, but with less for each extra pound, and a share under a told threshold buys nothing. Each unit has a hidden level, the chance that its volume yields. Before round 1 the agent reads a record of 200 past rounds, which ends on a split we call the standing split. Some rounds in, a change lowers one standing unit's level and raises a unit the standing split ignores. A dip looks the same at first but recovers. A seed fixes the luck, so every player on a seed sees the same dice.

How to read a score:

- **Four baselines mark the chart.** The perfect one is a ceiling no model can pass. The Bayesian one is the best inferrer we can build, and a model may beat it. The stale and uniform ones are floors.
- **Scores are in expected output**, what a split is worth at the true levels with the dice and the weather left out. See [Why each round is scored on expected output](decisions.md#why-each-round-is-scored-on-expected-output).
- **A proportion of the perfect baseline follows**, as a derived number, never as the headline.

## The four baselines

| Baseline | What it knows | What it does each round | What it marks | Can a model beat it? |
|---|---|---|---|---|
| Perfect | The true levels | Plays the best split for them | The most any split could earn | No |
| Bayesian | What the agent sees | Infers the levels and splits on a sample | What was knowable, and when | Yes |
| Stale | The levels before the change | Holds their best split for all 40 rounds | What stale notes earn | Yes |
| Uniform | Nothing | Splits the budget evenly over the ten units | What knowing nothing earns | Yes |

**Perfect baseline.** It is told the true levels every round, so it sees the change the round it starts and knows a dip for what it is. It plays the best split for those levels, given the falling return on share and the threshold. Expected output is scored at those same levels, so no split can earn more. It is a few lines of code on top of the generator and needs no record. Prior work uses "oracle" for fair bounds of other kinds, so this page avoids that word.

**Bayesian baseline.** It sees only what the agent sees. It keeps a belief about every unit's level, about whether a fall is a dip or a shift, and about when a change began, and each round it splits on a sample from that belief. Sampling means a unit it is unsure of sometimes draws high and gets a look. It also plays the previous operator, damped, who wrote the record. The gap between it and the perfect baseline is the price of having to infer.

**Stale baseline.** It plays the best split for the levels before the change, which is the perfect baseline's round 1 split, and holds it to the end. It needs no record. The standing split the agent inherits is the previous operator's last split, and sits within a hair of it.

**Uniform baseline.** It splits the budget evenly over the ten units every round. The gap between it and the stale baseline is what the record and the briefing are worth.

## How a score reads against them

Made up numbers, pooled over the same seeds:

| Player | Expected output | Proportion of perfect |
|---|---|---|
| Uniform baseline | 41,200 | 0.79 |
| Stale baseline | 46,800 | 0.90 |
| Model P | 48,900 | 0.94 |
| Bayesian baseline | 49,700 | 0.96 |
| Perfect baseline | 52,000 | 1.00 |

| Where a model sits | What it means |
|---|---|
| At the perfect line | No split could have earned more |
| Above the Bayesian line | It beat the best inferrer we built |
| Between stale and Bayesian | It acted on the change, but later or less fully than was knowable |
| Below the stale line | Its doubt cost more than it won |

## Probes

Other scripted players tune the game and check the measures. They don't mark the chart. Most are the Bayesian baseline with one part changed.

| Probe | How it is built | What it checks |
|---|---|---|
| Retune | Sides pooled, so each kind is one belief | That insight can tell a retune from a rethink |
| Dip-only | Its belief that a change can last is switched off | That the ramp passes for a dip for about ten rounds |
| Jumpy | Switching bar lowered | That paranoia and caution recover the dial |
| Cautious | Switching bar raised | The same, from the other side |
| Hedging | Standing units' share halved | That hedging reads the cut |
| Fixed | Switch at a set round, split at random, or look at a set share | That the score rewards no trick |
| CUSUM | A textbook change detector, fed the weather model | Caution, read as the line it would need |

See [Why the baselines set the difficulty](decisions.md#why-the-baselines-set-the-difficulty).

## Checks before any model plays

1. **The order holds.** Perfect beats Bayesian beats stale on every amplitude, the size of the fall, with Bayesian over stale by a margin set in `params.yaml`.
2. **No trick pays.** Every fixed probe scores well below the Bayesian baseline.
3. **The floor never switches.** The stale baseline catches no change.
4. **The record matches the floor.** The standing split is within a hair of the stale baseline's split. See [Why the standing split still pays](decisions.md#why-the-standing-split-still-pays).
