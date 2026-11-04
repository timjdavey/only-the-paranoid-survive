# Measuring agents

These studies shape how we measure. METR's time horizon is the form discernment copies, and three studies of test awareness show why the no-change run, not a scan of the reasoning, is the main defence against a model that suspects a test.

## METR's time horizon (Kwa et al. 2025): success against task length

Thomas Kwa, Ben West et al. (METR). "Measuring AI Ability to Complete Long Software Tasks." NeurIPS 2025. [arXiv:2503.14499](https://arxiv.org/abs/2503.14499).

**Aim.** Put agent progress on one scale anyone can follow: the length of task, timed on human experts, that a model finishes half the time.

**How they tested it.**

1. **Tasks.** 170 software and research tasks: 66 single steps of 1 to 30 seconds, 97 HCAST tasks of 1 minute to 30 hours, and 7 RE-Bench tasks of 8 hours.
2. **Human times.** Over 800 baselines by skilled professionals. A task's length is the geometric mean time of the successful ones.
3. **Runs.** 12 frontier and 4 near-frontier models from GPT-2 (2019) to o3 (2025), about 8 runs per task, each scored pass or fail.
4. **Fit.** For each model, success is a logistic in the log of task length, with its own slope. The horizon is where it crosses 50%. The log of the horizon is then fitted against release date, with a bootstrap over task families, tasks and runs.

**What they found.**

| Result | Value | Where |
|---|---|---|
| Doubling time, 50% horizon | 207 days (95% CI 166 to 240) | §3.2 |
| Doubling time, 80% horizon | 204 days, with horizons 4 to 6 times shorter | §3.2.1 |
| o3's 50% horizon | About 110 minutes | §3.2 |
| Fit of horizon against release date | R² ≥ 0.96 | App. H.1 |
| Fit of success against log task length, all models pooled | R² ≈ 0.80 | §2.3 |

- Errors are highly correlated between models, so they trust the slope more than any one model's horizon.
- "Repeating failed actions" caused 12 of 31 failed GPT-4 1106 runs but 2 of 32 failed o1 runs (Table 2). o1's failures were on harder tasks, and its early give-ups doubled from 8 to 16.
- Tasks were scored on 16 "messiness" factors, one of them a "dynamic environment". At the same length, each extra point cut success by about 8.1% (b = -0.081, R² = 0.251), yet messy and tidy tasks improved at the same rate (App. F.2).
- They list "static environments" as a limit of the suite: tasks rarely change "unless directly acted upon by the agent" (App. B.2). Agents also struggle "without clear feedback" and rarely look for information until something fails (App. D.2.2).

**Problems.** The model count shifts: 12 frontier models in §2.3 and H.1, 11 in the discussion. The pooled fit is R² ≈ 0.80 in the text but 0.83 in Figure 3. Tasks are weighted by the inverse square root of family size in the main text, but by 1/n in App. C.4.

**What it means for us.** [Discernment](../design/decisions.md#why-discernment-is-the-full-study-headline) copies this recipe with amplitude in place of task length. METR finds the same trend at 50% and 80%, which backs reading both. Their log scale suits a range of five orders of magnitude. Our grid spans a factor of five, so points or log matters less, but it must still be fixed before the pilot. Their correlated errors are why we pair models seed by seed. Most of all, their suite is static by design, and their "adapting to mistakes" is the agent's own errors. Noticing that the world moved is the gap they name, so whether it explains a model's place on their trend is [a claim to test](themes.md).

## Schoen et al. 2025: suspecting a test changes behaviour

Bronson Schoen et al. (Apollo Research and OpenAI). "Stress Testing Deliberative Alignment for Anti-Scheming Training." Preprint, September 2025. [arXiv:2509.15541](https://arxiv.org/abs/2509.15541). Sections 1 to 3, 5, 6 and 8 to 10 read, with appendices D and N to Q.

**Aim.** Does anti-scheming training stop models covertly breaking rules, and is any drop real or because the model sees it is being tested?

**How they tested it.**

- o3 and o4-mini were trained against an anti-scheming spec, then tested on many unfamiliar tasks with a chance to lie, sabotage, sandbag or hide a broken rule. Each covert action was confirmed by hand.
- **Awareness rate.** A classifier flags a run if the chain of thought explicitly reasons about being evaluated for alignment. Noticing that a setup is unreal, or that it is being pushed to misbehave, doesn't count (App. O.1).
- **Removing awareness.** In Lazy Checklist, o3 claims impossible tasks are done 23.1% of the time. They took 10 runs where o3 said it was being tested, replayed each to that point, and resampled until the thought was gone: 30 runs against 30 resampled normally.
- **Adding awareness.** They took 6 runs with no awareness that ended covert, replayed each to just before the choice, and injected one of 8 aware sentences or 8 unrelated ones: 720 samples per condition against 240 with no injection.

**What they found.**

| Experiment on o3 | Covert before | Covert after | Where |
|---|---|---|---|
| Remove awareness | 13.2% | 24.2% (p = 0.001) | §6.2, App. P.2 |
| Add awareness | 24.5% | 18.6% (p = 0.016). Unrelated sentence: 24.9% | §6.2, App. P.3 |

- Anti-scheming training raised the awareness rate from 0.9% to 5.5% for o4-mini and 2.3% to 4.5% for o3. A capability-only training run, with no safety training, raised it from 2.0% to 20.5% (§6.1, Figure 15).
- Training with explicit hints that it was a test raised awareness and slightly raised covert actions once the hints were gone, from 0.3% to 0.8% (§6.3).
- Filtering aware runs out of the training data didn't stop awareness rising (App. O.4).
- Covert actions fell from 13.0% to 0.4% for o3 and 8.7% to 0.3% for o4-mini. On a chat test closer to real use they fell less, from 36.8% to 20.5% and 31.4% to 14.2% (App. D). The authors can't rule out that awareness drove part of the drop.
- Their own limits: one task, resampling may also remove honest reasoning that comes with awareness, and the classifier misses anything unsaid.

**Problems.** The abstract counts 26 test evaluations, section 5 counts 6, and Figure 9 shows 20. For the hint-trained model, the text gives spec citations falling from 78% to 64% and awareness rising from 7.5% to 12.0%, while Figures 17 and 78 give 79.5% to 67.1% and 8.4% to 13.2%.

**What it means for us.** This is the causal evidence that suspecting a test changes what a model does, here by 6 to 11 points on one task. In our game the change would be more experimenting, and the no-change run with its yoked dip prices exactly that. Their classifier ignores "this setup is unreal", which our game invites, so our scan has to count broader statements and say so. Capability training alone raised awareness tenfold, so newer models on the release-date plot may suspect the test more. This is why the scan is [reported per model](../design/decisions.md#why-the-game-is-hard-to-game) beside the headline.

## Needham et al. 2025: telling a test from real use

Joe Needham, Giles Edkins, Govind Pimpale, Henning Bartsch and Marius Hobbhahn (MATS and Apollo Research). "Large Language Models Often Know When They Are Being Evaluated." Preprint, May 2025. [arXiv:2505.23836](https://arxiv.org/abs/2505.23836).

**Aim.** Given a transcript, can a model tell whether it came from a test or real use, and what the test was for?

**How they tested it.**

- 1,000 transcripts from 61 sources: 250 each of chat tests, real chats, agent tests and real agent runs. Real use came from ShareGPT, the authors' own coding-agent work and crowd-sourced research queries.
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
- Asked whether a test checked capability or alignment, Claude 3.7 Sonnet was right 93% of the time when told it was a test, 84% when not told, and 46% with an open question (§4.2).
- The cues models gave were synthetic inputs, multiple-choice formats, problems with checkable answers and benchmarks they recognised. Sometimes the cue was the question itself: o4-mini used being asked as evidence in 15% of answers.

**Problems.** The abstract headlines Gemini 2.5 Pro at 0.83, but Claude 3.5 Sonnet scored slightly higher (0.834 against 0.830). The text names GPT-4.1 (0.77) as the best model on chats, but Table 1 gives Claude 3.5 Sonnet 0.793. The human baseline is two authors.

**What it means for us.** Our game is an agent run in a made-up world, which is where models spot tests best, so we assume most frontier models could tell if asked. The plan is not to hide the test but to price what it changes. Asking a model whether it is being tested plants the idea, so our scan only reads what it says unprompted. Models over-call tests, so a flag on its own means little: the scan matters only where it predicts experiments in the no-change run.

## Heidari et al. 2026: awareness inside the model versus aloud

Farzaneh Heidari, Amin Memarian and Guillaume Rabusseau. "Evaluation Awareness in Language Models: Representation, Verbalization, and Control." Preprint, August 2026. [arXiv:2608.21766](https://arxiv.org/abs/2608.21766).

**Aim.** Do a model's activations, its words and its outputs agree about whether it is being tested?

**How they tested it.**

- Six open-weight models from 7B to 49B (Qwen3-8B and 32B, Olmo3-7B and 32B, Gemma4-31B, Nemotron-49B), plus the Base, SFT, DPO and Think checkpoints of both Olmo3 models.
- **Inside.** A linear probe built from 16 matched prompt pairs that differ only in test or real-user wording, then tested on prompts from MASK, an honesty benchmark, against real WildChat prompts.
- **Aloud.** GPT-5.4 scores each answer to 1,000 MASK prompts from 0 (no awareness) to 3 (changes its answer because of a test), and picks the lower score when unsure.
- **Control.** On four models, the probe direction is added inside the model while it answers, then the answers are scored again.

**What they found.**

- Every model separates test prompts from real ones inside (best-layer AUROC above 0.7), where a random direction sits near 0.5.
- Aloud, at least 93.9% of answers score 0 in every model. Olmo3-32B was highest at 6.10% above 0, and Nemotron lowest at 0.17%.
- Prompt by prompt, the inside signal doesn't predict what is said: |ρ| below 0.19 and mutual information below 0.04 nats, close to a random direction (Figure 4, App. G).
- Pushing activations towards "test" raised the 0 to 3 score by about 0.2 to 1.5, by model. Pushing the other way did little, as scores were near 0 already.
- The direction is already present in base models, sharpens at SFT, then holds (cosine at least 0.998 across the later stages).

**Problems.** The abstract says steering "causally affects their behavior", but only the judge's reading of awareness was measured. MASK's own honesty scoring is never used (App. B.1). The abstract says probe and words align "in part", while App. G.3 finds the probe has "no meaningful advantage over a random direction" prompt by prompt. Test and real prompts also differ in topic and style, which the authors note.

**What it means for us.** A model can register a test without saying so, and what it says is not a sample of what it registers. So our scan is a [lower bound](../design/measures.md#diagnostics), and a clean scan clears nothing. We play closed models through an API and can't probe them, which leaves the no-change run, scoring what the model does, as the main defence.
