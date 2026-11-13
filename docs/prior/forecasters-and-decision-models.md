# Forecasters and decision models

Our game plays three kinds of model on the same seeds: LLMs, decision models like Jev, and forecasters like Timestral. This page collects the studies that put two of those kinds side by side, and asks whether anyone has played all three. How our game plays each kind is on the [interface](../design/interface.md#models-that-cannot-place-bets) and [providers](../harness/providers.md) pages.

- **Decision models have been scored against LLMs, but only on one-shot questions.** Jev comes close to a small LLM, and it is about ten times faster and a quarter of the cost. In every study the answer is in the input.
- **Forecasters have been scored against LLMs, but only on one-shot plans.** A fixed forecaster policy sits in the same table as the LLMs, as our Timestral baselines do. No study we found uses Timestral.
- **We found no study that plays all three, or that plays any of them through a change.** As far as we can tell, ours is the first, see [is ours the first?](#is-ours-the-first)

## Artificial Analysis Decision Index v1.0 (2026): decision models against small LLMs

Artificial Analysis. "Artificial Analysis Decision Index v1.0." Launch article, 13 October 2026. [artificialanalysis.ai](https://artificialanalysis.ai/articles/artificial-analysis-decision-index).

**In short.** This is the first independent index to put decision models and LLMs on one scale. Jev 1.13 trails Claude Haiku 5.5 by 3 points, and it is far faster and cheaper.

**What they did.**

- **Models.** Decision models: Jev 1.13, GLiDE, Microsoft-Decision-1, d1, Decider v1.1 27B and Celeris-1 Decision. LLMs: Claude Haiku 5.5 (Low) and GPT-6 Luna (Low).
- **Tasks.** Four static evaluations: AA-Omniscience-Decision, HLE-MultiChoice, When2Call and WildGuardTest. Each decision model answers in "a single call with a probability for each option".
- **Score.** One index, plus speed and cost per task.

**What they found.**

| Model | Index | Time per task | Cost per 1M tasks |
|---|---|---|---|
| Claude Haiku 5.5 (Low) | 61 | 1.4 s | $184 |
| Jev 1.13 | 58 | 0.13 s | $42 |
| GLiDE, Microsoft-Decision-1 | 54 | | |

- On classification and tool calling, the leading decision models are about level with the LLMs.

**Watch out for.** Every task is one call with no history. Nothing in the input changes over time, and no forecaster takes part.

**Why it matters here.** It sets what we expect from Jev before it plays: close to a small LLM on a question whose answer is in the input. Our [Jev provider](../harness/providers.md#jev) asks the same kind of question every round, but the right answer moves with the world.

## JevBench (2026): a typed decision board

Benchmark Heaven's JevBench board, run by Florian Standhartinger independently of TypeSafe. Explained by Parallel, which builds a rival decisions API, in "JevBench explained: how decision models are benchmarked, and what it can't measure", citing data from 29 October to 6 November 2026. [parallel.ai](https://parallel.ai/articles/jevbench-benchmark). The board is at [benchmarkheaven.com](https://benchmarkheaven.com/jev-models).

**In short.** This is the main public board for decision models. It scores typed one-shot decisions on intelligence, calibration, speed and cost, and it says itself that it cannot test a world that changes.

**What they did.**

- **Format.** "State and rubric in, typed answer out." Every answer is in the input. 1,500 decisions: 300 public and 1,200 sealed.
- **Models.** Jev 1.13.0 and 1.14.0, Super Decider, d1-ultra, Torchcast and mammoth-1. Also OpenAI Decisions (gpt-6-luna), and GPT-6 Luna at medium reasoning as a plain LLM.

**What they found.**

- On board v1.8.7 (3 November 2026), Jev 1.13.0 has a Capability of 77.1 and a Composite of 71.4, 15th overall. Super Decider leads the hosted APIs at a Composite of 78.5.
- Jev 1.14 trails 1.13 on Capability, 75.0 against 77.1.
- In one post, Jev 1.13.0 leads the Composite even though GPT-5.6 Luna is much more accurate on hard cases. The author warns that this does not make Jev more capable overall.

**Watch out for.**

- The name JevBench covers several boards. Secondary sites republish older versions with other counts, so check the version and date of any number.
- Parallel sells a rival product.
- The board cannot test facts that "live outside the input and change over time".

**Why it matters here.** That stated limit is exactly what our game tests. Calibration matters to us too, because Jev's probabilities become its bets, see [providers](../harness/providers.md#jev).

## Forecast Workflow Bench (Nagashima 2026): LLMs that buy forecasts

Shunya Nagashima (Neurogica). "Forecast Workflow Bench: Evaluating Language-Model Decisions with Budgeted Forecast Tools." Preprint, 23 September 2026. [arXiv:2609.27385](https://arxiv.org/abs/2609.27385).

**In short.** LLMs choose which time-series forecasts to buy under a credit budget, then commit to a plan. Fixed forecaster policies are scored in the same table. The best LLM beats them, but the margin did not hold up on a repeat run.

**What they did.**

- **Task.** One capacity plan per case, 24 hours in eight 3-hour blocks, for electricity demand (EIA-930) or cycle hire (TfL), made one or seven days ahead. One round, not many.
- **Forecasters as tools.** Chronos-Bolt Tiny, Chronos-2 and TimesFM 2.5, each with a credit cost, and a limit of 12 tool calls.
- **LLMs.** GPT-5.4 nano and GPT-6 Astra, plus local Gemma 4 E4B, Gemma 4 12B, Qwen3 4B and Qwen3.6 35B-A3B, with thinking on and off.
- **Policies without an LLM.** Fixed Chronos-2, fixed Chronos-Bolt Tiny, backtest and hour-of-day selectors, and a catalog oracle.
- **Score.** S = ½[(loss − F)/σ + credits/B], where F is the hindsight optimum and B the budget. Lower is better.

**What they found.**

| Player | S | Note |
|---|---|---|
| Catalog oracle | 0.239 | Knows which forecast is best |
| GPT-6 Astra | 0.396 | Used about 2.5% of the budget |
| Hour-of-day empirical, free | 0.515 | Every local LLM did worse |
| Fixed Chronos-2 | 0.865 | Accurate, but bought at nearly the full budget |

- Qwen3.6 35B-A3B with thinking off hit the 12-call limit in 1,245 cases.

**Watch out for.**

- A repeat of Astra on 100 cases did not show it beats the best fixed policy.
- The abstract says Astra used 2.5% of the budget, and §4.2 says 2.6%.
- The paper does not say whether demand shifts within a case.
- There is no decision model and no Timestral. Decision models are named only as future work.

**Why it matters here.**

- **The closest design to ours on forecasters.** Fixed forecaster policies sit in the same table as LLMs, as our [Timestral baselines](../design/baselines.md#timestral) do.
- **The difference.** Our forecaster turns its own forecast into bets every round, and the world changes under it.
- **A cheap fixed rule beat most LLMs.** We expect the same of our simplest baselines, see the [baseline order](../pilot/engine-checks.md#baseline-order).

## Yang et al. 2026: where Jev's judgement stops

Yaodong Yang, Hongyao Tang, Yi Ma, Xingyu Fan, Weixun Wang, Jinpeng Li and Tianpei Yang. "Code Owns the Simulation, Jev Owns the Evaluation." Preprint, 1 October 2026. [arXiv:2610.01834](https://arxiv.org/abs/2610.01834). The appendices were not read.

**In short.** Jev is good when the right choice can be judged from what it is shown. When the answer needs simulating ahead, it falls back on surface cues. Hand the simulation to code and it does well again.

**What they did.**

- **One-shot tasks.** 150 cognitive reflection questions, and 3x3 matrix games with fixed payoffs.
- **Sequential tasks.** ALFWorld text games of up to 50 steps, and Stacker robot control.
- **Score.** Accuracy against the right option, or a set of acceptable options, compared with chance. Wrong answers that go to the surface "lure" are counted on their own.
- **No LLM was run.** The LLM numbers on the reflection questions are quoted from Hagendorff et al. (2023) "for reference only".

**What they found.**

| Task | Jev alone | Jev with code doing the simulation |
|---|---|---|
| Reflection questions with a lure | 99% | |
| Misleading matrix games | 28 to 37%, chance | 97 to 99% when told the opponent's move |
| ALFWorld, 134 unseen games | 42 solved, 31% | 116 solved, 87% |
| Stacker | 0 of 20 on raw torques | 9 of 20, against 8 for a hand-written controller |

**Watch out for.** There is no head-to-head LLM run and no forecaster. The tasks change only when the agent acts, never on their own.

**Why it matters here.**

- **It predicts where Jev will land.** In a shock, the record shows the answer: the hedge rises while the field falls, see [the tell](../pilot/engine-checks.md#the-tell). In a slow drift, the answer needs a trend projected ahead. So we would expect Jev to do better on the One shock scenario than on the Slow drift scenario.
- **It suggests a split.** Our `compute` tool is the code half of their split. Jev cannot call it, see [models that cannot place bets](../design/interface.md#models-that-cannot-place-bets).

## Timestral (Mistral 2026): a forecaster with no decision study yet

Mistral AI. "Timestral: Mistral's time-series foundation models." Launch post, 15 October 2026. [mistral.ai](https://mistral.ai/news/timestral/). Code at [mistralai/timestral](https://github.com/mistralai/timestral).

**In short.** Timestral comes in four sizes, from 5M to 209M parameters. It gives probabilistic forecasts across many variables at once, and is trained mostly on synthetic data.

**What they found.**

- The 209M model ranks first zero-shot on GIFT-Eval, TIME and fev-bench, on Mistral's own count.
- The 28M model beats Chronos-2, about four times its size, on GIFT-Eval and TIME.

**Watch out for.**

- The technical report is still pending, and these numbers have not been checked independently.
- Every benchmark scores forecast error. None scores a decision made from the forecast.

**Why it matters here.** We use the 209M model, see [providers](../harness/providers.md#timestral). Strong forecast scores don't tell us how it plays, because a forecast is only half a bet. The [forecast rule](../specs/baselines/forecast.md) makes the other half.

## Is ours the first?

As far as we can find, yes. We searched on 13 November 2026 and found no study that plays a decision model, a forecaster and LLMs on the same task. Each study covers two of the three at most, and none has a world that changes on its own.

| Study | Decision model | Forecaster | LLMs | Same task | World changes on its own |
|---|---|---|---|---|---|
| [Artificial Analysis](#artificial-analysis-decision-index-v10-2026-decision-models-against-small-llms) | Jev and five others | None | Haiku 5.5, GPT-6 Luna | Yes, one-shot | No |
| [JevBench](#jevbench-2026-a-typed-decision-board) | Jev and others | None | GPT-6 Luna | Yes, one-shot | No, a stated limit |
| [Forecast Workflow Bench](#forecast-workflow-bench-nagashima-2026-llms-that-buy-forecasts) | None | Chronos, TimesFM | GPT-6 Astra and others | Yes, one round | Not stated |
| [Yang et al.](#yang-et-al-2026-where-jevs-judgement-stops) | Jev | None | Quoted, not run | No | No |
| [Timestral](#timestral-mistral-2026-a-forecaster-with-no-decision-study-yet) | None | Timestral | None | Forecast error only | n/a |
| [happyc0der/ledger #6](https://github.com/happyc0der/ledger/issues/6), October 2026 | Jev, as a judgement layer | Timestral | None | No, both are parts of one sales tool | n/a |
| **Our game** | Jev and Decision Models | Timestral, as baselines | Many | Yes, the same seeds, scored the same way | Yes, a shock, switch or drift |

- **The claim is "first we found", not "first".** It rests on one search. Timestral was released a month before that search. Several of the decision model sources are blogs or vendors, and they disagree on some numbers.
- **What the game adds.** Every model, whatever its kind, plays the same seeds and is scored the same way, see [interface](../design/interface.md#models-that-cannot-place-bets). The world moves under all three, and false alarms cost, see the [prior work README](README.md#how-our-game-differs).
- **Search again before publishing.** Two things to check first: the Timestral technical report, and any decision model board that adds tasks with history.
