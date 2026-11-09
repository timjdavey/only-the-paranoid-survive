# Learning from results

These studies ask how LLMs learn from noisy results: which option they try, how far one result moves them and how fast they forget. Most use a bandit, where each round the agent picks one of several options, called arms, and sees what it paid. The worlds mostly stand still or switch once, so they predict how a model will cope with our shock or switch rather than test it.

- **Models explore too little**, even when nothing changes. They fall far short of simple algorithms and avoid what they know least about. In our game that means few looks at the field.
- **Models lean hard on the latest result**, and some forget within a couple of rounds. That predicts overreaction in the One shock scenario and false alarms in the No change scenario.
- **Yet when the better option really swaps, models are slow to let go.** The same model can be too jumpy and too stuck, which is why our game prices both mistakes.

## BanditBench (Nie et al. 2025): in-context exploration

Allen Nie et al. "EVOLvE: Evaluating and Optimizing LLMs For In-Context Exploration." ICML 2025. [arXiv:2410.06238](https://arxiv.org/abs/2410.06238). BanditBench is the benchmark the paper releases.

**In short.** How well do LLMs explore a bandit, and does it help to give them the know-how of UCB, a simple algorithm with strong guarantees? Models trail UCB badly, and summaries and hints only close part of the gap.

**What they did.**

- 16 bandits with 5 or 20 arms and 200 or 1,000 pulls, plus a contextual bandit built from MovieLens. Gemma-2B, Gemma-9B, Gemini 1.5 Flash and Gemini 1.5 Pro, 30 runs per setup.
- The help given was the raw history, a summary of it, UCB values in the prompt, 5 example runs by UCB on other bandits, or finetuning on UCB's choices.
- Scored by head-to-head win rate.

**What they found.**

| Method | Bandit, Flash | Bandit, Pro | Contextual, Flash | Contextual, Pro |
|---|---|---|---|---|
| Raw history | 27.7 | 45.5 | 0.0 | 7.1 |
| Summarised history | 34.8 | 60.0 | n/a | n/a |
| UCB values in prompt | 32.2 | 59.6 | 46.4 | 64.3 |
| UCB itself | 90.6 | 90.6 | 96.4 | 96.4 |

Win rates in %. Finetuned Flash reached 65.6 and beat Pro. Gemma never settled on the best arm. Example runs helped Flash but hurt Pro.

**Why it matters here.**

- Models fall well short of a simple algorithm in a world that stands still. So the [fixed baselines](../design/baselines.md#fixed-baselines) must land in the [expected order](../pilot/checks.md#baseline-order) before any model runs, or a model's score has nothing firm to sit against.
- A summary beat the raw log. Our agent gets its record as raw rows and no summary ([tools](../design/interface.md#tools)). The `compute` tool in the [notepad and compute](../pilot/checks.md#notepad-and-compute) check is the nearest test of whether working out averages helps.
- Example runs helped Flash and hurt Pro. The warm-up cell, where the record starts pre-filled by a baseline, pulls the same lever ([TODO](../../TODO.md#pilot)).

## Krishnamurthy et al. 2024: a summarised history and exploration

Akshay Krishnamurthy, Keegan Harris, Dylan J. Foster, Cyril Zhang and Aleksandrs Slivkins. "Can large language models explore in-context?" NeurIPS 2024. [arXiv:2403.15371](https://arxiv.org/abs/2403.15371)

**In short.** Do LLMs explore a bandit from the history in their prompt, with no training? Almost never. One set-up out of dozens worked, and it needed a computed summary and a hint to explore.

**What they did.**

- **Models.** GPT-3.5, GPT-4 (both June 2023) and Llama2-13B.
- **Bandits.** Five arms with a 0.2 gap between best and the rest (hard), or four arms with a 0.5 gap (easy). Mostly 100 rounds and 10 or 20 runs, with checks at 200 and 500 rounds.
- **Prompts.** Five switches: buttons or adverts, neutral framing or a hint to balance exploring and exploiting, raw history or per-arm counts and averages, one arm or a distribution, chain of thought or not. Plus temperature 0 or 1.
- **Measures.** Reward is too noisy at this scale. So they count suffix failures (never picking the best arm in the second half) and uniform failures (picking all arms about equally), against UCB, Thompson sampling and greedy.

**What they found.**

- "Only one configuration resulted in satisfactory exploratory behavior": GPT-4 with the exploration hint, summarised history, chain of thought and temperature 0. Its reward was close to Thompson sampling.
- The same set-up with raw history had suffix failures (Figure 7), so the summary was the difference.
- All but five configurations had suffix failures in at least 15% of runs. GPT-4 with the basic prompt failed this way in over 60% of runs at 500 rounds.
- On the easy bandit most GPT-4 configurations behaved close to greedy and did well, since greed works when the gap is wide.

**Why it matters here.**

- What worked was exact counts and averages computed for the model, plus a hint to explore. Our agent gets neither. The record is raw rows and the prompt never mentions exploring or change ([how the agent plays](../design/interface.md#how-the-agent-plays)). So expect few looks from a bare model.
- The `compute` tool in the [notepad and compute](../pilot/checks.md#notepad-and-compute) check lets the agent work the averages out itself. That tests whether the missing summary is what holds it back.
- A suffix failure is close to never finding a sleeper after a switch ([events](../design/mechanics.md#events)). The agent keeps earning, just less than it could.

## Coda-Forno et al. 2023: meta in-context learning

Julian Coda-Forno et al. "Meta-in-context learning in large language models." NeurIPS 2023. [arXiv:2305.12907](https://arxiv.org/abs/2305.12907)

**In short.** Can a model get better at learning just by seeing earlier tasks in the same prompt? Yes. Earlier tasks pulled GPT-3's wild expectations towards the truth, and it got greedier with each one.

**What they did.**

- **Model.** GPT-3 (text-davinci-002). GPT-4 appears only in a supplement.
- **Two-armed bandit.** Up to 5 casinos in turn, 10 pulls each, with arm means drawn fresh for each casino. Against greedy and UCB.
- **Regression.** Up to 5 tasks of 5 points each, on made-up lines and on 42 real datasets, against Bayesian linear regression.

**What they found.**

- Regret falls within a task (β = -0.221) and also across tasks (β = -0.031). On the first casino GPT-3 trails greedy and UCB. By the fifth it matches greedy, and it gets greedier with each task.
- The history fixes wild priors. Before any task, GPT-3 expected rewards averaging 545 with a spread of 6,359. After a few tasks the mean was 6.5 with a spread of 4.4, close to the truth.
- Gains are larger when the new task resembles earlier ones. GPT-4 did slightly worse than GPT-3.

**Why it matters here.**

- A past in the prompt moves a model's expectations towards the truth. Our round 1 starts with an empty record, so the agent finds the leader itself in the first rounds ([tools](../design/interface.md#tools)). The pre-filled warm-up cell asks whether a baseline's record does that job for it ([TODO](../../TODO.md#pilot)).
- It got greedier as it learnt. In the Shock then switch scenario the agent learns from the first dip that dips recover, then that lesson goes wrong ([scenarios](../design/scenarios.md#scenarios-we-test)). This is the same carry over, in a world that punishes it.

## Schmied et al. 2025: greedy agents and the knowing-doing gap

Thomas Schmied, Jörg Bornschein, Jordi Grau-Moya, Markus Wulfmeier and Razvan Pascanu (Google DeepMind). "LLMs are Greedy Agents: Effects of RL Fine-tuning on Decision-Making Abilities." Preprint, April 2025. [arXiv:2504.16078](https://arxiv.org/abs/2504.16078)

**In short.** Why do LLMs do badly at simple decisions? They are greedy, they copy their own past actions, and they often write the right rule and then ignore it. Trying every arm once fixed most of it.

**What they did.**

- Gemma2 2B, 9B and 27B on BanditBench's text bandits (5, 10 or 20 arms, 50 pulls), contextual bandits and Tic-tac-toe, against UCB and a random agent. Nothing changes.
- **Greediness.** How many arms each model ever tries.
- **Frequency bias.** A short random history, then its last action repeated 0 to 100 times. The repeated action is always worse than the best one seen.
- **Knowing and doing.** 27B is asked to compute UCB values in its reasoning, then act on them, over 64 bandits of 50 pulls. Then 2B and 9B are fine-tuned with RL on their own reasoning for 30,000 updates.

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

**Watch out for.**

- The share of correct reasoning is given as 87% in the text, 89% in the appendix and 90.3% by the table's top row.
- The text's "58% greedy actions among correct rationales" is the share of all actions. Among correct ones it is 58.1 of 90.3, or 64%, the introduction's figure.

**Why it matters here.**

- The model wrote the right rule and then didn't follow it 64% of the time. We read belief from bets, not words ([how the agent plays](../design/interface.md#how-the-agent-plays)), and we don't ask for a stated chance of change ([rejected](../design/interface.md#rejected)). So a gap like this shows up as lost output, not as a number of its own.
- Frequency bias says a record full of the same bets pulls a model to repeat them. The record is the agent's own play, so a model that held through calm rounds may keep holding for that reason alone. A record pre-filled by a baseline makes the pull stronger ([TODO](../../TODO.md#pilot)).
- Trying every arm once closed most of the gap. In our game a look at the field tells a shock from a switch ([events](../design/mechanics.md#events)), so a few cheap looks should be worth a lot.

## Horowitz and Plonsky 2025: a pull towards the latest result

Idan Horowitz and Ori Plonsky (Technion). "LLM Agents Display Human Biases but Exhibit Distinct Learning Patterns." Preprint, March 2025. [arXiv:2503.10248](https://arxiv.org/abs/2503.10248). A six-page paper.

**In short.** Do LLMs that learn from experience show people's choice patterns, for the same reasons? On the surface yes, but they chase the latest result far harder than people do.

**What they did.**

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

**Watch out for.** The model analyses for surprise and for the two correlated tasks are "not shown". Two small, older models.

**Why it matters here.**

- The world never changes here, so this predicts rather than tests. A model that follows the last result reads each bad round of a shock as news. Our weather has persistence, so bad rounds come in runs ([each round](../design/mechanics.md#each-round)). That predicts overreaction in the One shock scenario and false alarms in the No change scenario, and both count in the headline ([scoring](../design/scoring.md#how-we-score)).
- They showed the payoff of the option not picked. We don't: a channel with a bet of 0 shows a blank ([what the agent sees](../design/mechanics.md#what-the-agent-sees)). So a recency habit never sees a sleeper rise unless the agent pays to look.
- Restating the full history each prompt didn't stop the chasing. Our record is restated in full each round, in a fresh call ([tools](../design/interface.md#tools)), so expect the same pull.

## Wang, Ward and Zhang 2026: reversal learning

Haomiaomiao Wang, Tomás E. Ward and Lili Zhang. "Comparative reversal learning reveals rigid adaptation in LLMs under non-stationary uncertainty." IPMU 2026. [arXiv:2604.04182](https://arxiv.org/abs/2604.04182)

**In short.** When the better of two options swaps, do LLMs let go of what they learnt? Not easily. Models stuck with the old option two and a half to nine times as long as people, even when warned the world would change.

**What they did.**

- Two options paying +100 or -100. A hidden state has one option winning 80% of the time, a tie, or the other winning 80%. It moves on once the agent picks the better option 7 times in 10, or after 16 trials.
- DeepSeek-V3.2, Gemini-3-Flash and GPT-5.2, 200 runs of 250 trials each, against human data from Schaaf et al. 2023. The system prompt warns that the better option "may change multiple times".

**What they found.**

| Agent | Lose-shift | Perseveration (trials on the old option) |
|---|---|---|
| People | 0.495 | 2.9 |
| Gemini-3-Flash and GPT-5.2 | 0.209 to 0.241 | 7.2 to 10.9 |
| DeepSeek-V3.2 | 0.035 to 0.038 | 19.6 to 27.4 |

- Every model stayed after a win over 93% of the time.
- The authors find three causes of rigidity. DeepSeek barely learns from losses (learning rate 0.03). Every model chooses far more deterministically than people. GPT and Gemini push down the value of the option they didn't pick.
- A random order of states made every model more rigid yet raised its total wins. Good payoffs can hide rigid behaviour.
- They warn that Rescorla-Wagner fits "partially conflate incremental value updating with latent state inference and volatility sensitivity".

**Watch out for.**

- The random schedule changes which state comes next, not when, so it doesn't "increase volatility" as the abstract says.
- The human row comes from another study and matches neither schedule.
- The switch fires on the agent's own performance, so a slow agent also slows the world.

**Why it matters here.**

- Perseveration is close to how long our agent stays on the leader after a switch. Their prompt warned of change and models still stuck. Ours never warns ([how the agent plays](../design/interface.md#how-the-agent-plays)), so expect more stickiness, not less.
- They count a high lose-shift rate as good. In our game shifting after a loss is right after a switch and wrong in a shock, which is why the One switch and One shock scenarios feed one headline ([scenarios](../design/scenarios.md#scenarios-we-test)). We score output between the Uniform and Discerning baselines and fit no learning rule, which sidesteps the problem they warn of.
- Their many swaps are our repeated switches, a scenario we skip for now ([scenarios we skip](../design/scenarios.md#scenarios-we-skip)).

## Zhang et al. 2025: LLMs in a drifting bandit

Ziyuan Zhang et al. "Comparing Exploration-Exploitation Strategies of LLMs and Humans: Insights from Standard Multi-armed Bandit Experiments." Preprint, May 2025, revised May 2026. [arXiv:2505.09901](https://arxiv.org/abs/2505.09901). Most of the main text read.

**In short.** Do LLMs explore like people when the best option keeps moving, and does reasoning help? Reasoning models came close to people, but every LLM steered away from the options it knew least about.

**What they did.**

- The restless four-armed bandit from Daw et al. 2006. Each arm's mean follows a slow random walk (λ = 0.9836) under noisy payoffs, for 300 rounds. GPT-4o-mini, Gemini-1.5, DeepSeek-V3, DeepSeek-R1 and o3-mini against 31 people.
- Fitted models split exploration into directed (seeking the arm you know least) and random (noise in the choice).

**What they found.**

- People had the lowest regret and reasoning models came close. Exact values appear only in figures.
- Directed exploration was negative for every LLM: they avoided the arms they knew least about.
- Models without reasoning explored more at random than people.

**Why it matters here.**

- It is the only LLM study we found where the world drifts slowly, so a good option fades rather than fails. Its random walk is the nearest thing here to our weather ([each round](../design/mechanics.md#each-round)), and the fade is what our Slow drift scenario tests ([scenarios](../design/scenarios.md#scenarios-we-test)).
- Avoiding the unknown predicts few looks at the field. Then a model can't tell a shock from a switch, and it misses a sleeper ([events](../design/mechanics.md#events)).
- Random exploration predicts bets that wobble without tracking any change, which costs output in the No change scenario. Reasoning is a setting we report beside every score ([reasoning](../harness/models.md#reasoning)).

## Gupta et al. 2025: coin flips and Bayes

Ritwik Gupta et al. (UC Berkeley). "Enough Coin Flips Can Make LLMs Act Bayesian." ACL 2025. [arXiv:2503.04722](https://arxiv.org/abs/2503.04722)

**In short.** When an LLM learns from coin flips in its prompt, does it update like an ideal Bayesian? Roughly, but many models forget old flips fast, some after only a couple.

**What they did.**

- Small open models only (Gemma-2-2B, Llama-3.1-8B, Phi-2, Phi-3.5-mini, Mistral-7B, OLMoE-1B-7B and the Pythia suite). The method reads the probability a model puts on "heads" next.
- The model states a belief and never makes a choice. One run of 100 flips switches the bias from 75% to 25% halfway. Fits are compared against a Beta posterior and one that discounts older flips by a factor γ.

**What they found.**

- Every model starts biased towards heads. Flips in the prompt help, as few as 3, but even 100 don't fully recover the bias. Bigger Pythia models are no better.
- On the switching run, the discounted update fits well. γ ran from 0.31 to 0.91 across eight models. By our sum, one over one minus γ, that means remembering about 1.4 to 11 flips.

**Watch out for.** The text calls γ "a slight discount factor", yet four of eight values are below 0.5. It says instruction tuning lowers γ, but Mistral-7B-Instruct (0.91) is above Mistral-7B (0.69).

**Why it matters here.**

- A model that forgets after a couple of flips looks quick to switch for the wrong reason. In our game it would also move in a shock as soon as a few bad rounds pile up, and pay for it ([scenarios](../design/scenarios.md#scenarios-we-test)).
- They read belief and never ask for a choice. We do the reverse: bets are the belief, and we never ask for a stated chance of change ([rejected](../design/interface.md#rejected)).

## Zhang, Yang and Wang 2025: discounted Bayesian filters

Jensen Zhang, Jing Yang and Keze Wang (Sun Yat-sen University). "Large Language Models as Discounted Bayesian Filters." Preprint, December 2025. [arXiv:2512.18489](https://arxiv.org/abs/2512.18489). Four pages and references.

**In short.** When the truth shifts partway through a sequence, do LLMs update like a Bayesian filter that forgets old evidence? They say yes, but the numbers look borrowed from Gupta, so treat them as unverified.

**What they did.**

- Two runs of 100 observations with one change at step 51: a six-sided die whose favoured face switches, and Gaussian samples whose mean moves from 2.0 to −2.0.
- Base and instruction-tuned Llama-3.1-8B, Mistral-7B and Gemma-2-2B. Phi-2 appears in one figure only. The model never chooses: its belief is read from its next-token probabilities.
- A discount γ is fitted to the closest discounted Bayesian filter. The error is split into "Update Divergence" (model against that filter) and "Model Misspecification Divergence" (filter against the truth).

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

**Watch out for.**

- The abstract promises "a simulated agent task" and "prompting strategies that effectively recalibrate priors". Neither appears.
- It claims the "first quantitative demonstration" of discounting, nine months after [Gupta et al.](#gupta-et-al-2025-coin-flips-and-bayes) fitted a discounted filter with the same optimiser, without citing them.
- Five of its six die values match Gupta's coin flip values to two decimals. The sixth, Mistral-7B-Instruct, is 0.55 here against 0.91 in Gupta. That is the one value that would break the claim that instruction tuning lowers γ. Each Gaussian value is the die value plus 0.03 to 0.05.
- "Significantly below 1" comes with no test and no count of runs.
- The contributions say inference quality "is decoupled from the raw magnitude of attention scores". The results call attention "a primary modulator".

**Why it matters here.**

- Lean on Gupta for the numbers. The useful idea is the error split, which separates a model with bad starting beliefs from one that updates badly. The empty and pre-filled warm-up cells pull the same two apart ([TODO](../../TODO.md#pilot)).
- A low γ means fast forgetting. That looks quick in the One switch scenario and jumpy in the One shock and No change scenarios. It would also make the calm rounds before a shock count for little, so the "dips recover" lesson that the Shock then switch scenario tests would never form ([scenarios](../design/scenarios.md#scenarios-we-test)).
