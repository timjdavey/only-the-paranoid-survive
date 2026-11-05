# Headline measures

**The two numbers we score a model on, and how many runs each takes.**

How good is an agent at telling a change in the dynamics of a system from a run of ordinary bad luck? Two numbers answer it, one per tier. Neither says the round at which the agent noticed, because there is no such round. Suspicion grows.

- **Performance**, the proof of concept headline. The model's gain over the bot that never changes its split, as a share of the best bot's gain, pooled over every run and scored on luck-free output. 0 is the floor and 1 matches the bot.
- **Discernment**, the full study headline. Hold the change loud and make each round's results say less. Report the faintest evidence a round at which the model still takes half the gain on offer, in bits. Smaller is better, and every edition of the game sits on one axis.

The rest of this page builds those two numbers up one idea at a time. The tables at the end say what each model plays and what it costs.

## What one round is worth

Each round the agent splits a fixed budget across ten units and sees what each of them paid. A few rounds in, one unit's hidden rate slowly falls and a unit the agent had ignored rises. The split it inherited keeps paying, just less than the best split would.

What a round pays is partly the split and partly luck: the dice, and the weather of good and bad stretches every unit goes through. We score the split, not the luck. A round is worth what its split would have won on average at the true rates, with the dice and the weather left out. We call this expected output.

Luck drops out, so far fewer runs give the same error bar. The real output is reported beside it. See [Why each round is scored on expected output](decisions.md#why-each-round-is-scored-on-expected-output).

## Two bots fix the scale

Output on its own says nothing, because nobody knows how much there was to win. Two scripted players mark the scale.

| Bot | What it does | What it marks |
|---|---|---|
| No-update bot | Holds the split it inherited, the standing split, to the last round | The floor: what doing nothing earns |
| Reference bot | The best player we can build. It knows how the world works but not the dice, and keeps a belief about every unit and about whether a change has begun | The yardstick: what there was to win |

A model is read by where it sits between them. The reference bot is the best we can build, not the best possible, so a model may beat it. See [Why two bots bound the game](decisions.md#why-two-bots-bound-the-game).

## Performance, the proof of concept headline

The share of the reference bot's gain that the model also made.

1. **Score every run on expected output.**
2. **Add up** the model's expected output over all its runs.
3. **Subtract** the no-update bot's total over the same runs. What is left is the model's gain.
4. **Divide** by the reference bot's gain, worked out the same way.

A made-up example:

| | Total expected output | Gain over the no-update bot |
|---|---|---|
| No-update bot | 4,000 | 0 |
| Model P | 4,372 | 372 |
| Reference bot | 4,600 | 600 |

Model P's performance is 372 over 600, or 0.62. [measure-failure.md](measure-failure.md#a-profile-not-a-ranking) says where the other 0.38 went.

| Performance | Reading |
|---|---|
| 1 | As good as the reference bot |
| Above 1 | Better than the reference bot |
| 0 | No better than the no-update bot |
| Below 0 | Doubt cost more than it gained |

Every run adds what it won, so an early switch beats a late one and a timid switch earns less than a full one. There is no switch cut-off and no rule that throws out a run. See [Why performance is the proof of concept headline](decisions.md#why-performance-is-the-proof-of-concept-headline).

## Why there is a run where nothing changes

A model that moved its split at every wobble would score well if only runs with a change were counted. So every world is played more than once.

A seed is one fixed world: the dice, the weather, the round the change starts, the 200 rounds of record the agent reads before round 1, and the story the game is dressed in, its skin. On each seed a model holds one briefing, where it reads the record and writes its own notes, then plays one run where nothing changes and one or more where something does. We call them the no-change run and the change runs.

In the no-change run, the same unit sags on the same round the change would have started, then recovers on its own. We call this the yoked dip. For the first rounds the two runs look the same, so a model that moves on the dip has moved on bad luck.

Its loss in the no-change run is subtracted inside the same ratio, which is how a false alarm costs through output. Performance splits over that denominator into the gain the change runs added and the loss the no-change run took away, and both are reported. See [Why the yoked dip](decisions.md#why-the-yoked-dip) and [Why one no-change run and a grid per seed](decisions.md#why-one-no-change-run-and-a-grid-per-seed).

## Performance is the arbiter

Every other number answers to performance. Two rules follow.

1. **Every setting must be worth catching.** The reference bot's gain over the no-update bot there, pooled over seeds, must beat a margin set in `params.yaml`, or [next step 1](../../TODO.md#next-steps) moves it. If updating doesn't pay even for the reference bot, staying put is right, and a model that stays has shown nothing.
2. **Every [leak and reading](measure-failure.md) must predict performance.** Across bots built to be too jumpy, too cautious or too hedged, and then across models, a reading that doesn't track performance is dropped.

See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter).

## Why performance can't be the number for ever

Performance tops out at 1. Once a model matches the reference bot, the plot over releases goes flat. That is fine for a proof of concept, whose one job is to show that the measure separates models with usable error bars at about $100 a model. No model will be near 1 by then.

The full study needs a number that keeps moving as models improve. That is why there are two tiers. The game is the same in both, and only the number of runs, the kinds of change and the headline differ. See [Why two tiers](decisions.md#why-two-tiers).

## The hearing test, and why it is the wrong one

The obvious second number is the faintest change a model acts on. A hearing test works that way: it quietens the beep until you stop hearing it, and reports the volume where you did. Make the fall in the unit's rate smaller and smaller, and find where the model stops catching it.

It is the wrong test for us. A quieter change is also a smaller prize, so a model that ignores a change not worth catching is right to. And at faint changes the reference bot gains little, so performance there is a ratio of two small numbers and swings with the luck of the seeds. See [Why discernment is the full study headline](decisions.md#why-discernment-is-the-full-study-headline).

## Speech in noise: keep the change loud, make each round say less

Audiologists have a second test. Speech in noise keeps the words loud and raises the babble behind them, then reports the noise at which you still get half the words right. Discernment is that test. The change stays loud, each round gets noisier, and we find the noise at which the model still takes half the gain the reference bot takes.

What makes a round noisier? Each unit's results in a round are a sample: so many bought, so many that paid. A smaller sample says less. So the dial is how much volume a round buys, which the project calls N.

Turn N down and the fall, and the prize, stay loud, while each round's results say less about whether the fall has happened. The fall is held at 12 points of rate.

Three other things could make a round harder to read, and each is held fixed within an edition of the game instead.

| Candidate dial | Why it isn't the dial |
|---|---|
| A smaller fall | The prize shrinks with the signal, which is the hearing test's problem |
| Longer weather memory, so bad patches last longer | It changes what bad luck means between settings. An edition setting, not the dial |
| Fewer rounds | It tests speed, and the reference bot's own lag caps it |

## Evidence a round, one axis for every edition

N only means something inside one edition of the game. So each setting is published as evidence a round: how much one round's results shift the odds that a change has happened rather than ordinary weather, in bits. One bit doubles the odds, so a world at 0.2 bits a round takes about five rounds to double the odds that something has changed. The maths from N, the fall and the weather to evidence a round is written in [next step 1](../../TODO.md#next-steps) and checked with the bots.

Most benchmarks are replaced when models saturate them: MMLU gave way to MMLU-Pro, and the plot over releases broke. METR's time horizon avoids that because tasks of every length sit on one axis. Evidence a round is ours. A harder edition, with a lower N or a longer weather memory, extends it to the left instead of starting a new chart.

Two rules keep the join honest, a check that psychometrics calls test equating:

- **Adjacent editions overlap** by two or three settings, so a model's curve crosses from one into the other and the join is checked, not assumed.
- **Models near the top are re-run** on the new edition. A model whose threshold already sits on the axis need not be.

## Discernment, the full study headline

The faintest evidence a round at which the model still takes half the gain on offer. Smaller is better.

1. **At each noise setting, pool the seeds.** The model's gain in the change runs minus its loss in the no-change runs, divided by the same for the reference bot. That is performance at that setting.
2. **Fit a smooth S-shaped curve** of performance against evidence a round, and read off where it crosses a set level. Resampling the seeds gives the error bar.
3. **Read it at two levels.** 50% is the curve's centre, so the most precise estimate, and the line tracked over releases. 80% is what a reader means by "profits from", with a wider bar, and is the quoted number. Whether the 80% bar is tight enough to lead is settled in [next step 2](../../TODO.md#next-steps) with the bots.

| Reading | What it means |
|---|---|
| On the axis | The noisiest world the model handles at the set level |
| Off the left end | At or above the level at every setting. The edition has saturated for this model, and the remedy is a harder edition |
| Off the right end | Below the level at every setting |

The reference bot scores 1 at every setting by definition, so it sits off the left end. The proof of concept's two change sizes are two points on the same axis, so nothing is thrown away when the full grid is run.

Discernment says how much noise a model can profit through. It says nothing about when the model noticed. Where the output went is in [measure-failure.md](measure-failure.md).

## Catch rate, a backup

Both headlines lean on the reference bot and on our simulation's true rates, so a flaw in either would move both. Three backups check them without the bot, and none is a score.

- **Catch rate.** A change run is caught if the agent moves its largest share to the unit that rose before the last round, and its no-change run has no such switch. The noise at which half the runs are caught should rank models the same way as discernment.
- **Sensitivity, d′.** A catch rate mixes how well the agent tells signal from noise with how readily it raises the alarm. Signal detection theory splits the two and calls the first d′. With 20 no-change runs it is a check, not a score.
- **The dot against the CUSUM curve.** The textbook change detector, called CUSUM, sums how much each round favours a change and fires when the sum crosses a line. Swept from hasty to patient, it draws the trade between delay and false alarms, and each model is one dot against that curve.

## The two tiers at a glance

| | Proof of concept | Full study |
|---|---|---|
| Headline | Performance | Discernment |
| Runs per seed | A briefing, a no-change run and two change sizes | A briefing, then a no-change run and one loud change at each of five noise settings |
| Seeds | 20 | About 30 |
| Runs a model | 60 and 20 briefings, about $100 at the target | About 300 at one reasoning setting |
| Reasoning | One setting | A sweep |
| Kind of change | One unit's rate falls and another's rises, the level change | Level, then coupling, gain and observation |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | Four skins and two styles of record, tried in the pilot to see if they can be pooled | A real task with a stale handoff note as well |

The kinds of change are the four blocks of [the generator](mechanics.md#the-generator).

## What each model plays

A change has a size, its amplitude: how far the standing unit's rate falls, in points. If it yields 70 in 100 before and 58 after, the amplitude is 12. 15 is loud and 3 a whisper.

**Proof of concept.** 20 seeds, one briefing and three runs of 40 rounds on each:

- **One no-change run.** Nothing changes, so any doubt here is misplaced, and the yoked dip tempts it.
- **Two change runs**, one at 12 points and one at 5. The faint one is moved to 8 if [next step 1](../../TODO.md#next-steps) finds 5 isn't worth catching.

That is 60 runs and 20 briefings a model. Twenty no-change runs, rather than ten, halve the error bar on the [doubt tax and the false alarm leak](measure-failure.md#where-the-output-went).

**Full study.** About 30 seeds. On each, a no-change run and a 12 point change run at each of five noise settings, since the no-change world gets noisier too. That is ten runs a seed and about 300 a model at one reasoning setting, with extra runs where a model starts to miss.

Every run at either tier plays the same game, set out in [mechanics.md](mechanics.md): 40 rounds, a change that starts between round 3 and round 10 and ramps over about 15, a 200 round record written by the reference bot, the same dice and weather for every run on a seed, four public skins with private ones held back, and a sandboxed code tool.

## What it costs

The target is about $100 a model, since the benchmark is run out of pocket. At the thinking we now expect, it costs more.

**Proof of concept.**

- **Calls.** 60 runs of 40 rounds is about 2,400 calls a model, plus 20 briefings, reads and code calls.
- **Typical prices.** At $4 in and $20 out per million tokens, with prompt caching and 3,000 to 5,000 thinking tokens a round, a run costs about $3 to $4.50, or $180 to $270 a model.
- **Top prices.** At $10 in and $50 out, about $7 to $11 a run, or $420 to $660 a model.
- **Thinking** is most of the bill, so the pilot, a first run on two models over a few seeds, measures it first. If the figure holds, the choice is a higher target or fewer seeds, settled by the error bars from [next step 2](../../TODO.md#next-steps). We cut seeds rather than thinking, since a model run below its best says little, and never the no-change run. Bots cost nothing.

**Full study.** About 300 runs a model at one reasoning setting, five times the proof of concept: $900 to $1,350 a model at typical prices, before the reasoning sweep and the other kinds of change multiply it. That is a funded figure, and the reason the threshold waits.
