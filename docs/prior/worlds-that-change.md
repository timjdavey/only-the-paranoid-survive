# Worlds that change

These studies change the world under the agent, apart from Schmied and Horowitz, whose static tasks show habits that predict how an agent copes with a change.

- **No record of earlier play.** None starts the agent from a record it must read and write its own notes on.
- **Noise without memory.** Only STOCKTAKE has noise with a run in it.
- **The old plan mostly fails outright.** The exceptions are STOCKTAKE, Zhang et al. 2025 and Allen and McDonald, where the core business still earns.

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

**What it means for us.** It is the closest benchmark in shape. Calibrated accuracy runs from a floor to an oracle, as our chart runs from the stale baseline to the perfect baseline. Swaps being noticed far more than reversals bears on the [later kinds of change](../design/future.md#how-the-world-changes), and forced probing doing nothing says experiments have to be the agent's own idea. Their oracle knows the true rule, like our perfect baseline, but nothing in it plays our Bayesian baseline's part of seeing only what the agent sees. Feedback is exact, and false alarms aren't counted.

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

**What it means for us.** It is the closest study in method: their oracle is our Bayesian baseline, their 0 to 1 skill is the shape of our proportion of the perfect baseline, and their event tape is our shared luck. Its week-long false alarm is the nearest thing in the literature to noise with a run in it, and the shape of our yoked dip, yet calm-week overreactions "are excluded from every reported metric by construction", so false alarms go uncounted. Their split between knowing and acting is what our [doubt question](../design/future.md#how-the-agent-can-act) would measure, and their supplier story is close to our planned second game.

## KellyBench (Grady et al. 2026): a season of football bets

Thomas Grady, Kip Parker, Iliyan Zarov, Henry Course, Chengxi Taylor and Ross Taylor (General Reasoning). "KellyBench: A Benchmark for Long-Horizon Sequential Decision Making." Preprint, April 2026. [arXiv:2604.27865](https://arxiv.org/abs/2604.27865). A longer leaderboard is on the [release page](https://www.gr.inc/releases/introducing-kellybench).

**Aim.** Can agents learn from experience in a world that shifts, by building models and betting through a real football season?

**How they tested it.**

- The 2023/24 Premier League, one matchday at a time, 120 matchdays, at real bookmaker odds with a margin of about 5.3%.
- Each matchday the agent builds models in a sandbox, bets on home, draw, away or over and under 2.5 goals, then gets the results. It must bet at least once a matchday.
- The reward is the change in log bankroll. Match data runs back to 1993/94, player data to 2008.
- Five models, five seeds each, 500 to 1,000 tool calls a run. Nothing is scripted to change: the shift is the real season, such as three newly promoted teams.
- Also scored against human baselines and a 52-point expert rubric for how sophisticated the strategy is.

**What they found.**

| Agent | Average return | Ruined in a seed | Rubric score |
|---|---|---|---|
| GPT-5.4 | −7.9% | No | 22.3% |
| Claude Opus 4.6 | −11.2% | No | 26.5% |
| GLM-5 | −51.6% | Yes | 17.3% |
| Gemini 3.1 Pro | −66.0% | Yes | 8.8% |
| Kimi K2.5 | −89.6% | Yes | 12.7% |
| Human quant | +5.1% | n/a | 73.1% |

- 3 of 25 seeds made money and 6 of 25 lost everything. Every model predicted worse than the market.
- Models rarely adapted. 7 of 25 seeds never retrained, and 22 of 25 had no general fix for promoted teams. Fully adaptive seeds averaged −11.1% against −70.0% for fully static ones.
- Knowing didn't mean acting. Opus 4.6 called an edge on Burnley implausible, then bet on it anyway. GLM-5 wrote three self-critiques blaming its fixed 25% draw rate and never changed it. 7 of 25 seeds wrote Kelly code and never used it.

**Problems.** The release page's leaderboard has twelve models, not the paper's five. The text says most seeds never retrained, but its table says 7 of 25. Its tests pool matchdays across seeds that share one schedule, which the authors say may overstate significance. The adaptive versus static comparison is observational, since the models that retrained were also the strongest.

**What it means for us.** A bankroll that compounds adds sizing and ruin, which the authors say made losses worse here, and is why our [budget is fixed](../design/decisions.md#why-a-budget-split). The change is the real season, so nobody can say when it began or what a good agent should have done. With no no-change copy, a model that bets less after losses can't be told from one that noticed something. Its knowing and not acting is what the [doubt question](../design/future.md#how-the-agent-can-act) would measure.

## Bazaar (Ahmed et al. 2026): pricing when customers' tastes swap

Shimaa Ahmed, Yiwei Cai, Mohsen Minaei and Rahul Rachuri (Visa Research). "Can LLM Agents Price Competitively? A Dynamic Multi-Attribute Auction Benchmark for Agentic Commerce." Preprint, July 2026. [arXiv:2608.00102](https://arxiv.org/abs/2608.00102). Bazaar is the benchmark the paper releases.

**Aim.** Can an LLM merchant learn what hidden customers value, price for margin, and adapt when their tastes change without notice?

**How they tested it.**

- One LLM merchant against three rule-based bots that adapt only their price. 24 customers with hidden values over three attributes, five levels each.
- Each round, each customer runs a sealed-bid auction. The agent sees only the winning offer, and its profit if it won. It writes a belief note per customer each round and one strategy note.
- Twelve customers swap the values of two attributes once, unannounced, at a round drawn from 31 to 40. The other twelve never change. About 79 rounds in all.
- 11 models from four providers at several effort levels, 10 seeds each, plus Thompson sampling and EXP4 baselines. Scored on profit and against an oracle that knows each customer's values.

**What they found.**

| Model | Win rate after the shock, against its peak before |
|---|---|
| Gemini 3.1 Pro | +3.3 points |
| Grok 4.1 Reasoning | +1.4 |
| Gemini 3 Flash | −3.1 |
| Claude Opus 4.6 | −11.9 |
| Claude Sonnet 4.6 | −13.4 |
| Claude Opus 4.5 | −19.2 |
| GPT-5.3 | −19.2 |

Shocked customers only, the last ten rounds against rounds 26 to 30.

- The best agent, Opus 4.6 at its highest effort, earned $2,976 and captured 0.321 of the oracle's profit.
- The fastest learners before the shock, GPT-5.3 (+46 points) and Opus 4.5 (+40), adapted worst after it.
- "Revision, not detection, is the bottleneck." Models noticed losses within a few rounds, then committed to one new guess. Opus 4.6 kept a price ledger headed "ABSOLUTELY IDENTICAL, DO NOT CHANGE". Sonnet 4.6 called its first loss "a significant anomaly after 29 consecutive wins", cut its price by $1, blamed rivals' costs and won none of the 35 rounds after the shock for that customer.
- Thompson sampling earned $1,426, more than six of eleven base models, but took 30 rounds to recover its 78% win rate.

**Problems.** Recovery speed is stated three ways: "10–15 rounds for the best LLMs" in the text and Figure 6 caption, "5–10 rounds" a paragraph later, while the table shows only two of seven models back at their peak. No result is reported for the twelve unshocked customers. The introduction credits Opus 4.6 at its highest effort with $2.22 per win, but its table row says $2.39.

**What it means for us.** The unshocked customers sit in the same run as the shocked ones, so they are not a matched [no-change copy](../design/decisions.md#why-the-yoked-dip), and false alarms on them go uncounted. The lock-in notes are the risk in our `write_notes`, and "revision, not detection" is why we [split doubting from switching](../design/decisions.md#why-split-doubting-from-switching). A swap makes the old offer lose outright, unlike our standing bets. Thompson sampling beating half the models on profit, yet recovering slowly, is why [our baselines](../design/decisions.md#why-the-baselines-set-the-difficulty) are tuned before they set anything.

## CoffeeBench (Sugiura et al. 2026): a coffee supply chain with a demand surge

Issa Sugiura, Daichi Hattori, Kazuo Araragi, Keita Ogawa, Shota Onose, Taro Makino, Teppei Usuki and Takashi Ishida (Sakana AI, KPMG AZSA). "CoffeeBench: Benchmarking Long-Horizon LLM Agents in Heterogeneous Multi-Agent Economies." Preprint, June 2026. [arXiv:2606.16613](https://arxiv.org/abs/2606.16613). Code at [SakanaAI/CoffeeBench](https://github.com/SakanaAI/CoffeeBench).

**Aim.** How well do LLM agents run a firm over a long horizon among other firms?

**How they tested it.**

- Two farmers, two roasters and two retailers trade for 90 simulated days. The model under test plays one roaster, and Claude Sonnet 4.6 plays the other five firms.
- Trade runs through listings and offers, on 30 days' credit, with delivery lags, spoilage, daily costs and bankruptcy if cash goes negative.
- The score is cumulative net income. Seven models, three runs each, reasoning off or minimal, plus a roaster that does nothing and one with fixed rules.
- Consumer demand triples on days 40 to 53, a "spring_break" festival. The paper calls it "predictable", and the released code puts its dates in every agent's system prompt but not its size.

**What they found.**

| Roaster | Net income ($) | Idle days of 90 |
|---|---|---|
| GPT-5.5 | +3,109 ± 1,123 | 0 |
| Claude Opus 4.7 | +2,782 ± 2,263 | 0 |
| Claude Sonnet 4.6 | +2,236 ± 1,489 | 0 |
| Gemini 3.1 Pro | +1,695 ± 508 | 0 |
| GLM-5.1 | +1,597 ± 1,199 | 0 |
| Kimi K2.6 | +454 ± 1,420 | 4 |
| Claude Haiku 4.5 | −630 ± 1,745 | 40 |
| Fixed rules | −1,931 ± 429 | 0 |
| Does nothing | −2,765 | 90 |

- Haiku 4.5 stopped acting from day 26, 66 and 25 in its three runs and never restarted, while writing that the business "is now operating at peak efficiency". The authors call it idle drift.
- Higher earners messaged other firms more. None of the five models analysed sent the rival roaster more than one message a run on average.
- The best result reached about 13% of a loose ceiling of $23,800. There is no oracle.

**Problems.** The abstract says the other firms are "fixed reference agents", but they are LLM agents. Three runs, with error bars often as wide as the means. The surge is never analysed.

**What it means for us.** The surge is announced and passes, so it tests planning for a known event, not telling a passing shock from a lasting one. It gives no evidence on when switching is the mistake. Idle drift is coherent reasoning with no action. In our game that would show as holding the standing bets, which is close to the stale baseline, so it is scored rather than hidden. A supply chain is a candidate [second game](../design/future.md#whether-it-holds-outside-our-game), but this one has no no-change copy or oracle.

## Allen and McDonald 2026: a strategy class simulation

Ryan T. Allen and Rory M. McDonald. "How Well Can AI Do Strategy? Empirical Benchmarking Using Strategy Simulations." Strategy Science 11(1): 93 to 117, 2026. [doi:10.1287/stsc.2025.0444](https://doi.org/10.1287/stsc.2025.0444). Open access. Code at [ryantallen/bbb_benchmark_public](https://github.com/ryantallen/bbb_benchmark_public).

**Aim.** Can LLMs make strategic decisions in a teaching simulation they meet for the first time, and how do they compare with MBA students?

**How they tested it.**

- Back Bay Battery (Christensen and Shih 2019), a business school teaching game. Over eight simulated years the player sets prices, sales forecasts and R&D for a core technology, about 80% of revenue, and an emerging one, about 20%.
- The game is scripted and deterministic. Around year 4 the core business declines under foreign price pressure. The emerging one takes off only after years of focused R&D.
- In the standard mode the player is fired for badly missed forecasts or three years of losses.
- Names were masked and the briefing reworded. Asked to explain the original game, four of six models could. Asked about the masked one, none could.
- 21 proprietary and 13 open models. The score is an equal mix of cumulative profit, cumulative revenue and final-year revenue from the emerging technology, each scaled across the dataset.
- Humans: first runs by 249 second-year MBA students from five years between 2018 and 2025.

**What they found.** Model scores appear only in figures.

- Early-2025 models scored best: o3-mini, then o4-mini, Claude Sonnet 4 and Gemini 2.0 Flash, all above the MBA average.
- GPT-5, o3 and Gemini 2.5 Pro scored below them and below the MBA average. They earned high profit but little revenue from the emerging technology, partly because they were fired earlier. GPT-5 wrote "Pause all QSC R&D due to long lead times".
- The same held in a mode with no firing, except that GPT-5.2 ranked first there.
- Telling models to aim at the emerging technology helped GPT-5, o3 and Gemini 2.5 Pro only "marginally", and made o3-mini much worse.
- Up to o4-mini, BBB scores rose with GPQA scores. For the latest models the trend reversed.

**Problems.** The MBA comparison is lines on a chart with no test, and the authors call it "contextual reference points rather than a direct apples-to-apples comparison": the students were primed by their course and worked unsupervised. The abstract lists Claude Opus 4.5 and Gemini 3 among the models that declined, but the text only discusses GPT-5, o3 and Gemini 2.5 Pro. The text doesn't say how many runs each model got.

**What it means for us.** Playing for the core business still earned high profit after the downturn, the shape of standing bets that keep paying. Newer models doing worse, and breaking from GPQA, is why we [keep older models and a general ability check](../design/decisions.md#why-older-models-and-a-general-ability-check). The masking test backs our [private skins](../design/decisions.md#why-four-skins-over-one-interface). As a [human baseline](../design/future.md#whether-it-holds-outside-our-game) it is too loose to borrow, and with one deterministic world and no no-change copy it can't separate noticing from guessing.

## Goel et al. 2026: a teammate who switches tasks

Harsh Goel, Aditya Sai Ellendula, Vaishnav Tadiparthi, Ehsan Moradi Pari, Hossein Nourkhiz Mahjoub and Sandeep P. Chinchali (UT Austin, Honda Research Institute). "Bayesian Partner Modelling enables Adaptive Replanning for LLM Coordination." Preprint, August 2026. [arXiv:2608.18490](https://arxiv.org/abs/2608.18490)

**Aim.** When a teammate switches what it is doing, does an LLM agent that knows it stop its own task in time, and does a Bayesian tracker help?

**How they tested it.**

- An Overcooked-style kitchen, three layouts, 2,400 steps. The teammates are 12 RL policies that each prefer some subtasks and switch between them in the course of play, not on a script.
- The agent is an LLM planner (GPT-4o or GPT-5.2) choosing multi-step skills. The baseline, ProAgent, replans only when its skill ends, fails or times out.
- Their agent tracks a posterior over the teammate's current skill. It interrupts its own skill only when a teammate's move is unlikely under a stable, confident estimate.
- **Belief-action gap**: the share of decisions where the agent's estimate of the teammate is right, yet it starts or keeps a stale or duplicate skill.
- 5 seeds and 4 teammates per setting.

**What they found.**

| Layout | Accuracy, theirs | Accuracy, ProAgent | Gap, theirs | Gap, ProAgent |
|---|---|---|---|---|
| Open | 0.79 | 0.78 | 0.20 | 0.41 |
| Ring | 0.71 | 0.71 | 0.28 | 0.38 |
| Forced coordination | 0.61 | 0.60 | 0.42 | 0.47 |

- Both agents knew the teammate equally well, yet the baseline acted on a stale plan twice as often in the open layout.
- Using the posterior to interrupt beat putting it in the prompt in most settings.
- Generic triggers matched the reward only by replanning far more: 43, 169 and 119 times an episode against 2.0 in one setting.
- RL agents beat every LLM agent in most settings.

**Problems.** ProAgent's gap is partly built in, since by design it "does not interrupt an active skill solely because the teammate's behavior changes". The paper says its agent beats ProAgent and Hypothetical Minds "in every layout", but in one setting it scores 337 against their 388 and 369. The abstract says "an order of magnitude fewer replans" and the introduction "two orders".

**What it means for us.** It is the cleanest measure of knowing and not acting: a correct belief and a stale action, the gap the [doubt question](../design/future.md#how-the-agent-can-act) would show. Their fix is a trigger outside the model, which our agent never gets, so it predicts an LLM left alone keeps going. Their teammate's switch is always real, so a quick trigger costs only a replan. Our no-change run puts a price on it.
