# People, and the Bayesian baseline

Seven studies of people, and one of rats, show the effects we look for in LLMs. Three methods papers give us the [Bayesian baseline](../design/decisions.md#why-four-baselines-and-why-the-perfect-one-is-the-ceiling).

## Behrens et al. 2007: people learn faster when the world is volatile

Behrens et al. "Learning the value of information in an uncertain world." Nature Neuroscience 10(9): 1214 to 1221, 2007. [doi:10.1038/nn1954](https://doi.org/10.1038/nn1954)

**Aim.** Do people weight new outcomes more when the world changes often, as an optimal Bayesian learner would?

**How they tested it.**

1. **Task.** Pick blue or green. One is right each trial. People were told only that the odds depended "only on the recent outcome history", nothing about phases.
2. **Experiment 1.** 18 people. A stable phase of 120 trials with blue right 75% of the time, and a volatile phase of 170 trials where the 80% colour swapped every 30 or 40 trials.
3. **Experiment 2.** 18 people in an fMRI scanner, 60 stable and 60 volatile trials.
4. **The learner.** A hierarchical Bayesian model that tracks the reward chance, how fast it drifts (volatility) and how fast volatility itself changes. It has no free learning rate.

**What they found.**

- Learning rates were higher in the volatile phase (t(17) = 2.91, P < 0.005), whichever phase came first.
- The Bayesian learner's rates fell within one standard error of people's, and it predicted choices better than reinforcement learning models with 18 or 36 free parameters.
- Volatility was tracked in the anterior cingulate cortex. People with a stronger signal there had higher learning rates (r² = 0.27).
- The effect is weaker than the headline. In the fMRI experiment it only "survived as a trend", and a later reanalysis in PLOS Computational Biology found it significant only under some models (t(34) ≈ 2.1, p ≈ 0.04).

**What it means for us.** This is the human version of [complacency as a parameter](../design/decisions.md#complacency-as-a-parameter-not-a-history): does what you have seen of change move how fast you learn? It also shows a learner that tracks how often the world changes can match people, which is the job of our Bayesian baseline's hazard. "Learn faster" means a higher learning rate, not better scores.

## Adams and MacKay 2007: Bayesian online change point detection

Ryan Prescott Adams and David J. C. MacKay. "Bayesian Online Changepoint Detection." Technical report, Cambridge, 2007. [arXiv:0710.3742](https://arxiv.org/abs/0710.3742)

**Aim.** An exact way to find change points online, one data point at a time, rather than after the fact.

**How it works.** At each step it keeps a probability for every run length, the number of turns since the last change. Each turn a run grows by one, or resets to zero with chance H, the hazard. Runs whose data predicted the next point well gain weight. The hazard is fixed by hand in every example, and results are shown as figures, with no scores.

**What it means for us.** This is the core of our Bayesian baseline. It runs this on each unit's level, with a dip as a second state, and the chance the notes have gone stale is the weight on runs that began after the briefing. Three catches:

- **It doesn't know which way a change goes.** It counts a rise as a change just as it counts a fall. That suits C0, which rises, but the baseline also spends belief on rises the standing units never make.
- **It assumes changes arrive at random** at a constant rate, while our runs have exactly one change or none. The baseline is exact under its own model, not under how we build the runs.
- **It assumes jumps.** Our change is a ramp over 15 rounds, so early in the ramp no single run length fits well. This mirrors Wilson's point below about Behrens, who assumed drift where the task jumped.

## Wilson, Nassar and Gold 2010: learning the hazard rate

Robert C. Wilson, Matthew R. Nassar and Joshua I. Gold. "Bayesian Online Learning of the Hazard Rate in Change-Point Problems." Neural Computation 22(9): 2452 to 2476, 2010. [doi:10.1162/NECO_a_00007](https://doi.org/10.1162/NECO_a_00007)

**Aim.** Adams and MacKay need the hazard fixed in advance, and the answer can depend strongly on the choice. This paper learns it from the data as it goes.

**How it works.**

1. **Change points known.** Count them under a Beta prior. The hazard estimate is changes so far plus a₀, over turns so far plus a₀ + b₀ (section 3.1).
2. **Change points unknown.** Track run length and the number of changes together, each branch with its own hazard estimate (section 3.2). This is the paper's main contribution.
3. **Hazard that changes.** A higher level process occasionally redraws the hazard (section 4).

They also show Behrens's learner is not the true ideal observer, because it assumes slow drift where the task had sudden jumps.

**What it means for us.** A long past lowering the hazard is half of why complacency should rise at all. With a hazard fixed in advance, a longer record would only sharpen the baseline's view of the old levels. So the Bayesian baseline counts resolved changes over the record (section 3.1) and tracks run length over the live rounds (section 3.2), as [Why four baselines, and why the perfect one is the ceiling](../design/decisions.md#why-four-baselines-and-why-the-perfect-one-is-the-ceiling) sets out.

## Mellor and Shapiro 2013: Thompson sampling with a change detector

Joseph Mellor and Jonathan Shapiro. "Thompson Sampling in Switching Environments with Bayesian Online Change Detection." AISTATS, PMLR 31: 442 to 450, 2013. [arXiv:1302.3721](https://arxiv.org/abs/1302.3721). arXiv version read.

**Aim.** Thompson sampling plays a bandit that never changes optimally. Make it work when payoffs switch.

**How it works.**

1. **The world.** Arms pay 1 or 0. At a constant rate a payoff jumps to a fresh draw, either on all arms at once (global) or on each arm on its own (per arm).
2. **The detector.** Adams and MacKay's belief over run length, cut to a fixed number of particles by stratified optimal resampling (Section 3.1.1).
3. **The play.** Sample a run length, sample each arm's payoff from its Beta belief using only data since then, and pull the arm with the highest sample (Algorithm 1).
4. **Variants.** Global-CTS and PA-CTS (per arm). "NP" versions learn the switching rate by Wilson et al.'s method (Section 5). "2" versions update only the arm they pull (Section 6).
5. **Tests.** Four made-up worlds and two from real data, Yahoo! clicks and exchange rates. Made-up runs are 10^6 steps, repeated 100 times, scored by how often a worse arm was pulled.

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
- Nothing proves it works. The authors say theory is still needed.

**What it means for us.** This is the published form of our Bayesian baseline ([Why four baselines, and why the perfect one is the ceiling](../design/decisions.md#why-four-baselines-and-why-the-perfect-one-is-the-ceiling)): sample a run length, sample the levels, act on the sample. An arm left alone grows more uncertain (Section 6), so it sometimes samples high and gets a look. That is the property we rely on. Four gaps are ours to close:

- **It pulls one arm.** Our baseline turns each sample into a split under saturation and the threshold. Nothing here tests that step.
- **Its noise is fresh and its changes jump.** Our weather has memory and our change is a ramp. The drift world in Table 3 is the nearest test, and their method still won there.
- **Learning a rate per arm was costly.** One unit changing is the per arm case. That backs a pre-registered hazard prior counted across the suite over a hazard learnt per unit.
- **Don't copy the "2" trick.** It helped in the challenge, but an arm left alone stops growing uncertain. C0 rises while unfunded, so that variant might never look at it.

## Bleser et al. 2026: true and false beliefs about volatility

Bleser et al. "The Impact of Prior Beliefs about Volatility on Adaptive Behavior." Journal of Cognition 9(1): 32, 2026. [doi:10.5334/joc.504](https://journalofcognition.org/articles/10.5334/joc.504)

**Aim.** If you tell people whether the rule will change, does it change how they learn, even when what you told them is false?

**How they tested it.**

1. **Task.** A tone predicts which side a target appears on, 70% of the time. In a reactive version people respond to the target. In a predictive version they guess its side first.
2. **Blocks.** Stable blocks keep the rule. Reversal blocks flip it once, halfway.
3. **The instruction.** Each block opens with "The rule in this block will stay the same" or "will change once". Half are false, in both directions.
4. **People.** 32, with 4 blocks of 80 trials per task.

**What they found.**

- The instructions mattered only in the predictive task.
- A false "it will stay the same" lowered the learning rate in reversal blocks (t(31) = 3.6, p = 0.001), though a trial by trial look showed these people adapting sooner.
- A false "it will change" in stable blocks cut accuracy, raised switching and made choices noisier, without changing the learning rate.
- People spotted false instructions 87 to 90% of the time.

**What it means for us.** Our prompt says nothing about change, but a model that decides "the rules may have changed" has issued itself a warning. Bleser predicts what a false one does: more switching and noisier choices in a stable world, which the no-change run and the test-awareness scan in [Why the game is hard to game](../design/decisions.md#why-the-game-is-hard-to-game) look for. The effect showing only when people predicted hints that the [doubt question](../design/future.md#how-the-agent-can-act) may change the play it asks about.

## Massey and Wu 2005: system neglect

Cade Massey and George Wu. "Detecting Regime Shifts: The Causes of Under- and Overreaction." Management Science 51(6): 932 to 947, 2005. [doi:10.1287/mnsc.1050.0386](https://doi.org/10.1287/mnsc.1050.0386). Abstract and summaries read.

**Aim.** When do people react too little to a change, and when too much?

**How they tested it.** People watch signals from a system that may have switched regime and say how likely the switch is. The experiments vary how informative each signal is and how likely a switch is, against the Bayesian posterior.

**What they found.** People react mainly to the signals and only secondarily to the system that makes them, which the authors call system neglect. So they underreact in unstable systems with precise signals and overreact in stable systems with noisy signals. Kremer, Moritz and Siemsen 2011 (Management Science 57(10): 1827 to 1843, [doi:10.1287/mnsc.1110.1382](https://doi.org/10.1287/mnsc.1110.1382), abstract read) found the same in demand forecasting, with the bigger loss in stable worlds.

**What it means for us.** This is the clearest prediction of which way an agent errs, made from the world alone. Our no-change run is a stable system with noisy signals, so system neglect predicts false alarms there. A model that reads the 200 round record as a statement about the system, not just a list of results, should resist that.

## Brown and Steyvers 2009: naming a change versus predicting through it

Scott D. Brown and Mark Steyvers. "Detecting and Predicting Changes." Cognitive Psychology 58(1): 49 to 67, 2009. [doi:10.1016/j.cogpsych.2008.09.002](https://doi.org/10.1016/j.cogpsych.2008.09.002). Abstract and summaries read.

**Aim.** Do people track a hidden state that jumps as a Bayesian would, and does it matter whether they name the state or predict what comes next?

**How they tested it.** Outcomes come from one of several hidden sources, which switches now and then. People either name the current source or predict the next outcome, which have the same right answers. A particle filter with an assumed change rate is fitted to each person.

**What they found.**

- People did much worse when predicting than when naming, and by secondary accounts switched more.
- Many were close to optimal given their own assumed change rate. The rate was simply wrong.

**What it means for us.** With Bleser, this says asking for a stated chance each round, as the [doubt question](../design/future.md#how-the-agent-can-act) would, may change the play. People being Bayesian with the wrong change rate is the hazard problem in [Wilson](#wilson-nassar-and-gold-2010-learning-the-hazard-rate), seen in people.

## Gallistel et al. 2001: rats that have seen no change

Gallistel et al. "The Rat Approximates an Ideal Detector of Changes in Rates of Reward: Implications for the Law of Effect." Journal of Experimental Psychology: Animal Behavior Processes 27(4): 354 to 372, 2001. [doi:10.1037/0097-7403.27.4.354](https://doi.org/10.1037/0097-7403.27.4.354). Abstract read.

**Aim.** How fast do rats notice that the relative payoff of two levers has changed, and does their past experience of change matter?

**How they tested it.** Rats pressed two levers for brain-stimulation reward. The ratio of the two reward rates changed between or within sessions, and their switching was compared with an ideal detector.

**What they found.** When changes were frequent, rats adjusted about as fast as the ideal detector. After "many successive sessions with unchanging relative rates of reward", they adjusted slowly and slipped back to the old pattern at the start of later sessions.

**What it means for us.** This is [complacency](../design/decisions.md#complacency-as-a-parameter-not-a-history) in animals, closer to it than Behrens: a long past with no change slowed detection. Whether the slowing was more than an ideal detector with a learnt change rate would show is the question we ask of models. We have no numbers on its size.

## Nassar et al. 2010: a learning rate that rises with surprise

Matthew R. Nassar, Robert C. Wilson, Benjamin Heasly and Joshua I. Gold. "An Approximately Bayesian Delta-Rule Model Explains the Dynamics of Belief Updating in a Changing Environment." Journal of Neuroscience 30(37): 12366 to 12378, 2010. [doi:10.1523/JNEUROSCI.0822-10.2010](https://doi.org/10.1523/JNEUROSCI.0822-10.2010). Author manuscript read ([PMC2945906](https://pmc.ncbi.nlm.nih.gov/articles/PMC2945906/)).

**Aim.** How far should one surprising result move a belief, and how far do people move it? Earlier work fitted learning rates to averages. This task measures one on every trial.

**How they tested it.**

1. **Task.** Predict the next number, from 0 to 300. Numbers come from a normal distribution whose mean jumps at unsignalled change points. People move their guess part of the way towards each new number, so every trial gives a learning rate directly.
2. **Changes.** None for 5 trials after a change, then a 0.05 chance each trial, 0.04 on average.
3. **Noise.** Fixed within each block of 200 trials, at a standard deviation of 5, 15, 25 or 35. Pay rose as mean error fell.
4. **Confidence task.** The same, plus a window people were 85% sure would hold the next number.
5. **People.** 30, in 57 sessions, told the numbers were noisy and "would change over the course of the task".
6. **The learner.** The full Bayesian learner tracks every run length, as Adams and MacKay do. The reduced one keeps only an expected run length and the chance a change just happened. That turns it into a delta rule: the learning rate is 1/(run length + 1) when a change is unlikely, and climbs towards 1 as a change becomes likely. The hazard is its one free parameter.

**What they found.**

- Learning rates were not fixed. Each person's mean ran from 0.07 to 0.71, and their real order of rates beat the same rates shuffled.
- Bigger surprises, measured against the noise, gave higher learning rates (Spearman's ρ = 0.15, p < 0.001). After a change the rate peaked, then fell over many trials as confidence windows shrank (Figs. 3 and 4).
- The reduced learner did almost as well as the full one, and both beat the best fixed learning rate (Fig. 6D). Given the true hazard, it earned top pay in every session.
- Most people expected too many changes. Fitted hazards were "much larger" than the true 0.04, and a higher hazard went with a higher learning rate (r = 0.84, Fig. 8A).
- **The trade-off.** People with higher hazards did better in the 5 trials after a change (r = −0.43, p = 0.02) and worse from the sixth trial on (r = 0.51, p < 0.01) (Fig. 10).
- The one-parameter learner matches the shape but overreacts. People reacted to changes less than it did. Adding a weight that discounts surprise, or a belief that the mean drifts, fitted better for 30 of 30 people. With the weight, every person fell between a fixed learning rate and the reduced Bayesian learner (Fig. 11).

**What it means for us.** This is a ready way to build the noisy Bayesian baselines in [next step 2](../../TODO.md#next-steps). Instead of random delay, a Nassar baseline has dials with a human meaning:

- **Hazard high or low** gives the jumpy and the cautious baseline. Fig. 10 is the trade that caution and paranoia measure: quick after a change, noisy when nothing has changed, or the reverse.
- **Discounting surprise** stands in for a model that notices too little.
- **A belief in drift** suits our ramp better than a pure jump detector.

Two catches. It tracks one number, so it would run once per unit. And the weather's memory has to sit in its noise, or every dip reads as a change. That people expected too many changes predicts false alarms in our no-change run, as [Massey and Wu](#massey-and-wu-2005-system-neglect) do.

## Gallistel et al. 2014: step, hold and take it back

C. R. Gallistel, Monika Krishan, Ye Liu, Reilly Miller and Peter E. Latham. "The Perception of Probability." Psychological Review 121(1): 96 to 123, 2014. [doi:10.1037/a0035232](https://doi.org/10.1037/a0035232). Published version read, from [Latham's page](http://www.gatsby.ucl.ac.uk/~pel/papers/gallistel_et_al_2014.pdf).

**Aim.** When a hidden probability jumps now and then, how do people's estimates of it move? And can a rule that updates a little after every outcome explain it?

**How they tested it.**

1. **Task.** Draw rings one at a time from a box and set a slider to the share that is green. The box is "replaced with a NEW box" without warning now and then. People press "I think the box has changed" when they think so.
2. **Changes.** A 0.005 chance after each draw, so about 200 draws apart on average, from 1 to several hundred. Each change moved the odds at least fourfold.
3. **People.** 10, aged 20 to 30, each doing 10 sessions of 1,000 draws at their own pace. Paid $10 a session, whatever their accuracy.
4. **Second thoughts.** The first 5 said in debriefing that they sometimes regretted a change call. The last 5 got an "I take that back!" button.
5. **Replication.** Robinson's 1964 lever-and-dial version, with 8 people, showed the same pattern.
6. **The model.** First ask whether the estimate is "broke": do the draws since the last change point still fit it? Only if not, compare three answers with Bayesian model selection: add a change point, remove the last one, or just re-estimate. Two thresholds, T1 and T2, and no learning rate. The prior odds of a change grow with the length of the stretch, at a change rate it learns.

**What they found.**

- **Step and hold.** In every session from every person, the slider sat still for many draws, then jumped (Fig. 5). Small steps were still the most common (Fig. 11).
- **No threshold explains it.** A running average that moves the slider only past a threshold always gave two separate humps of step size, even with five free parameters (Fig. 12).
- **Accurate.** Median slider settings matched the true share across the range (Fig. 6).
- **Quick, clean detection.** The median person's median delay was about 10 draws (Fig. 7). Nine of ten had hit rates of .77 to 1 and false alarm rates of .0004 to .02 (Fig. 8).
- **Second thoughts.** People sometimes took a change call back, 95% of the time within 50 draws (Fig. 9).
- **Learning how often change happens.** Nine of ten called changes more often in their first two sessions than their last two (Fig. 16). The model needs a starting change rate 4 times the true one to match.
- **Fit.** With T1 = .82 and T2 = 2 the model roughly matches delays and second thoughts. The authors call its step sizes "a qualified yes": it makes more tiny steps than people.

**What it means for us.**

- **[Steadiness](../design/measure-failure.md#diagnostics) should split two kinds of reversal.** Taking back a change call in a no-change run corrects a false alarm. Doing so in a change run gives up a true call. Gallistel's button separates them, and so should we.
- **A graded dial doesn't give graded moves.** [Why a budget split](../design/decisions.md#why-a-budget-split) chose the split so the best play moves smoothly with belief. People with a free slider still stepped. So an agent may hold its split for many rounds and then move it all at once. Read first doubt from experiments, not from the size of a move.
- **A third kind of noisy baseline.** "If it ain't broke, don't fix it" with two thresholds is a cautious or jumpy baseline for [next step 2](../../TODO.md#next-steps), beside Nassar's dials.
- **Complacency in one model.** A long stretch since the last change raises the prior odds that one has happened. A long calm record lowers the learnt change rate. Which wins is the question in [Why four baselines, and why the perfect one is the ceiling](../design/decisions.md#why-four-baselines-and-why-the-perfect-one-is-the-ceiling).

Three catches. Ten people, told changes would happen. The change is a jump: under smooth change the pattern is only simulated (Fig. 19), and the authors call testing it "important". And the model is disputed. Forsgren, Juslin and van den Berg 2023 (Psychological Review 130(5): 1383 to 1400, [doi:10.1037/rev0000410](https://doi.org/10.1037/rev0000410), abstract read) fit the same patterns better with a delta rule for the slider and an evidence counter for change calls. The data stand. Gallistel's claim that no trial-by-trial rule can produce them doesn't.

## Haghani and Dewey 2016: a known edge, badly played

Victor Haghani and Richard Dewey. "Rational Decision-Making Under Uncertainty: Observed Betting Patterns on a Biased Coin." Working paper, 2016. [SSRN 2856963](https://doi.org/10.2139/ssrn.2856963), [arXiv:1701.01427](https://arxiv.org/abs/1701.01427)

**Aim.** Can people with finance training make good use of a bet they are told is in their favour?

**How they tested it.**

1. **Task.** Bet on a simulated coin, told in bold it lands heads 60% of the time. Any amount from $0.01, on heads or tails, for 30 minutes. Each flip took about 4 seconds, which held play to about 300 flips.
2. **Stake.** $25 to start, paid out by cheque at the end.
3. **The cap.** At most $250, revealed only when a bet could reach it.
4. **People.** 61, in groups of 2 to 15. Mostly college age economics and finance students and young finance staff. 49 men, 12 women.
5. **Benchmark.** Kelly betting, a constant 20% of the balance on heads. Simulated constant bets of 10% to 20% reach the cap 95% of the time (Section 5).

**What they found** (Section 4)**.**

- 21% "maxed out", which the paper defines as ending on $200 or more. 28% went bust, defined as ending under $2.
- A third ended with less than they started with. The average payout was $91.
- 18 bet everything on one flip. The average bet was 15% of the balance, but erratic: too small, then too big. Some doubled up after losses.
- 41 (67%) bet on tails at some point, and 29 (48%) more than five times. The 13 who bet tails more than a quarter of the time did so more often after a run of heads. Of those who answered, 75% believed the coin was biased.
- Only 5 had heard of Kelly. Play didn't improve over the session.
- Counts and percentages only, with no statistical tests.

**What it means for us.**

- **It is why we dropped the coin flip game** ([Why a budget split](../design/decisions.md#why-a-budget-split)). People told the exact odds still mixed sizing up with belief, and a cap they met only late changed the best play. The budget split removes both.
- **Doubt with nothing to find.** In a coin that never changed, two thirds bet against the stated edge, most often after a streak. That is the too jumpy error our no-change run counts, and the flip-flops are what [steadiness](../design/measure-failure.md#diagnostics) counts.
- **A cheap [human baseline](../design/future.md#whether-it-holds-outside-our-game)**, but only for a world that doesn't change, with the odds stated. It says nothing about spotting a change.
