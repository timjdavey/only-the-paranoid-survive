# Glossary

**The one word we use for each idea in the benchmark, and the older names it replaces.**

Use the word in the left column, in prose and in code. "Also called" lists older names for the same thing, now retired. Studies in [prior work](prior/README.md) keep their own words. The abstract words below are the game's own. Each skin dresses them in its own nouns, listed in [mechanics](design/mechanics.md#the-words).

## The game

"The game" means the rules. One playthrough of them is a [run](#what-each-model-plays).

| Word | What it means | Also called |
|---|---|---|
| Round | One week: split the budget across the units, see the yield | Turn |
| Unit | One of the ten things the agent funds. The only thing a share goes on. A0, A1, B0 and so on | Campaign, arm, cell |
| Kind | The five types, A to E, two units each. The market skin calls them channels | Channel |
| Side | The second tag on a unit, 0 or 1. Each kind has one unit on each side. The market skin calls them devices | Device |
| Red herring | A unit that never changes in any run. E0 and E1 are built as red herrings | Distractor |
| Lever | Something the agent sets. There is only one, the split | Action |
| Budget | The fixed amount the agent splits each round. It doesn't grow or shrink | Bankroll, money |
| Share | The part of the round's budget put on one unit. Shares are zero or more and sum to one | Stake, bet size, f |
| Split | The ten shares for one round | Allocation |
| Threshold | The share below which a unit buys no volume and reports nothing. A rule the agent is told | Minimum share |
| Volume | What a share above the threshold buys on a unit, more for a bigger share but with less for each extra pound | Impressions |
| Saturation | That falling return, set by alpha. It is why a player with no doubt still spreads a little | |
| Level | A unit's hidden underlying rate, the chance that one of its volume yields. A change moves the level | Conversion rate, win rate, p |
| Weather | The ordinary variation around a level: a per-unit term with memory, a shared factor and dips. Weather is luck, and the score ignores it | Natural variation, noise |
| Memory | How long weather lasts, as the autoregressive coefficient. It sets how many rounds a ramp is hard to tell from a bad stretch | AR coefficient |
| Shared factor | One hidden term every unit loads on, so a bad round for everyone is ordinary | Common shock |
| Dip | A fall on one unit that recovers on its own over a few rounds. The record holds several | Transient, soft patch |
| Yield | The count a unit's volume returns in a round | Conversions, wins |
| Output | Yield added up. The score is expected output, from the true levels with the weather left out | Customers, final bankroll |
| Shared luck | A stream of random numbers per unit per round, and a stream for each weather term, drawn in advance, so every run on a seed sees the same dice | Outcome tape, tape |

## The generator

| Word | What it means | Also called |
|---|---|---|
| Generator | The code that makes the world: four blocks that turn a split into a reading | World, engine |
| Block | One of the generator's four parts: inputs, state, coupling and observation | |
| Inputs | What drives the world from outside: the shared factor, and in later skins anything shown to the agent | External inputs |
| State | A level per unit and its weather | Hidden state |
| Coupling | How units pull on each other. In the proof of concept they don't | |
| Observation | How a split and the state become volume and yield: saturation, the threshold and the count | |
| Kind of change | Which block a change edits: level, coupling, gain or observation. The proof of concept runs the level change only | New driver |

## The change

| Word | What it means | Also called |
|---|---|---|
| Change | The hidden shift in a block, starting between round 3 and round 10 | Break |
| Stale notes | Notes that still win output, but less than the best split | Stale plan |
| Ramp | The change arrives over about 15 rounds, not all at once | Slow ramp |
| Amplitude | How far the standing unit's level falls, in points. It is also how far the unit that rises ends up ahead of the best of the old units on its side | Change size, break size, grid point |
| Yoked dip | The dip in the no-change run that starts on the same round and the same unit as the change run's ramp, so the first rounds of the two runs match | False alarm bait |
| Retune | Moving share among the units the notes already favour, keeping their rule | Patch |
| Rethink | Finding the new rule, here that on one side a unit the notes ignored now leads | |

## The record and the briefing

| Word | What it means | Also called |
|---|---|---|
| Handoff | The start of the agent's run, when it takes over a record from a previous operator | Takeover, handover |
| Previous operator | The reference bot, damped, which played the 200 rounds in the record | Previous agent |
| Record | The 200 rounds before the handoff, rounds −199 to 0. Each row holds the split, volume and yield per unit, and output | History, handoff history, track record, log |
| History style | How much the previous operator experimented in the record: steady or jittery. A pilot factor, then frozen | |
| Resolved change | A change inside the record that the previous operator caught and moved for. The record holds one or two | Past change |
| Standing split | The split the record ends on. The no-update bot holds it to the end | The plan's share, the plan's split |
| Briefing | The separate call before round 1 where the agent reads the record and writes its notes | |
| Notes | The agent's own working note on how to split and why, written at the briefing and read and rewritten through `read_notes` and `write_notes` | Plan, frozen plan, guide, strategy guide, handoff document |

## What the agent does

| Word | What it means | Also called |
|---|---|---|
| Experiment | A round that puts share above the threshold on a unit the standing split leaves out, or cuts one of the standing units below half its usual share | Test bet, probe, look, trade |
| First doubt | The round of the first experiment | First probe |
| Switch | The round from which the largest share on a side moves to a unit the standing split leaves out, and stays there in most later rounds. Rewriting the notes confirms it | Commit |
| False alarm | A switch in the no-change run | |
| Reversal | Switching and then switching back | Flip-flop |
| Compute tool | `compute(code)`, a sandboxed Python call that sees only what the agent passes in. No files, no network | Code tool, sandbox |

## What each model plays

| Word | What it means | Also called |
|---|---|---|
| Run | One playthrough of the game, 40 rounds long, after one briefing per seed | Game, sample |
| Seed | Fixes the luck, the weather, when the change starts, the yoked dip, the record and the skin. In the proof of concept each model plays 20, with three runs on each | Setup |
| No-change run | The run on a seed where nothing changes, with the yoked dip in it | Calm game, steady run, steady twin, twin |
| Change run | A run on a seed with a change at one amplitude | Change game, break run |
| Grid | The amplitudes each seed is played at. Two in the proof of concept, five in the full study | |
| Skin | A story the game is dressed in, over the same numbers. Four: abstract, fictional, plant and market. Code keeps `skin_id` and `skins/` | Narrative skin |
| Abstract skin | The bare game, with letters for names. The anchor every other skin is read against | No-skin run, plain game |
| Public and private sets | Seeds and skins we publish, and ones held back to catch a model that learnt the public ones | |

## Bots

Every scripted player is a bot, named for what it does. Bots play every seed, make no API calls and write the same log rows as models.

| Word | What it means | Also called |
|---|---|---|
| Reference bot | The best bot we can build, and the yardstick. A filter on the generator's own family that keeps a belief about every level, about whether a unit is in a dip or has shifted, and about when a change began. It samples from that belief each round and splits on the sample. A model may beat it | Bayes bot, perfect player, perfect learner |
| No-update bot | The floor. Holds the standing split to the end | Never-update, never changing the plan |
| Retune bot | The reference bot with sides pooled, so each kind is one belief and it can only retune | Dumb learner, simple player |
| CUSUM bot | The textbook change detector, fed the weather model. Sums evidence for a change and switches when the sum crosses a line | CUSUM detector |
| Fixed bots | Switch at a fixed round, split at random, split evenly, or always look at a set share. Each must score well below the reference bot | Dumb bots |
| Disposition bots | Built to have too much or too little of one disposition, to check that the trait costs output | |
| Dip-only bot | The reference bot with its belief that a change can be permanent switched off, so it reads every fall as a dip | |

## Traits

Each model gets six traits. An **ability** is better the more of it there is. A **disposition** has a right amount, so it is a signed gap from the reference bot: zero is ideal, and positive means more of the trait.

| Word | What it means | Also called |
|---|---|---|
| Performance | The model's gain over the no-update bot as a share of the reference bot's, no-change run included. The proof of concept's headline | Edge captured, edge |
| Gain and loss | The two parts of performance: what the change runs added, and what the no-change run took away | |
| Discernment | The full study's headline. The amplitude at which a model's performance crosses a set level. Smaller is better | Threshold, hearing test |
| Catch rate | A backup to discernment. The share of change runs caught, where a run is caught if the agent switched before the last round and the no-change run on that seed had no switch | Caught, catch rule |
| Expected output | What a round's split was worth at the true levels, with the weather and the dice left out | Expected customers, luck-adjusted score |
| Insight | Whether the agent rewrote what it believed and acted on it: near the end of each change run, the share of rounds and sides where the largest share on that side is on its best unit, and whether the rewritten notes state the new rule | Rethinking share |
| Paranoia | How much the agent doubts notes that are working, read in the no-change run, sharpest at the yoked dip | |
| Caution | How much evidence the agent needs before it switches, read as the CUSUM line it would take to fire on the same round | |
| Conviction | After the switch, its share on the unit that rose against the reference bot's | |
| Profile | The six boxes that paranoia and caution place a model in, from complacent to jumpy | Six-cell table |

Paranoia has three readings: **experimenting** (share of the budget beyond the standing split on other units, also called probing), **hedging** (share held back from the standing units) and **looking** (record reads a round), plus the **dip reading**, whether it switched during the yoked dip.

Diagnostics explain the traits but are not scores: curiosity, first doubt, calibration, steadiness, anchoring, candour, briefing quality, skin and history spread, tool use, test awareness and dollar cost. Each is defined in [Measures](design/measures.md#diagnostics).

## The suite and the code

| Word | What it means | Also called |
|---|---|---|
| Proof of concept | The first tier: what gets built and run first, at about $100 a model, to show the measure works | First edition, v1, core suite, PoC |
| Full study | The second tier: the funded version, with the five-amplitude grid, more seeds, a reasoning sweep and every model on release | Funded version |
| Pilot | Runs on two models that test the design before the proof of concept is frozen. It sizes the skin spread and the history style spread | Trial run |
| Hazard | How often the reference bot expects a change. It starts from a prior fixed before any model runs, and learns from the record and the live rounds | Change rate |
| Canary | A unique string in every published file, so training on the benchmark can be spotted | Canary GUID |
| Realism ladder | Later steps that move the game closer to real work | |
| Harness | The code that lets a model play through tool calls | |
| Skin lint | A check that a skin renames the game and adds nothing: same tables, same numbers | |
| `AgentView` and `RunLog` | What the agent may see, and the full record with the true levels | |

## Names we've retired

- **Plan, frozen plan, guide.** The agent no longer inherits a note written by someone else. It writes its own at the briefing, so the note is its notes.
- **Previous agent.** The record is written by a bot, not a model. "Previous operator" says so.
- **Campaign, channel, device, impressions, conversions, customers.** They were the market skin's nouns. The game now has four skins, so the abstract words stand in prose and each skin keeps its own in its own file.
- **New driver.** There are kinds of change now, and the proof of concept's is the level change.
- **Minimum share.** It is a told rule of the game, so it has the plainer name, the threshold.
- **Twin, calm game, steady run.** They hid what the run is for. "No-change run" says it.
- **Game, for one playthrough.** It clashed with the game as a set of rules.
- **Setup.** "Seed" is shorter and already in the code.
- **Test bet, probe.** "Experiment" says why the agent does it.
- **Observation, segment, cell, for a weekly condition.** They named a condition the week arrived in. A real week is a blend. Side is a tag on a unit, so a unit is the only thing funded. "Observation" now names the generator's last block.
- **Signal.** A dashboard index that moved on its own. It was a clue nobody could say the right response to, so it went. Whether a later skin shows the generator's inputs is an [open question](../TODO.md#open-questions).
- **Bayes bot, perfect player, dumb learner.** Bot names now say what each one is for. The reference bot isn't perfect, and a model may beat it.
- **Caught, as the headline.** The catch rate stays as a backup to discernment.
- **Edge captured, edge.** A niche name for a headline. Performance says what it is in one word.
- **First edition.** "Proof of concept" says what the first tier is for.
- **Flip.** A change ramps. Other shapes of change are [future work](design/future.md).
- **Bet, stake, bankroll, option, win rate.** The coin flip game they belonged to was dropped for the budget split. See [alternatives](design/alternatives.md).
- **Kelly, expected log growth.** A fixed budget doesn't compound, so the right split maximises expected output and nothing needs Kelly's sizing.
- **Promotion week.** An older version lifted every unit in some weeks. There are no weekly conditions now.
- **Week, for the unit of play.** A round is a week of spend, and every page says round.

## Adding a word

1. **Add the idea here before using a new name** on any other page.
2. **One word per idea.** If a page needs a second name, list it under "Also called" rather than inventing a third.
3. **Prefer the word that says what the thing is**, not where it came from or what it was first used for.
4. **Prose uses the abstract words.** A skin's nouns appear only in examples, and the example says which skin it is in.
