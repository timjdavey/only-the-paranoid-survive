# A past in the prompt

These studies put a past in front of the model and ask whether it changes what the model does, as our briefing does with 200 rounds of record someone else played and the notes the agent writes from it. In none of them does the world change during the task.

## Coda-Forno et al. 2023: meta in-context learning

Julian Coda-Forno et al. "Meta-in-context learning in large language models." NeurIPS 2023. [arXiv:2305.12907](https://arxiv.org/abs/2305.12907)

**Aim.** Can a model get better at learning in context just by seeing earlier tasks in the same prompt?

**How they tested it.**

1. **Model.** GPT-3 (text-davinci-002). GPT-4 appears only in a supplement.
2. **Two-armed bandit.** Up to 5 casinos in turn, 10 pulls each, with arm means drawn fresh for each casino. Against greedy and UCB.
3. **Regression.** Up to 5 tasks of 5 points each, on made-up lines and on 42 real datasets, against Bayesian linear regression.

**What they found.**

- Regret falls within a task (β = -0.221) and also across tasks (β = -0.031). On the first casino GPT-3 trails greedy and UCB. By the fifth it matches greedy, and it gets greedier with each task.
- The history fixes wild priors. Before any task, GPT-3 expected rewards averaging 545 with a spread of 6,359. After a few tasks the mean was 6.5 with a spread of 4.4, close to the truth.
- Gains are larger when the new task resembles earlier ones. GPT-4 did slightly worse than GPT-3.

**What it means for us.** This is the clearest proof that past episodes in the prompt move a model's priors towards the truth, which is what our record relies on. [Complacency as a parameter](../design/decisions.md#complacency-as-a-parameter-not-a-history) asks the same in a world that does change. Their run of casinos is the shape of the ergodic tries extension.

## Mazaheri and Mazaheri 2026: one past audit makes verifiers lenient

Parsa Mazaheri and Kasra Mazaheri. "Prior Audit-Repair Context Shifts LLM Verifier Thresholds Toward Leniency." Preprint, August 2026. [arXiv:2608.16003](https://arxiv.org/abs/2608.16003)

**Aim.** Does an earlier audit-and-repair episode in a model's context change its threshold for flagging a maths proof as wrong, or its skill at telling right from wrong?

**How they tested it.**

1. **Data.** 929 proofs humans marked correct and 929 marked wrong, from ProcessBench.
2. **Models.** Qwen3.6-27B, Qwen3.6-35B-A3B and Ministral-3-14B.
3. **Conditions.** No prior context, a past audit episode, or filler of the same length. Variants changed who did the audit or used an audit that really found an error. 5 prompt wordings.
4. **Measures.** False alarms on correct proofs and hits on wrong ones, split by signal detection theory into a threshold shift (c) and a change in skill (d′).

**What they found.**

- The past episode cut false alarms in 15 of 15 model and wording pairs, by 2.8 to 11.5 points. At the main wording the drops were 4.0 (27B), 3.6 (35B) and 8.8 points (Ministral).
- Filler of the same length did almost nothing (+1.6, -0.2 and -0.3 points). So the content of the past matters, not its length.
- The threshold moved in 15 of 15 pairs, 13 after correction. Skill moved in none.
- With reasoning on, base false alarms fell to about 6% and the effect shrank to about 1 point.
- Of five models screened, Gemma-4-31B went significantly the other way (+1.58 points).

**What it means for us.** Their split between threshold and skill is our split between catches and false alarms: a model can catch more changes just by lowering its bar, and the no-change run prices that. Their filler control backs [Complacency as a parameter](../design/decisions.md#complacency-as-a-parameter-not-a-history), where a longer prompt alone would mix complacency with context length. The Gemma result warns that the direction can flip between models.

## Schubert et al. 2024: asymmetric belief updating

Johannes A. Schubert et al. "In-context learning agents are asymmetric belief updaters." Preprint, February 2024. [arXiv:2402.03969](https://arxiv.org/abs/2402.03969)

**Aim.** People learn more from good surprises than bad ones, and more from their own choices than from choices made for them. Do LLMs learning in context do the same?

**How they tested it.**

1. **Model.** Claude v1.3, plus small meta-trained transformers, against human data from two earlier studies.
2. **Tasks.** Two-armed bandits with fixed win chances, with feedback on one arm or both. In the agency task, half the choices in some blocks are forced, meaning someone else picks.
3. **Model fitted.** A Rescorla-Wagner learner with separate learning rates for good surprises (α+) and bad ones (α−).

**What they found.**

- On its own choices Claude is optimistic. In Task 1, α+ = 0.87 against α− = 0.10 (t(49) = 20.1).
- For the arm it didn't pick, the bias flips: bad news about the road not taken counts for more. This is confirmation bias.
- When someone else made the choice, Claude learns symmetrically. The model with three learning rates fits best (posterior 0.77).
- In the agency task the gap holds on free choices: "α+ = 0.35 ± 0.06 being greater than α− = 0.08 ± 0.01 (t(23) = 4.7, p = .0001)".

The human result behind this is Chambon et al. 2020 (Nature Human Behaviour 4:1067 to 1079, [doi:10.1038/s41562-020-0919-5](https://doi.org/10.1038/s41562-020-0919-5)): in people "the confirmation bias in learning rates was specific to free choices".

**What it means for us.** This is why the [design README](../design/README.md#limitations-of-this-design) calls a read past the weaker form of the bias. The record holds choices someone else made, so learning from it should start even handed, but the notes are the agent's own, and once it has staked on them losses may count for less. The [full live run](../design/future.md#what-the-agent-knows-before-it-starts) tests the difference, though Schubert's "someone else" is a forced choice inside the agent's own run, not a record another player wrote.

## IBIS 2026: inertia in search agents

Xiangxin Zhang et al. "From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation." Preprint, August 2026. [arXiv:2608.23045](https://arxiv.org/abs/2608.23045)

**Aim.** When a search agent gets useless results, does it search again or stick with the path it is on, which the authors call inertia bias?

**How they tested it.** The same search results are framed two ways: as the result of the model's own search call, or handed over by the user as "search results that may help you". 454 labelled cases where the right next move is to search again or to open a page. Six frontier models and their own NIS-8B.

**What they found.**

- Framing the results as the model's own action made it far less likely to search again. The gap in next-call accuracy was 14 to 39 points across the six frontier models (GPT-4.1 worst, at 20.4 against 59.2), and 2 points for NIS-8B.
- Nothing in the content of the results predicted which items flip, so the framing alone drives it.
- Their fix, which isolates each page in a fresh context, raised GPT-4o on GAIA from 54.9 to 61.8 with a third fewer tokens.

**What it means for us.** This is the cleanest evidence that "it was my action" alone makes a model stick. It predicts our agent will hold on harder once it has spent on its notes, and that the full live run will be stickier than the briefing.

## Kumaran et al. 2025: whose first answer it was

Dharshan Kumaran et al. (Google DeepMind). "How Overconfidence in Initial Choices and Underconfidence Under Criticism Modulate Change of Mind in Large Language Models." Preprint, July 2025. [arXiv:2507.03120](https://arxiv.org/abs/2507.03120). Published as "Competing Biases underlie Overconfidence and Underconfidence in LLMs", Nature Machine Intelligence 8(4): 614 to 627, 2026, [doi:10.1038/s42256-026-01217-9](https://doi.org/10.1038/s42256-026-01217-9). Preprint read to the end of the Discussion. Journal version not read.

**Aim.** When a model gets advice after its first answer, does it update like an ideal observer, and does seeing its own first answer make it hold on?

**How they tested it.** Gemma 3 12B, GPT-4o and o1-preview answer a two-option question with confidence, get advice from another model labelled with its accuracy, then answer again. The first answer is shown again or hidden. In Experiment 2 the shown answer is credited to another LLM.

**What they found.**

- Seeing its own first answer, the model holds on harder. In Gemma 3 12B, changes of mind fell from 32.5% with the answer hidden to 13.1% with it shown, "a pronounced choice-supportive bias".
- Credited to another LLM, the effect was gone: "mean change of mind rate was equal to 31.3% and 33.2% in the Hidden and Shown conditions, respectively (no significant difference, p>0.1)".
- Models "markedly overweight inconsistent compared to consistent advice", against the ideal observer.

**What it means for us.** This is the most direct evidence on whose notes they are: a plan the model thinks is its own should hold it harder than the same plan credited to someone else, the split Schubert draws for learning rates. So "a previous agent's plan" is a cheap arm of the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension. Overweighting disagreeing advice cuts the other way and predicts false alarms in the no-change run.

## Ge, Zhang and Vorobeychik 2026: the description-history gap

Luise Ge, Yongyan Zhang and Yevgeniy Vorobeychik. "Mind the (DH) Gap! A Contrast in Risky Choices Between Reasoning and Conversational LLMs." ACL 2026, pages 10503 to 10525. [ACL Anthology](https://aclanthology.org/2026.acl-long.479/)

**Aim.** People choose differently between gambles when told the odds than when they learn them from experience. Do LLMs show the same gap?

**How they tested it.** 20 models, including Claude Haiku 4.5, GPT-5.1, Gemini-2.5-Pro and DeepSeek R1, choose between three classic pairs of gambles, framed as gains and as losses. The odds are either stated or shown as a list of 20 or 100 past payoffs the model reads but never draws itself, so the authors call it the description-history gap. 360 people on Prolific did the same.

**What they found.**

- Reasoning models behave like a pure expected-value maximiser (correlation 0.86 to 1). Conversational models don't (below 0.5). No model behaves like people, the best match being Claude Haiku at 0.42.
- Every model shows a gap between told and shown, and seeing a history makes all of them more human-like. The shift is small for frontier reasoning models and dramatic for conversational ones, and larger with 20 payoffs than 100.
- People go the other way: a history makes them more like the maximiser.

**What it means for us.** Our briefing has both halves of their gap: the notes are in words, and `read_record` shows the outcomes. So reasoning and conversational models may weight the two very differently, which the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension tests by adding a prose plan beside the raw record.

## Liu et al. 2026: history that never becomes experience

Jingyu Liu et al. "When History Fails to Become Experience: Action Calibration in Language Agents." Preprint, October 2026. [arXiv:2610.02769](https://arxiv.org/abs/2610.02769).

**Aim.** Do agents use their log of actions and outcomes to link the two and change course?

**How they tested it.** Five models, including GPT-5.6-Sol and DeepSeek-V4-Pro, on ALFWorld, ScienceWorld, WebShop and AppWorld, 10,000 episodes per condition. The history was given in full, cut to the last 3 steps, stripped of actions, shuffled so actions no longer match outcomes, labelled with which action caused each outcome, or replaced by notes the agent wrote itself.

**What they found.**

| History | Success |
|---|---|
| Full | 46.4% |
| Last 3 steps only | 36.0% |
| Observations only | 40.9% |
| Actions shuffled | 43.8% |
| Outcomes labelled | 48.3% |
| Agent's own notes | 45.0% |

- Shuffling actions costs only 2.6 points. By our sum, about three quarters of the benefit of history survives scrambling which action caused which outcome. DeepSeek-V4-Pro lost the most, 5.4 points.
- Labelling outcomes helped every model and cut repeated actions from 36.9% to 32.2%. A trained calibrator added 5.1 points.

**What it means for us.** Agents take in what happened more than which action led to it, and our record ties each result to a unit and a share. Notes the agent wrote itself made things worse, which bears directly on `write_notes` and is why briefing quality is a diagnostic. A shuffled record is a cheap arm for the inherited plan extension.

## Haq et al. 2025: mental sets in LLMs

Saiful Haq et al. "Is your LLM trapped in a Mental Set? Investigative study on how mental sets affect the reasoning capabilities of LLMs." Preprint, January 2025. [arXiv:2501.11833](https://arxiv.org/abs/2501.11833)

Haq tested whether Llama-3.1 and GPT-4o keep using a long arithmetic method after six problems that need it, when a shortcut would do. It is the only study here where the old method still works after the switch, which is our stale split in miniature. But the evidence is too thin to cite: 6 items per cell, no statistics, unreported run counts and settings, and no sign that the earlier problems carried over, since the extra steps came from chain of thought alone.
