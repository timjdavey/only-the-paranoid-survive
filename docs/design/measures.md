# Measures

## The steps an agent goes through

Handling a change takes the agent through these steps. Each measure reads one or more of them.

| Step | What the agent does | Measured by |
|---|---|---|
| 1. Learn normal | Builds a picture of the status quo and how noisy it is | Nothing yet |
| 2. Stay alert | Spends a little on looking while things seem fine | Paranoia, the looking and experimenting rates |
| 3. Notice | Starts to doubt the status quo | Paranoia, and the first doubt curve |
| 4. Test if it's real | Gathers evidence that tells a change from bad luck | Discernment, and the experiments it runs |
| 5. Diagnose | Works out what changed and what now leads | Insight, from the shares |
| 6. Decide | Picks how much evidence it needs before switching | Caution |
| 7. Execute | Commits to the new split | Conviction |
| 8. Record | Rewrites the notes so the next operator inherits the new rule | Insight, from the notes |
| 9. Keep watching | Checks the new split, backs down after a false alarm, stays open to a reversal | Partly the dip reading. Reversals are future work |

- **The steps explain, they don't score.** They overlap, and a good agent runs them as one loop. Scoring each step in order was tried and dropped, see [Why split doubting from switching](decisions.md#why-split-doubting-from-switching).
- **Noticing can come from looking.** The rising unit is one the agent doesn't fund, so it shows nothing unless the agent pays to look. A good agent may find the change in step 2 before anything seems wrong.
- **Step 1 has no measure yet.** A model whose briefing notes miss the weather will look paranoid later, and we can't yet tell that apart from a jumpy temperament.


## Currently measured

We break the question of "How good is an agent at telling a change in the dynamics of a system from simply a run of bad luck?" into the following measures:

Dispositions (a balance is required):
- **Paranoia.** How readily it doubts the status quo and notices a change.
- **Caution.** How much evidence it requires for before switching how it acts.
- **Conviction.** How fully it acts once it has switched.

Abilities (more is better):
- **Discernment.** How small of a change can it discern signal from noise.
- **Insight.** How well it can understand the system dynamics.
- **Performance.** (encompassing measure) How much it can profit from noticing a change and executing plans accordingly.

## Two tiers

| | Proof of concept | Full study |
|---|---|---|
| Headline | Performance, the share of the gain on offer the model took | Discernment, the smallest drop the model acts on |
| Runs per seed | A briefing, a no-change run and two change sizes | A briefing, a no-change run and five change sizes |
| Kind of change | The level change | Level, then coupling, gain and observation |
| Seeds | 20 | About 30 |
| Runs a model | 60 and 20 briefings, about $100 at the target | About 180 at one reasoning setting |
| Reasoning | One setting | A sweep |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | Four skins and two styles of record, tried in the pilot to decide whether their results can be pooled | A real task with a stale handoff note as well |

## What each model plays

A seed fixes the luck, the weather, when the change starts, the yoked dip, the record and how the game is dressed. On each seed a model holds one briefing, then plays one run where nothing changes and one or more runs with a change of a set size, its amplitude: how far the standing unit's level falls, in points. If A0 yields 70 in 100 before and 58 after, the amplitude is 12. 15 is loud and 3 a whisper.

**Proof of concept.** 20 seeds, one briefing and three runs of 40 rounds on each:

- **One no-change run.** Nothing changes, so any doubt here is misplaced, and the yoked dip tempts it.
- **Two change runs**, one at 12 points and one at 5. The faint one is moved to 8 if [next step 1](../../TODO.md#next-steps) finds 5 isn't worth catching.

That is 60 runs and 20 briefings a model. Twenty no-change runs, rather than ten, halve the error bar on paranoia, which is read there alone.

**Full study.** About 30 seeds, six runs on each: the no-change run and five change runs at 3, 5, 8, 12 and 15 points, with extra runs at the amplitudes where a model starts to miss. Each model also plays at several reasoning settings. That is about 180 runs a model at one setting. Later rungs add the other kinds of change.

Every run at either tier shares these settings:

- **The kind of change.** The level change: A0 falls and C0 rises, on side 0 only. A0 never falls below 0.55, so the standing split still pays.
- **The weather.** Memory 0.8, so a bad month is ordinary, with a shared factor and dips.
- **The threshold.** 3%, told to the agent. The standing split funds four units, so the rest are dark until it looks.
- **A record of 200 rounds** from the damped reference bot, with one or two resolved changes and several dips.
- **40 rounds**, so a round spent experimenting is a round not spent earning.
- **A start between round 3 and round 10**, drawn per seed, and a ramp of about 15 rounds.
- **Shared luck.** Every run on a seed sees the same dice and the same weather, and a bigger share sees more of them.
- **Skins.** Public seeds use the abstract, fictional, plant and market skins. Private seeds, with their own skins, catch a model that learnt the public ones.
- **Tools.** A sandboxed code tool beside the four game tools.


## Performance, the proof of concept headline

The share of the reference bot's gain that the model also made. 0 means it did no better than holding the standing split. 1 means it did as well as the reference bot.

1. **Score every run on expected output**, the output the split would win on average at the true levels, whatever the weather and the dice did.
2. **Add up** the model's expected output over all its runs, change and no-change alike.
3. **Subtract** the no-update bot's total over the same runs.
4. **Divide** by the reference bot's total minus the same.

Every amplitude counts by what was on offer in it, and the no-change run counts once. Each run adds what it won, so an early switch beats a late one and a timid switch earns less than a full one. There is no switch cut-off and no rule that throws out a seed after a false alarm: a false alarm counts through the output it cost.

| Performance | Reading |
|---|---|
| 1 | As good as the reference bot |
| Above 1 | Better than the reference bot |
| 0 | No better than the no-update bot |
| Below 0 | Doubt cost more than it gained |

It splits in two over the same denominator. **Gain** is what the change runs added over the no-update bot, and **loss** what the no-change run took away. A high gain with a large loss is paranoid, and a small gain with no loss is complacent. Real output is reported beside both.

It tops out at 1, so it will saturate once a model matches the reference bot. No model will be near that in the proof of concept, which is why it leads there and discernment, which has no such ceiling short of the bot's own, leads the full study. See [Why performance is the proof of concept headline](decisions.md#why-performance-is-the-proof-of-concept-headline).

Performance is the arbiter through two rules:

1. **Every amplitude must be worth catching.** The reference bot's pooled gain over the no-update bot there must beat a margin set in `params.yaml`, or [next step 1](../../TODO.md#next-steps) moves it.
2. **Every trait must predict performance.** Across the disposition bots, built to be too jumpy, too cautious or too hedged, and then across models, a trait that doesn't track performance becomes a diagnostic.

## Discernment, the full study headline

The smallest drop in level the model acts on, in points. Smaller is better. A score of 6 means it moves budget once a unit yielding 70 in 100 has slipped to 64.

1. **At each amplitude, pool the seeds.** Take the model's gain over the no-update bot in the change runs at that amplitude, and subtract what it lost against that bot in the no-change runs.
2. **Divide** by the same figure for the reference bot. That is performance at that amplitude.
3. **Fit a smooth S-shaped curve** of performance against amplitude, and read off where it crosses a set level. Resampling the seeds gives the error bar.

It works like a hearing test, which finds the quietest beep you still hear. The beep is the fall: the unit that rises sits under the threshold at the standing split, so its rise is never heard for free, and the test is of how faint a slip makes the model look and move. METR's time horizon has the same shape: a curve of success against one natural unit, read off at a set level and plotted against release date. The proof of concept's two amplitudes are two points on this curve, in the same unit against the same bot, so nothing is thrown away when the full grid is run.

**The reading level.** The curve is read at two levels, and both are reported:

| Level | Why | Reads as |
|---|---|---|
| 50% | The curve's centre, so the most precise estimate, and the one most models reach somewhere on the grid. This is the line tracked over releases | The faintest change the model profits from half as well as the reference bot |
| 80% | What a reader means by "acts on": the model takes most of what was on offer. Its error bar is wider, and more models fall off the grid | The smallest drop the model reliably acts on |

Whether the 80% bar is tight enough to lead with is settled in [next step 2](../../TODO.md#next-steps) with the bots. Whether amplitude enters the fit as points or their log is fixed before the pilot.

| Reading | What it means |
|---|---|
| A threshold inside the grid | The model handles changes louder than this at the set level |
| Below the grid | At or above the level at every amplitude. The edition has saturated for this model |
| Above the grid | Below the level at every amplitude |

The reference bot scores 1 at every amplitude by definition, so its own threshold sits below the grid, and a model that matches it reads "below the grid". That is saturation, and the remedy is a harder edition, with a lower N, a longer memory or a fainter grid. Each threshold is also published as the evidence a round carries at that amplitude, so every edition sits on one axis. See [Why discernment is the full study headline](decisions.md#why-discernment-is-the-full-study-headline).

## Catch rate, a backup

Three backups check the headline without leaning on the reference bot, and the catch rate needs no true levels either. All three are reported at both tiers, and none is a score.

- **Catch rate.** A change run is caught if the agent switches before the last round and its no-change run has no switch. The amplitude caught half the time should rank models the same way as discernment.
- **Sensitivity, d′.** Signal detection theory splits a catch rate into how well the signal is told from noise, called d′, and how readily the alarm is raised. With 20 no-change runs it is a check, not a score.
- **The dot against the CUSUM curve.** The [CUSUM bot](#caution), swept from hasty to patient, draws the trade between delay and false alarms. Each model is one dot against it.

## Insight

Whether the agent rewrote what it believed and acted on it, or only moved share among the units it already favoured. More is better.

Two readings, both reported:

- **The shares.** In the last 20 rounds of each change run, on each side, the share of rounds and sides where the largest share on that side is on its best unit. The no-update bot scores a half, right on side 1 and wrong on side 0. The retune bot, the reference bot with sides pooled, moves both sides together or neither, so it also scores about a half. An agent that moves A0's share to B0 scores a half too: it retuned. The reference bot scores near 1. The window is set in `params.yaml`.
- **The notes.** Whether the rewritten notes state the new rule, such as "on side 0, C now leads", in the skin's nouns, read by a simple check rather than a judge. The notes are the agent's own, so a rewrite is the agent changing its mind.

## Paranoia

How much the agent doubts notes that are working. Read in the no-change run only, where every doubt is misplaced. Each reading is a gap from the reference bot on the same seed, and positive means more paranoid.

Three rates over 40 rounds:

- **Experimenting.** The average share a round put on units beyond the standing split. It is the main reading, because it costs output.
- **Hedging.** One minus its share on the standing units as a share of the reference bot's. It mirrors experimenting, and [next step 2](../../TODO.md#next-steps) decides whether it stays.
- **Looking.** Record reads a round. It costs nothing, so it is the weakest.

And one moment:

- **The dip reading.** During the yoked dip, the rounds in which the first bad stretch is the change as far as the agent can tell, the share it moved off the dipping unit and whether it switched. The reference bot moves a little and looks. A false alarm is the extreme case.

Made up example, one no-change run:

| Reading | Reference bot | Model | Gap |
|---|---|---|---|
| Experimenting | 3.1% of budget a round | 5.6% | +2.5 points |
| Hedging | 0 | 0.03 | +0.03 |
| Looking | 0.05 reads a round | 0.40 | +0.35 |
| Moved during the dip | 4% off A0, a look at C0 | 18% off A0, switched to B0 | +14 points, and a false alarm |

All four gaps are positive, so it doubted notes that were working, and it switched on a dip.

## Caution

How much evidence the agent needs before it switches. Read in the change runs only, at the round it switched. Positive means it waited for more than the reference bot did. A run with no switch has no caution score.

**The main reading is the CUSUM line.** The CUSUM bot is the textbook change detector, fed the weather model so a dip adds little. Round by round it adds up how much the yield favours a shifted level over the old one with its weather, resets to zero when the sum goes negative, and raises the alarm when the sum crosses a line. For each switch we ask how high the line would have to be for the CUSUM bot, fed the same rounds, to fire on the same round. Caution is that height minus the height for the reference bot's switch. The bot needs only a reference amplitude and the weather settings in `params.yaml`.

Beside it:

- **The plain reading.** Rounds from the start of the change to the switch, minus the reference bot's. Bad weather and clear evidence count the same.
- **The evidence backup.** The reference bot's odds that the change had started, at the model's switch. It depends on the bot's hazard prior, its starting guess at how often changes happen.
- **Diagnostics.** Experiments before the switch, and the output given up before it.

Made up example, one change run where the change starts at round 6:

| | Reference bot | Model | Gap |
|---|---|---|---|
| Switch round | 16 | 19 | |
| Plain reading | 10 rounds | 13 rounds | +3 rounds |
| CUSUM line | 2.8 | 4.0 | +1.2 |
| Evidence at the switch | 3 to 1 that it changed | 9 to 1 | |
| Experiments before the switch | 3 | 1 | |

It is cautious on both readings, and ran fewer experiments, so the extra rounds bought nothing.

## Conviction

Once it has switched, how fully it acts. Read in the change runs from the switch to the last round: its share on the unit that rose, C0, as a share of the reference bot's, minus one. Positive means it moved harder than the evidence justified. Negative means it found the new rule and held back, like Kodak with its digital camera.

The backup is the say/do gap: the rewritten notes state the new rule while the shares don't follow it, or the reverse.

## Diagnostics

These explain the traits and are reported beside them. None is a score.

| Diagnostic | What it shows |
|---|---|
| **Curiosity** | The share on units the standing split leaves out, which ones it tried, and the output given up to experiments |
| **First doubt** | The share of runs with an experiment by each round, as a curve, so runs that never doubted still count |
| **Calibration** | Its share on the standing units, round by round, against the reference bot's |
| **Steadiness** | Reversals: how often it switched and then switched back |
| **Anchoring** | Whether a longer record slows it more than it slows the reference bot. Measured once, by varying the record's length |
| **Candour** | Whether the rewritten notes record what changed and when |
| **Briefing quality** | Whether the notes name the standing split, the second rate units and the resolved changes in the record |
| **Skin and history spread** | How far each trait moves across the four skins and the two history styles, from the pilot |
| **Tool use** | How often it calls `compute`, and whether runs that use it score better |
| **Test awareness** | How often its reasoning says it is being tested, or that the rules may change, before there is any evidence. A lower bound |
| **Dollar cost** | API spend per run, in its own column. Not a measure of skill |

## A profile, not a ranking

Paranoia and caution together place a model in one of six boxes.

| | Calm when nothing changes (paranoia at or below zero) | Doubts working notes (paranoia above zero) |
|---|---|---|
| **Switches on less evidence** (caution below zero) | Reckless, like an Olympics bid on a forecast nobody tested | Jumpy, like Shopify and Hopin after COVID |
| **About the same evidence** (caution near zero) | The target | Nervy but right. It pays for its doubt in the no-change run |
| **Needs more evidence** (caution above zero) | Complacent, like Blockbuster, which turned Netflix down | Knows and doesn't act, like Kodak, which built the digital camera |

The companies illustrate each box. They are not evidence that a model behaves like them.

A made up results table. The top block is what the proof of concept reports, and the bottom block what the full study adds:

| Trait | Model P | Model Q | Reference bot |
|---|---|---|---|
| Performance | 0.62 | 0.41 | 1 |
| Gain in the change runs | 0.70 | 0.42 | 1.03 |
| Loss in the no-change run | −0.08 | −0.01 | −0.03 |
| Insight, shares | 0.80 | 0.55 | 0.95 |
| Insight, notes | Yes | No | n/a |
| Paranoia, experimenting gap | +2.5 points | −0.1 points | 0 |
| Paranoia, dip reading | +14 points | 0 | 0 |
| Caution, CUSUM gap | +0.4 | +2.1 | 0 |
| Conviction | −0.15 | −0.40 | 0 |
| Discernment at 50%, points | 6.5 | 11.0 | Below the grid |
| Discernment at 80%, points | 10.0 | Above the grid | Below the grid |
| Catch rate threshold, points | 7.0 | 12.5 | 3.0 |

Model P took 62% of the gain on offer. It doubts working notes and pays for it, but switches on about the right evidence, so it is nervy but right. Model Q is calm but slow to switch, and holds back once it does. It is complacent.

A made up log from one 12 point change run, showing the two side 0 units that matter. The other eight stay at the standing split throughout, and C0 is dark until the agent funds it. Yield is shown as won out of volume bought.

    Round  A0                  C0                  Output
    3      25%   27 of 43      0     dark          118
    6      25%   26 of 43      0     dark          117   the change starts, unseen
    9      25%   23 of 43      0     dark          114   two bad weeks on A0, ordinary weather or the ramp
    12     25%   22 of 43      0     dark          113   the no-change run has matched until here
    13     20%   18 of 36      5%    8 of 10       114   first doubt: a look at C0 (diagnostic)
    19     8%    9 of 15       22%   32 of 39      121   the switch. Caution is read here, against the bot's round 16
    19     rewrites the notes: "on side 0, C now leads"             candour, and insight's notes reading
    20     8%    8 of 15       22%   33 of 39      122   side 1 stays on A and B, as it should
    21 to 40   C leads on side 0 and A and B on side 1 in 19 of 20 rounds   insight 0.95

## What it costs

The target is about $100 a model, since the benchmark is run out of pocket. At the thinking we now expect, it costs more.

**Proof of concept.**

- **Calls.** 60 runs of 40 rounds is about 2,400 calls a model, plus 20 briefings, reads and code calls.
- **Typical prices.** At $4 in and $20 out per million tokens, with prompt caching and 3,000 to 5,000 thinking tokens a round, a run costs about $3 to $4.50, or $180 to $270 a model. A briefing reads the record once and costs about a round.
- **Top prices.** At $10 in and $50 out, about $7 to $11 a run, or $420 to $660 a model.
- **Thinking** is most of the bill, so the pilot, a first run on two models, measures it first. If the figure holds, the choice is a higher target or fewer seeds, settled by the error bars from [next step 2](../../TODO.md#next-steps). We cut seeds rather than thinking, since a model run below its best says little. Bots cost nothing.
- **The no-change run** is the one thing not to cut.
- **The pilot** runs four skins and two history styles on two models over a few seeds, which is where the spreads come from. It is tuning, not the suite.

**Full study.** About 180 runs a model at one reasoning setting, so three times the proof of concept: $540 to $810 a model at typical prices, before the reasoning sweep and the other kinds of change multiply it. That is a funded figure, and the reason the threshold waits.
