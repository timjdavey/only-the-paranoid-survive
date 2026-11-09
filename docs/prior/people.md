# People, and ideal observers

Long before LLMs, psychologists asked how people and animals tell a passing blip from a real change. This page holds seven studies of people, one of rats, and three methods papers on the maths of spotting a change as it happens. Those methods are the blueprint for a Bayesian baseline, which is [parked for now](../design/baselines.md#not-yet).

- **People err both ways, and the world predicts which.** They overreact when the world is stable and the signals are noisy, and underreact when it is the reverse ([Massey and Wu](#massey-and-wu-2005-system-neglect)). Our No change and One shock scenarios are the stable, noisy case.
- **A long calm past slows people and rats down.** Rats that have seen no change for many sessions are slow to notice one ([Gallistel 2001](#gallistel-et-al-2001-rats-that-have-seen-no-change)). That is the habit our Shock then switch scenario tests.
- **An ideal observer is easy to write down and hard to fit to our game.** The standard methods assume fresh noise and sudden jumps. Our weather has persistence and our switches ramp.

## Behrens et al. 2007: people learn faster when the world is volatile

Behrens et al. "Learning the value of information in an uncertain world." Nature Neuroscience 10(9): 1214 to 1221, 2007. [doi:10.1038/nn1954](https://doi.org/10.1038/nn1954)

**In short.** People weight new results more when the world changes often, about as much as an ideal learner would. The effect is weaker than the headline suggests.

**What they did.**

- People pick blue or green, and one is right each trial. They were told only that the odds depend "only on the recent outcome history".
- **Experiment 1.** 18 people. A stable phase of 120 trials with blue right 75% of the time, and a volatile phase of 170 trials where the 80% colour swapped every 30 or 40 trials.
- **Experiment 2.** 18 people in an fMRI scanner, 60 stable and 60 volatile trials.
- **The learner.** A Bayesian model that tracks the chance of reward, how fast it drifts (volatility) and how fast that drift changes. It has no free learning rate.

**What they found.**

- Learning rates were higher in the volatile phase (t(17) = 2.91, P < 0.005), whichever phase came first.
- The Bayesian learner's rates fell within one standard error of people's. It predicted choices better than reinforcement learning models with 18 or 36 free parameters.
- Volatility was tracked in the anterior cingulate cortex. People with a stronger signal there had higher learning rates (r² = 0.27).

**Watch out for.**

- In the fMRI experiment the effect only "survived as a trend". A later reanalysis in PLOS Computational Biology found it significant only under some models (t(34) ≈ 2.1, p ≈ 0.04).
- "Learn faster" means a higher learning rate, not better scores.

**Why it matters here.**

- **The Shock then switch scenario asks the reverse question.** Behrens says seeing change should make you quicker to update. A model that held through a shock may instead learn "dips recover" and get slower. See [scenarios](../design/scenarios.md#scenarios-we-test).
- **Repeated shocks, which we skip, is this study's design.** Whether models get calmer or jumpier is the habituation question in [scenarios we skip](../design/scenarios.md#scenarios-we-skip).

## Adams and MacKay 2007: Bayesian online change point detection

Ryan Prescott Adams and David J. C. MacKay. "Bayesian Online Changepoint Detection." Technical report, Cambridge, 2007. [arXiv:0710.3742](https://arxiv.org/abs/0710.3742)

**In short.** An exact way to spot change points one data point at a time, as they happen, rather than looking back afterwards.

**How it works.**

- It keeps a probability for every run length, the number of turns since the last change.
- Each turn a run grows by one, or resets to zero with a fixed chance called the hazard.
- Runs whose data predicted the next point well gain weight.
- The hazard is set by hand in every example. Results are shown as figures, with no scores.

**Why it matters here.** This would be the core of a Bayesian baseline, run on each channel's level. That baseline is [parked](../design/baselines.md#not-yet), and these are the catches it would have to handle in our [generator](../design/mechanics.md#generator):

- **It doesn't know which way a change goes.** A rise counts as much as a fall. That suits a sleeper, which rises. But the hedge also rises in every shock, and the method would read that as a change too.
- **It assumes fresh noise.** Our weather has persistence, so three bad rounds in a row are ordinary. Run on raw levels, it would see a change in every bad stretch.
- **It assumes one channel at a time.** A shock moves every channel through the shared factor. Run per channel, it would call a change in all ten at once, unless it models the factor.
- **It assumes jumps.** A switch ramps over 1 to 5 rounds and a drift over many more, so early on no single run length fits well. This mirrors Wilson's point below about Behrens, who assumed drift where the task jumped.
- **It assumes changes arrive at random** at a constant rate. Our scenarios hold a set list of events. The method is exact under its own model, not under how we build the tapes.

## Wilson, Nassar and Gold 2010: learning the hazard rate

Robert C. Wilson, Matthew R. Nassar and Joshua I. Gold. "Bayesian Online Learning of the Hazard Rate in Change-Point Problems." Neural Computation 22(9): 2452 to 2476, 2010. [doi:10.1162/NECO_a_00007](https://doi.org/10.1162/NECO_a_00007)

**In short.** Adams and MacKay need the hazard fixed in advance, and the answer can depend strongly on that choice. This paper learns the hazard from the data as it goes.

**How it works.**

- **Change points known.** Count them under a Beta prior. The hazard estimate is changes so far plus a₀, over turns so far plus a₀ + b₀ (section 3.1).
- **Change points unknown.** Track run length and the number of changes together, each branch with its own hazard estimate (section 3.2). This is the paper's main contribution.
- **Hazard that changes.** A higher level process now and then redraws the hazard (section 4).
- They also show Behrens's learner is not the true ideal observer, because it assumes slow drift where the task had sudden jumps.

**Why it matters here.**

- **It removes a dial.** The [parked baseline](../design/baselines.md#not-yet) is parked partly because its hazard prior is a dial we would have to fix in advance. Learning the hazard from the run is the alternative.
- **It is how a shock could teach complacency the right way.** A learner that counts changes, and correctly counts a shock as no change, ends the shock with a lower hazard. So it is slower to call the later switch, for a good reason. A model that is slower for the wrong reason is what the [Shock then switch scenario](../design/scenarios.md#scenarios-we-test) looks for.

## Mellor and Shapiro 2013: Thompson sampling with a change detector

Joseph Mellor and Jonathan Shapiro. "Thompson Sampling in Switching Environments with Bayesian Online Change Detection." AISTATS, PMLR 31: 442 to 450, 2013. [arXiv:1302.3721](https://arxiv.org/abs/1302.3721). arXiv version read.

**In short.** Thompson sampling plays a bandit that never changes very well. This paper bolts on Adams and MacKay's change detector so it copes when payoffs switch, either on every arm at once or on one arm at a time.

**What they did.**

- **The world.** Arms pay 1 or 0. At a constant rate a payoff jumps to a fresh draw, either on all arms at once (global) or on each arm on its own (per arm).
- **The detector.** Adams and MacKay's belief over run length, cut to a fixed number of particles (Section 3.1.1).
- **The play.** Sample a run length, sample each arm's payoff from data since then, and pull the arm with the highest sample (Algorithm 1).
- **Variants.** Global-CTS and PA-CTS (per arm). "NP" versions learn the switching rate by Wilson's method (Section 5). "2" versions update only the arm they pull (Section 6).
- **Tests.** Four made-up worlds and two from real data, Yahoo! clicks and exchange rates. Made-up runs are 10^6 steps, repeated 100 times, scored by how often a worse arm was pulled.

**What they found.**

| World | Result, in thousands of wrong pulls |
|---|---|
| All arms switch, rate 10^-4 (Table 1) | Global-CTS 5.9, DiscountedUCB 15.5, UCB 178.3 |
| Each arm switches (Table 2) | PA-CTS 13.0, DiscountedUCB 16.8, UCB 175.1 |
| Slow drift, no jumps (Table 3) | Best CTS 94.8, DiscountedUCB 162.4, UCB 194.5 |
| PASCAL 2006 challenge (Table 4) | Global-CTS 67.2, Global-CTS2 35.8, winner Adapt-EvE 34.7 |

- Each version does best in the world it assumes.
- Learning the rate cost little when all arms switch (6.7 against 5.9, Table 1) but a lot when each arm switches (30.8 against 13.0, Table 2). The authors suspect the rate was "not being learned quickly enough".
- On exchange rates every CTS version made about 350 to 380 thousand errors, against about 610 for UCB and DiscountedUCB and 623 for random (Table 6). On Yahoo! clicks the best, Global-CTS2, scored 0.443 against 0.526 for UCB, with error bars of 0.03 to 0.04 (Table 5).

**Watch out for.** Nothing proves it works. The authors say theory is still needed.

**Why it matters here.**

- **Global and per arm is our shock and switch.** A shock moves every channel through the shared factor. A switch moves one. Each version here wins only in its own world, so a baseline for our suite has to hold both, as the [events](../design/mechanics.md#events) do.
- **An arm left alone grows more uncertain, so it sometimes gets a look.** That is the property a [parked Bayesian baseline](../design/baselines.md#not-yet) would rely on. Don't copy the "2" trick: there an arm left alone stops growing uncertain, and a sleeper rises while unfunded, so it might never be looked at.
- **Learning a rate per arm was costly.** One channel falling in a switch is the per arm case. That backs a hazard prior fixed in advance over one learnt per channel.
- **It pulls one arm.** Our agent splits its bets, and a small bet gives a rough reading ([what the agent sees](../design/mechanics.md#what-the-agent-sees)). Nothing here tests turning a sample into bets.

## Bleser et al. 2026: true and false beliefs about volatility

Bleser et al. "The Impact of Prior Beliefs about Volatility on Adaptive Behavior." Journal of Cognition 9(1): 32, 2026. [doi:10.5334/joc.504](https://journalofcognition.org/articles/10.5334/joc.504)

**In short.** Telling people the rule will or won't change alters how they learn, even when what you told them is false. A false warning of change makes them switch more in a world that stays put.

**What they did.**

- A tone predicts which side a target appears on, 70% of the time. In a reactive version people respond to the target. In a predictive version they guess its side first.
- Stable blocks keep the rule. Reversal blocks flip it once, halfway.
- Each block opens with "The rule in this block will stay the same" or "will change once". Half are false, in both directions.
- 32 people, with 4 blocks of 80 trials per task.

**What they found.**

- The instructions mattered only in the predictive task.
- A false "it will stay the same" lowered the learning rate in reversal blocks (t(31) = 3.6, p = 0.001), though a trial by trial look showed these people adapting sooner.
- A false "it will change" in stable blocks cut accuracy, raised switching and made choices noisier, without changing the learning rate.
- People spotted false instructions 87 to 90% of the time.

**Why it matters here.**

- **Our prompt never mentions change** ([interface](../design/interface.md#how-the-agent-plays)), so we don't plant a warning. But a model that decides "the rules may have changed" has issued itself one. Bleser predicts what a false one does: more switching and noisier bets in a stable world. The No change and One shock scenarios price exactly that.
- **Asking can change the answer.** The effect showed only when people had to predict. That is one reason we don't ask the agent for a chance that the world changed ([interface rejected](../design/interface.md#rejected)).

## Massey and Wu 2005: system neglect

Cade Massey and George Wu. "Detecting Regime Shifts: The Causes of Under- and Overreaction." Management Science 51(6): 932 to 947, 2005. [doi:10.1287/mnsc.1050.0386](https://doi.org/10.1287/mnsc.1050.0386). Abstract and summaries read.

**In short.** People react mainly to the signals in front of them and too little to the system that makes them. The authors call this system neglect, and it predicts which way people err from the world alone.

**What they did.** People watch signals from a system that may have switched regime and say how likely the switch is. The experiments vary how informative each signal is and how likely a switch is, against the Bayesian answer.

**What they found.**

- People underreact in unstable systems with precise signals, and overreact in stable systems with noisy signals.
- Kremer, Moritz and Siemsen 2011 (Management Science 57(10): 1827 to 1843, [doi:10.1287/mnsc.1110.1382](https://doi.org/10.1287/mnsc.1110.1382), abstract read) found the same in demand forecasting, with the bigger loss in stable worlds.

**Why it matters here.**

- **It is the clearest prediction of which way an agent errs.** The No change and One shock scenarios are stable systems with noisy signals, so system neglect predicts false alarms there. A switch at low noise is the other corner, where it predicts a late move. See [scenarios](../design/scenarios.md#scenarios-we-test).
- **Our noise dials move the game across their map.** The [pilot](../pilot/checks.md#noise-grid) sets own-weather scale, persistence and shared-factor scale, so we can check whether the error flips with them.

## Brown and Steyvers 2009: naming a change versus predicting through it

Scott D. Brown and Mark Steyvers. "Detecting and Predicting Changes." Cognitive Psychology 58(1): 49 to 67, 2009. [doi:10.1016/j.cogpsych.2008.09.002](https://doi.org/10.1016/j.cogpsych.2008.09.002). Abstract and summaries read.

**In short.** People track a hidden state that jumps about as well as a Bayesian with the wrong idea of how often it jumps. They do worse when asked to predict the next outcome than when asked to name the current state.

**What they did.** Outcomes come from one of several hidden sources, which switches now and then. People either name the current source or predict the next outcome, which have the same right answers. A particle filter with an assumed change rate is fitted to each person.

**What they found.**

- People did much worse when predicting than when naming and, by secondary accounts, switched more.
- Many were close to optimal given their own assumed change rate. The rate was simply wrong.

**Why it matters here.**

- **How you ask changes the play.** With Bleser, this is why we only ask for bets and never for a view on change ([interface rejected](../design/interface.md#rejected)).
- **Right method, wrong rate** is the hazard problem in [Wilson](#wilson-nassar-and-gold-2010-learning-the-hazard-rate), seen in people.

## Gallistel et al. 2001: rats that have seen no change

Gallistel et al. "The Rat Approximates an Ideal Detector of Changes in Rates of Reward: Implications for the Law of Effect." Journal of Experimental Psychology: Animal Behavior Processes 27(4): 354 to 372, 2001. [doi:10.1037/0097-7403.27.4.354](https://doi.org/10.1037/0097-7403.27.4.354). Abstract read.

**In short.** Rats notice a change in which lever pays best about as fast as an ideal detector, unless they have gone many sessions with no change. Then they are slow, and slip back to the old habit.

**What they did.** Rats pressed two levers for brain-stimulation reward. The ratio of the two reward rates changed between or within sessions, and their switching was compared with an ideal detector.

**What they found.** When changes were frequent, rats adjusted about as fast as the ideal detector. After "many successive sessions with unchanging relative rates of reward", they adjusted slowly and slipped back to the old pattern at the start of later sessions.

**Watch out for.** Abstract only, so we have no numbers on how big the slowing was.

**Why it matters here.**

- **This is learned complacency in animals.** A long past with no change slowed detection. That is the habit the [Shock then switch scenario](../design/scenarios.md#scenarios-we-test) sets up, and the reason the [pilot](../pilot/checks.md#game-length-and-switch-round) wants enough calm rounds before a change to set a habit.
- **The open question is whether the slowing is rational.** An ideal detector that learns the change rate would also slow down. Whether models slow down more than that is what we'd ask.

## Nassar et al. 2010: a learning rate that rises with surprise

Matthew R. Nassar, Robert C. Wilson, Benjamin Heasly and Joshua I. Gold. "An Approximately Bayesian Delta-Rule Model Explains the Dynamics of Belief Updating in a Changing Environment." Journal of Neuroscience 30(37): 12366 to 12378, 2010. [doi:10.1523/JNEUROSCI.0822-10.2010](https://doi.org/10.1523/JNEUROSCI.0822-10.2010). Author manuscript read ([PMC2945906](https://pmc.ncbi.nlm.nih.gov/articles/PMC2945906/)).

**In short.** How far should one surprising result move a belief? People move it further the more surprising it is, and a simple one-dial version of the ideal learner explains most of it. Most people also expect far more changes than there are.

**What they did.**

- Predict the next number, from 0 to 300. Numbers come from a normal distribution whose mean jumps at unsignalled change points. Every guess gives a learning rate directly.
- No change for 5 trials after a change, then a 0.05 chance each trial, 0.04 on average.
- Noise was fixed within each block of 200 trials, at a standard deviation of 5, 15, 25 or 35. Pay rose as mean error fell.
- 30 people, in 57 sessions, told the numbers were noisy and "would change over the course of the task".
- **The learner.** The full Bayesian learner tracks every run length. The reduced one keeps only an expected run length and the chance a change just happened. Its learning rate is 1/(run length + 1) when a change is unlikely, and climbs towards 1 as a change becomes likely. The hazard is its one free dial.

**What they found.**

- Learning rates were not fixed. Each person's mean ran from 0.07 to 0.71.
- Bigger surprises, measured against the noise, gave higher learning rates (Spearman's ρ = 0.15, p < 0.001). After a change the rate peaked, then fell over many trials (Figs. 3 and 4).
- The reduced learner did almost as well as the full one, and both beat the best fixed learning rate (Fig. 6D). Given the true hazard, it earned top pay in every session.
- Most people expected too many changes. Fitted hazards were "much larger" than the true 0.04, and a higher hazard went with a higher learning rate (r = 0.84, Fig. 8A).
- **The trade-off.** People with higher hazards did better in the 5 trials after a change (r = −0.43, p = 0.02) and worse from the sixth trial on (r = 0.51, p < 0.01) (Fig. 10).
- People reacted to changes less than the one-dial learner did. Adding a weight that discounts surprise, or a belief that the mean drifts, fitted better for 30 of 30 people.

**Why it matters here.**

- **Fig. 10 is our trade-off.** A high hazard wins in the One switch scenario and loses in the No change and One shock scenarios. The geometric mean [headline](../design/scoring.md#how-we-score) is built so that you can't buy one with the other.
- **A cheap family of baselines with human meaning.** A high or low hazard gives a jumpy or a cautious player. Discounting surprise stands in for one that notices too little, and a belief in drift suits our ramps and [drift](../design/mechanics.md#events). It would sit beside the [parked Bayesian baseline](../design/baselines.md#not-yet).
- **People expect too many changes**, which predicts false alarms in the No change and One shock scenarios, as [Massey and Wu](#massey-and-wu-2005-system-neglect) do.
- **Two catches.** It tracks one number, so it would run once per channel and miss the shared factor. And the weather's persistence has to sit in its noise, or every bad stretch reads as a change.

## Gallistel et al. 2014: step, hold and take it back

C. R. Gallistel, Monika Krishan, Ye Liu, Reilly Miller and Peter E. Latham. "The Perception of Probability." Psychological Review 121(1): 96 to 123, 2014. [doi:10.1037/a0035232](https://doi.org/10.1037/a0035232). Published version read, from [Latham's page](http://www.gatsby.ucl.ac.uk/~pel/papers/gallistel_et_al_2014.pdf).

**In short.** Given a free slider to track a hidden probability, people don't nudge it after every outcome. They hold it still for a long time, then jump. They also sometimes take back a change they called.

**What they did.**

- People draw rings one at a time from a box and set a slider to the share that is green. Now and then the box is "replaced with a NEW box" without warning. People press "I think the box has changed" when they think so.
- A 0.005 chance of change after each draw, so about 200 draws apart on average. Each change moved the odds at least fourfold.
- 10 people, each doing 10 sessions of 1,000 draws. Paid $10 a session, whatever their accuracy. The last 5 also got an "I take that back!" button.
- **The model.** First ask whether the estimate is "broke": do the draws since the last change point still fit it? Only if not, choose between adding a change point, removing the last one, or re-estimating. Two thresholds, and no learning rate.

**What they found.**

- **Step and hold.** In every session from every person, the slider sat still for many draws, then jumped (Fig. 5). Small steps were still the most common (Fig. 11).
- **No threshold explains it.** A running average that moves only past a threshold always gave two separate humps of step size, even with five free parameters (Fig. 12).
- **Quick, clean detection.** The median person's median delay was about 10 draws (Fig. 7). Nine of ten had hit rates of .77 to 1 and false alarm rates of .0004 to .02 (Fig. 8).
- **Second thoughts.** People sometimes took a change call back, 95% of the time within 50 draws (Fig. 9).
- **Learning how often change happens.** Nine of ten called changes more often in their first two sessions than their last two (Fig. 16).

**Watch out for.**

- Ten people, told changes would happen. The change is a jump, and the pattern under smooth change is only simulated (Fig. 19).
- The model is disputed. Forsgren, Juslin and van den Berg 2023 (Psychological Review 130(5): 1383 to 1400, [doi:10.1037/rev0000410](https://doi.org/10.1037/rev0000410), abstract read) fit the same patterns better with a simple update rule plus an evidence counter. The data stand. Gallistel's claim that no trial by trial rule can produce them doesn't.

**Why it matters here.**

- **Graded bets may not give graded moves.** Our bets are meant to move smoothly with belief ([interface](../design/interface.md#how-the-agent-plays)). People with a free slider still stepped. So an agent may hold its bets for many rounds, then move them all at once. Read its first doubt from its looks, not from the size of a move.
- **Taking it back means different things in different scenarios.** Moving back after a shock corrects a false alarm. Moving back after a switch gives up a true call. A per scenario score keeps them apart.
- **"If it ain't broke, don't fix it"** with two thresholds is a third cautious or jumpy baseline, beside Nassar's dials, for the [not yet](../design/baselines.md#not-yet) list.

## Haghani and Dewey 2016: a known edge, badly played

Victor Haghani and Richard Dewey. "Rational Decision-Making Under Uncertainty: Observed Betting Patterns on a Biased Coin." Working paper, 2016. [SSRN 2856963](https://doi.org/10.2139/ssrn.2856963), [arXiv:1701.01427](https://arxiv.org/abs/1701.01427)

**In short.** Finance students told a coin lands heads 60% of the time still bet badly on it. They sized bets erratically, and two thirds bet against the edge at some point, most often after a run of heads.

**What they did.**

- Bet on a simulated coin, told in bold it lands heads 60% of the time. Any amount, heads or tails, for 30 minutes, about 300 flips.
- $25 to start, paid out by cheque. A cap of $250, revealed only when a bet could reach it.
- 61 people, mostly economics and finance students and young finance staff.
- **Benchmark.** Kelly betting, a constant 20% of the balance on heads. Constant bets of 10% to 20% reach the cap 95% of the time in simulation (Section 5).

**What they found** (Section 4)**.**

- 21% "maxed out", ending on $200 or more. 28% went bust, ending under $2.
- A third ended with less than they started with. The average payout was $91.
- 18 bet everything on one flip. The average bet was 15% of the balance, but erratic: too small, then too big. Some doubled up after losses.
- 41 (67%) bet on tails at some point, and 29 (48%) more than five times. The 13 who bet tails more than a quarter of the time did so more often after a run of heads. Of those who answered, 75% believed the coin was biased.
- Only 5 had heard of Kelly. Play didn't improve over the session.

**Watch out for.** Counts and percentages only, with no statistical tests.

**Why it matters here.**

- **It is why there is no bankroll.** People told the exact odds still mixed bet sizing up with belief, and a cap they met late changed the best play. A fixed budget each round with a linear payout removes both ([interface rejected](../design/interface.md#rejected), [payout](../design/mechanics.md#payout)).
- **Doubt with nothing to find.** In a coin that never changed, two thirds bet against the stated edge, most often after a streak. That is the false alarm that the No change and One shock scenarios count.
- **A human baseline is not in the current design.** This would be a cheap one, but only for a world that doesn't change.
