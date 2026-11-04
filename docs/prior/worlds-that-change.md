# Worlds that change

These studies change the world under the agent. None starts the agent from a record it must read and write its own notes on, only STOCKTAKE has noise with a run in it, and in all but STOCKTAKE and Zhang the old plan fails outright once the change lands.

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

**What it means for us.** Even in a world that stays the same, models fall well short of a simple algorithm, which is why our bots are tuned before any model runs. A summary beats the raw log, which is the bet behind having the agent write its own notes at the briefing and defaulting `read_record` to the last 20 rounds. The example runs moved behaviour, which is why our record is written by a bot and its style is sized in the pilot.

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
- They warn that Rescorla-Wagner fits "partially conflate incremental value updating with latent state inference and volatility sensitivity", which backs scoring choices against the reference bot rather than fitting learning rules.

**Problems.** The random schedule changes which state comes next, not when, so it doesn't "increase volatility" as the abstract says. The human row comes from another study and matches neither schedule. The switch fires on the agent's own performance, so a slow agent also slows the world.

**What it means for us.** Their perseveration is close to how long our agent takes to switch. They treat a high lose-shift rate as good, whereas in our game it would include false alarms. Lose-shift can be read from our log for comparison, though it isn't one of our [measures](../design/measures.md).

## Set-shifting 2026: tool groups that stop working

Ziwei Ye. "Set-shifting Behavioral Test for Harnessed Agents." COLM 2026 Workshop on Agent Behavior. [arXiv:2607.13396](https://arxiv.org/abs/2607.13396). Code at [zwycl/agent-wcst-mini-bench](https://github.com/zwycl/agent-wcst-mini-bench).

**Aim.** Can an agent change route when the group of tools that works changes silently, in the spirit of the Wisconsin Card Sorting Test?

**How they tested it.** The Hermes Agent harness with mimo-v2.5, deepseek-v4-pro, gemini-3.5-flash-lite and gpt-5.5, and claude-opus-4.8 as a smaller replication. Groups of identical tools differ only in name, and tools outside the working group always fail. Nothing in the prompt says the world can change. Over 90 turns the working group may change at turns 15, 40 and 65, and at each later change point the saved session is resumed three times: back to an old group, on to a new one, or no change. One arm adds an "adaptive" prompt that says to switch the moment a tool fails.

**What they found.**

- Locking into one routine was common: 66% for mimo and gemini, 50% for deepseek, 9% for gpt-5.5.
- gpt-5.5 kept calling old and new tools together. It finished tasks (0.87) but rarely committed.
- Only the latest change mattered, not the route to it. Off target, models went back to a group that had worked before, claude-opus-4.8 93% of the time.
- The adaptive prompt raised gpt-5.5 from 0.14 to 0.86 and deepseek from 0.38 to 0.74, and did almost nothing for mimo or gemini.

**What it means for us.** The resumed copies with no change are the closest thing in the literature to our no-change run, but a failed call is certain, so one failure reveals the change and a false alarm is almost impossible. Our standing unit never yields below 0.55, which goes past the noisy tools the authors list as future work. gpt-5.5 testing new tools without committing is knowing and not acting, and the adaptive prompt's large effect is why our prompt never names change.

## AdaExploreBench 2026: hidden rules that drift

Rui Wang et al. "AdaExploreBench: Benchmarking LLM Agents for Proactive Exploration and Test-time Adaptation in Evolving Environments." Preprint, October 2026. [arXiv:2610.25950](https://arxiv.org/abs/2610.25950)

**Aim.** Can agents explore to learn how a world works, then notice and adapt when it changes without notice?

**How they tested it.** Each case has 8 input fields, and a hidden rule over 3 of them picks the best of 4 actions. Once per episode, after batch 5, 6 or 7 of 12, one field is swapped for another and another's direction is reversed. Before each batch the agent may test up to 16 cases it designs. The prompt says the rule "may or may not change". 256 episodes, 8 models. Calibrated accuracy runs from 0 for a random policy to 1 for an oracle that knows the true rule.

**What they found.**

- Calibrated accuracy ranged from 67.3 (Gemini-3.8-Flash) to 8.1 (Llama-3.1-8B). The share of episodes where the agent's stated beliefs named the change ran from 63.7 to 6.3.
- At the drift, accuracy fell 26.9 points on average, and no model got back to its pre-drift level, ending 7 to 19 points below.
- Swapped fields were noticed three times as often as reversed directions (33.5% against 10.8%).
- Forcing the agent to probe did nothing.
- The abstract implies GPT-6-Sol (61.9) is the best model, but its own table puts Gemini-3.8-Flash higher.

**What it means for us.** It is the closest benchmark in shape. Calibrated accuracy runs from a floor to an oracle, as performance runs from the no-update bot to the reference bot. Swaps being noticed far more than reversals bears on the [later kinds of change](../design/future.md#how-the-world-changes), and forced probing doing nothing says experiments have to be the agent's own idea. But the oracle knows the true rule rather than seeing what the agent sees, feedback is exact, and false alarms aren't counted.

## STOCKTAKE 2026: a fair oracle for supply chains

Sagar Deb and Ashwanth Krishnan (QpiAI). "STOCKTAKE: Measuring the Gap Between Perception and Action in LLM Agents with a Fair Oracle." Preprint, July 2026. [arXiv:2607.13618](https://arxiv.org/abs/2607.13618)

**Aim.** When an agent does badly in a world with hidden state, did it misread the world, or read it right and fail to act? Only an oracle that sees exactly what the agent sees can tell.

**How they tested it.**

1. **World.** 26 weeks of importing one product. Six hidden factors drift on their own, among them demand, freight and supplier health, which runs from reliable through wobbling and degraded to defunct.
2. **Signals.** A weekly dashboard of noisy symptoms. A real canal closure and a false alarm look the same for a week.
3. **Shared randomness.** Each seed fixes an event tape, so every policy faces the same shocks and noise.
4. **Oracle and score.** An exact Bayes filter on the agent's own observations, plus planning over about 200 sampled futures. Its one advantage is knowing the true parameters. The score is 0 for a policy that ignores the dashboard and 1 for the oracle.
5. **Models.** Claude Sonnet 5, GPT-5.4, DeepSeek-V4-Pro and Grok 4.5, 50 seeds each. A grader checks the agent's weekly reasoning for whether it named the real problem.

**What they found.**

| Model | Skill | Seeds beating the floor | Acted when it knew (persistent stress) |
|---|---|---|---|
| GPT-5.4 | 0.62 | 42 of 50 | 0.37 |
| Claude Sonnet 5 | 0.49 | 40 of 50 | 0.43 |
| Grok 4.5 | -0.13 | 21 of 50 | 0.34 |
| DeepSeek-V4-Pro | -0.23 | 28 of 50 | 0.40 |

- Every model spotted 84 to 88% of real problems, usually within half a week. The two models below the floor spotted them fastest.
- Knowing didn't mean acting. Even after naming the problem, an agent ran out of stock in a third or more of those weeks.
- Failures ran both ways. Claude froze through a port jam, GPT-5.4 never locked in freight in 87% of freight spikes, and DeepSeek flailed. The two worst models overbought protection against problems that were real.

**What it means for us.** It is the closest study in method: their oracle is our reference bot, their 0 to 1 skill is the shape of performance, and their event tape is our shared luck. Its week-long false alarm is the nearest thing in the literature to noise with a run in it, and the shape of our yoked dip, yet calm-week overreactions "are excluded from every reported metric by construction", so false alarms go uncounted. Their split between knowing and acting is what our [doubt question](../design/future.md#how-the-agent-can-act) would measure, and their supplier story is close to our planned second game.

## Gupta et al. 2025: coin flips and Bayes

Ritwik Gupta et al. (UC Berkeley). "Enough Coin Flips Can Make LLMs Act Bayesian." ACL 2025. [arXiv:2503.04722](https://arxiv.org/abs/2503.04722)

**Aim.** When an LLM learns from examples in its prompt, does it update like a Bayesian?

**How they tested it.** Small open models only (Gemma-2-2B, Llama-3.1-8B, Phi-2, Phi-3.5-mini, Mistral-7B, OLMoE-1B-7B and the Pythia suite), since the method reads the probability a model puts on "heads" next. The model states a belief and never makes a choice. One run of 100 flips switches the bias from 75% to 25% halfway, and fits are compared against a Beta posterior and one that discounts older flips by a factor γ.

**What they found.**

- Every model starts biased towards heads. Flips in the prompt help, as few as 3, but even 100 don't fully recover the bias. Bigger Pythia models are no better.
- On the switching run, the discounted update fits well. γ ran from 0.31 to 0.91 across eight models, which by our sum means remembering about 1.4 to 11 flips.

**Problems.** The text calls γ "a slight discount factor", yet four of eight values are below 0.5. It says instruction tuning lowers γ, but Mistral-7B-Instruct (0.91) is above Mistral-7B (0.69).

**What it means for us.** Some models forget after a couple of flips, the opposite of leaning on the past. A fast forgetter would look quick to switch for the wrong reason, and would show up as a switch during the no-change run's dip.

## Zhang et al. 2025: LLMs in a drifting bandit

Ziyuan Zhang et al. "Comparing Exploration-Exploitation Strategies of LLMs and Humans: Insights from Standard Multi-armed Bandit Experiments." Preprint, May 2025, revised May 2026. [arXiv:2505.09901](https://arxiv.org/abs/2505.09901). Most of the main text read.

**Aim.** Do LLMs explore like people when the best option keeps moving, and does reasoning help?

**How they tested it.** The restless four-armed bandit from Daw et al. 2006, where each arm's mean follows a slow random walk (λ = 0.9836) under noisy payoffs, for 300 rounds. GPT-4o-mini, Gemini-1.5, DeepSeek-V3, DeepSeek-R1 and o3-mini against 31 people. Fitted models split exploration into directed (seeking the arm you know least) and random (noise in the choice).

**What they found.**

- People had the lowest regret and reasoning models came close. Exact values appear only in figures.
- Directed exploration was negative for every LLM: they avoided the arms they knew least about.
- Models without reasoning explored more at random than people.

**What it means for us.** It is the only LLM study we found where the world drifts slowly, so a good arm fades rather than fails, and its random walk is the closest any study here comes to our weather. The models were noisy and avoided the unknown, which in our game predicts no look at C0 and a split that wobbles without tracking the change.
