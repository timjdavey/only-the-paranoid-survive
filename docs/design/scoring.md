# Scoring

## How we score

- **Each round the agent bets a fixed budget across channels**, see [interface](interface.md). Its bets are its belief: a small bet on a channel is a look, a large one is a switch.
- **A run scores output as a fraction of what the [oracle](baselines.md), which knows each round's levels, would earn on the same seed.** This sits between 0 and 1 and strips out luck in the world's levels.
- **A scenario score is the plain mean of its runs.** Every model plays the same seeds, see [below](#seeds). The gap reads directly as the scenario's failure mode: in the No change scenario it is jumpiness, in the One shock scenario overreaction, in the One switch scenario underreaction.
- **The headline is the geometric mean across [scenarios](scenarios.md).** A model must do well on every shape to score highly. One bad scenario drags the whole figure down.

## Seeds

- **A seed fixes the world.** It draws every channel's noise for every round up front, bet on or not, so two agents on one seed see the same world and differ only by what they do. The oracle runs on it too.
- **One fixed set of seeds per scenario, the same set for every model.** A model is compared with a rival on the same worlds, not on a different roll of the dice, so the gaps between models are tighter.
- **The headline plays the held-out seeds.** Public seeds are for checking our work, and the gap between the two is reported beside the headline. See [contamination](../harness/contamination.md#two-seed-sets).
- **Each seed is played once.** A seed whose noise looks like a switch for a few rounds is one world among many, and the mean absorbs it. How many seeds, and whether a model's own sampling needs repeats on top, is for the [pilot](../pilot/checks.md#seeds).

## Why a mean within and a geometric mean across

- **Seeds are one question asked many times**, so we want the expected value. A geometric mean over seeds would punish one unlucky world, which is noise, not a trait.
- **Scenarios are different questions** and we want an AND. The geometric mean makes one bad trait pull the headline down, where a plain mean would let a strong trait hide it.

## Error bars

- **An error bar says how sure we are of a score** (epistemic uncertainty). It is the [spread](#spread) divided by the square root of the number of seeds, so more seeds shrink it. It points at the true mean, which we never see, but it is computed from the runs we have.
- **Scenario.** Resample the seeds with replacement, take the plain mean each time, and report the 2.5th and 97.5th percentiles (a percentile bootstrap). Not SD/√n: run scores sit in [0, 1] and bunch near 1 in the No change scenario, and a bootstrap can never put a bar above 1. No geometric mean at this level.
- **Headline.** Resample seeds within each scenario, then take the geometric mean of the scenario means. Never resample scenarios. They are a fixed list of questions, not a sample.
- **The weakest scenario sets the bar.** In logs each scenario adds its relative error, bar over score. A scenario at 0.3 ± 0.05 widens the headline far more than one at 0.9 ± 0.05.
- **Gaps between models.** Every model plays the same seeds, so draw one set of seed indices and apply it to both models each time. The world's luck cancels. Report the difference with its paired interval.
- **The unit is the seed.** If a seed is ever played more than once, average its repeats first and resample seeds, not runs. Pooling repeats counts one world twice and shrinks the bar falsely.

## Spread

- **Spread says how far one run lands from another** (aleatoric uncertainty). It does not shrink with more seeds, it only gets estimated better. Spread and error bar come from the same runs: the SD of the run scores is the spread, and that SD over √n is the error bar.
- **Two sets of dice.** World spread, from the seed, and sampling spread, from the model's own draws. Played once per seed the two are mixed, and the error bar is still honest for "a fresh run on a fresh world". The [pilot](../pilot/checks.md#repeats) measures the split once and we report it as a number, such as "two fifths of the spread in the One shock scenario is sampling".
- **Why it is reported, not just absorbed.** Two models can share a mean while one nails 15 seeds and tanks 5 and the other is middling everywhere. Consistency is close to a trait here: overreacting on some worlds and not others is jumpiness.
- **How it is shown.** A strip of per-seed run scores next to each scenario's bar, and the 10th percentile run score beside the mean.
- **Why the headline still plays each seed once.** For a fixed run budget, more seeds always shrinks the error bar faster than repeats of a seed. Repeats only buy the split.
- **Skins are a sensitivity, not an error.** If a model scores 0.8 on one story and 0.6 on another with the same engine and seed, that is a finding: the story swayed it (skin sensitivity). Averaging skins and widening the bar would hide the most interesting number, so skins are never resampled and never pooled into a headline. **The proof of concept runs one skin**, so skin sensitivity is a named layer we do not measure yet. When more skins run, each gets its own headline and the gap between them is reported beside it.
- **Scenario differences are not spread either.** A gap between scenarios is the signal (trait profile). It gets no bar and is never resampled.

| Name | What changes between runs | Kind | Where it shows |
|---|---|---|---|
| Level luck | The channels' levels | Noise, removed by the oracle on the same seed | Nowhere, by design |
| Sampling spread | Nothing. Same seed, same skin, run again | Aleatoric, more seeds don't shrink it | A share of the spread, from the pilot |
| World spread | The seed | Aleatoric, more seeds don't shrink it | The per-seed dots |
| Spread | The seed, each played once, so both mixed | Aleatoric, more seeds don't shrink it | The dots and the 10th percentile run |
| Error bar | Our estimate of the mean | Epistemic, more seeds shrink it | Every scenario score and the headline |
| Skin sensitivity | The story, with engine and seed fixed | A finding, more seeds don't shrink it | A gap per skin, outside the headline. Not measured in the proof of concept, which runs one skin |
| Trait profile | The scenario | The signal, more seeds don't shrink it | The per-scenario scores |

## Extension: inertia

- **A fixed budget is forgiving.** A model that never moves still earns most of the output, so being late costs less than it cost Kodak.
- **A cap on how far bets can move each round** would amplify the lateness signal. It is switched on only if the [pilot](../pilot/checks.md#inertia) finds the base score too flat.
