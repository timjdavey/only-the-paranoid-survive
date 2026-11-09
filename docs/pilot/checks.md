# Pilot

A short run before the full study to settle the knobs.

## Seeds

Sizes the [error bar](../design/scoring.md#error-bars).

- **Question.** How many seeds a scenario needs.
- **Run.** One model, one scenario, say shock. Twenty public seeds played once, as pilot logs are published. See [contamination](../harness/contamination.md#two-seed-sets).
- **Measure.** The SD of the run score across seeds. This is the [spread](../design/scoring.md#spread).
- **Decide.** Seeds per scenario = (SD ÷ target error bar)², rounded up. The target is a fraction, say a fifth, of the smallest gap between [baselines](../design/baselines.md) we want to read. This sizes the held-out seed set.

## Repeats

Splits [spread](../design/scoring.md#spread) into the world's dice and the model's.

- **Question.** How much of the spread is the model's own sampling, so we know whether a per-seed dot means "this world was hard" or "the model rolled badly".
- **Run.** Five of the twenty seeds from [Seeds](#seeds), each played three more times. Pick them across the range of single-run scores, not the first five, because sampling matters most on ambiguous worlds. 15 extra runs.
- **Measure.** SD within a seed across repeats (sampling spread), against SD across seeds (spread). Within variance over total variance is the sampling share.
- **Decide.** Report the share next to the spread. The headline still plays each seed once, as more seeds beats repeats for the error bar. If the share is large, note that pairing by seed buys less and the dots read as spread, not difficulty.

## Noise

Noise is the difficulty knob. It has three dials, own-weather spread, memory and shared-factor spread, see [difficulty](../design/mechanics.md#difficulty). With low noise one reading settles whether a dip is a shock or a switch. With high noise it takes many rounds.

- **Question.** What settings of the three dials make shock and switch hard to tell apart for a while, but not forever.
- **Run.** The fixed [baselines](../design/baselines.md) on shock and switch, at a few settings of each dial.
- **Measure.** How the baseline scores spread at each setting, and whether the [baseline order](#baseline-order) holds.
- **Decide.** The three dials per scenario. If the base score is flat across models, raise them. Raising them later is also how the study avoids saturating.

## Game length and switch round

- **Question.** How many rounds a run lasts, and in which round the shock or switch hits.
- **Run.** The fixed baselines on shock and switch, at a few game lengths and switch rounds.
- **Measure.** How far steady pulls ahead of stale after the switch, and how many rounds that takes.
- **Decide.** Enough calm rounds before the change to set a habit, and enough rounds after it for steady to pull clear of stale. Longer runs cost more, see [cost per run](#cost-per-run).

## Reading roughness

A small bet gives a rough reading and a large bet a clean one, see [what the agent sees](../design/mechanics.md#what-the-agent-sees). That rewards a look, and is how it works in the real world.

- **Question.** How fast the read noise shrinks as the bet grows.
- **Run.** The constant look [Timestral baselines](../design/baselines.md#timestral) at 2, 5 and 10 points, at a few strengths of read noise.
- **Measure.** Whether a bigger look buys a better read of the switch, and how much a look costs in output.
- **Decide.** One strength, where a look is worth its cost but no look tells the whole story.

## Baseline order

- **Question.** Do the fixed baselines land in the order we expect.
- **Run.** Every [baseline](../design/baselines.md) on switch and calm.
- **Measure.** Their scores, against these orders:
  - **Switch:** oracle > steady > Timestral > stale > uniform.
  - **Calm:** stale ≈ oracle ≈ steady.
- **Decide.** If the order breaks, the [noise](#noise) is likely too high or a baseline is wrong. Fix it before any model runs.

## Timestral checks

Checks before we trust the [Timestral baselines](../design/baselines.md#timestral).

- **Gap test.** Ten readings, then thirty blanks. The quantiles should widen as the gap grows. If they do not, probability of best cannot look and is dropped.
- **Rounding.** A tiny probability rounds to 0, which is a blank, so a channel can still fall out of view. Watch how often it happens.

## Notepad and compute

A deployed agent would have a scratchpad and a calculator at the very least, so a bare harness may not be a fair test. The headline plays without them, see [interface](../design/interface.md#tools).

- **Question.** Does a scratchpad or a calculator change how a model plays.
- **Run.** The same models and seeds with and without each tool.
- **Measure.** The score gap, and how often each tool is used.
- **Decide.** Whether the headline needs either tool.

| Tool | What it does |
|---|---|
| `notes(text)` | Replaces a file the agent keeps between rounds. It comes back next round as a tool message, never as the agent's own words. Length is capped and logged |
| `compute(code)` | Runs Python in a sandbox that sees the record as a file and nothing else. No network, no engine, no seeds |

| Rejected | Why not |
|---|---|
| Notes in the headline | Notes an agent wrote itself scored below the full history ([Liu](../prior/past-in-the-prompt.md#liu-et-al-2026-history-that-never-becomes-experience)), rewrites wipe detail ([ACE](../prior/past-in-the-prompt.md#ace-2025-notes-that-collapse-when-rewritten)) and progress summaries did not free the agent ([Fork-and-Flush](../prior/past-in-the-prompt.md#fork-and-flush-2026-a-fresh-session-on-old-work)) |
| A `read_notes` tool | The notes are in the prompt |
| Pasting data into `compute` | Retyping hundreds of rows measures tedium, not judgement. The sandbox gets the record as a file instead |

## Inertia

A fixed budget is forgiving. A model that never moves still earns most of the output, so being late costs less than it cost Kodak. Inertia amplifies the lateness signal.

- **The rule.** Cap how far bets can move each round, say 10 points. Moving takes time, so the agent has to decide early.
- **Cost.** The cap is a rule the agent must be told, and it mixes planning into every trait.
- **Question.** Is the base score too flat to separate models.
- **Measure.** The gaps between models on switch and drift, from the main pilot runs.
- **Decide.** Switched off by default. A generator option, turned on only if the gaps are too small to read.

## Cost per run

- **Question.** What the full study costs.
- **Measure.** Tokens per run for each model, from the [seeds](#seeds) and [repeats](#repeats) runs.
- **Decide.** Tokens per run × seeds × scenarios × models gives the budget. If it is too high, cut seeds before scenarios, as every scenario feeds the headline.
