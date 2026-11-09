# Provider checks

The second half of the pilot, a short run before the full study to settle the knobs.

- **These need a model behind a provider**, so they cost tokens. That covers LLMs, Timestral and Jev.
- **Run them once the [engine checks](engine-checks.md) pass.** The noise grid, read noise and baseline order they settle are fixed by then.

## Seeds

Sizes the [error bar](../design/scoring.md#error-bars).

- **Question.** How many seeds a scenario needs.
- **Run.** One model, one scenario, say the One shock scenario. Twenty public seeds played once, as pilot logs are published. See [contamination](../harness/contamination.md#two-seed-sets).
- **Measure.** The SD of the run score across seeds. This is the [spread](../design/scoring.md#spread).
- **Decide.** Seeds per scenario = (SD ÷ target error bar)², rounded up. The target is a fraction, say a fifth, of the smallest gap between [baselines](../design/baselines.md) we want to read. This sizes the held-out seed set.

## Repeats

Splits [spread](../design/scoring.md#spread) into the world's dice and the model's.

- **Question.** How much of the spread is the model's own sampling, so we know whether a per-seed dot means "this world was hard" or "the model rolled badly".
- **Run.** Five of the twenty seeds from [Seeds](#seeds), each played three more times. Pick them across the range of single-run scores, not the first five, because sampling matters most on ambiguous worlds. 15 extra runs.
- **Measure.** SD within a seed across repeats (sampling spread), against SD across seeds (spread). Within variance over total variance is the sampling share.
- **Decide.** Report the share next to the spread. The headline still plays each seed once, as more seeds beats repeats for the error bar. If the share is large, note that pairing by seed buys less and the dots read as spread, not difficulty.

## Up against down

Splits the three kinds of switch, see [Up and down](engine-checks.md#up-and-down). A fall shows in the agent's own output and a rise does not, so this check asks whether a model looks before anything tells it to.

- **Question.** Does a model find a rise it was not cued to look for, and does a fall with a riser differ from a fall alone.
- **Run.** One model on the Down switch seeds from [Seeds](#seeds), split by whether a sleeper rose, plus the Up switch scenario on the same seeds. No extra Down switch runs.
- **Measure.**
  - Run score on fall-only, fall-with-riser and rise-only, paired by seed.
  - How often any bet reaches the sleeper after onset, and in which round.
  - Mean points on unfunded channels before onset, which is looking when nothing is wrong.
- **Decide.** Whether the Up switch scenario needs its own seed count, as its run scores may split into found and not found. Report the three kinds beside the headline.

## Timestral checks

Checks before we trust the [Timestral baselines](../design/baselines.md#timestral).

- **Gap test.** Ten readings, then thirty blanks. The quantiles should widen as the gap grows. If they do not, Timestral odds cannot look and is dropped.
- **Rounding.** A tiny probability rounds to 0, which is a blank, so a channel can still fall out of view. Watch how often it happens.
- **On the grid.** Timestral top pick and Timestral odds at every setting on the [noise grid](engine-checks.md#noise-grid). Each should land between the hedge rule baseline and the Complacent baseline, as in the [baseline order](engine-checks.md#baseline-order).
- **Looks.** Timestral top pick with looks at 1, 2 and 5 points, at the read noise [reading roughness](engine-checks.md#reading-roughness) chose. This confirms a look is still worth its cost for a forecaster, not just for the hedge rule baseline.

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

## Rolling conversation

Each round is a fresh call with the record in the prompt, see [tools](../design/interface.md#tools). A deployed agent keeps its conversation, so this check prices the difference.

- **Question.** How much does the fresh call change how a model plays.
- **Run.** One model in the One shock and Down switch scenarios, the seeds from [Seeds](#seeds), twice: once as fresh calls, once with the conversation kept from round 1 to the end and never compacted.
- **Measure.** The score gap, paired by seed, and tokens per run.
- **Decide.** Report the gap beside the headline. The headline stays on fresh calls, as the [interface](../design/interface.md#rejected) page says why. If the gap is large, say so where the score is read.

## Inertia

A fixed budget is forgiving. A model that never moves still earns most of the output, so being late costs less than it cost Kodak. Inertia amplifies the lateness signal.

- **The rule.** Cap how far bets can move each round, say 10 points. Moving takes time, so the agent has to decide early.
- **Cost.** The cap is a rule the agent must be told, and it mixes planning into every trait.
- **Question.** Are the gaps between models too small to read, even with the Complacent baseline sitting near 0.55.
- **Measure.** The gaps between models in the Down switch and Slow drift scenarios, from the main pilot runs.
- **Decide.** Switched off by default. A generator option, turned on only if the gaps are too small to read.

## Cost per run

- **Question.** What the full study costs.
- **Measure.** Tokens per run for each model, from the [seeds](#seeds) and [repeats](#repeats) runs. Also the share of replies cut off by max tokens, which should be close to 0, see [sampling](../harness/models.md#sampling).
- **Decide.** Tokens per run × seeds × scenarios × models gives the budget. If it is too high, cut seeds before scenarios, as every scenario feeds the headline.
