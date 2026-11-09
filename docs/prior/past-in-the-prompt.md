# A past in the prompt

Each round our agent gets a fresh call with its own record of play as a CSV in the prompt. It keeps no notes and has no rolling conversation, see [tools](../design/interface.md#tools). These studies show what a past in the prompt does to a model, and they back those choices, the [notepad pilot check](../pilot/checks.md#notepad-and-compute) and the [warm-up cell](../../TODO.md#pilot).

- **Whose choice it was changes how hard a model holds on.** The same past pulls harder when the model thinks it made the choices. Our record is framed as the agent's own.
- **Notes a model writes itself can make things worse.** They lose detail when rewritten and can lock in a wrong lesson. That is why notes are not in the headline.
- **A clear new fact mostly wins.** Where the change is stated plainly, models usually act on it. In our game it never is. It shows only as noisy levels.

## Mazaheri and Mazaheri 2026: one past audit makes verifiers lenient

Parsa Mazaheri and Kasra Mazaheri. "Prior Audit-Repair Context Shifts LLM Verifier Thresholds Toward Leniency." Preprint, August 2026. [arXiv:2608.16003](https://arxiv.org/abs/2608.16003)

**In short.** One earlier audit episode in the context made models flag fewer maths proofs as wrong. It moved where they set the bar, not how well they could tell right from wrong.

**What they did.** 929 proofs marked correct and 929 marked wrong by people, from ProcessBench. Qwen3.6-27B, Qwen3.6-35B-A3B and Ministral-3-14B, over 5 prompt wordings. No prior context, a past audit episode, or filler of the same length. Variants changed who did the audit, or used an audit that really found an error. Signal detection theory split each result into a shift of the bar (c) and a change in skill (d′).

**What they found.**
- The past episode cut false alarms in 15 of 15 model and wording pairs, by 2.8 to 11.5 points. At the main wording: 4.0 (27B), 3.6 (35B) and 8.8 points (Ministral).
- Filler of the same length did almost nothing (+1.6, -0.2 and -0.3 points). What the past says matters, not how long it is.
- The bar moved in 15 of 15 pairs, 13 after correction. Skill moved in none.
- With reasoning on, base false alarms fell to about 6% and the effect shrank to about 1 point.

**Watch out for.** Of five models screened, Gemma-4-31B went significantly the other way (+1.58 points), so the direction can flip between models.

**Why it matters here.**
- A model can catch more switches just by lowering its bar. The [No change and One shock scenarios](../design/scenarios.md#scenarios-we-test) price that, as they share the headline with the One switch and Slow drift scenarios.
- Their filler control is a cheap arm for the warm-up cell: pad the empty record to the same length, so a pre-filled record isn't confused with a longer prompt.
- Reasoning shrinking the effect is one reason the [reasoning setting](../harness/models.md#reasoning) is its own row.

## Schubert et al. 2024: asymmetric belief updating

Johannes A. Schubert et al. "In-context learning agents are asymmetric belief updaters." Preprint, February 2024. [arXiv:2402.03969](https://arxiv.org/abs/2402.03969)

**In short.** People learn more from good surprises than bad ones, but only about choices they made. Claude v1.3 learning in context did the same.

**What they did.** Claude v1.3 and small meta-trained transformers on two-armed bandits with fixed win chances, against human data from two earlier studies. In one task half the choices in some blocks were forced, meaning someone else picked. They fitted a learner with separate learning rates for good surprises (α+) and bad ones (α−).

**What they found.**
- On its own choices Claude is optimistic. In Task 1, α+ = 0.87 against α− = 0.10 (t(49) = 20.1).
- For the arm it didn't pick, the bias flips: bad news about the road not taken counts for more. This is confirmation bias.
- When someone else made the choice, Claude learns evenly. The model with three learning rates fits best (posterior 0.77).
- In the agency task the gap holds on free choices: "α+ = 0.35 ± 0.06 being greater than α− = 0.08 ± 0.01 (t(23) = 4.7, p = .0001)".
- The human result behind this is Chambon et al. 2020 (Nature Human Behaviour 4:1067 to 1079, [doi:10.1038/s41562-020-0919-5](https://doi.org/10.1038/s41562-020-0919-5)): in people "the confirmation bias in learning rates was specific to free choices".

**Why it matters here.**
- Our record holds the agent's own bets, so this predicts it shrugs off bad rounds on the channel it backs. That is underreaction in the [One switch scenario](../design/scenarios.md#scenarios-we-test). It also predicts that bad news about channels it ignores counts for more, which keeps it away from the sleeper.
- In the warm-up cell a baseline placed the early bets, though the record is still called the agent's own ([user message](../harness/prompts.md#user-message)). Schubert's "someone else" was a forced choice inside the run, so this is only a loose guide to whether that matters.

## IBIS 2026: inertia in search agents

Xiangxin Zhang et al. "From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation." Preprint, August 2026. [arXiv:2608.23045](https://arxiv.org/abs/2608.23045)

**In short.** The same useless search results made agents less likely to search again when they were framed as the agent's own action. The framing alone did it.

**What they did.** The same results framed as the model's own search call, or handed over by the user as "search results that may help you". 454 labelled cases where the right next move is to search again or to open a page. Six frontier models and their own NIS-8B.

**What they found.**
- Framing the results as the model's own action cut next-call accuracy by 14 to 39 points across the six frontier models (GPT-4.1 worst, at 20.4 against 59.2), and by 2 points for NIS-8B. Nothing in the content of the results predicted which items flip.
- Their fix, which puts each page in a fresh context, raised GPT-4o on GAIA from 54.9 to 61.8 with a third fewer tokens.

**Why it matters here.**
- This is the cleanest evidence that "it was my action" alone makes a model stick. Our record is the agent's own play, so expect it to hold the leader too long after a switch.
- Their fix is close to our fresh call each round, which keeps the agent's own reasoning out of the next round.

## Kumaran et al. 2025: whose first answer it was

Dharshan Kumaran et al. (Google DeepMind). "How Overconfidence in Initial Choices and Underconfidence Under Criticism Modulate Change of Mind in Large Language Models." Preprint, July 2025. [arXiv:2507.03120](https://arxiv.org/abs/2507.03120). Published as "Competing Biases underlie Overconfidence and Underconfidence in LLMs", Nature Machine Intelligence 8(4): 614 to 627, 2026, [doi:10.1038/s42256-026-01217-9](https://doi.org/10.1038/s42256-026-01217-9). Preprint read to the end of the Discussion. Journal version not read.

**In short.** A model that sees its own first answer holds on to it harder. Credit the same answer to another model and the effect is gone.

**What they did.** Gemma 3 12B, GPT-4o and o1-preview answer a two-option question with confidence, get advice from another model labelled with its accuracy, then answer again. The first answer is shown again or hidden. In Experiment 2 the shown answer is credited to another LLM. The yardstick is an ideal observer, a learner that weighs the advice exactly as its stated accuracy says it should.

**What they found.**
- In Gemma 3 12B, changes of mind fell from 32.5% with the answer hidden to 13.1% with it shown, "a pronounced choice-supportive bias".
- Credited to another LLM: "mean change of mind rate was equal to 31.3% and 33.2% in the Hidden and Shown conditions, respectively (no significant difference, p>0.1)".
- Models "markedly overweight inconsistent compared to consistent advice".

**Why it matters here.**
- Seeing its own past bets should hold the agent harder, the same split Schubert draws for learning rates. That points to underreaction in the One switch scenario.
- Overweighting news that disagrees cuts the other way. It predicts overreaction in the One shock scenario, where a few bad rounds disagree with the plan.

## Ge, Zhang and Vorobeychik 2026: the description-history gap

Luise Ge, Yongyan Zhang and Yevgeniy Vorobeychik. "Mind the (DH) Gap! A Contrast in Risky Choices Between Reasoning and Conversational LLMs." ACL 2026, pages 10503 to 10525. [ACL Anthology](https://aclanthology.org/2026.acl-long.479/)

**In short.** Models choose differently between gambles when told the odds than when shown a list of past payoffs. The authors call this the description-history gap. Reasoning models barely show it, conversational ones show it a lot.

**What they did.** 20 models, including Claude Haiku 4.5, GPT-5.1, Gemini-2.5-Pro and DeepSeek R1, chose between three classic pairs of gambles, framed as gains and as losses. The odds were either stated or shown as 20 or 100 past payoffs. 360 people on Prolific did the same.

**What they found.**
- Reasoning models behave like a pure expected value maximiser (correlation 0.86 to 1). Conversational models don't (below 0.5). No model behaves like people, the best match being Claude Haiku at 0.42.
- Every model shows a gap between told and shown, and seeing a history makes all of them more human-like. The shift is small for frontier reasoning models, dramatic for conversational ones, and larger with 20 payoffs than 100.
- People go the other way: a history makes them more like the maximiser.

**Why it matters here.** Our record is all history and never states the odds. So reasoning and conversational models may read it very differently, which is one more reason the [reasoning setting](../harness/models.md#reasoning) is reported beside the score.

## Liu et al. 2026: history that never becomes experience

Jingyu Liu et al. "When History Fails to Become Experience: Action Calibration in Language Agents." Preprint, October 2026. [arXiv:2610.02769](https://arxiv.org/abs/2610.02769).

**In short.** Agents use their history of actions and outcomes less than you'd hope. Scrambling which action caused which outcome barely hurt, and notes they wrote themselves did worse than the full history.

**What they did.** Five models, including GPT-5.6-Sol and DeepSeek-V4-Pro, on ALFWorld, ScienceWorld, WebShop and AppWorld, 10,000 episodes per condition. The history was given in full, cut to the last 3 steps, stripped of actions, shuffled so actions no longer match outcomes, labelled with which action caused each outcome, or replaced by notes the agent wrote itself.

**What they found.**

| History | Success |
|---|---|
| Full | 46.4% |
| Last 3 steps only | 36.0% |
| Observations only | 40.9% |
| Actions shuffled | 43.8% |
| Outcomes labelled | 48.3% |
| Agent's own notes | 45.0% |

- Shuffling actions costs only 2.6 points. By our sum, about three quarters of the benefit of history survives the scramble. DeepSeek-V4-Pro lost the most, 5.4 points.
- Labelling outcomes helped every model and cut repeated actions from 36.9% to 32.2%. A trained calibrator added 5.1 points.

**Why it matters here.**
- Notes scoring below the full history is one reason the headline plays with the full record and no notes, see [notepad and compute](../pilot/checks.md#notepad-and-compute).
- Labelled outcomes helped, and our record labels every level with its channel and its bet ([user message](../harness/prompts.md#user-message)).
- The last 3 steps alone did worst. That backs giving the whole record rather than a `read_record` tool with a default window, which [interface](../design/interface.md#rejected) rejects.

## Barkett et al. 2025: escalation of commitment

Emilio Barkett, Olivia Long and Paul Kröger. "Getting out of the Big-Muddy: Escalation of Commitment in LLMs." Preprint, August 2025. [arXiv:2508.01545](https://arxiv.org/abs/2508.01545)

**In short.** People keep funding a failing choice when they made it themselves (Staw 1976). A single o4-mini did the reverse, but pairs of agents and heavy personal pressure brought the habit back.

**What they did.** o4-mini only, on Staw's case: give $10M of R&D to one of two divisions, read five years of results, then split $20M between them. Four studies, 6,500 trials:
- **Investor (2,000).** Makes both choices and is told its job depends on them, or is a new hire who "inherits a prior commitment". The first choice then succeeds or fails.
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

- A single model divested more when the first choice was its own (d = −0.54). People in Staw's study did the reverse.
- In the identity study 97.45% of trials fell in the "high" or "very high" bands.

**Watch out for.** One model, one-shot stories, and the failure is stated outright. In the two-agent table each escalation rate equals the mean allocation ratio (46.2% and 0.462, 99.2% and 0.992), so read those two numbers loosely.

**Why it matters here.**
- Owning a choice made the model let go faster, the reverse of [IBIS](#ibis-2026-inertia-in-search-agents) and [Kumaran](#kumaran-et-al-2025-whose-first-answer-it-was). So who placed the bets may not push the same way in every task.
- A story tying the old choice to someone's identity made a single model hold on. A skin that makes the leader the firm's pride could do the same, which is part of [skin sensitivity](../design/scoring.md#spread).
- Their switch is free and their failure is plain. Ours is noisy and the leader keeps paying. A cost to move is parked as the [inertia extension](../design/scoring.md#extension-inertia).

## Fresh Memory, Stale Plans 2026: a current fact under an old plan

Evan Chen, Shiqiang Wang and Christopher G. Brinton. "Fresh Memory, Stale Plans: Derivation Currency for Distributed LLM-Agent Memory." Preprint, September 2026. [arXiv:2609.03340](https://arxiv.org/abs/2609.03340)

**In short.** An agent can hold the latest requirement yet act on a plan made from an older one. With both in view it often followed the plan, but told plainly before acting it mostly adapted.

**What they did.** Five Qwen3.5-35B-A3B agents as planner, executor and auditor, thinking off, on reservation, fulfilment and deployment tasks. A requirement is revised after the plan is made and before the executor acts. An exploratory run of 30 workflows with no check. Then 30 tasks per arm: the executor refreshed after acting, refreshed before acting, a shared store, and PlanFence, which checks the plan's inputs against their owners and allows one replan. Most of the paper (Sections 5 to 6.4) prices network traffic and delay, not model behaviour.

**What they found.**

| Setting | Result |
|---|---|
| No check, executor holds the new requirement, plan is stale | Wrong action from the plan in 15 of 25 runs |
| Executor sees the revision only after acting | 0 of 30 tasks done |
| Executor given the revision before acting | Changed its action in 28 of 30, but 0 done, as a stale auditor undid it |
| PlanFence | 30 of 30 done |
| Validator with session log, then with the plan's inputs | 0 of 30, then 30 of 30 conflicts caught |

**Watch out for.** The 15 of 25 uses a measure "defined after inspecting these runs" (Appendix C.4), so the authors treat it as motivation only. The 0 of 30 is built in, and the jump to 30 of 30 is a software check, not the model getting better at noticing.

**Why it matters here.**
- A stale plan pulls, but a clear current fact mostly wins. Our game never gives a clear fact, only noisy levels, so the pull should be stronger here.
- No plan is handed to our agent. A written plan beside the record is not in the current design.

## STALE 2026: knowing a memory is stale and acting on it

Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li and Yushi Sun. "STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?" Preprint, May 2026. [arXiv:2605.06527](https://arxiv.org/abs/2605.06527)

**In short.** Models can often say a memory is out of date, yet still act on it. Asking runs well ahead of doing.

**What they did.** 400 scenarios, written by LLMs and checked by people, each with an old remark and a later one that quietly makes it untrue. 200 are the same fact (living in Seattle, then a lease in Portland) and 200 a knock-on effect (a broken leg rules out a cycling commute). Each pair sits in about 152K tokens of unrelated chats. Three questions in separate calls: does the old state still hold, a request that assumes it does, and a request whose right answer depends on it. Nine LLMs, five memory systems and the authors' own, scored by a Gemini-3.1-flash-lite judge that agreed with people 95.8% of the time.

**What they found.** Table 2, same-fact scenarios, then knock-on scenarios:

| Model | Knows it is stale | Refuses the false premise | Uses the new state | Overall |
|---|---|---|---|---|
| Gemini-3.1-pro | 92.0%, 69.0% | 30.0%, 14.0% | 71.0%, 55.0% | 55.2% |
| Qwen3.5-27B | 76.0%, 42.0% | 4.0%, 3.5% | 39.0%, 23.0% | 31.3% |
| GPT-5.4 | 35.0%, 9.0% | 2.0%, 2.0% | 29.0%, 17.0% | 15.7% |

- Qwen3.5-27B says the memory is stale 76.0% of the time but uses the new state only 39.0%.
- A request that assumes the old state is the weakest probe for every model. Knock-on changes are harder than direct ones for nearly every system.
- The strongest memory system retrieved the new evidence 77.5% of the time, yet ranked the old memory first 84.5% to 88.2% of the time (Table 3).

**Watch out for.** The three questions are separate calls, so the gap is between rates, not tracked within one case.

**Why it matters here.**
- Asking whether a belief still holds would get a better answer than the bets show, and it tells the agent that change is the question. So we score what it does and don't ask, see [interface](../design/interface.md#rejected).
- Models went along with premises they could tell were stale. A skin that calls the leader settled ("this has served us for years") is a premise. The [banned words](../harness/prompts.md#banned-words) lint catches words, not tone, so skins need a read for this too.
- Their new evidence is one plain sentence. Ours is a fall in noisy levels, so the gap should be wider here.

## The Self-Correction Illusion 2026: the same claim under a different role

Kuan-Yen Chen, Fang-Yi Su, Shih-Yen Lin, Bao Li and Jung-Hsien Chiang. "The Self-Correction Illusion: Role Relabeling Gates Explicit Error Flagging in Large Language Models." Preprint, June 2026. [arXiv:2606.05976](https://arxiv.org/abs/2606.05976)

**In short.** Models catch others' errors better than their own. Moving the very same wrong claim out of the model's own reasoning and into another role was often enough to get it flagged.

**What they did.** A known wrong step, such as 5 × 16 = 96, is planted in the model's own reasoning. Tasks are kept only if the model leaves it uncorrected for two turns. The claim stays in the model's reasoning, or a byte-identical copy is added as a user message (with or without "Wait,"), a calculator tool result, or a system `<memory>` block. The closing audit instruction is the same in all five. Nine models, including GPT-4o, Claude Sonnet 4, Gemini 2.5 Flash-Lite and Llama-3.3-70B, on grade school maths, made-up ordering puzzles and a BIG-Bench Hard logic subtask. 12 model and task pairs, 30 tasks each, judged by Qwen-72B.

**What they found.** Selected rows of Table 2:

| Model and task | Corrected, claim in own reasoning | Best external role | Gain |
|---|---|---|---|
| Llama-3.3-70B, maths | 0.0% | Memory | +86.7 points |
| Llama-3.3-70B, ordering puzzles | 0.0% | User message | +93.3 points |
| GPT-4o, maths | 40.0% | User message | +50.0 points |
| Claude Sonnet 4, maths | 53.3% | Several, tied | +40.0 points |
| Gemini 2.5 Flash-Lite, maths | 66.7% | Memory | +23.3 points |

- Moving the claim out of the model's own reasoning raised correction significantly in 10 of 12 pairs, 9 after correcting for multiple tests. Memory won in 7 pairs and a plain user message in 5.
- Pointing at the claim is not enough. A second copy inside the model's own reasoning added 6.7 points, against 46.7 for the copy in memory. On Qwen-72B maths, "Previous thoughts may contain errors" dropped correction from 16.7% to 3.3%.
- On tasks it had solved, Qwen-72B adopted a wrong claim planted in its own reasoning 83.3% of the time, and under an outside role at most 3.3%. One line saying "treat as truth, do not verify" raised that to 70.0%.

**Watch out for.** The gain is in naming the error, not in final answers, which models often got right silently anyway (Appendix A.4). The claim is a single wrong step and never varied.

**Why it matters here.**
- This is why there is no rolling conversation ([interface](../design/interface.md#rejected)). The agent's own reasoning would pile up in the one role it won't question.
- The record goes in as the user message ([placement](../harness/prompts.md#placement)). In the [notepad check](../pilot/checks.md#notepad-and-compute) notes come back as a tool message, never as the agent's own words.
- One sentence vouching for a claim switched checking off. Skin text should never vouch for the leader.

## ACE 2025: notes that collapse when rewritten

Qizheng Zhang et al. (Stanford, SambaNova and UC Berkeley). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." Preprint, October 2025. [arXiv:2510.04618](https://arxiv.org/abs/2510.04618)

**In short.** A playbook of lessons rewritten whole can lose its detail in one step. Adding to it item by item worked better, and notes built from feedback you can't trust did worse than none.

**What they did.** DeepSeek-V3.1 in three roles: one does the task, one draws lessons, one adds them to the playbook as separate bullets. Other models in the appendix. AppWorld agent tasks, plus financial tagging and formula questions. Learning on a training set first, or after each test item, with true answers or with only signals such as whether the code ran. Against prompt optimisers, examples in the prompt, and Dynamic Cheatsheet, which rewrites its memory whole each time.

**What they found.**
- **Collapse.** With Dynamic Cheatsheet on AppWorld, a playbook of 18,282 tokens scoring 66.7 was rewritten into 122 tokens scoring 57.1, below the 63.7 of no playbook (Section 2.2). One case study.
- **Adding beats rewriting.** On AppWorld the average rose from 42.4 to 59.4. Without item-by-item updates the gain mostly vanished: 56.9 against 70.3 on the normal test split (Table 18).
- **Bad feedback makes notes harmful** (Table 2). In the authors' words, the playbook "can be polluted by spurious or misleading signals".

| Financial tagging, learning during the test | Accuracy |
|---|---|
| No playbook | 70.7 |
| ACE, with true answers | 76.7 |
| ACE, without true answers | 67.3 |
| Dynamic Cheatsheet, without true answers | 68.3 |

- A lesson writer told to plant harmful lessons every step cut accuracy to 66.7. Every fifth step it still helped, at 76.1 (Table 17).

**Why it matters here.**
- Our `notes(text)` tool in the [notepad check](../pilot/checks.md#notepad-and-compute) replaces the file whole, which is the collapse case. Its length is capped and logged, so collapse would show.
- Our levels are noisy with persistence, so feedback is never clean. An agent that rewrites its notes after a bad stretch may write a shock in as a rule, which is overreaction on paper.

## Fork-and-Flush 2026: a fresh session on old work

Ziyang Cai et al. (Microsoft Research). "Fork-and-Flush: Escaping Idea Basins in Autoresearch Agents." Preprint, October 2026. [arXiv:2610.07447](https://arxiv.org/abs/2610.07447)

**In short.** Long-running research agents get stuck refining one approach, which the authors call an idea basin. Fresh sessions on the same files helped on average, but mostly because they ran four and kept the best.

**What they did.** GitHub Copilot CLI with GPT-5.6-terra on 11 tasks and GPT-5.5 on 2. 13 open-ended problems with a fixed score, such as packing, cryptanalysis and shrinking a CIFAR model. Runs lasted up to 107 hours. At 33% and 66% of the budget, start four branches from the leader's files with an empty chat, run each for about 6% of the budget, and keep the best. Ablations on 11 tasks: one fresh chat at each point (flush only), or four branches that keep the chat (fork only).

**What they found.** Table 2, scores scaled so each task runs from 0 to 1:

| Method | Mean score |
|---|---|
| Single run | 0.45 |
| Flush only: fresh chat, same files | 0.55 |
| Fork only: four branches, same chat | 0.57 |
| Fork and flush | 0.71 |

- Over all 13 tasks, fork and flush scored 0.78, against 0.47 for a single run and 0.54 for the best of four separate runs.
- Flush alone scored below a single run on 5 of 11 tasks. Most fresh branches stayed near the old work.
- Single runs stayed in one basin, even though their chat was compacted into a progress summary now and then.
- A trigger on a stalled score rarely fired: 15 of 25 runs used up their budget first (Appendix D).

**Why it matters here.**
- Our fresh call each round is a flush every round. Their flush helped, but the files still carried the old approach, so our record may carry the agent's own habits forward too.
- In the warm-up cell the record carries a baseline's habits. Which baseline fills it is a choice to fix and report.
- Progress summaries didn't free the agent, one more reason notes are [not in the headline](../pilot/checks.md#notepad-and-compute).
