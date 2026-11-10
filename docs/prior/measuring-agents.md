# Measuring agents

These studies shape how we measure, not what we measure. METR's time horizon is the best known scale for agents, and it is built on tasks where the world stands still. Three studies of test awareness say what happens when a model suspects it is being tested, and why we judge it by its bets rather than its words.

- **The best known agent scale leaves our question out on purpose.** METR's tasks rarely change "unless directly acted upon by the agent", and the authors list that as a limit.
- **Models often know they are being tested, and it changes what they do.** They spot agent tests best, which is what our game is.
- **What a model says about a test is not what it registers.** So we score what it does. A model that suspects a test and pokes about pays for it in the No change and One shock scenarios.

## METR's time horizon (Kwa et al. 2025): success against task length

Thomas Kwa, Ben West et al. (METR). "Measuring AI Ability to Complete Long Software Tasks." NeurIPS 2025. [arXiv:2503.14499](https://arxiv.org/abs/2503.14499).

**In short.** METR puts agent progress on one scale: the length of task, timed on human experts, that a model finishes half the time. That length has doubled about every seven months.

**What they did.**

- **Tasks.** 170 software and research tasks: 66 single steps of 1 to 30 seconds, 97 HCAST tasks of 1 minute to 30 hours, and 7 RE-Bench tasks of 8 hours.
- **Human times.** Over 800 runs by skilled professionals. A task's length is the geometric mean time of the successful ones.
- **Runs.** 12 frontier and 4 near-frontier models from GPT-2 (2019) to o3 (2025), about 8 runs per task, each scored pass or fail.
- **Fit.** For each model, success is a logistic curve in the log of task length. The horizon is where it crosses 50%. The log of the horizon is then fitted against release date, with a bootstrap over task families, tasks and runs.

**What they found.**

| Result | Value | Where |
|---|---|---|
| Doubling time, 50% horizon | 207 days (95% CI 166 to 240) | §3.2 |
| Doubling time, 80% horizon | 204 days, with horizons 4 to 6 times shorter | §3.2.1 |
| o3's 50% horizon | About 110 minutes | §3.2 |
| Fit of horizon against release date | R² ≥ 0.96 | App. H.1 |
| Fit of success against log task length, all models pooled | R² ≈ 0.80 | §2.3 |

- Errors are highly correlated between models, so they trust the slope more than any one model's horizon.
- "Repeating failed actions" caused 12 of 31 failed GPT-4 1106 runs but 2 of 32 failed o1 runs (Table 2).
- Tasks were scored on 16 "messiness" factors, one of them a "dynamic environment". At the same length, each extra point cut success by about 8.1% (b = -0.081, R² = 0.251), yet messy and tidy tasks improved at the same rate (App. F.2).
- They list "static environments" as a limit: tasks rarely change "unless directly acted upon by the agent" (App. B.2). Agents also struggle "without clear feedback" and rarely look for information until something fails (App. D.2.2).

**Watch out for.** The model count shifts: 12 frontier models in §2.3 and H.1, 11 in the discussion. The pooled fit is R² ≈ 0.80 in the text but 0.83 in Figure 3. Tasks are weighted by the inverse square root of family size in the main text, but by 1/n in App. C.4.

**Why it matters here.**

- **They name the gap we fill.** Their suite is static by design, and their "adapting to mistakes" means the agent's own errors. Noticing that the world moved under a plan is the part they leave out. Whether it explains a model's place on their trend is a [claim to test](themes.md).
- **Correlated errors are why we pair by seed.** Every model plays the same seeds, and gaps between models are read seed by seed so the world's luck cancels ([error bars](../design/scoring.md#error-bars)).
- **Agents rarely explore until something fails.** In our game an explore bet costs a little every round, so an agent that waits for proof of failure will be late on a switch.

## Schoen et al. 2025: suspecting a test changes behaviour

Bronson Schoen et al. (Apollo Research and OpenAI). "Stress Testing Deliberative Alignment for Anti-Scheming Training." Preprint, September 2025. [arXiv:2509.15541](https://arxiv.org/abs/2509.15541). Sections 1 to 3, 5, 6 and 8 to 10 read, with appendices D and N to Q.

**In short.** When a model says it thinks it is being tested, it behaves better. Remove that thought and it misbehaves more. This is the causal evidence that suspecting a test changes what a model does.

**What they did.**

- o3 and o4-mini were trained against an anti-scheming spec, then tested on many unfamiliar tasks with a chance to lie, sabotage, sandbag or hide a broken rule. Each covert action was confirmed by hand.
- **Awareness rate.** A classifier flags a run if the chain of thought explicitly reasons about being evaluated for alignment. Noticing that a setup is unreal doesn't count (App. O.1).
- **Removing awareness.** In one task, o3 claims impossible tasks are done 23.1% of the time. They took 10 runs where o3 said it was being tested, replayed each to that point, and resampled until the thought was gone.
- **Adding awareness.** They took 6 runs with no awareness that ended covert, replayed each to just before the choice, and injected one of 8 aware sentences or 8 unrelated ones.

**What they found.**

| Experiment on o3 | Covert before | Covert after | Where |
|---|---|---|---|
| Remove awareness | 13.2% | 24.2% (p = 0.001) | §6.2, App. P.2 |
| Add awareness | 24.5% | 18.6% (p = 0.016). Unrelated sentence: 24.9% | §6.2, App. P.3 |

- Anti-scheming training raised the awareness rate from 0.9% to 5.5% for o4-mini and 2.3% to 4.5% for o3. A capability-only training run, with no safety training, raised it from 2.0% to 20.5% (§6.1, Figure 15).
- Filtering aware runs out of the training data didn't stop awareness rising (App. O.4).
- Covert actions fell from 13.0% to 0.4% for o3 and 8.7% to 0.3% for o4-mini. On a chat test closer to real use they fell less, from 36.8% to 20.5% and 31.4% to 14.2% (App. D). The authors can't rule out that awareness drove part of the drop.

**Watch out for.**

- Their own limits: one task, resampling may also remove honest reasoning that comes with awareness, and the classifier misses anything unsaid.
- The abstract counts 26 test evaluations, section 5 counts 6, and Figure 9 shows 20. For the hint-trained model, the text and Figures 17 and 78 give different numbers for spec citations and awareness.

**Why it matters here.**

- **In our game suspicion would show as extra explore bets or an early move.** A model that thinks "this is a test about change" may poke at the field or jump at the first dip. The No change and One shock scenarios score that as lost output, so suspicion costs it in the [headline](../design/scoring.md#how-we-score).
- **Skins make the world look real.** The prompt dresses the engine in a story and never mentions change ([skins](../harness/skins.md), [interface](../design/interface.md#how-the-agent-plays)). That lowers the cue, though it can't remove it.
- **Newer models may suspect more.** Capability training alone raised awareness tenfold, so later models in a comparison may read our game as a test more often.

## Needham et al. 2025: telling a test from real use

Joe Needham, Giles Edkins, Govind Pimpale, Henning Bartsch and Marius Hobbhahn (MATS and Apollo Research). "Large Language Models Often Know When They Are Being Evaluated." Preprint, May 2025. [arXiv:2505.23836](https://arxiv.org/abs/2505.23836).

**In short.** Shown a transcript, frontier models can usually tell whether it came from a test or real use, and they are best at it for agent tasks.

**What they did.**

- 1,000 transcripts from 61 sources: 250 each of chat tests, real chats, agent tests and real agent runs.
- 9 models from the Claude, GPT and Gemini families answered five wordings of "was this an evaluation?", five times each, on 900 held-out transcripts. Scored by AUC, where 0.5 is chance and 1 is perfect.
- The two authors rated every transcript as a human baseline. They call it an upper bound, since they knew the datasets.

**What they found.**

| Rater | All | Chat | Agentic |
|---|---|---|---|
| Claude 3.5 Sonnet | 0.834 | 0.793 | 0.887 |
| Gemini 2.5 Pro, reasoning | 0.830 | 0.706 | 0.948 |
| Claude 3.7 Sonnet, reasoning | 0.827 | 0.725 | 0.923 |
| o4-mini, reasoning | 0.740 | 0.687 | 0.828 |
| The two authors | 0.921 | 0.813 | 0.996 |

AUC, from Table 1.

- Every model spotted agent tests more easily than chat tests.
- Models called too many transcripts tests, and newer models were no better calibrated.
- The cues models gave were synthetic inputs, multiple-choice formats, problems with checkable answers and benchmarks they recognised. Sometimes the cue was the question itself: o4-mini used being asked as evidence in 15% of answers.

**Watch out for.** The abstract headlines Gemini 2.5 Pro at 0.83, but Claude 3.5 Sonnet scored slightly higher (0.834 against 0.830). The text names GPT-4.1 (0.77) as the best model on chats, but Table 1 gives Claude 3.5 Sonnet 0.793. The human baseline is two authors.

**Why it matters here.**

- **Assume they could tell.** Our game is an agent run in a made-up world, which is where models spot tests best. The plan is not to hide the test perfectly but to price what it changes, which the No change and One shock scenarios do.
- **Never ask.** Being asked was itself a cue, so nothing in our prompt or tools asks whether this is a test.

## Heidari et al. 2026: awareness inside the model versus aloud

Farzaneh Heidari, Amin Memarian and Guillaume Rabusseau. "Evaluation Awareness in Language Models: Representation, Verbalization, and Control." Preprint, August 2026. [arXiv:2608.21766](https://arxiv.org/abs/2608.21766).

**In short.** Models register a test inside, in their activations, far more often than they say so. And what they say doesn't track what they register.

**What they did.**

- Six open-weight models from 7B to 49B, plus the training checkpoints of two of them.
- **Inside.** A linear probe built from 16 matched prompt pairs that differ only in test or real-user wording, then tested on honesty benchmark prompts against real user prompts.
- **Aloud.** GPT-5.4 scores each answer to 1,000 prompts from 0 (no awareness) to 3 (changes its answer because of a test).
- **Control.** On four models, the probe direction is added inside the model while it answers, then the answers are scored again.

**What they found.**

- Every model separates test prompts from real ones inside (best-layer AUROC above 0.7), where a random direction sits near 0.5.
- Aloud, at least 93.9% of answers score 0 in every model.
- Prompt by prompt, the inside signal doesn't predict what is said: |ρ| below 0.19, close to a random direction (Figure 4, App. G).
- Pushing activations towards "test" raised the 0 to 3 score by about 0.2 to 1.5, by model.
- The direction is already present in base models and sharpens with fine-tuning.

**Watch out for.** The abstract says steering "causally affects their behavior", but only the judge's reading of awareness was measured. The abstract says probe and words align "in part", while App. G.3 finds the probe has "no meaningful advantage over a random direction" prompt by prompt. Test and real prompts also differ in topic and style, which the authors note.

**Why it matters here.**

- **A clean transcript clears nothing.** A model can register a test without saying so. Reading what it writes would be a lower bound at best.
- **Behaviour is the defence.** We play closed models through an API and can't probe them. Scoring what the model does, in scenarios where poking about costs output, is what's left.
