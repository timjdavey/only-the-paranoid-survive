# Scoring

## How we score

- **Each round the agent bets a fixed budget across channels**, see [interface](interface.md). Its bets are its belief: a small bet on a channel is a look, a large one is a switch.
- **A scenario score is the share of the gap between two baselines that the model earned**, on the same seeds:

      scenario score = (model − Uniform) ÷ (Discerning − Uniform), each summed over seeds

- **Zero is knowing nothing and one is knowing the climate.** The [Uniform baseline](baselines.md) bets evenly and learns nothing. The [Discerning baseline](baselines.md) knows every channel's base level, so it holds through a shock and moves the round a switch lands. The score is the share of the value of that knowledge the model captured.
- **Seeds are pooled, not scored one by one.** Add up the model's gain over every seed and divide by the total gap, so a seed with more on offer counts for more. See [pooling seeds](#pooling-seeds).
- **The Complacent baseline is a mark on every bar, not the floor.** Where there is a switch it lands near 0.55, so a model below the mark is visibly complacent and a model above it has acted. Where there is no switch it sits at 1 with the Discerning baseline.
- **The headline is the plain mean across [scenarios](scenarios.md)**, reported with the weakest trait named beside it. A negative scenario score counts as it is. The mean says how good a model is overall, and the weakest trait says where it fails.

A worked Down switch run, output over 40 rounds:

| Player | Output | Scenario score |
|---|---|---|
| Uniform baseline | 1,720 | 0.00 |
| Complacent baseline | 2,300 | 0.56 |
| A model | 2,500 | 0.76 |
| Discerning baseline | 2,750 | 1.00 |
| Perfect baseline | 2,900 | A mark, not a score |

The model's missing 0.24 is lag, looks and a wrong destination. None of it is weather.

## Why these two baselines

- **The Discerning baseline is reachable.** It knows the climate, not the weather, so its only edge over an ideal reader is zero lag, and lag is what we want to price. The Perfect baseline knows each round's weather too, so part of the gap to it is luck nobody could read. It stays in the table as a mark for how much luck was on offer, and divides nothing.
- **The Uniform baseline is not a strategy.** It is what knowing nothing earns, so it needs no case per scenario and it is the same floor for any scenario we add. The Complacent baseline would give more range where there is a switch, but it equals the Discerning baseline where there is not, which makes the ratio 0 ÷ 0.
- **The denominator never gets close to zero.** The Discerning baseline holds the leader or better and the Uniform baseline earns the average of ten channels, and the ladder puts the leader well above that average on every seed.
- **Scores outside 0 to 1 are possible on one seed.** Lucky weather can lift a run above the Discerning baseline, and a run can fall below the Uniform baseline. Both are reported as they come. Pooled over seeds they wash out, and the [baseline order](../pilot/engine-checks.md#baseline-order) check reports any player that sits above the Discerning baseline where nothing changes.
- **A yardstick must not peek.** A Bayesian yardstick that sees only what the agent saw depends on what the agent chose to look at, so a lazy agent gets a lenient yardstick. Bayesian, CUSUM and the hedge rule are fine as [players](baselines.md) with their own marks. Only the denominator must be independent of the agent's play.

## Traits

Each scenario tests one trait, named as the virtue a high score shows. A low score is that trait's failure mode.

| Scenario | Trait | What a high score means | Failure mode |
|---|---|---|---|
| [No change](scenarios.md#scenarios-we-test) | Composure | Ignores noise when nothing is happening | False alarms |
| [One shock](scenarios.md#scenarios-we-test) | Patience | Holds through a dip that passes | Overreaction |
| [Down switch](scenarios.md#scenarios-we-test) | Doubt | Questions the plan when the change is real | Underreaction |
| [Up switch](scenarios.md#scenarios-we-test) | Curiosity | Looks at the field when nothing is wrong | Contentment: the old plan still pays, so it never looks |
| [Shock then switch](scenarios.md#scenarios-we-test) | Unlearning | Drops "dips recover" once it stops being true | Learned complacency |
| [Slow drift](scenarios.md#scenarios-we-test) | Vigilance | Notices a decline that has no sudden move | Boiling frog: never acts, as no single round looks bad |
| [Switch then shock](scenarios.md#scenarios-we-test) | Conviction | Holds a plan it just chose through a dip that passes | Second thoughts: the first bad round on the new plan sends it back to the old one |
| [Up switch then down switch](scenarios.md#scenarios-we-test) | Recall | Goes back to a plan it has seen pay when the change undoes itself | Burnt bridges: treats the old leader as finished, so relearns a climate it has already seen, or never returns |
| [One boom](scenarios.md#scenarios-we-test) | Perspective | Judges a fall from a peak against the long record, not the peak | Anchoring: reads the end of a good spell as a decline, and moves |
| [Up drift](scenarios.md#scenarios-we-test) | Diligence | Keeps looking long enough for a slow rise to add up | A glance, not a watch: one look shows nothing, so the looking stops |
| [Short rise](scenarios.md#scenarios-we-test) | Selectivity | Moves only for a rise that beats the plan | Distraction: chases a channel that is improving but still worse |

- **Composure and patience differ.** Composure ignores noise when nothing is happening. Patience holds through a real dip that passes.
- **Composure and curiosity pull against each other.** Every look costs in the No change scenario and is the only way to score in the Up switch scenario. A model buys one with the other unless its looks are small and steady.
- **Curiosity and selectivity pull the other way.** The look that finds the sleeper in the Up switch scenario tempts a move in the Short rise scenario, where the sleeper never passes the leader.
- **Conviction and recall pull against each other.** A model that always goes back scores in the Up switch then down switch scenario and not in the Switch then shock scenario. One that never goes back does the reverse.
- **The trait profile is the eleven scores side by side.** The headline averages them, so the weakest trait is named beside it: a model can buy one trait with another in the mean, but not in that number.
- **Four scenarios ask the agent to hold and seven ask it to move.** Holding is right throughout the No change, One shock, One boom and Short rise scenarios, so the Complacent baseline sits at 1 in each. Equal weights are still the prior, see [limits](limits.md).

## Seeds

- **A seed fixes the world.** It draws every channel's noise for every round up front, bet on or not, so two agents on one seed see the same world and differ only by what they do. The baselines run on it too.
- **One seed, twin tapes.** Seed *i* draws the same ladder, weather and onset round in every scenario, so the One shock and Down switch tapes match until the event begins and differ only in what it is. A model's gap between the two is paired on one world, and a move at onset reads as a hit on one tape and a false alarm on the other.
- **One fixed set of seeds per scenario, the same set for every model.** A model is compared with a rival on the same worlds, not on a different roll of the dice, so the gaps between models are tighter.
- **The headline plays the held-out seeds.** Public seeds are for checking our work, and the gap between the two is reported beside the headline. See [contamination](../harness/contamination.md#two-seed-sets).
- **Each seed is played once.** A seed whose noise looks like a switch for a few rounds is one world among many, and the pool absorbs it. How many seeds, and whether a model's own sampling needs repeats on top, is for the [pilot](../pilot/provider-checks.md#seeds).

## Pooling seeds

A scenario score adds up gains across seeds and then divides once. It is not the plain mean of the run scores.

- **The gap** on a seed is how much more the Discerning baseline earns than the Uniform baseline. It is all there was to gain.
- **The gain** is how much more the model earns than the Uniform baseline.
- **The run score** is one seed's gain divided by its gap. It is the dot on the strip, see [spread](#spread).

Two Down switch seeds. Each seed draws its own switch size and timing, so one has more on offer:

| Seed | Uniform | Discerning | Gap | Model | Gain | Run score |
|---|---|---|---|---|---|---|
| A, big early switch | 1,700 | 2,800 | 1,100 | 2,580 | 880 | 0.80 |
| B, small late switch | 1,700 | 2,250 | 550 | 1,920 | 220 | 0.40 |
| Both, pooled | | | 1,650 | | 1,100 | 0.67 |

- **Pooled, the scenario score is 0.67.** (880 + 220) ÷ (1,100 + 550). The model missed 550 of the 1,650 on offer, a third.
- **A plain mean of run scores would say 0.60.** (0.80 + 0.40) ÷ 2. That gives seed B as much say as seed A, though it had half as much to win.
- **Pooling is a mean weighted by gap.** Seed A has twice the gap, so its run score counts twice as much. A point missed counts the same whichever seed it was missed on.
- **A small gap gets a small say.** A run score can land well outside 0 to 1 on one seed, but its weight is its gap, so it can't swing the scenario score far.

## Why a pool within and a plain mean across

- **Seeds are one question asked many times**, so we want the expected gain. [Pooling](#pooling-seeds) is that gain, weighted by what each world had on offer. A geometric mean over seeds would punish one unlucky world, which is noise, not a trait.
- **Scenarios are different questions in one unit.** Every scenario score is a share of the same kind of gap, so adding them means something. A plain mean with equal weights is the simplest prior to state, and a reader with a base rate can reweight the profile, see [limits](limits.md).
- **Why not a geometric mean.** It cannot take a negative score, and flooring at 0 makes a near miss and a disaster read the same. It only differs from the plain mean when one scenario sits far below the rest, which is the case where it breaks. The weakest trait gives that AND as a second number without the maths problem.

## Error bars

- **An error bar says how sure we are of a score** (epistemic uncertainty). It shrinks with more seeds. It points at the true score, which we never see, but it is computed from the runs we have.
- **Scenario.** Resample the seeds with replacement, recompute the pooled ratio each time, and report the 2.5th and 97.5th percentiles (a percentile bootstrap). Not SD/√n: a ratio is not a mean, and run scores bunch near 1 in the No change scenario.
- **Headline.** Resample seeds within each scenario, then take the plain mean of the scenario scores. Never resample scenarios. They are a fixed list of questions, not a sample. The weakest trait's bar is that scenario's bar.
- **The weakest scenario sets the bar.** In logs each scenario adds its relative error, bar over score. A scenario at 0.3 ± 0.05 widens the headline far more than one at 0.9 ± 0.05.
- **Gaps between models.** Every model plays the same seeds, so draw one set of seed indices and apply it to both models each time. The world's luck cancels. Report the difference with its paired interval.
- **The unit is the seed.** If a seed is ever played more than once, average its repeats first and resample seeds, not runs. Pooling repeats counts one world twice and shrinks the bar falsely.

## Spread

- **Spread says how far one run lands from another** (aleatoric uncertainty). It does not shrink with more seeds, it only gets estimated better. It is the SD of the run scores, each seed's own share of the gap.
- **Two sets of dice.** World spread, from the seed, and sampling spread, from the model's own draws. Played once per seed the two are mixed, and the error bar is still honest for "a fresh run on a fresh world". The [pilot](../pilot/provider-checks.md#repeats) measures the sampling share once and we report it as a number, such as "two fifths of the spread in the One shock scenario is sampling".
- **Why it is reported, not just absorbed.** Two models can share a score while one nails 15 seeds and tanks 5 and the other is middling everywhere. Consistency is close to a trait here: overreacting on some worlds and not others is poor composure.
- **How it is shown.** A strip of per-seed run scores next to each scenario's bar, and the 10th percentile run score beside it.
- **Why the headline still plays each seed once.** For a fixed run budget, more seeds always shrinks the error bar faster than repeats of a seed. Repeats only buy the sampling share.
- **Skins are a sensitivity, not an error.** If a model scores 0.8 on one story and 0.6 on another with the same engine and seed, that is a finding: the story swayed it (skin sensitivity). Averaging skins and widening the bar would hide the most interesting number, so skins are never resampled and never pooled into a headline. **The proof of concept runs one skin**, so skin sensitivity is a named layer we do not measure yet. When more skins run, each gets its own headline and the gap between them is reported beside it.
- **Scenario differences are not spread either.** A gap between scenarios is the signal (trait profile). It gets no bar and is never resampled.

| Name | What changes between runs | Kind | Where it shows |
|---|---|---|---|
| Level luck | The channels' levels | Noise. Every player on a seed meets the same levels, so pairing by seed cancels it | The gap between the Perfect and Discerning baselines says how much there was |
| Sampling spread | Nothing. Same seed, same skin, run again | Aleatoric, more seeds don't shrink it | A share of the spread, from the pilot |
| World spread | The seed | Aleatoric, more seeds don't shrink it | The per-seed dots |
| Spread | The seed, each played once, so both mixed | Aleatoric, more seeds don't shrink it | The dots and the 10th percentile run |
| Error bar | Our estimate of the score | Epistemic, more seeds shrink it | Every scenario score and the headline |
| Skin sensitivity | The story, with engine and seed fixed | A finding, more seeds don't shrink it | A gap per skin, outside the headline. Not measured in the proof of concept, which runs one skin |
| Trait profile | The scenario | The signal, more seeds don't shrink it | The per-scenario scores |

## Noise threshold

The full study headline. The proof of concept reports the headline at one noise setting. The full study plays a [noise grid](../pilot/engine-checks.md#noise-grid) and reports where the model gives out, the way a hearing test raises the babble behind the words until you stop catching them.

- **Keep the prize loud, raise the noise.** On the grid every event is pinned in level points, so the gain the Discerning baseline makes over the Complacent baseline is the same at every setting. Only the weather scale moves, see [difficulty](mechanics.md#difficulty). A fainter change would be a smaller prize, and a model that ignores a change not worth catching is right to.
- **The axis is signal to noise**: the switch size in level points over the weather's SD per round. It means the same thing in every release, so a harder release extends the grid to lower settings instead of starting a new chart.
- **At each setting, compute the headline.** The No change and One shock scenarios get harder with noise too, as rougher readings tempt more false alarms, so false alarms cost inside the sweep too.
- **In the Up switch scenario a look fights two noises**, the weather and the read noise at the look's size. The [reading roughness](../pilot/engine-checks.md#reading-roughness) setting matters most there.
- **The Complacent baseline is the reference floor.** Its headline does not move with noise, as it never reads anything. Fit a logistic curve of the model's headline against the log of signal to noise and read off the setting at which the model sits half way between the Complacent baseline's headline and 1. That is the noise threshold: the noisiest world the model still reads. Lower is better. Report the 80% crossing beside it, as METR does.
- **The crossing does not depend on the floor.** Half way from the Complacent to the Discerning baseline is the same world whether the scale starts at the Uniform baseline or at the Complacent one.
- **Error bar.** Resample seeds at every setting and refit.
- **Off the grid.** A model that never crosses within the grid reads "off the quiet end" (saturated, extend the grid) or "off the noisy end", never a number.
- **Releases join on the axis.** Adjacent releases overlap by two settings, and a fixed set of anchor models is rerun on each.
- **The grid is set from baselines, not models.** The pilot places it so the hedge rule and Timestral baselines span a full curve, before any model runs.

## Extension: inertia

- **A fixed budget is forgiving.** A model that never moves still earns most of the output. The scenario score prices that: the Complacent baseline sits near 0.55 where there is a switch, so never moving forfeits nearly half the range on its own.
- **A cap on how far bets can move each round** would amplify the lateness signal further. It is switched on only if the [pilot](../pilot/provider-checks.md#inertia) still finds the gaps between models too small to read.
