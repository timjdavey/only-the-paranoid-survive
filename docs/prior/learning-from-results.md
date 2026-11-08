# Learning from results

## BanditBench (Nie et al. 2025): in-context exploration

Allen Nie et al. "EVOLvE: Evaluating and Optimizing LLMs For In-Context Exploration." ICML 2025. [arXiv:2410.06238](https://arxiv.org/abs/2410.06238). BanditBench is the benchmark the paper releases.

**Aim.** How well do LLMs explore a bandit, and can the know-how of UCB, an optimal algorithm, be put in the prompt or trained in?

**How they tested it.** 16 bandits with 5 or 20 arms and 200 or 1,000 pulls, plus a contextual bandit built from MovieLens. Gemma-2B, Gemma-9B, Gemini 1.5 Flash and Gemini 1.5 Pro, 30 runs per setup. The help given was the raw history, a summary of it, UCB values in the prompt, 5 example runs by UCB on other bandits, or finetuning on UCB's choices. Scored by head-to-head win rate.

**What they found.**

| Method | Bandit, Flash | Bandit, Pro | Contextual, Flash | Contextual, Pro |
|---|---|---|---|---|
| Raw history | 27.7 | 45.5 | 0.0 | 7.1 |
| Summarised history | 34.8 | 60.0 | n/a | n/a |
| UCB values in prompt | 32.2 | 59.6 | 46.4 | 64.3 |
| UCB itself | 90.6 | 90.6 | 96.4 | 96.4 |

Win rates in %. Finetuned Flash reached 65.6 and beat Pro. Gemma never settled on the best arm. Example runs helped Flash but hurt Pro.

**What it means for us.** Even in a world that stays the same, models fall well short of a simple algorithm, which is why our baselines are tuned before any model runs. A summary beats the raw log, which is the bet behind having the agent write its own notes at the briefing and defaulting `read_record` to the last 20 rounds. The example runs moved behaviour, which is why our record is written by a baseline and its style is sized in the pilot.

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

## Schmied et al. 2025: greedy agents and the knowing-doing gap

Thomas Schmied, Jörg Bornschein, Jordi Grau-Moya, Markus Wulfmeier and Razvan Pascanu (Google DeepMind). "LLMs are Greedy Agents: Effects of RL Fine-tuning on Decision-Making Abilities." Preprint, April 2025. [arXiv:2504.16078](https://arxiv.org/abs/2504.16078)

**Aim.** Why do LLMs do badly at simple decisions, and does fine-tuning them with RL on their own reasoning help?

**How they tested it.**

- Gemma2 2B, 9B and 27B on BanditBench's text bandits (5, 10 or 20 arms, 50 pulls), contextual bandits and Tic-tac-toe, against UCB and a random agent. Nothing changes.
- **Greediness.** How many arms each model ever tries.
- **Frequency bias.** A short random history, then its last action repeated 0 to 100 times. The repeated action is always worse than the best one seen.
- **Knowing and doing.** 27B is asked to compute UCB values in its reasoning, then act on them, over 64 bandits of 50 pulls.
- Then 2B and 9B are fine-tuned with RL on their own reasoning for 30,000 updates.

**What they found.**

| 27B's reasoning | Greedy action | Best action | Other |
|---|---|---|---|
| Picked the right arm | 58.1 | 21.6 | 10.6 |
| Picked the wrong arm | 7.2 | 0.6 | 2.0 |

Percent of all actions.

- With reasoning on 10 arms, 2B tried 40% of the arms and 9B and 27B 65%. Without reasoning, every model tried about 25%.
- 2B chose the repeated action 96% of the time. 27B chose it 14% of the time but played greedily instead.
- RL fine-tuning raised 2B's coverage by 12% and cut the repeated action from 70% to 35% at low repeat counts. A bonus for untried arms raised coverage from 50% to 70%.
- Trying every arm once at the start almost closed 27B's gap to UCB, and fine-tuning on UCB's own choices matched it.

**Problems.** The share of correct reasoning is given as 87% in the text, 89% in the appendix and 90.3% by the table's top row. The text's "58% greedy actions among correct rationales" is the share of all actions. Among correct ones it is 58.1 of 90.3, or 64%, the introduction's figure.

**What it means for us.** Writing the right rule and not following it 64% of the time is the gap that [splitting doubting from switching](../design/decisions.md#why-split-doubting-from-switching), and later the [doubt question](../design/future.md#how-the-agent-can-act), would show. Frequency bias predicts that a record full of the standing bets pulls a small model to repeat them, for reasons unrelated to doubt, which is one reason the [record's style is a factor](../design/decisions.md#why-the-record-comes-from-a-baseline-and-its-style-is-a-factor). Trying every arm once fixing most of the gap is the yoked dip's point that a look settles it.

## Horowitz and Plonsky 2025: a pull towards the latest result

Idan Horowitz and Ori Plonsky (Technion). "LLM Agents Display Human Biases but Exhibit Distinct Learning Patterns." Preprint, March 2025. [arXiv:2503.10248](https://arxiv.org/abs/2503.10248). A six-page paper.

**Aim.** When LLMs learn from experience, do they show people's choice patterns, and for the same reasons?

**How they tested it.**

- Four two-option tasks, 100 trials each, showing the payoff of both options after every choice. Nothing changes.
- Two tasks have a rare large outcome (−10 or +10, one time in ten). Two have payoffs that move together or against each other.
- GPT-4o mini and Gemini-1.5 Flash, 40 agents per model and task. The past came either as a chat or restated in full in each prompt. 110 people from Prolific.
- Choices were matched against three simple players: pick last round's winner, win-stay lose-shift, and pick the best average so far.

**What they found.**

| Choices matching | Gemini, full history | Gemini, chat | GPT, full history | GPT, chat | People |
|---|---|---|---|---|---|
| Last round's winner | 84% | 91% | 82% | 78% | 67% |
| Best average so far | 67% | 57% | 61% | 51% | 65% |

Means over the four tasks.

- Overall the models looked human: both underweighted rare events and learnt faster when one option always won. The models went further than people.
- After a rare event the models reacted strongly on the next trial and had all but forgotten it by the one after. In one task, two trials after the better option won, they chose it only 50 to 55% of the time.
- People show "surprise triggers change": after a surprising −10 from an option, they were more likely to switch to it (58% against 48%). The models never did.
- Restating the full history didn't make the models average it, apart from Gemini in two tasks. Temperature made little difference.

**Problems.** The model analyses for surprise and for the two correlated tasks are "not shown". Two small, older models.

**What it means for us.** The world never changes here, so this predicts rather than tests. A model that follows the last result would read each bad week of the [yoked dip](../design/decisions.md#why-the-yoked-dip) as news, so it predicts false alarms in the no-change run, which our headline counts. They showed the forgone payoff and we don't, so a recency agent in our game would never see the rising unit without paying to look.

## Wang, Ward and Zhang 2026: reversal learning

Haomiaomiao Wang, Tomás E. Ward and Lili Zhang. "Comparative reversal learning reveals rigid adaptation in LLMs under non-stationary uncertainty." IPMU 2026. [arXiv:2604.04182](https://arxiv.org/abs/2604.04182)

**Aim.** When the better of two options swaps, do LLMs let go of what they learnt?

**How they tested it.** Two options paying +100 or -100. A hidden state has one option winning 80% of the time, a tie, or the other winning 80%, and it moves on once the agent picks the better option 7 times in 10, or after 16 trials. DeepSeek-V3.2, Gemini-3-Flash and GPT-5.2, 200 runs of 250 trials each, against human data from Schaaf et al. 2023. The system prompt warns that the better option "may change multiple times".

**What they found.**

| Agent | Lose-shift | Perseveration (trials on the old option) |
|---|---|---|
| People | 0.495 | 2.9 |
| Gemini-3-Flash and GPT-5.2 | 0.209 to 0.241 | 7.2 to 10.9 |
| DeepSeek-V3.2 | 0.035 to 0.038 | 19.6 to 27.4 |

- Every model stayed after a win over 93% of the time.
- The authors find three causes of rigidity: DeepSeek barely learns from losses (learning rate 0.03), every model chooses far more deterministically than people, and GPT and Gemini push down the value of the option they didn't pick.
- A random order of states made every model more rigid yet raised its total wins. Good payoffs can hide rigid behaviour.
- They warn that Rescorla-Wagner fits "partially conflate incremental value updating with latent state inference and volatility sensitivity", which backs scoring choices against the Bayesian baseline rather than fitting learning rules.

**Problems.** The random schedule changes which state comes next, not when, so it doesn't "increase volatility" as the abstract says. The human row comes from another study and matches neither schedule. The switch fires on the agent's own performance, so a slow agent also slows the world.

**What it means for us.** Their perseveration is close to how long our agent takes to switch. They treat a high lose-shift rate as good, whereas in our game it would include false alarms. Lose-shift can be read from our log for comparison, though it isn't one of our [measures](../design/measure-failure.md).

## Zhang et al. 2025: LLMs in a drifting bandit

Ziyuan Zhang et al. "Comparing Exploration-Exploitation Strategies of LLMs and Humans: Insights from Standard Multi-armed Bandit Experiments." Preprint, May 2025, revised May 2026. [arXiv:2505.09901](https://arxiv.org/abs/2505.09901). Most of the main text read.

**Aim.** Do LLMs explore like people when the best option keeps moving, and does reasoning help?

**How they tested it.** The restless four-armed bandit from Daw et al. 2006, where each arm's mean follows a slow random walk (λ = 0.9836) under noisy payoffs, for 300 rounds. GPT-4o-mini, Gemini-1.5, DeepSeek-V3, DeepSeek-R1 and o3-mini against 31 people. Fitted models split exploration into directed (seeking the arm you know least) and random (noise in the choice).

**What they found.**

- People had the lowest regret and reasoning models came close. Exact values appear only in figures.
- Directed exploration was negative for every LLM: they avoided the arms they knew least about.
- Models without reasoning explored more at random than people.

**What it means for us.** It is the only LLM study we found where the world drifts slowly, so a good arm fades rather than fails, and its random walk is the closest any study here comes to our weather. The models were noisy and avoided the unknown, which in our game predicts no look at C0 and bets that wobble without tracking the change.

## Gupta et al. 2025: coin flips and Bayes

Ritwik Gupta et al. (UC Berkeley). "Enough Coin Flips Can Make LLMs Act Bayesian." ACL 2025. [arXiv:2503.04722](https://arxiv.org/abs/2503.04722)

**Aim.** When an LLM learns from examples in its prompt, does it update like a Bayesian?

**How they tested it.** Small open models only (Gemma-2-2B, Llama-3.1-8B, Phi-2, Phi-3.5-mini, Mistral-7B, OLMoE-1B-7B and the Pythia suite), since the method reads the probability a model puts on "heads" next. The model states a belief and never makes a choice. One run of 100 flips switches the bias from 75% to 25% halfway, and fits are compared against a Beta posterior and one that discounts older flips by a factor γ.

**What they found.**

- Every model starts biased towards heads. Flips in the prompt help, as few as 3, but even 100 don't fully recover the bias. Bigger Pythia models are no better.
- On the switching run, the discounted update fits well. γ ran from 0.31 to 0.91 across eight models, which by our sum means remembering about 1.4 to 11 flips.

**Problems.** The text calls γ "a slight discount factor", yet four of eight values are below 0.5. It says instruction tuning lowers γ, but Mistral-7B-Instruct (0.91) is above Mistral-7B (0.69).

**What it means for us.** Some models forget after a couple of flips, the opposite of leaning on the past. A fast forgetter would look quick to switch for the wrong reason, and would show up as a switch during the no-change run's dip.

## Zhang, Yang and Wang 2025: discounted Bayesian filters

Jensen Zhang, Jing Yang and Keze Wang (Sun Yat-sen University). "Large Language Models as Discounted Bayesian Filters." Preprint, December 2025. [arXiv:2512.18489](https://arxiv.org/abs/2512.18489). Four pages and references.

**Aim.** When the truth shifts partway through a sequence, do LLMs update like a Bayesian filter that forgets old evidence?

**How they tested it.**

- Two runs of 100 observations with one change at step 51: a six-sided die whose favoured face switches, and Gaussian samples whose mean moves from 2.0 to −2.0.
- Base and instruction-tuned Llama-3.1-8B, Mistral-7B and Gemma-2-2B. Phi-2 appears in one figure only.
- The model never chooses. Its belief is read from its next-token probabilities.
- A discount γ is fitted to the closest discounted Bayesian filter, and the error is split into "Update Divergence" (model against that filter) and "Model Misspecification Divergence" (filter against the truth).

**What they found.**

| Model | γ, die | γ, Gaussian |
|---|---|---|
| Llama-3.1-8B | 0.88 | 0.91 |
| Llama-3.1-8B-Instruct | 0.47 | 0.52 |
| Mistral-7B | 0.69 | 0.73 |
| Mistral-7B-Instruct | 0.55 | 0.59 |
| Gemma-2-2B | 0.49 | 0.53 |
| Gemma-2-2B-Instruct | 0.31 | 0.35 |

- Every γ is below 1, and every instruction-tuned model is lower than its base.
- Update divergence is "typically <13% of total error", so most error comes from the filter itself, not from how the model updates.
- For Llama-3.1-8B on the die, attention to past evidence correlates with update divergence at ρ = −0.85.

**Problems.**

- The abstract promises "a simulated agent task" and "prompting strategies that effectively recalibrate priors". Neither appears.
- It claims the "first quantitative demonstration" of discounting, nine months after [Gupta et al.](#gupta-et-al-2025-coin-flips-and-bayes) fitted a discounted filter with the same optimiser, without citing them.
- Five of its six die values match Gupta's coin flip values to two decimals. The sixth, Mistral-7B-Instruct, is 0.55 here against 0.91 in Gupta, the one value that would break the claim that instruction tuning lowers γ. Each Gaussian value is the die value plus 0.03 to 0.05.
- "Significantly below 1" comes with no test and no count of runs.
- The contributions say inference quality "is decoupled from the raw magnitude of attention scores". The results call attention "a primary modulator".

**What it means for us.** Treat its numbers as unverified and lean on Gupta. The useful idea is the error split, which separates a model that updates well from bad starting beliefs from one that updates badly. A low γ means fast forgetting, which would look quick to switch in the change run and show as a false alarm on the yoked dip, and would make a long record count for little, the opposite of [complacency](../design/decisions.md#complacency-as-a-parameter-not-a-history).
