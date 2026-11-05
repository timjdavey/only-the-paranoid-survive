# Headline measures

**The two numbers we score, and how many runs each takes.**

## The question

How good is an agent at telling a change in the dynamics of a system from a run of ordinary bad luck?

Two numbers answer it, one per tier: performance in the proof of concept, discernment in the full study. When a number falls short of the reference bot's, [measure-failure.md](measure-failure.md) traces where the output went and what the agent did there. Neither page claims to read the round at which an agent noticed, because there is no such round. Suspicion grows.

## Two headlines

| | Proof of concept | Full study |
|---|---|---|
| Headline | Performance, the share of the gain on offer the model took | Discernment, the noisiest world in which it still takes half that gain |
| Runs per seed | A briefing, a no-change run and two change sizes | A briefing, then a no-change run and one loud change at each of five noise settings |
| Seeds | 20 | About 30 |
| Runs a model | 60 and 20 briefings, about $100 at the target | About 300 at one reasoning setting |
| Reasoning | One setting | A sweep |
| Kind of change | The level change | Level, then coupling, gain and observation |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | Four skins and two styles of record, tried in the pilot to decide whether their results can be pooled | A real task with a stale handoff note as well |

The game is the same at both tiers. See [Why two tiers](decisions.md#why-two-tiers).

## Performance, the proof of concept headline

The share of the reference bot's gain that the model also made. 0 means it did no better than holding the standing split. 1 means it did as well as the reference bot.

1. **Score every run on expected output**, the output the split would win on average at the true levels, whatever the weather and the dice did.
2. **Add up** the model's expected output over all its runs, change and no-change alike.
3. **Subtract** the no-update bot's total over the same runs.
4. **Divide** by the reference bot's total minus the same.

Every change size counts by what was on offer in it, and the no-change run counts once. Each run adds what it won, so an early switch beats a late one and a timid switch earns less than a full one. There is no switch cut-off and no rule that throws out a seed after a false alarm: a false alarm counts through the output it cost.

| Performance | Reading |
|---|---|
| 1 | As good as the reference bot |
| Above 1 | Better than the reference bot |
| 0 | No better than the no-update bot |
| Below 0 | Doubt cost more than it gained |

It splits in two over the same denominator. **Gain** is what the change runs added over the no-update bot, and **loss** what the no-change run took away. Real output is reported beside both. It tops out at 1, so it will saturate once a model matches the reference bot, which is why discernment leads the full study. See [Why performance is the proof of concept headline](decisions.md#why-performance-is-the-proof-of-concept-headline).

Performance is the arbiter through two rules:

1. **Every setting must be worth catching.** The reference bot's pooled gain over the no-update bot there must beat a margin set in `params.yaml`, or [next step 1](../../TODO.md#next-steps) moves it.
2. **Every [leak and reading](measure-failure.md) must predict performance.** Across the disposition bots, built to be too jumpy, too cautious or too hedged, and then across models, a reading that doesn't track performance is dropped.

## Discernment, the full study headline

A hearing test quietens the beep until you stop hearing it. That is the wrong test for us. A quieter change is also a smaller prize, and a model that ignores a change not worth catching is right to.

The better test is the one audiologists call speech in noise. It keeps the words loud and raises the babble behind them, then reports the signal-to-noise ratio at which you still get half the words right, as a loss against people with normal hearing. Discernment is that test. The change stays loud, each round gets noisier, and we find the noise at which the model still takes half the gain the reference bot takes.

**The number.** The faintest evidence a round at which the model still takes half the gain on offer. Evidence a round is how much one round's results say that a shift has happened rather than ordinary weather, in bits: one bit doubles the odds. Smaller is better. A score of 0.2 bits means the model still profits in a world where it takes about five rounds of results to double the odds that something has changed.

How it is read:

1. **At each noise setting, pool the seeds.** Take the model's gain over the no-update bot in the change runs at that setting, and subtract what it lost against that bot in the no-change runs at the same setting. Divide by the same figure for the reference bot. That is performance at that setting.
2. **Fit a smooth S-shaped curve** of performance against evidence a round, and read off where it crosses a set level. Resampling the seeds gives the error bar.
3. **Read it at two levels.** 50% is the curve's centre, so the most precise estimate, and the line tracked over releases. 80% is what a reader means by "profits from", with a wider bar, and is the quoted number. Whether the 80% bar is tight enough to lead is settled in [next step 2](../../TODO.md#next-steps) with the bots.

**The dial.** Four things could make a round harder to read. One is the dial, and the rest are held fixed within an edition.

| Dial | What gets harder | Why it isn't the dial |
|---|---|---|
| A smaller drop | The signal is fainter | The prize shrinks with the signal. At faint drops the reference bot gains little, so the ratio swings on a small denominator |
| **Less volume a round, a lower N** ✓ | Each round's results are a smaller sample, so they say less. The drop, and the prize, stay loud | |
| Longer weather memory | Bad patches last longer, so they look more like changes | It changes what bad luck means between settings. An edition setting, not the dial |
| Fewer rounds | Less time to catch and profit | It tests speed, and the reference bot's own lag caps it |

The drop is held at 12 points. The maths that turns N, the drop and the weather into evidence a round is written in [next step 1](../../TODO.md#next-steps) and verified with the bots.

**One axis for every edition.** Most benchmarks get replaced when models saturate them: MMLU gave way to MMLU-Pro, and the plot over releases broke. METR's time horizon avoids that because tasks of every length sit on one axis. Evidence a round is our axis. A harder edition, with a lower N or a longer memory, extends it to the left instead of starting a new chart. Two rules keep the join honest, and psychometrics calls the check test equating:

- **Adjacent editions overlap** by two or three settings, so a model's curve crosses from one into the other and the join is checked, not assumed.
- **Models near the top are re-run** on the new edition. A model whose threshold already sits on the axis need not be.

| Reading | What it means |
|---|---|
| On the axis | The noisiest world the model handles at the set level |
| Off the left end | At or above the level at every setting. The edition has saturated for this model, and the remedy is a harder edition |
| Off the right end | Below the level at every setting |

The reference bot scores 1 at every setting by definition, so it sits off the left end. The proof of concept's two change sizes are two points on the same axis, in the same unit against the same bot, so nothing is thrown away when the full grid is run.

Discernment says how much noise a model can profit through. It says nothing about when the model noticed. Where the output went is in [measure-failure.md](measure-failure.md).

## What each model plays

A seed fixes the luck, the weather, when the change starts, the yoked dip, the record and how the game is dressed. On each seed a model holds one briefing, then plays one run where nothing changes and one or more runs with a change. A change has a size, its amplitude: how far the standing unit's level falls, in points. If A0 yields 70 in 100 before and 58 after, the amplitude is 12. 15 is loud and 3 a whisper.

**Proof of concept.** 20 seeds, one briefing and three runs of 40 rounds on each:

- **One no-change run.** Nothing changes, so any doubt here is misplaced, and the yoked dip tempts it.
- **Two change runs**, one at 12 points and one at 5. The faint one is moved to 8 if [next step 1](../../TODO.md#next-steps) finds 5 isn't worth catching.

That is 60 runs and 20 briefings a model. Twenty no-change runs, rather than ten, halve the error bar on the [doubt tax and the false alarm leak](measure-failure.md#where-the-output-went), which are read there.

**Full study.** About 30 seeds. On each, a no-change run and a 12 point change run at each of five noise settings, since the no-change world gets noisier too. That is ten runs a seed and about 300 a model at one setting, with extra runs at the settings where a model starts to miss. Each model also plays at several reasoning settings. Later rungs add the other kinds of change.

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

## Catch rate, a backup

Three backups check the headlines without leaning on the reference bot, and the catch rate needs no true levels either. All three are reported at both tiers, and none is a score.

- **Catch rate.** A change run is caught if the agent switches before the last round and its no-change run has no switch. The noise at which half the runs are caught should rank models the same way as discernment.
- **Sensitivity, d′.** Signal detection theory splits a catch rate into how well the signal is told from noise, called d′, and how readily the alarm is raised. With 20 no-change runs it is a check, not a score.
- **The dot against the CUSUM curve.** The CUSUM bot, swept from hasty to patient, draws the trade between delay and false alarms. Each model is one dot against it.

## What it costs

The target is about $100 a model, since the benchmark is run out of pocket. At the thinking we now expect, it costs more.

**Proof of concept.**

- **Calls.** 60 runs of 40 rounds is about 2,400 calls a model, plus 20 briefings, reads and code calls.
- **Typical prices.** At $4 in and $20 out per million tokens, with prompt caching and 3,000 to 5,000 thinking tokens a round, a run costs about $3 to $4.50, or $180 to $270 a model. A briefing reads the record once and costs about a round.
- **Top prices.** At $10 in and $50 out, about $7 to $11 a run, or $420 to $660 a model.
- **Thinking** is most of the bill, so the pilot, a first run on two models, measures it first. If the figure holds, the choice is a higher target or fewer seeds, settled by the error bars from [next step 2](../../TODO.md#next-steps). We cut seeds rather than thinking, since a model run below its best says little. Bots cost nothing.
- **The no-change run** is the one thing not to cut.
- **The pilot** runs four skins and two history styles on two models over a few seeds, which is where the spreads come from. It is tuning, not the suite.

**Full study.** About 300 runs a model at one reasoning setting, five times the proof of concept: $900 to $1,350 a model at typical prices, before the reasoning sweep and the other kinds of change multiply it. That is a funded figure, and the reason the threshold waits.
