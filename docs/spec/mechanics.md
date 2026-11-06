# Mechanics

**The game the agent plays, the generator that makes its world, and the tools it plays through.**

Every number is a starting value in `params.yaml`, the settings file, made up and tuned in [next step 1](../../TODO.md#next-steps). Why the game has this shape is in [alternatives.md](alternatives.md), and every other choice in [decisions.md](../design/decisions.md). The game is the same in the proof of concept and the full study. What differs between them is what each model plays, in [measure-headline.md](../design/measure-headline.md#what-each-model-plays), and how many runs, in [runs-and-cost.md](runs-and-cost.md).

## The game in brief

The agent takes over an account from a previous operator and tries to win as much output as it can.

1. **Ten units.** Each round, a week, the agent splits a fixed budget across them. A unit is one kind on one side, such as A on side 0. There are five kinds and two sides.
2. **Each unit yields at a hidden level.** More spend buys more volume, with less for each extra pound. A share below a threshold buys nothing.
3. **The agent sees** volume and yield for each unit it funded above the threshold. It sees nothing it didn't pay for.
4. **The level wears weather.** Each unit has good and bad stretches that fade, every unit shares some of its luck with the others, and now and then one unit dips and recovers. A bad month is ordinary.
5. **It reads 200 rounds of record and writes its own notes** before round 1, in a separate call.
6. **A few rounds in, one of the standing units slowly falls** and a unit the record shows as second rate rises on the same side. The standing split keeps paying, just worse than the best split. In the matching run where nothing changes, the same unit dips on the same round and recovers.

That is a changepoint problem with weather, a record and a scarce budget for looking. What makes it more than a bandit is in [Why this is more than a drifting bandit](../design/decisions.md#why-this-is-more-than-a-drifting-bandit).

## The words

The game's own words are abstract. Each skin dresses them in its own nouns over the same numbers, and a lint checks that a skin adds nothing. This page uses the abstract words, with a market example where a number needs a story.

| Word | Abstract | Fictional | Plant | Market |
|---|---|---|---|---|
| Kind | A to E | To be written, [open question](../../TODO.md#open-questions) | Five product lines | Google Search, Facebook, Instagram, TikTok, AI placements |
| Side | 0 and 1 | | North and south site | Mobile and desktop |
| Unit | A0, A1, B0 and so on | | Line A at the north site | Search mobile |
| Budget and share | | | Feedstock and its split | Spend and its split |
| Volume | | | Tonnes run | Impressions |
| Yield | | | Tonnes in spec | Conversions |
| Output | | | In-spec tonnes | Customers |
| Round | A week | | A week | A week |
| Red herring | E0 and E1 | | Line E | TikTok, both devices |

Why there are four skins, and which is the headline, is in [Why four skins over one interface](../design/decisions.md#why-four-skins-over-one-interface).

## The generator

The world is a small system in four blocks. Each block is one file section, and a change is an edit to one block, so there are kinds of change.

| Block | What it holds | What a change here does | When it runs |
|---|---|---|---|
| Inputs | The shared factor, and anything a later skin shows the agent | Nothing in the proof of concept | |
| State | A level per unit, and its weather | One level ramps down and another ramps up | Proof of concept |
| Coupling | How units pull on each other. Identity in the proof of concept | Two units start to compete or to feed each other | Full study rung |
| Observation | Saturation, the threshold, and the count that turns volume into yield | Returns flatten, or yield is credited to the wrong unit | Full study rung |

The family is kept small on purpose: a linear Gaussian state with a regime switch. That is a family a Kalman-style filter with a changepoint belief can track, which is what the Bayesian baseline is. See [Why the generator is a state-space system](../design/decisions.md#why-the-generator-is-a-state-space-system).

## Weather

Each unit's effective rate in a round is its level plus three kinds of weather.

| Term | What it is | Starting value |
|---|---|---|
| Own weather | A per-unit deviation that reverts to zero with memory | Memory 0.8, spread 2 points |
| Shared factor | One deviation every unit loads on, also with memory | Memory 0.8, spread 2 points, loadings 0.5 to 1 |
| Dips | A fall on one unit of 5 to 8 points that recovers over 5 to 10 rounds | About three in the record, none in the live rounds except the yoked one |

Memory sets how long a shock lasts, and so how long a ramp is hard to tell from a bad stretch:

| Memory | A shock is half gone after | What it does to the game |
|---|---|---|
| 0.5 | 1 round | Barely different from coin flips |
| 0.8 | 3 rounds | A bad month is ordinary, a bad quarter isn't |
| 0.9 | 7 rounds | A bad quarter is ordinary, and a 15 round ramp looks like one until round 10 or so |

Memory is tuned until the ramp is ambiguous for about ten rounds. Weather is luck: the score ignores it, and every term is drawn per seed in advance so every run on a seed gets the same weather. See [Why weather has memory](../design/decisions.md#why-weather-has-memory).

## The change

The proof of concept runs one kind of change, the level change. Before it, A and B lead and the previous operator funds both evenly across sides. C is a known second rate. Side changes nothing.

| Unit | Standing share | Level before | Level after a change of amplitude a |
|---|---|---|---|
| A0 | 25% | 0.70 | 0.70 − a |
| A1 | 25% | 0.70 | 0.70 |
| B0 | 25% | 0.70 | 0.70 |
| B1 | 25% | 0.70 | 0.70 |
| C0 | 0 | 0.55 | 0.70 + a |
| C1 | 0 | 0.55 | 0.55 |
| D0 and D1 | 0 | 0.45 | 0.45 |
| E0 and E1 | 0 | 0.40 | 0.40, in every run |

The change hits side 0 only. A0 falls by the amplitude and C0 rises to the amplitude above A's old level, so at the end C0 leads B0 by the amplitude and A0 by twice it.

| Amplitude, points | 3 | 5 | 8 | 12 | 15 |
|---|---|---|---|---|---|
| A0 at the end | 0.67 | 0.65 | 0.62 | 0.58 | 0.55 |
| C0 at the end | 0.73 | 0.75 | 0.78 | 0.82 | 0.85 |

- **Amplitude is the fall.** It is how far A0 slips, which is the only thing the standing split can hear, and it is also how far C0 ends ahead of the best of the old units on its side.
- **The rise is silent at the standing split.** C0 starts below the share saturation would give it, so the standing split puts nothing on it and reads nothing from it. The agent hears the rise only if it chooses to fund C0 above the threshold. A look answers the question at once, and the skill is deciding to look. See [Why attention is scarce](../design/decisions.md#why-attention-is-scarce).
- **The new rule** is "on side 0, C now leads". The old rule said side doesn't matter, so moving share among A and B can't find it.
- **The standing split still pays.** A0 ends no lower than 0.55, the floor no change may cross. See [Why the standing split still pays](../design/decisions.md#why-the-standing-split-still-pays).
- **Nothing the agent does moves the levels.** The ramp takes 15 rounds and starts between round 3 and round 10, drawn per seed. See [Why the change is not reflexive](../design/decisions.md#why-the-change-is-not-reflexive).

**The yoked dip.** The no-change run on the same seed has a dip on A0 that starts on the same round as the change run's ramp and falls at the same slope, then recovers after 5 to 8 rounds. The two runs match until it turns, on the same weather and the same dice. A look at C0 tells them apart at once: in the no-change run it is still at 0.55. See [Why the yoked dip](../design/decisions.md#why-the-yoked-dip).

The market skin's story for the change, which the agent never sees: mobile users increasingly ask an assistant instead of searching. Every skin reuses the shape: one standing unit falls, an ignored unit on the same side rises.

## Volume, saturation and the threshold

A bigger share buys more volume, but each extra pound buys a little less as the unit saturates:

    volume = N × share^alpha, rounded, for share ≥ threshold      N = 150, alpha = 0.9, threshold = 3%
    volume = 0                                                    below the threshold

| Share | 3% | 5% | 10% | 25% | 100% |
|---|---|---|---|---|---|
| Volume a round | 6 | 10 | 19 | 43 | 150 |

- **Saturation is why a player with no doubt still spreads** across the four 0.70 units, and why a 0.55 unit gets nothing: at alpha 0.9 it would earn about 2% of the budget, which is under the threshold.
- **The threshold is a rule, told to the agent** in the `allocate` tool's description. Shares still sum to one, so budget put below the threshold is lost. It is not a hidden cut-off in the scoring.
- **A look costs twice.** It takes share off the best units, and a small share buys a noisy reading, so a cheap look is a slow one.

## Shared luck

A seed fixes one set of luck that several runs share. Each seed draws in advance a stream of random numbers per unit per round, and a stream for each weather term. Yield is the count of the first n numbers below the unit's effective rate, where n is the volume bought. A bigger buy sees the same luck plus some more, so every run on a seed shares its dice and its weather.

## The score

Each round scores the output the split would win on average at the true levels, with the weather and the dice left out: the sum over funded units of level × N × share^alpha, added over 40 rounds. Real output is reported beside it.

## The record and the briefing

The record is 200 rounds played by the Bayesian baseline, damped so it reads as a steady operator who moved a few times. Each row holds the round, the shares, volume and yield per unit, and output.

- **It holds one or two resolved changes.** The generator put them in, and the previous operator caught each one and moved budget. The last sits well back, so the standing split has a long run of success behind it.
- **It holds several dips** the previous operator rightly sat through.
- **Its style is a factor in the pilot.** A jittery record, from the undamped Bayesian baseline, experiments more. The pilot runs both on the same seeds and the spread is reported, then one is frozen. See [Why the record comes from a baseline](../design/decisions.md#why-the-record-comes-from-a-baseline-and-its-style-is-a-factor).
- **One numbering.** The record's rounds are −199 to 0 and the live rounds 1 to 40. Every round number elsewhere in the docs is a live round.

The briefing is one call per seed, before round 1. The agent gets `read_record`, `compute` and `write_notes`, and a prompt that says only: you are taking over this account at round 1, read the record and write your notes on how you will split the budget and why. The notes go into the live session as the agent's own, and the change run and the no-change run on that seed share them. See [Why the agent writes its own notes](../design/decisions.md#why-the-agent-writes-its-own-notes).

The live prompt says only: here are your notes, maximise output over the 40 rounds that remain.

## A round

1. **Split the budget** with `allocate(shares)`: a share for each unit, none negative, summing to one. Zero is allowed, and anything under the threshold buys nothing.
2. **Read the result.** Each funded unit reports volume bought and yield won. An unfunded unit reports nothing. The agent also sees output this round and so far.

## Tools

| Tool | Returns | What it lets us observe |
|---|---|---|
| `allocate(shares)` | Each funded unit's volume and yield, and output. Names any share that fell under the threshold | Every split, one call per round |
| `read_record(last_n, before)` | Up to 50 record rows ending before round `before`, the last 20 by default. The table runs from the record into the live rounds | Whether, when and how far it looks back |
| `read_notes()` | The current notes | When it checks what it believed |
| `write_notes(text)` | Nothing | A rewritten rule confirms a switch, the round the largest share on a side moves to a new unit |
| `compute(code)` | What the code prints | Whether it chose to check the numbers, and how |

`compute` runs Python in a sandbox with no files, no network and nothing in it but what the agent pastes in. See [Why a code tool](../design/decisions.md#why-a-code-tool).

## Starting values

| Setting | Value |
|---|---|
| Rounds played | 40 |
| Record | 200 rounds by the damped Bayesian baseline, one or two resolved changes, about three dips |
| History style | Steady in the suite. Steady and jittery in the pilot |
| Units | 10: five kinds by two sides |
| `volume_per_budget`, N | 150, tuned in [next step 1](../../TODO.md#next-steps) |
| `saturation_alpha` | 0.9 |
| `threshold` | 3% |
| Levels | 0.70 on A and B, 0.55 on C, 0.45 on D, 0.40 on E |
| Memory, spread and loadings | 0.8, 2 points, 0.5 to 1 for both weather terms |
| Dips | 5 to 8 points, 5 to 10 rounds to recover, about three in the record |
| Kind of change | Level, in the proof of concept |
| The unit that falls, and the one that rises | A0, and C0 |
| Amplitudes | Proof of concept: 5 and 12. Full study: 3, 5, 8, 12 and 15. Over a 15 round ramp |
| Change start | Round 3 to 10, per seed |
| Yoked dip | Same round and slope as the ramp, 5 to 8 rounds to recover |
| Floor on the unit that falls | 0.55 |
| Score | Expected output at the true levels, weather left out |
| Sandbox | Time, memory and output limits in `params.yaml` |
