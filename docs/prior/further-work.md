# Further work, read less closely

Related work found in searches, grouped by the part of the design it bears on. Many were read only as an abstract, and each entry says how deeply.

## The new CEO

**Grove 1996.** *Only the Paranoid Survive*, Currency Doubleday. Not read in full. Its chapter "Signal or Noise?" is our game's question, and its new CEO thought experiment is the basis of the takeover. The Grove and Moore exchange is known to us only from secondary sources that disagree on the wording, so check a print copy before quoting it. We found no LLM paper that uses Grove's framing.

**Burgelman 1994.** "Fading Memories: A Process Theory of Strategic Business Exit in Dynamic Environments." Administrative Science Quarterly 39(1): 24 to 56, [doi:10.2307/2393493](https://doi.org/10.2307/2393493). Abstract read. The scholarly account of Intel leaving memory chips. Intel's rules for allocating factory capacity moved it to microprocessors before official strategy changed. A good agent's log should look the same: spend drifts away from its notes before the notes are rewritten.

**Denrell and March 2001.** "Adaptation as Information Restriction: The Hot Stove Effect." Organization Science 12(5): 523 to 538, [doi:10.1287/orsc.12.5.523.10092](https://doi.org/10.1287/orsc.12.5.523.10092). Abstract read. A learner stops trying an option that starts badly, so it never learns that the option has improved. That is why the rising unit can't be found from the record: the record's author stopped funding it long ago, so the evidence only comes if the agent pays to look.

**Tripsas and Gavetti 2000.** "Capabilities, Cognition, and Inertia: Evidence from Digital Imaging." Strategic Management Journal 21(10 to 11): 1147 to 1161. Abstract read. Polaroid built strong digital imaging skills, but beliefs formed in instant film held back what it did with them. A sourced case of knowing and not acting.

**Barkett et al. 2025.** "Getting out of the Big-Muddy: Escalation of Commitment in LLMs." [arXiv:2508.01545](https://arxiv.org/abs/2508.01545), read in full. A replication of Staw (1976) over 6,500 trials, where the model either made the first allocation or "inherit[s] a prior commitment" from a predecessor. Single models showed little escalation, and high responsibility made them divest more after failure (d = −0.54). Escalation appeared only in groups of agents. One-shot vignettes, not a sequence.

**Scaling Discovery Requires Forgetting** (Tan et al. 2026, [arXiv:2610.20563](https://arxiv.org/abs/2610.20563), read in full). Agents "become anchored to their own past attempts", and periodic resets give up to 39% over a single agent. The reset clears the session and the past candidates together. **Fork-and-Flush** (Cai et al. 2026, [arXiv:2610.07447](https://arxiv.org/abs/2610.07447), main text read) separates them: clearing the chat but keeping past candidates lifted the score from 0.45 to 0.55. Our takeover is that kind of reset, a fresh session that keeps the record.

**The Self-Correction Illusion** (Chen et al. 2026, [arXiv:2606.05976](https://arxiv.org/abs/2606.05976), abstract). Putting a byte-identical claim under a different chat role raised correction by 23 to 93 points, "significant in 10 of 12 experimental settings", and which role wins depends on the task. So the chat role a plan sits in may matter as much as what it says, an arm for the inherited plan extension.

**Debugging Decay Index** (Adnan and Kuhn 2025, [arXiv:2506.18403](https://arxiv.org/abs/2506.18403), Scientific Reports, abstract). Models lose "60-80% of their debugging capability within just 2-3 attempts", and a fresh start restores much of it.

**Others, snippet or abstract only.**

- **Mitigating Conversational Inertia in Multi-Turn Agents** ([arXiv:2602.03664](https://arxiv.org/abs/2602.03664)). A longer history of its own turns makes an agent copy its earlier answers more.
- **PsyAgentBench** (Bose 2026, [arXiv:2609.22090](https://arxiv.org/abs/2609.22090)). A "robust absence of sunk-cost effects" in open models. With Barkett, this says the past may not hold agents back at all, which would be a finding too.

## Inherited memory that goes stale

The notes are a memory the agent wrote from a record someone else played, and they may go out of date. These papers test the same pull with stored procedures that are wrong for the task. All use exact feedback, and none counts the opposite failure, dropping a stored method that still works.

- **SKILL.nb** (El Hattami et al. 2026, [arXiv:2606.08049](https://arxiv.org/abs/2606.08049), method and results read). Workflow memory carried across a real GitLab upgrade cut AWM from 48.9% to 34.4% and ReasoningBank from 50.0% to 38.9%. The clearest case of know-how going stale because the world changed.
- **The Compliance Trap** (Chen, Bai and Yuille 2026, [arXiv:2607.10608](https://arxiv.org/abs/2607.10608), main text read). Agents adopt hand-written wrong advice 63% to 72% of the time, at a cost of up to 26 points, and stronger models lose more. The advice was never right.
- **Hu, Long and Wang 2026** ([arXiv:2604.27003](https://arxiv.org/abs/2604.27003), read in full). Raw trajectories from one ALFWorld task cut success by 9.5 points on a task that needs one more step, and by 26.1 on hard cases.
- **Xiong et al. 2025** (ACL 2026, [arXiv:2505.16067](https://arxiv.org/abs/2505.16067), read in full). Agents copy a retrieved past record when the inputs look alike. Storing every run made all four agents worse than a small fixed memory.
- **Cao 2026** ([arXiv:2609.09774](https://arxiv.org/abs/2609.09774), read in full). A null result: with current evidence in plain view, a stale procedure caused none of the expected errors. So stale notes may bite only when evidence is weak, which is what noisy results make it.
- **STALE** (Chao et al. 2026, [arXiv:2605.06527](https://arxiv.org/abs/2605.06527), results read). Qwen3.5-27B recognised an invalidated memory 76.0% of the time but acted on it only 39.0%. Knowing and not acting, which the doubt question would catch.
- **When Memory Lies** (Sun and Zhang 2026, [arXiv:2608.04574](https://arxiv.org/abs/2608.04574), introduction read). In FrozenLake with a map that goes stale, an agent that trusts raw memory "dies more than twice as often as the same agent given no memory at all".
- **TRACE** (Xiong et al. 2026, [arXiv:2609.33517](https://arxiv.org/abs/2609.33517), abstract). An agent returns after teammates changed shared state. Restoring its memory in full admits stale state, starting empty discards what was still true, and each scores 0% on one of the two. A cost on both sides, as in our game.
- **Fresh Memory, Stale Plans** (Chen, Wang and Brinton 2026, [arXiv:2609.03340](https://arxiv.org/abs/2609.03340), abstract). An executor that checks only whether its memory is fresh acted on a stale inherited plan in 30 of 30 workflows. Telling it which inputs the plan rested on raised the conflicts caught from 0 to 30 of 30. The closest analogue to our takeover, with exact feedback.
- **TEPA** (Zhou et al. 2026, [arXiv:2608.07429](https://arxiv.org/abs/2608.07429), main text read). A hidden tool regime that reverses, after which append-only memory scores below no memory (0.210 against 0.309). The executor is a fixed script, not an LLM.

**What it means for us.** The pull of stored know-how is real and sometimes large, so the agent's own notes should bite. Our game adds noise with memory, so stale notes don't show at once, and a no-change run, so dropping notes that still work is counted.

## Handoffs and notes for a successor

- **Anthropic's engineering notes.** "Effective context engineering for AI agents" (September 2025) and "Effective harnesses for long-running agents" (Young, November 2025), both read in full. Agents hand over through a progress file, a feature list and git history. The failures named are a successor that sees progress and declares the job done, work left "half-implemented and undocumented", and "overly aggressive compaction" that loses "subtle but critical context". Our takeover is this pattern, made controlled.
- **ACE** (Zhang et al. 2025, [arXiv:2510.04618](https://arxiv.org/abs/2510.04618), abstract and section 2). Rewriting a playbook over and over makes it shorter and vaguer. In one example a rewrite cut it from 18,282 tokens to 122, and accuracy fell from 66.7 to 57.1, below the 63.7 of no playbook. Notes can lose the detail that would let their reader notice a change, which bears on `write_notes`.
- **Handoff Debt** (KC and Budathoki 2026, [arXiv:2606.02875](https://arxiv.org/abs/2606.02875), abstract). In 724 takeovers of interrupted coding tasks per model, handing over context cut the successor's events by 20 to 59% but barely changed how often it solved the task.
- **MAST** (Cemri et al. 2025, [arXiv:2503.13657](https://arxiv.org/abs/2503.13657), taxonomy read). In 1,600 multi-agent traces, failing to check work (9.1%) was far more common than failing to pass information on (under 3%). The weak link is the reader, not the writer.
- **Notes to self.** Reflexion (Shinn et al. 2023, [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)) and Dynamic Cheatsheet (Suzgun et al. 2025, [arXiv:2504.07952](https://arxiv.org/abs/2504.07952), abstract) show large gains from notes for the next attempt on fixed tasks, while Liu et al. found self-written notes made things worse. Nobody has tested notes written for a world that then changes.

## LLMs in worlds that change

- **KellyBench** (Grady et al. 2026, [arXiv:2604.27865](https://arxiv.org/abs/2604.27865), abstract and release page). Agents bet through a simulated 2023 to 2024 Premier League season with a log-bankroll goal. Every model lost money on average over five seeds, and six of twelve went bust at least once. Models "frontload model development" and "lack adaptivity throughout the season". The drift is the real season, uncontrolled, with no no-change copy.
- **Schmied et al. 2025** ("LLMs are Greedy Agents", [arXiv:2504.16078](https://arxiv.org/abs/2504.16078), read in full). Gemma2-27B wrote a correct UCB rationale 87% of the time, yet 58% of those choices were still greedy (the introduction says 64%). Gemma2-2B picked the most common action in its context 96% of the time. So an agent may write that its notes look stale and keep spending on them, and a record full of the standing split may pull smaller models to repeat it.
- **Rigidity in LLM bandits** (Wang, Ward and Zhang 2026, [arXiv:2603.07717](https://arxiv.org/abs/2603.07717), abstract). Over 20,000 trials per condition, models settle into "stubborn one-arm policies". Predicts too slow.
- **Explore or Confirm?** (Karim and Keon 2026, [arXiv:2610.25111](https://arxiv.org/abs/2610.25111), abstract). Five LLMs choosing noisy measurements err both ways: three confirm too much, one too little, and all end worse than a scripted baseline.
- **Goel et al. 2026** ([arXiv:2608.18490](https://arxiv.org/abs/2608.18490), abstract). In Overcooked, agents keep a stale plan after a teammate changes strategy, a "belief-action gap" of correct belief and wrong action.
- **Horowitz and Plonsky 2025** ([arXiv:2503.10248](https://arxiv.org/abs/2503.10248), abstract). LLMs show a strong pull towards the latest result, without the human pattern where a surprise triggers a change. Predicts jumpiness in the no-change run's dip.
- **Challenge alone flips answers.** Laban et al. 2023 ([arXiv:2311.08596](https://arxiv.org/abs/2311.08596)) found nine models flip 46% of the time when merely challenged, and Sharma et al. 2023 ([arXiv:2310.13548](https://arxiv.org/abs/2310.13548)) found Claude 1.3 wrongly conceded a mistake on 98% of questions. Social pressure, not data, but it shows how cheaply a model drops a correct position.
- **Plan against evidence.** Xie et al. 2024 ([arXiv:2305.13300](https://arxiv.org/abs/2305.13300), ICLR, abstract) found models accept coherent counter-evidence but show strong confirmation bias when evidence is mixed. Xu et al. 2024 ([arXiv:2403.08319](https://arxiv.org/abs/2403.08319)) survey these knowledge conflicts. Our results are always mixed.
- **Checked and set aside**, since nothing changes: Park et al. ([arXiv:2403.16843](https://arxiv.org/abs/2403.16843), which has some changing loss sequences we haven't checked), Monea et al. ([arXiv:2410.05362](https://arxiv.org/abs/2410.05362)), Harris and Slivkins ([arXiv:2502.00225](https://arxiv.org/abs/2502.00225)), Arumugam and Griffiths ([arXiv:2504.20997](https://arxiv.org/abs/2504.20997)) and "When Greedy Wins" ([arXiv:2509.24923](https://arxiv.org/abs/2509.24923)).

## Length alone

The record is read through a tool, 50 rows at a time, so its length doesn't set the prompt's. These papers are why.

- **Causal History Effects** (Li et al. 2026, [arXiv:2609.05882](https://arxiv.org/abs/2609.05882), abstract). Replacing an agent's own turns with neutral text helps a little (0.027), but no more than a neutral edit of the same length, as in Mazaheri's filler control.
- **Zhang et al. 2026** (ACL Findings, [arXiv:2601.02179](https://arxiv.org/abs/2601.02179)). Confidence rose by 11.75 and 14.61 points on placebo turns that added nothing, for Llama3.1-8B and Qwen2.5-72B.
- **A debate study** ([arXiv:2505.19184](https://arxiv.org/abs/2505.19184), abstract). Confidence rose from 72.9% to 83.3% over rounds of debate.

**What it means for us.** Change and no-change runs share the record and the notes, so comparing them is safe. [Complacency](../design/decisions.md#complacency-as-a-parameter-not-a-history) is less safe, since a longer record is longer wherever the agent reads it raw, so how much each agent reads is logged as the looking rate.

## The headline form

### Kwa et al. 2025: METR's time horizon

Kwa et al. (METR). "Measuring AI Ability to Complete Long Software Tasks." NeurIPS 2025. [arXiv:2503.14499](https://arxiv.org/abs/2503.14499). Abstract and method read, not the appendices.

**What they did.** 170 tasks from 1 second to 30 hours, each timed on human experts. For each of 12 frontier and 4 near-frontier models from 2019 to 2025, success is fitted as a logistic function of the log of task length, and the time horizon is where the curve crosses 50%.

**What they found.** Frontier horizons have doubled about every seven months since 2019 (R² ≈ 0.80 for the fit). Longer horizons come partly from "greater reliability and ability to adapt to mistakes": in reviews of about 60 failed runs, repeated failed actions fell from 12 to 2. Models do worse on "messier" tasks of the same length.

**What it means for us.** [Discernment](../design/decisions.md#why-discernment-is-the-full-study-headline) copies the recipe: success against one natural unit, read at 50% and 80%, plotted against release date. METR fits the log of length, so we must fix whether amplitude enters as points or their log before the pilot. Their "mistakes" are the agent's own in a task that stays the same, so the link to the time horizon is a claim to test.

## Belief, decisions and the reference bot

**Kelly 1956.** "A New Interpretation of Information Rate." Bell System Technical Journal 35(4): 917 to 926, [doi:10.1002/j.1538-7305.1956.tb03809.x](https://doi.org/10.1002/j.1538-7305.1956.tb03809.x). Citation checked, not read. Betting a share of the bankroll set by the edge. It shaped the [dropped coin flip game](../design/alternatives.md#why-the-coin-flip-game-was-dropped). A fixed budget doesn't compound, so the [budget split](../design/decisions.md#why-a-budget-split) doesn't need it.

**Shiryaev 1963.** "On optimum methods in quickest detection problems." Theory of Probability and Its Applications 8(1): 22 to 46, [doi:10.1137/1108002](https://doi.org/10.1137/1108002). Citation checked, not read. The classic problem behind our catch rule: spot a change that comes at a random time, trading delay against false alarms. The best rule is a threshold on the belief that the change has happened.

**Zhang, Yang and Wang 2025.** "Large Language Models as Discounted Bayesian Filters." [arXiv:2512.18489](https://arxiv.org/abs/2512.18489), read in full. One change at step 51 of 100, on small open models, with γ "significantly below 1" for every model. The useful idea is splitting error into "update divergence" and "misspecification divergence". The paper is inconsistent: a promised agent task never appears, and it claims a "first" nine months after Gupta et al.

**BayesBench** (Samanta et al. 2026, [arXiv:2606.30850](https://arxiv.org/abs/2606.30850), abstract). Bigger open models get closer to an exact posterior, but "these gains do not reliably carry over to downstream prediction". That gap between belief and use is why we score decisions.

**Qiu et al.** "Bayesian teaching enables probabilistic reasoning in large language models." Nature Communications, [arXiv:2503.17523](https://arxiv.org/abs/2503.17523), abstract. Off-the-shelf LLMs "fall far short" of an optimal Bayesian assistant, and training them to copy it helps.

**Krishnamurthy et al. 2024.** "Can large language models explore in-context?" NeurIPS 2024, [arXiv:2403.15371](https://arxiv.org/abs/2403.15371), method. "Only one configuration resulted in satisfactory exploratory behavior": GPT-4 with chain of thought and "an externally summarized interaction history". With BanditBench, this backs notes that summarise the record over the raw rows.

**Baker and McHale 2013.** "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion." Decision Analysis 10(3): 189 to 199, [doi:10.1287/deca.2013.0271](https://doi.org/10.1287/deca.2013.0271). Abstract read. Acting on an estimated rate as if it were known overcommits, most of all just after a change.

**Haghani and Dewey 2016.** "Rational Decision-Making Under Uncertainty: Observed Betting Patterns on a Biased Coin." [SSRN 2856963](https://doi.org/10.2139/ssrn.2856963), [arXiv:1701.01427](https://arxiv.org/abs/1701.01427). Read. 61 quantitatively trained young adults bet on a 60% heads coin: 28% went bust, 21% hit the $250 cap and 67% bet on tails at least once. A ready human baseline with no change, and no one has run LLMs on it.

**Griffin and Tversky 1992.** "The Weighing of Evidence and the Determinants of Confidence." Cognitive Psychology 24(3): 411 to 435, [doi:10.1016/0010-0285(92)90013-R](https://doi.org/10.1016/0010-0285(92)90013-R). Not read. People overweight how extreme evidence looks and underweight how reliable it is. The no-change run's dip is vivid and unreliable. Later replications are mixed.

**Geisler 2011.** "Contributions of ideal observer theory to vision research." Vision Research 51(7): 771 to 781, [doi:10.1016/j.visres.2010.09.027](https://doi.org/10.1016/j.visres.2010.09.027). Not read. The source of the ideal observer method we borrow.

## Quickest detection and drifting bandits

All citations checked, none read in full unless stated.

- **CUSUM.** Page 1954 (Biometrika 41(1/2): 100 to 115, [doi:10.1093/biomet/41.1-2.100](https://doi.org/10.1093/biomet/41.1-2.100)) adds up how much each result favours "changed" over "unchanged" and raises the alarm when the sum crosses a line. Lorden 1971 (Annals of Mathematical Statistics 42(6): 1897 to 1908, [doi:10.1214/aoms/1177693055](https://doi.org/10.1214/aoms/1177693055)) shows it is close to the best trade between delay and false alarms. Textbooks: Poor and Hadjiliadis 2009, and Tartakovsky, Nikiforov and Basseville 2014. Sweeping a CUSUM bot's line traces the whole trade between too slow and too jumpy. See [Corrections owed](../../TODO.md#corrections-owed).
- **Mellor and Shapiro 2013.** "Thompson Sampling in Switching Environments with Bayesian Online Change Detection." AISTATS, PMLR 31: 442 to 450, [arXiv:1302.3721](https://arxiv.org/abs/1302.3721). Thompson sampling, which picks each option with the chance it is best, joined to Adams and MacKay's detector. The bandit version of our reference bot, and one that experiments.
- **Nassar et al. 2010.** "An Approximately Bayesian Delta-Rule Model Explains the Dynamics of Belief Updating in a Changing Environment." Journal of Neuroscience 30(37): 12366 to 12378, [doi:10.1523/JNEUROSCI.0822-10.2010](https://doi.org/10.1523/JNEUROSCI.0822-10.2010). A learning rate that rises with the chance a change just happened, which fits people. A candidate for the noisy bots in [next step 2](../../TODO.md#next-steps).
- **Gallistel et al. 2014.** "The Perception of Probability." Psychological Review 121(1): 96 to 123, [doi:10.1037/a0035232](https://doi.org/10.1037/a0035232). Read. People tracking a probability that jumps hold an estimate, step to a new one, and sometimes take a detected change back, which [steadiness](../design/measures.md#diagnostics) counts. Forsgren et al. 2023 dispute the step-and-hold account.
- **Switching and drifting bandits.** Garivier and Moulines 2011 (ALT, [doi:10.1007/978-3-642-24412-4_16](https://doi.org/10.1007/978-3-642-24412-4_16)) give UCB rules that forget old results for arms that jump. Besbes, Gur and Zeevi 2014 (NeurIPS; Stochastic Systems 9(4): 319 to 337, 2019) bound any policy when total drift is limited, which fits a slow ramp better than a jump model.
- **Kinds of drift.** Gama et al. 2014 ("A Survey on Concept Drift Adaptation", ACM Computing Surveys 46(4): 44, [doi:10.1145/2523813](https://doi.org/10.1145/2523813)) name sudden, incremental, gradual and reoccurring drift. Our ramp is incremental and CoffeeBench's passing shock is reoccurring. See [How the world changes](../design/future.md#how-the-world-changes).

## Test awareness

- **Schoen et al. 2025** ("Stress Testing Deliberative Alignment for Anti-Scheming Training", [arXiv:2509.15541](https://arxiv.org/abs/2509.15541), abstract and section 6). Removing eval-aware reasoning from o3's chain of thought raised covert actions from 13.2% to 24.2%, and adding it lowered them from 24.5% to 18.6%. A capabilities-only training run raised how often models said it from 2.0% to 20.5%.
- **Abdelnabi and Salem 2025** ("The Hawthorne Effect in Reasoning Models", [arXiv:2505.14617](https://arxiv.org/abs/2505.14617), results read). Steering awareness changes behaviour in different directions for different models. Steering Qwen3-32B away from it doubled harmful execution, from 20.1% to 41.8%.
- **Needham et al. 2025** ([arXiv:2505.23836](https://arxiv.org/abs/2505.23836), abstract). Models tell eval transcripts from real ones well above chance, more easily for agentic ones. Gemini 2.5 Pro scored AUC 0.83 against 0.92 for people.
- **Heidari et al. 2026** ([arXiv:2608.21766](https://arxiv.org/abs/2608.21766), abstract). Being evaluated can be read from activations in every model tested, but what a model says aloud tracks it only in part. A scan of the reasoning is a lower bound.
- **System cards.** The Claude Sonnet 4.5 card (September 2025) reports eval awareness as common in automated audits, about 13% of transcripts by press accounts. We couldn't open the section, and snippets say later cards report more, with "modest behavioral effects".

**What it means for us.** Awareness changes behaviour and a scan sees only what is said, which is why the no-change run is the main defence. See [Why the game is hard to game](../design/decisions.md#why-the-game-is-hard-to-game).

## Can the architecture do it?

If a transformer can track a hidden change, a model that fails our game is failing at something it could do.

- **In-Context Learning Under Regime Change** ([arXiv:2604.16988](https://arxiv.org/abs/2604.16988)). Transformer constructions approximate the Bayesian predictor under an unknown change point, and small trained ones "match the performance of theoretically optimal baselines".
- **Akram and Vikalo** ([arXiv:2410.16546](https://arxiv.org/abs/2410.16546)). Transformers track a Kalman filter in context, the same point for smooth change.
- **Pre-trained LLMs learn HMMs in-context** ([arXiv:2506.07298](https://arxiv.org/abs/2506.07298)). Pretrained LLMs approach the best possible prediction on hidden Markov data.
- **Wang et al. 2016.** "Learning to reinforcement learn" ([arXiv:1611.05763](https://arxiv.org/abs/1611.05763)). A recurrent network meta-trained on restless bandits raised its learning rate in volatile episodes, the effect [complacency](../design/decisions.md#complacency-as-a-parameter-not-a-history) looks for.
- **CogBench** (Coda-Forno et al. 2024, [arXiv:2402.18225](https://arxiv.org/abs/2402.18225), methods and results read). Its restless bandit reports only how well confidence tracks accuracy, not learning rate by volatility, so no LLM test of that exists yet. **Centaur** (Binz et al., Nature 2025) is excerpts only.
- **Not Yet AlphaFold for the Mind** ([arXiv:2508.07887](https://arxiv.org/abs/2508.07887)). Run as a player, Centaur "exhibits weaker reversal dynamics", and some seeds never adapt.

## Card sorting

The Wisconsin Card Sorting Test, which Set-shifting 2026 borrows, is the classic test of dropping a rule that stopped working. In both studies below the switch follows the agent's own success, the old rule then always fails, and feedback is exact, so bad luck never passes for a change.

- **Li et al. 2025** ([arXiv:2506.16163](https://arxiv.org/abs/2506.16163), abstract). The rule changes after eight correct answers in a row. LLMs are "near-optimal decision-makers with a non-human learning behavior".
- **Hao, Alexandre and Yu 2025** ([arXiv:2505.22112](https://arxiv.org/abs/2505.22112), method). With chain of thought, GPT-4o, Gemini 1.5 Pro and Claude 3.5 Sonnet "achieve or surpass human-level set-shifting capabilities".

## Business simulations

A business world is a candidate [second game](../design/future.md#whether-it-holds-outside-our-game). These are the nearest besides STOCKTAKE.

**Bazaar** (Ahmed et al. 2026, [arXiv:2608.00102](https://arxiv.org/abs/2608.00102), abstract and method). Twelve customers swap tastes once, between rounds 31 and 40, and twelve unshocked customers act as controls, close to our no-change run. The best LLMs recover in about 5 to 15 rounds (text and caption disagree), and Thompson sampling three to five times slower. A scripted baseline losing to LLMs is a warning that [our bots](../design/decisions.md#why-the-bots-set-the-difficulty) must be tuned before they set anything.

**CoffeeBench** (Hattori et al. 2026, [arXiv:2606.16613](https://arxiv.org/abs/2606.16613), method). Demand triples on days 40 to 53, then returns. A shock that passes, where switching is the mistake, as Shopify and Hopin found. Only "rough reference values", no oracle.

**EconEvals** (Fish et al. 2025, [arXiv:2503.18825](https://arxiv.org/abs/2503.18825)). Procurement, scheduling and pricing against optimal profit. Only pricing changes, in a "predictable pattern".

**Long business simulations**, abstracts only: Vending-Bench ([arXiv:2502.15840](https://arxiv.org/abs/2502.15840)), RetailBench ([arXiv:2603.16453](https://arxiv.org/abs/2603.16453)), EnterpriseArena ([arXiv:2603.23638](https://arxiv.org/abs/2603.23638)), CEO-Bench ([arXiv:2606.17459](https://arxiv.org/abs/2606.17459)), Business Arena ([arXiv:2608.08621](https://arxiv.org/abs/2608.08621)) and MerchantBench ([arXiv:2607.28956](https://arxiv.org/abs/2607.28956)). EnterpriseArena runs 132 months "across changing macroeconomic regimes". None has a no-change control or a takeover.

**Allen and McDonald 2026.** "How Well Can AI Do Strategy? Empirical Benchmarking Using Strategy Simulations." Strategy Science 11(1): 93 to 117, [doi:10.1287/stsc.2025.0444](https://doi.org/10.1287/stsc.2025.0444). Abstract read. 34 LLMs on Back Bay Battery, a teaching game about when to invest in a disruptive technology. Models from late 2024 to early 2025 matched or beat MBA class averages, and later frontier models (GPT-5, Claude Opus 4.5, Gemini 3) scored lower, partly by favouring the core business. The comparison with 249 MBA students is unchecked. Newer was not better, a reason to keep older models in our line.

## Wording and familiar tasks

- **Familiar tasks flatter models.** Binz and Schulz 2023 (PNAS 120(6): e2218523120) found GPT-3 solved classic vignettes but failed small rewordings, and Ullman 2023 ([arXiv:2302.08399](https://arxiv.org/abs/2302.08399)) found the same for theory of mind. Neither read in full. This backs synthetic seeds and private skins.
- **Words bring priors.** With flipped labels, in-context learning plateaus short of the default labels (Kossen et al., [arXiv:2307.12375](https://arxiv.org/abs/2307.12375)), and larger models override their priors more (Shi et al. 2024, [arXiv:2405.19592](https://arxiv.org/abs/2405.19592)). Each skin's words carry priors of their own, which [Why four skins over one interface](../design/decisions.md#why-four-skins-over-one-interface) partly covers.
- **Kind and wicked learning.** Hogarth, Lejarraga and Soyer 2015 (Current Directions in Psychological Science 24(5): 379 to 385, [doi:10.1177/0963721415591878](https://doi.org/10.1177/0963721415591878)) split worlds where experience teaches the right lesson from worlds where it misleads. Our record is kind, and the ramp turns the world wicked without saying so.
