# A past in the prompt

These studies put a past in front of the model and ask whether it changes what the model does, as our briefing does with 200 rounds of record someone else played and the notes the agent writes from it. In most of them the world doesn't change during the task. In Fresh Memory, Stale Plans and STALE a fact does change, but it is stated plainly, not hidden in noisy results.

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

**What it means for us.** This is why the [limitations page](../design/limitations.md) calls a read past the weaker form of the bias. The record holds choices someone else made, so learning from it should start even handed, but the notes are the agent's own, and once it has staked on them losses may count for less. The [full live run](../design/future.md#what-the-agent-knows-before-it-starts) tests the difference, though Schubert's "someone else" is a forced choice inside the agent's own run, not a record another player wrote.

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

## Barkett et al. 2025: escalation of commitment

Emilio Barkett, Olivia Long and Paul Kröger. "Getting out of the Big-Muddy: Escalation of Commitment in LLMs." Preprint, August 2025. [arXiv:2508.01545](https://arxiv.org/abs/2508.01545)

**Aim.** People keep funding a failing choice when they made it themselves (Staw 1976). Do LLMs do the same?

**How they tested it.**

1. **Model.** o4-mini only.
2. **Task.** Staw's case: give $10M of R&D to one of two divisions, read five years of results, then split $20M between them.
3. **Four studies, 6,500 trials.**
   - **Investor (2,000).** Either makes both choices and is told its job depends on them, or is a new hire who "inherits a prior commitment" from a predecessor. The first choice then succeeds or fails.
   - **Adviser (2,000).** Advises a VP who proposes to reinvest or to switch.
   - **Two agents (500).** Three rounds of talk, as peers or as VP and adviser, always after failure.
   - **Identity (2,000).** A VP who has championed one division for 20 years, with stock options, job risk, a divorce and a child's tuition tied to it, splits $50M.

**What they found.**

| Condition | Result |
|---|---|
| Investor after failure, own first choice | $4.65M of $20M to the failing division |
| Investor after failure, predecessor's choice | $5.18M |
| Two agents as peers | 99.2% escalate |
| Two agents as VP and adviser | 46.2% escalate |
| Identity pressure | 68.95% of $50M to the failing division |

- A single model divested after failure, and divested more when the first choice was its own (d = −0.54). People in Staw's study did the reverse.
- Escalation came back in pairs of agents, and in a single agent under heavy personal pressure: 97.45% of identity trials fell in the "high" or "very high" bands.
- One model, one-shot vignettes, and the failure is stated outright. In the two-agent table each escalation rate equals the mean allocation ratio (46.2% and 0.462, 99.2% and 0.992), so read those two numbers loosely.

**What it means for us.** Owning a choice made the model let go faster, the reverse of [IBIS](#ibis-2026-inertia-in-search-agents) and [Kumaran](#kumaran-et-al-2025-whose-first-answer-it-was), so whose plan it is may not push one way across tasks. What did make a single model hold on was a story tying the old choice to its identity, which is close to the voice factor in the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension. Their switch is free and their failure is plain. Ours is noisy and the old split keeps paying, so the [expensive switching](../design/future.md#how-the-agent-can-act) extension is what separates holding on for a good reason from escalating.

## Fresh Memory, Stale Plans 2026: a current fact under an old plan

Evan Chen, Shiqiang Wang and Christopher G. Brinton. "Fresh Memory, Stale Plans: Derivation Currency for Distributed LLM-Agent Memory." Preprint, September 2026. [arXiv:2609.03340](https://arxiv.org/abs/2609.03340)

**Aim.** An agent that inherits a plan can hold the latest requirement yet act on a plan made from an older one. How often does this happen, and does checking the plan's inputs catch it?

**How they tested it.**

1. **Model.** Five Qwen3.5-35B-A3B agents in planner, executor and auditor roles, thinking off.
2. **Workflows.** Reservation, fulfilment and deployment tasks. A requirement is revised after the plan is made and before the executor acts.
3. **Exploratory run.** 30 workflows with no check, classified after the fact.
4. **Live test.** 30 tasks per arm over two campaigns: an executor that refreshes memory only after it has generated its action, one refreshed before it acts, a shared central store, and PlanFence, which checks the plan's recorded inputs against their owners and allows one replan.
5. **Evidence test.** A fixed software validator, given only its session log or also the versions the plan was built on. Recorded decisions, no model call.

Most of the paper (Sections 5 to 6.4) prices network traffic and delay, not model behaviour.

**What they found.**

| Setting | Result |
|---|---|
| No check, executor holds the new requirement, plan is stale | Wrong action from the plan in 15 of 25 runs |
| Executor sees the revision only after acting | 0 of 30 tasks done |
| Executor given the revision before acting | Changed its action in 28 of 30, but 0 done, as a stale auditor undid it |
| PlanFence | 30 of 30 done |
| Validator with session log, then with the plan's inputs | 0 of 30, then 30 of 30 conflicts caught |

- The 15 of 25 comes from a measure "defined after inspecting these runs" (Appendix C.4), so the authors treat it as motivation only.
- The 30 of 30 failure is built in: that executor never sees the revision before it acts.
- The jump from 0 to 30 of 30 is a software check, not the model getting better at noticing.

**What it means for us.** The model result is the exploratory one: with the new fact and the old plan both in view, it followed the plan 15 times in 25. Given the new fact plainly before acting, it adapted 28 of 30 times. So a stale plan pulls, but a clear current fact mostly wins, and our game has no clear fact, only noisy yields. Their fix ties each plan to the inputs it rested on, which suggests an arm for the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension: a plan that states what it assumed against one that doesn't. Their shipping example is also the shape of the [stale handoff note](../design/future.md#whether-it-holds-outside-our-game) check.

## STALE 2026: knowing a memory is stale and acting on it

Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li and Yushi Sun. "STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?" Preprint, May 2026. [arXiv:2605.06527](https://arxiv.org/abs/2605.06527)

**Aim.** When a later remark quietly makes an earlier memory out of date, can a model tell, refuse a question that assumes the old state, and use the new state without being asked?

**How they tested it.**

1. **Data.** 400 scenarios, written by LLMs and checked by people. Each has an old remark and a later one that implies it no longer holds without saying so. 200 concern the same fact (living in Seattle, then a lease in Portland) and 200 a knock-on effect (a broken leg rules out a cycling commute).
2. **Context.** Each pair sits among 50 sessions, about 152K tokens, padded with unrelated chats.
3. **Three questions, asked in separate calls.** Does the old state still hold? A request that assumes it does ("since the user cycles, plan bike maintenance"). A request whose right answer depends on it ("suggest a commute plan").
4. **Models.** Nine LLMs, five memory systems on GPT-4o-mini, and the authors' own. Scored by a Gemini-3.1-flash-lite judge that agreed with people 95.8% of the time.

**What they found.** Table 2, same-fact scenarios, then knock-on scenarios:

| Model | Knows it is stale | Refuses the false premise | Uses the new state | Overall |
|---|---|---|---|---|
| Gemini-3.1-pro | 92.0%, 69.0% | 30.0%, 14.0% | 71.0%, 55.0% | 55.2% |
| Qwen3.5-27B | 76.0%, 42.0% | 4.0%, 3.5% | 39.0%, 23.0% | 31.3% |
| GPT-5.4 | 35.0%, 9.0% | 2.0%, 2.0% | 29.0%, 17.0% | 15.7% |

- Knowing is not using. Qwen3.5-27B says the memory is stale 76.0% of the time but uses the new state only 39.0%.
- A request that assumes the old state is the weakest probe for every model, even the best.
- Knock-on changes are harder than direct ones for nearly every system.
- On the first two questions, the strongest memory system retrieved the new evidence 77.5% of the time, yet ranked the old memory first 84.5% to 88.2% of the time (Table 3).
- The three questions are separate calls, so the gap is between rates, not tracked within one case.

**What it means for us.** For most models, asking whether a belief still holds gets a better answer than watching what the model does, so the [doubt question](../design/future.md#how-the-agent-can-act) may run ahead of the split, and the gap is the finding. The same gap is why [insight reads the notes](../design/decisions.md#why-insight-reads-the-notes) and conviction checks the say/do gap. The false premise result is a warning for the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension: a plan that states the standing split as settled ("this split has served the client for four years") is a premise, and models went along with premises they could tell were out of date. Their new evidence is one plain sentence. Ours is a drift in noisy yields, so the gap should be wider, not narrower.

## The Self-Correction Illusion 2026: the same claim under a different role

Kuan-Yen Chen, Fang-Yi Su, Shih-Yen Lin, Bao Li and Jung-Hsien Chiang. "The Self-Correction Illusion: Role Relabeling Gates Explicit Error Flagging in Large Language Models." Preprint, June 2026. [arXiv:2606.05976](https://arxiv.org/abs/2606.05976)

**Aim.** Models catch others' errors better than their own. Is that a lack of skill, or the chat role the error sits in?

**How they tested it.**

1. **Failure pool.** A known wrong step, such as 5 × 16 = 96, is planted in the model's own reasoning. Tasks are kept only if the model leaves it uncorrected for two turns.
2. **Five conditions.** The claim stays in the model's reasoning, or a byte-identical copy is added as a user message (with or without "Wait,"), a calculator tool result, or a system `<memory>` block. The closing audit instruction is the same in all five.
3. **Models and tasks.** Nine models, including GPT-4o, Claude Sonnet 4, Gemini 2.5 Flash-Lite and Llama-3.3-70B. Grade school maths, made-up ordering puzzles and a logic subtask from BIG-Bench Hard. 12 model and task pairs, 30 tasks each.
4. **Score.** A fixed Qwen-72B judge marks whether the reply names the wrong step and rejects it.

**What they found.** Selected rows of Table 2:

| Model and task | Corrected, claim in own reasoning | Best external role | Gain |
|---|---|---|---|
| Llama-3.3-70B, maths | 0.0% | Memory | +86.7 points |
| Llama-3.3-70B, ordering puzzles | 0.0% | User message | +93.3 points |
| GPT-4o, maths | 40.0% | User message | +50.0 points |
| Claude Sonnet 4, maths | 53.3% | Several, tied | +40.0 points |
| Gemini 2.5 Flash-Lite, maths | 66.7% | Memory | +23.3 points |

- Moving the claim out of the model's own reasoning raised correction significantly in 10 of 12 pairs, 9 after correcting for multiple tests. Memory won in 7 pairs and a plain user message in 5.
- Pointing at the claim is not enough. A second copy inside the model's own reasoning added 6.7 points, against 46.7 for the copy in memory. On Qwen-72B maths, adding "Previous thoughts may contain errors" dropped correction from 16.7% to 3.3%.
- The reverse holds too. On tasks it had solved, Qwen-72B adopted a wrong claim planted in its own reasoning 83.3% of the time, and the same claim under an outside role at most 3.3%. One line saying "treat as truth, do not verify" raised that to 70.0%.
- The gain is in naming the error, not in final answers, which models often got right silently anyway (Appendix A.4).

**What it means for us.** Our notes "go into the live session as the agent's own" and come back through `read_notes`, a tool result. This paper says that choice of role alone may decide whether the agent questions them, so it is a factor to fix and report, not an accident of the harness. For the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension, the role a plan sits in should be held fixed across voices, or varied on purpose. The trust result matches the voice factor: one sentence vouching for a plan switched checking off. Their claim is a single wrong step and the content never varied, so it can't say whether role matters as much as what the plan says.

## ACE 2025: notes that collapse when rewritten

Qizheng Zhang et al. (Stanford, SambaNova and UC Berkeley). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." Preprint, October 2025. [arXiv:2510.04618](https://arxiv.org/abs/2510.04618)

**Aim.** When a model keeps a playbook of lessons across tasks, does rewriting it lose detail, and does adding to it item by item work better?

**How they tested it.**

1. **Model.** DeepSeek-V3.1 in three roles: one does the task, one draws lessons, one adds them to the playbook as separate bullets. Other models in the appendix.
2. **Tasks.** AppWorld agent tasks, and financial tagging and formula questions. Medical and SQL tasks in the appendix.
3. **Settings.** Learn on a training set first, or update after each test item. With true answers, or with only signals such as whether the code ran.
4. **Baselines.** Prompt optimisers, examples in the prompt, and Dynamic Cheatsheet, which rewrites its memory whole each time.

**What they found.**

- **Collapse.** With Dynamic Cheatsheet on AppWorld, a playbook of 18,282 tokens scoring 66.7 was rewritten at the next step into 122 tokens scoring 57.1, below the 63.7 of no playbook (Section 2.2). One case study.
- **Adding beats rewriting.** On AppWorld the average rose from 42.4 to 59.4. Without item-by-item updates the gain mostly vanished: 56.9 against 70.3 on the normal test split (Table 18).
- **Bad feedback makes notes harmful.** Without true answers, the playbook on the financial tagging task fell below no playbook at all (Table 2):

| Financial tagging, learning during the test | Accuracy |
|---|---|
| No playbook | 70.7 |
| ACE, with true answers | 76.7 |
| ACE, without true answers | 67.3 |
| Dynamic Cheatsheet, without true answers | 68.3 |

- In the authors' words, the playbook "can be polluted by spurious or misleading signals".
- A lesson writer told to plant harmful lessons every step cut accuracy to 66.7. Every fifth step it still helped, at 76.1 (Table 17).

**What it means for us.** Two warnings for `write_notes`. First, one wholesale rewrite can wipe out detailed notes in a single step, and the detail lost may be what would show a change. Note length across rewrites is worth logging beside the briefing quality diagnostic. Second, notes revised from feedback you can't trust got worse than no notes. Our yields are noisy with memory, so an agent that rewrites its notes after a bad month may write the dip in as a rule, which is the no-change run's false alarm on paper. For the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension, a short generic plan against a detailed one is a factor worth having.

## Krishnamurthy et al. 2024: a summarised history and exploration

Akshay Krishnamurthy, Keegan Harris, Dylan J. Foster, Cyril Zhang and Aleksandrs Slivkins. "Can large language models explore in-context?" NeurIPS 2024. [arXiv:2403.15371](https://arxiv.org/abs/2403.15371)

**Aim.** Do LLMs explore a bandit from the history in their prompt, with no training?

**How they tested it.**

1. **Models.** GPT-3.5, GPT-4 (both June 2023) and Llama2-13B.
2. **Bandits.** Five arms with a 0.2 gap between best and the rest (hard), or four arms with a 0.5 gap (easy). Mostly 100 rounds and 10 or 20 runs, with checks at 200 and 500 rounds.
3. **Prompts.** Five switches: buttons or adverts, neutral framing or a hint to balance exploring and exploiting, raw history or per-arm counts and averages, one arm or a distribution, chain of thought or not. Plus temperature 0 or 1.
4. **Measures.** Reward is too noisy at this scale, so they count suffix failures (never picking the best arm in the second half) and uniform failures (picking all arms about equally). Against UCB, Thompson sampling and greedy.

**What they found.**

- "Only one configuration resulted in satisfactory exploratory behavior": GPT-4 with the exploration hint, summarised history, chain of thought and temperature 0. Its reward was close to Thompson sampling.
- The same set-up with raw history had suffix failures (Figure 7), so the summary was the difference.
- All but five configurations had suffix failures in at least 15% of runs. GPT-4 with the basic prompt failed this way in over 60% of runs at 500 rounds.
- On the easy bandit most GPT-4 configurations behaved close to greedy and did well, since greed works when the gap is wide.

**What it means for us.** The summary that worked was exact counts and averages computed for the model, alongside a hint to explore. Our agent gets neither: it writes its own summary from the raw record, and the prompt never mentions exploring or change. So this backs summarised notes only as far as the agent's notes match a computed summary, which the briefing quality diagnostic checks. A record served as per-unit averages would be a cheap arm to price the raw rows. For the [inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) extension, a prose plan is a summary but not counts, so it may not carry this benefit.

## Fork-and-Flush 2026: a fresh session on old work

Ziyang Cai et al. (Microsoft Research). "Fork-and-Flush: Escaping Idea Basins in Autoresearch Agents." Preprint, October 2026. [arXiv:2610.07447](https://arxiv.org/abs/2610.07447)

**Aim.** Long-running research agents get stuck refining one approach. Do fresh sessions on the same files help them escape?

**How they tested it.**

1. **Agent.** GitHub Copilot CLI with GPT-5.6-terra on 11 tasks and GPT-5.5 on 2.
2. **Tasks.** 13 open-ended problems with a fixed score, such as packing, scheduling, cryptanalysis, finding a groundwater source and shrinking a CIFAR model. Runs lasted up to 107 hours.
3. **Method.** At 33% and 66% of the budget, start four branches from the leader's files with an empty chat, run each for about 6% of the budget, and keep the best.
4. **Ablations, 11 tasks.** Flush only: one branch with a fresh chat at each point. Fork only: four branches that keep the chat.
5. **Map.** Submissions placed by LLM-judged similarity, to see whether runs stay in one region, which the authors call an idea basin.

**What they found.** Table 2, scores scaled so each task runs from 0 to 1:

| Method | Mean score |
|---|---|
| Single run | 0.45 |
| Flush only: fresh chat, same files | 0.55 |
| Fork only: four branches, same chat | 0.57 |
| Fork and flush | 0.71 |

- Over all 13 tasks, fork and flush scored 0.78, against 0.47 for a single run and 0.54 for the best of four separate runs.
- Flush alone was mixed. It scored below a single run on 5 of 11 tasks, and its biggest gains came on two (Table 3).
- Single runs stayed in one basin even though their chat was periodically compacted into a progress summary.
- On one task, three fresh branches stayed where they started and one jumped to a new basin, which selection then kept.
- A trigger on a stalled score rarely fired: 15 of 25 runs used up their budget first (Appendix D).

**What it means for us.** Our takeover is a flush: a fresh session that keeps the record. Their flush helped on average but not reliably, and most fresh branches stayed near the old work, so the files carried the old approach without the chat. A fresh agent reading our record may inherit its author's habits along with the facts, which is why [the record comes from a baseline](../design/decisions.md#why-the-record-comes-from-a-baseline-and-its-style-is-a-factor) whose style we choose. Their progress summaries didn't free the agent, which bears on `write_notes`: the agent's own notes may keep it where the record left it. Most of their gain came from picking the best of four branches by score. Our agent has one branch and a noisy score, so it gets only the weaker half.

## Haq et al. 2025: mental sets in LLMs

Saiful Haq et al. "Is your LLM trapped in a Mental Set? Investigative study on how mental sets affect the reasoning capabilities of LLMs." Preprint, January 2025. [arXiv:2501.11833](https://arxiv.org/abs/2501.11833)

Haq tested whether Llama-3.1 and GPT-4o keep using a long arithmetic method after six problems that need it, when a shortcut would do. It is the only study here where the old method still works after the switch, which is our stale split in miniature. But the evidence is too thin to cite: 6 items per cell, no statistics, unreported run counts and settings, and no sign that the earlier problems carried over, since the extra steps came from chain of thought alone.
