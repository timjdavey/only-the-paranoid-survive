# Headline measures

How good is an agent at telling a change in the dynamics of a system from a run of ordinary bad luck? We measure the headline capability in two ways:

**Performance**
- the simpler proof of concept headline
- fundamentally the top line "score" the agent gets from playing the game
- but pooled over multiple runs
- reported in expected output, with the four [baselines](baselines.md) marked, and as a proportion of the perfect baseline.

**Discernment**
- is a more subtle version that scales with agent capability
- the model plays increasingly difficult games (where the standard variable noise becomes greater)
- we can calculate the line at which it stops detecting or taking advantage of a change (analogous to a hearing test)
- there is a practical upper bound where change and noise are indiscernable, but in theoretical saturation point.

These measures are bundle a few capabilities into one i.e. being able to notice a change, then the tendency and ability to explore & exploit a new strategy. This is by design. As to be economically valuable a model needs all these skills, so it is the most pragmatic measure.

However, when a model fails it is important to know _why_ it failed. There are many skills we need to effectively _stack trace_ against. The design of these can be found in [measure-failure.md](measure-failure.md).


## Baselines

It would be possible to naively compare models performance against each other, which is fine from a relative perspective but we need baselines to understand the models absolute performance.

| Baseline | What it does | What it marks |
|---|---|---|
| Perfect | Told the true rates each round, it plays the best split for them | The ceiling. No model can beat it |
| Bayesian | The best inferrer we can build. It knows how the world works but not the dice, and keeps a belief about every unit and about whether a change has begun | What was knowable, and when. A model may beat it |
| Stale | Holds the best split for the rates before the change to the last round | What stale notes earn |
| Uniform | Splits the budget evenly over the ten units every round | What knowing nothing earns |

Each one is set out on [Baselines](baselines.md). See [Why four baselines, and why the perfect one is the ceiling](decisions.md#why-four-baselines-and-why-the-perfect-one-is-the-ceiling).

## Performance, the proof of concept headline

The model's expected output, pooled over every run on the seed set, change and no-change together.

1. **Score every run on expected output**, what its splits were worth at the true rates with the dice and the weather left out.
2. **Add up** the model's expected output over all its runs.
3. **Report it beside the four baselines' totals** on the same seeds.
4. **Then give it as a proportion** of the perfect baseline's total.

A made-up example:

| Player | Expected output | Proportion of perfect |
|---|---|---|
| Uniform baseline | 236,000 | 0.82 |
| Stale baseline | 274,000 | 0.95 |
| Model P | 279,000 | 0.97 |
| Bayesian baseline | 282,000 | 0.98 |
| Perfect baseline | 288,000 | 1.00 |

Model P acted on the change, but later or less fully than was knowable. [measure-failure.md](measure-failure.md#a-profile-not-a-ranking) says where the 3,000 between it and the Bayesian baseline went.

| Where a model sits | Reading |
|---|---|
| At the perfect line | No split could have earned more |
| Above the Bayesian line | It beat the best inferrer we built |
| Between stale and Bayesian | It acted on the change, but later or less fully than was knowable |
| Below the stale line | Its doubt cost more than it won |

Every run adds what it won, so an early switch beats a late one and a timid switch earns less than a full one. There is no switch cut-off and no rule that throws out a run. See [Why performance is the proof of concept headline](decisions.md#why-performance-is-the-proof-of-concept-headline).

## Why there is a run where nothing changes

A model that moved its split at every wobble would score well if only runs with a change were counted. So every world is played more than once.

A seed is one fixed world: the dice, the weather, the round the change starts, the 200 rounds of record the agent reads before round 1, and the story the game is dressed in, its skin. On each seed a model holds one briefing, where it reads the record and writes its own notes, then plays one run where nothing changes and one or more where something does. We call them the no-change run and the change runs.

In the no-change run, the same unit sags on the same round the change would have started, then recovers on its own. We call this the yoked dip. For the first rounds the two runs look the same, so a model that moves on the dip has moved on bad luck.

The no-change run's output sits in the same total, so a false alarm costs output. The total is also reported split by kind of run, so a reader can see whether a model lost in the change runs or the no-change run. See [Why the yoked dip](decisions.md#why-the-yoked-dip) and [Why one no-change run and a grid per seed](decisions.md#why-one-no-change-run-and-a-grid-per-seed).

## Performance is the arbiter

Every other number answers to performance. Two rules follow.

1. **Every setting must be worth catching.** Pooled over seeds, the Bayesian baseline must beat the stale baseline there by a margin set in `params.yaml`, or [next step 1](../../TODO.md#next-steps) moves it. If updating doesn't pay even for the Bayesian baseline, staying put is right, and a model that stays has shown nothing.
2. **Every [leak and reading](measure-failure.md) must predict performance.** Across baselines built to be too jumpy, too cautious or too hedged, and then across models, a reading that doesn't track performance is dropped.

See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter).

## Why performance can't be the number for ever

Performance tops out at the perfect baseline. Once models get as close to it as inference allows, the plot over releases goes flat. That is fine for a proof of concept, whose one job is to show that the measure separates models with usable error bars at a [cost we can carry](../spec/runs-and-cost.md). No model will be that close by then.

The full study needs a number that keeps moving as models improve. That is why there are two tiers. The game is the same in both, and only the number of runs, the kinds of change and the headline differ. See [Why two tiers](decisions.md#why-two-tiers).

## The hearing test, and why it is the wrong one

The obvious second number is the faintest change a model acts on. A hearing test works that way: it quietens the beep until you stop hearing it, and reports the volume where you did. Make the fall in the unit's rate smaller and smaller, and find where the model stops catching it.

It is the wrong test for us. A quieter change is also a smaller prize, so a model that ignores a change not worth catching is right to. And at faint changes the stale baseline earns nearly what the perfect one does, so there is little room between floor and ceiling and the luck of the seeds swamps it. See [Why discernment is the full study headline](decisions.md#why-discernment-is-the-full-study-headline).

## Speech in noise: keep the change loud, make each round say less

Audiologists have a second test. Speech in noise keeps the words loud and raises the babble behind them, then reports the noise at which you still get half the words right. Discernment is that test. The change stays loud, each round gets noisier, and we find the noise at which the model still gets half of the way from its floor to the perfect baseline.

What makes a round noisier? Each unit's results in a round are a sample: so many bought, so many that paid. A smaller sample says less. So the dial is how much volume a round buys, which the project calls N.

Turn N down and the fall, and the prize, stay loud, while each round's results say less about whether the fall has happened. The fall is held at 12 points of rate.

Three other things could make a round harder to read, and each is held fixed within an edition of the game instead.

| Candidate dial | Why it isn't the dial |
|---|---|
| A smaller fall | The prize shrinks with the signal, which is the hearing test's problem |
| Longer weather memory, so bad patches last longer | It changes what bad luck means between settings. An edition setting, not the dial |
| Fewer rounds | It tests speed, and the Bayesian baseline's own lag caps it |

## Evidence a round, one axis for every edition

N only means something inside one edition of the game. So each setting is published as evidence a round: how much one round's results shift the odds that a change has happened rather than ordinary weather, in bits. One bit doubles the odds, so a world at 0.2 bits a round takes about five rounds to double the odds that something has changed. The maths from N, the fall and the weather to evidence a round is written in [next step 1](../../TODO.md#next-steps) and checked with the baselines.

Most benchmarks are replaced when models saturate them: MMLU gave way to MMLU-Pro, and the plot over releases broke. METR's time horizon avoids that because tasks of every length sit on one axis. Evidence a round is ours. A harder edition, with a lower N or a longer weather memory, extends it to the left instead of starting a new chart.

Two rules keep the join honest, a check that psychometrics calls test equating:

- **Adjacent editions overlap** by two or three settings, so a model's curve crosses from one into the other and the join is checked, not assumed.
- **Models near the top are re-run** on the new edition. A model whose threshold already sits on the axis need not be.

## Discernment, the full study headline

The faintest evidence a round at which the model still gets half of the way from its floor to the perfect baseline. Smaller is better.

1. **At each noise setting, pool the seeds.** Add the model's expected output over the change runs and the no-change runs, as a proportion of the perfect baseline's on the same runs. That is performance at that setting.
2. **Fit a smooth S-shaped curve** of performance against evidence a round, with its lower end left free, and read off where it has risen a set share of the way from that fitted floor to 1. So no floor is chosen by hand. Fitting it is a judgement call, settled in [next step 2](../../TODO.md#next-steps). Resampling the seeds gives the error bar.
3. **Read it at two levels.** 50% is the curve's centre, so the most precise estimate, and the line tracked over releases. 80% is what a reader means by "profits from", with a wider bar, and is the quoted number. Whether the 80% bar is tight enough to lead is settled in [next step 2](../../TODO.md#next-steps) with the baselines.

| Reading | What it means |
|---|---|
| On the axis | The noisiest world the model handles at the set level |
| Off the left end | At or above the level at every setting. The edition has saturated for this model, and the remedy is a harder edition |
| Off the right end | Below the level at every setting |

The perfect baseline is 1 at every setting by definition. The Bayesian baseline gets a curve of its own on the chart, so a reader can see how far a model sits from what was knowable. The proof of concept's two change sizes are two points on the same axis, so nothing is thrown away when the full grid is run.

Discernment says how much noise a model can profit through. It says nothing about when the model noticed. Where the output went is in [measure-failure.md](measure-failure.md).

## Catch rate, a backup

Both headlines lean on the Bayesian and perfect baselines and on our simulation's true rates, so a flaw in any of them would move both. Three backups check them without those, and none is a score.

- **Catch rate.** A change run is caught if the agent moves its largest share to the unit that rose before the last round, and its no-change run has no such switch. The noise at which half the runs are caught should rank models the same way as discernment.
- **Sensitivity, d′.** A catch rate mixes how well the agent tells signal from noise with how readily it raises the alarm. Signal detection theory splits the two and calls the first d′. With one no-change run a seed it is a check, not a score.
- **The dot against the CUSUM curve.** The textbook change detector, called CUSUM, sums how much each round favours a change and fires when the sum crosses a line. Swept from hasty to patient, it draws the trade between delay and false alarms, and each model is one dot against that curve.

## The two tiers at a glance

| | Proof of concept | Full study |
|---|---|---|
| Headline | Performance | Discernment |
| Runs per seed | A briefing, a no-change run and two change sizes | A briefing, then a no-change run and one loud change at each of five noise settings |
| Reasoning | One setting | A sweep |
| Kind of change | One unit's rate falls and another's rises, the level change | Level, then coupling, gain and observation |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | Four skins and two styles of record, tried in the pilot to see if they can be pooled | A real task with a stale handoff note as well |

The kinds of change are the four blocks of [the generator](../spec/mechanics.md#the-generator). Seed counts, run totals and cost are in [runs-and-cost.md](../spec/runs-and-cost.md).

## What each model plays

A change has a size, its amplitude: how far the standing unit's rate falls, in points. If it yields 70 in 100 before and 58 after, the amplitude is 12. 15 is loud and 3 a whisper.

**Proof of concept.** On each seed, one briefing and three runs:

- **One no-change run.** Nothing changes, so any doubt here is misplaced, and the yoked dip tempts it.
- **Two change runs**, one at 12 points and one at 5. The faint one is moved to 8 if [next step 1](../../TODO.md#next-steps) finds 5 isn't worth catching.

**Full study.** On each seed, one briefing, then a no-change run and a 12 point change run at each of five noise settings, since the no-change world gets noisier too. Extra runs go where a model starts to miss.

Every run at either tier plays the same game, set out in [mechanics.md](../spec/mechanics.md): 40 rounds, a change that starts between round 3 and round 10 and ramps over about 15, a 200 round record written by the Bayesian baseline, the same dice and weather for every run on a seed, four public skins with private ones held back, and a sandboxed code tool.

