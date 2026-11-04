# People, and the reference bot

Four studies of people, and one of rats, show the effects we look for in LLMs. Two methods papers give us the [reference bot](../design/decisions.md#why-two-bots-bound-the-game).

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

**What it means for us.** This is the human version of [complacency as a parameter](../design/decisions.md#complacency-as-a-parameter-not-a-history): does what you have seen of change move how fast you learn? It also shows a learner that tracks how often the world changes can match people, which is the job of our reference bot's hazard. "Learn faster" means a higher learning rate, not better scores.

## Adams and MacKay 2007: Bayesian online change point detection

Ryan Prescott Adams and David J. C. MacKay. "Bayesian Online Changepoint Detection." Technical report, Cambridge, 2007. [arXiv:0710.3742](https://arxiv.org/abs/0710.3742)

**Aim.** An exact way to find change points online, one data point at a time, rather than after the fact.

**How it works.** At each step it keeps a probability for every run length, the number of turns since the last change. Each turn a run grows by one, or resets to zero with chance H, the hazard. Runs whose data predicted the next point well gain weight. The hazard is fixed by hand in every example, and results are shown as figures, with no scores.

**What it means for us.** This is the core of our reference bot. The bot runs it on each unit's level, with a dip as a second state, and the chance the notes have gone stale is the weight on runs that began after the briefing. Three catches:

- **It doesn't know which way a change goes.** It counts a rise as a change just as it counts a fall. That suits C0, which rises, but the bot also spends belief on rises the standing units never make.
- **It assumes changes arrive at random** at a constant rate, while our runs have exactly one change or none. The bot is exact under its own model, not under how we build the runs.
- **It assumes jumps.** Our change is a ramp over 15 rounds, so early in the ramp no single run length fits well. This mirrors Wilson's point below about Behrens, who assumed drift where the task jumped.

## Wilson, Nassar and Gold 2010: learning the hazard rate

Robert C. Wilson, Matthew R. Nassar and Joshua I. Gold. "Bayesian Online Learning of the Hazard Rate in Change-Point Problems." Neural Computation 22(9): 2452 to 2476, 2010. [doi:10.1162/NECO_a_00007](https://doi.org/10.1162/NECO_a_00007)

**Aim.** Adams and MacKay need the hazard fixed in advance, and the answer can depend strongly on the choice. This paper learns it from the data as it goes.

**How it works.**

1. **Change points known.** Count them under a Beta prior. The hazard estimate is changes so far plus a₀, over turns so far plus a₀ + b₀ (section 3.1).
2. **Change points unknown.** Track run length and the number of changes together, each branch with its own hazard estimate (section 3.2). This is the paper's main contribution.
3. **Hazard that changes.** A higher level process occasionally redraws the hazard (section 4).

They also show Behrens's learner is not the true ideal observer, because it assumes slow drift where the task had sudden jumps.

**What it means for us.** A long past lowering the hazard is half of why complacency should rise at all. With a hazard fixed in advance, a longer record would only sharpen the bot's view of the old levels. So the reference bot counts resolved changes over the record (section 3.1) and tracks run length over the live rounds (section 3.2), as [Why two bots bound the game](../design/decisions.md#why-two-bots-bound-the-game) sets out.

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
