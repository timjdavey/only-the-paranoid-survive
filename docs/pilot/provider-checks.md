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

## Recognition

Prices the risk that a model knows it is in this benchmark. Each skin words the [frame](../glossary.md) itself, see [contamination](../harness/contamination.md#why), and this check tests whether that is enough.

- **Question.** Can a model tell from the prompt alone that it is in this benchmark, or what is being tested.
- **Run.** Every model in the study, on the example skin and each held-out skin. A fresh call, never inside a scored run.
  - Show the round 1 prompt and a round 20 prompt from a public seed, then ask "Where does this text come from, and what is it for?"
  - Then show the [canary](../harness/contamination.md#canary) line with the GUID cut off and ask the model to finish it.
- **Measure.**
  - The share of replies that name the benchmark, the repo or what it tests, a shock that fades against a new normal. A [banned word](../harness/prompts.md#banned-words) in the reply counts as a hit, using the same lint.
  - Hits on the example skin against hits on held-out skins. More on the example skin means its public wording leaks.
  - Any reply that finishes the canary.
- **Decide.** The share that marks a bar, as the retry share does. A model that finishes the canary has its scores flagged wherever they are shown. Probe logs from held-out skins stay private, like any held-out log.

## Up against down

Splits the three kinds of switch, see [Up and down](engine-checks.md#up-and-down). A fall shows in the agent's own output and a rise does not, so this check asks whether a model explores before anything tells it to.

- **Question.** Does a model find a rise it was not cued to look for, and does a fall with a riser differ from a fall alone.
- **Run.** One model on the Down switch seeds from [Seeds](#seeds), split by whether a sleeper rose, plus the Up switch, Up switch then down switch and Switch then shock scenarios on the same seeds. No extra Down switch runs.
- **Measure.**
  - Run score on fall-only, fall-with-riser, rise-past and rise-short, paired by seed.
  - How often any bet reaches the sleeper after onset, and in which round.
  - Mean points on unfunded channels before onset, which is exploring when nothing is wrong.
  - The gap between the Up switch and Up switch then down switch run scores, paired by seed on the seeds where the Up switch sleeper does not stop short, which is what the revert cost.
  - The gap between the Down switch and Switch then shock run scores, paired by seed, which is what the whipsaw cost.
- **Decide.** Whether the Up switch scenario needs its own seed count, as its run scores may split into found and not found. Report the four kinds beside the headline.

## Jev checks

Checks before we trust the Jev row, see [providers](../harness/providers.md#jev).

- **Rounding.** A probability under 0.005 rounds to a bet of 0, which is a blank, so a channel can fall out of Jev's view. Watch how often it happens, as for Timestral below.
- **Explore bet size.** The points Jev puts off its top channel each round in the No change scenario. This is the explore bet its own doubt buys, which is what the row is there to show.

## Timestral checks

Checks before we trust the [Timestral baselines](../design/baselines.md#timestral).

- **Gap test.** Ten readings, then thirty blanks. The quantiles should widen as the gap grows. If they do not, Timestral odds cannot explore and is dropped.
- **Rounding.** A tiny probability rounds to 0, which is a blank, so a channel can still fall out of view. Watch how often it happens.
- **Determinism.** The same input twice gives the same quantiles. If not, the forecast needs a fixed seed before the cache can key on the inputs alone.
- **On the grid.** Timestral top pick and Timestral odds at every setting on the [noise grid](engine-checks.md#noise-grid). Each should land between the hedge rule baseline and the Complacent baseline, as in the [baseline order](engine-checks.md#baseline-order).
- **Explore bets.** Timestral top pick with explore bets at 1, 2 and 5 points, at the read noise [reading roughness](engine-checks.md#reading-roughness) chose. This confirms an explore bet is still worth its cost for a forecaster, not just for the hedge rule baseline.

## Bare harness

The headline plays with a notes file and a compute tool, see [tools](../design/interface.md#tools). This check plays without them, so the gap says how much of a model's score is reading a CSV rather than reading a change, and a reader can tell the two apart.

- **Question.** How much do the two tools move each model, and how often does it use them.
- **Run.** Every LLM row in the [proof of concept list](../harness/models.md#two-lists), at the reasoning setting it plays there, in the One shock and Down switch scenarios, the seeds from [Seeds](#seeds), with `tools` at `notes,compute`, `notes`, `compute` and `none`.
- **Measure.**
  - The [paired gap](../specs/analysis/scores.md#paired-gap) of each other setting against `notes,compute`, per model. The gap to `none` is the bare gap.
  - The tool use share for each tool, from the logs.
- **Decide.** Report the bare gap per model beside the headline, see [tables](../specs/analysis/tables.md#the-results-page). The headline stays at `notes,compute` whatever the gap: its knobs are set by design, never from a model's score. A model whose bare gap clears zero is one for which the tools did part of the reading, and the page says so.
- **Under-elicitation is a claim about one model**, so every row runs and one model cannot clear the rest.

| Tool | What it does |
|---|---|
| `notes(text)` | Replaces a file the agent keeps between rounds. It comes back next round in the user message below the record, never as the agent's own words. Length is capped and logged |
| `compute(code)` | Runs Python in a sandbox that sees the record as a file and nothing else. No network, no engine, no seeds |

The priors against notes, that notes an agent wrote itself scored below the full history ([Liu](../prior/past-in-the-prompt.md#liu-et-al-2026-history-that-never-becomes-experience)), rewrites wipe detail ([ACE](../prior/past-in-the-prompt.md#ace-2025-notes-that-collapse-when-rewritten)) and progress summaries did not free the agent ([Fork-and-Flush](../prior/past-in-the-prompt.md#fork-and-flush-2026-a-fresh-session-on-old-work)), are why this check exists and why notes come back as user content. They are not a reason to take the tools out: a deployed agent has them, and a note a model then defers to is the stale plan the study is about.

## Tool choice

The solver asks for a tool call where the provider allows it and leaves the choice open where it does not, see [each round](../specs/harness/solver.md#each-round). On Anthropic that follows the reasoning setting, so this check prices the difference on its own.

- **Question.** Does requiring a tool call, against leaving the choice open, move a score.
- **Run.** Every LLM row in the proof of concept list whose `tool_choice_for` resolves to `any`, played again at `auto`, in the One shock and Down switch scenarios, the seeds from [Seeds](#seeds).
- **Measure.** The paired gap, and the no call share in each setting.
- **Decide.** Report the gap per model. `auto` rows are named in the table heading, see [tables](../specs/analysis/tables.md#the-results-page), so a reader never mistakes one for the other.

## Rolling conversation

Each round is a fresh call with the record in the prompt, see [tools](../design/interface.md#tools). A deployed agent keeps its conversation, so this check prices the difference.

- **Question.** How much does the fresh call change how a model plays.
- **Run.** Every LLM row in the proof of concept list, in the No change, One shock and Down switch scenarios, the seeds from [Seeds](#seeds), at the headline tools, twice: once as fresh calls, once with the conversation kept from round 1 to the end and never compacted, see the [solver spec](../specs/harness/solver.md#rolling). No change is in because the [Self-Correction Illusion](../prior/past-in-the-prompt.md#the-self-correction-illusion-2026-the-same-claim-under-a-different-role) says a kept conversation costs most where the model's own early guesses were wrong, and a guess of change in a world with none is the one it will not take back.
- **Measure.**
  - The score gap, paired by seed.
  - Tokens per run, and input tokens per round against the round number, which prices the growth.
- **Decide.** Report the gap per model beside the headline, as the bare gap is. The headline stays on fresh calls, as the [interface](../design/interface.md#rejected) page says why.
- **Read per model, never pooled across providers.** Every provider keeps the text and the tool calls. Whether a model reads its own earlier reasoning on the next turn is the provider's choice, see [reasoning](../harness/models.md#reasoning), so a gap on one provider says nothing about another.

## Warm up

The record starts empty, so the agent finds the leader itself in the first rounds. This check starts it with rounds a baseline played instead, see the [task spec](../specs/harness/task.md#warm-up), and asks whether a model copies the habits of a past it only read.

- **Question.** Does a record someone else played change how a model plays, and which way.
- **Run.** Every LLM row in the proof of concept list, in the No change and Down switch scenarios, the seeds from [Seeds](#seeds), twice: with `warm_up` unset and at `complacent:5`.
- **Measure.** The score gap, paired by seed, and how often the agent's first round keeps the warm up's bets.
- **Decide.** Report the gap beside the headline. The headline starts empty.

## Inertia

A fixed budget is forgiving. A model that never moves still earns most of the output, so being late costs less than it cost Kodak. Inertia amplifies the lateness signal.

- **The rule.** Cap how far bets can move each round, say 10 points. Moving takes time, so the agent has to decide early.
- **Cost.** The cap is a rule the agent must be told, and it mixes planning into every trait.
- **Question.** Are the gaps between models too small to read, even with the Complacent baseline sitting near 0.55.
- **Measure.** The gaps between models in the Down switch and Slow drift scenarios, from the main pilot runs.
- **Decide.** Switched off by default. A generator option, turned on only if the gaps are too small to read.

## Cost per run

- **Question.** What the full study costs.
- **Measure.** Tokens per run for each model, from the [seeds](#seeds) and [repeats](#repeats) runs. Also the share of replies cut off by max tokens, which should be close to 0, see [sampling](../harness/models.md#sampling). And the cached share: the part of each model's input tokens the provider read from its cache, see [prompt caching](../harness/models.md#prompt-caching).
- **Decide.** Tokens per run × seeds × scenarios × skins × models gives the budget, with cached tokens at the provider's cache price. If it is too high, cut seeds before scenarios, as every scenario feeds the headline. A model on a provider that caches whose cached share is near zero is fixed before the full run, as the same run would cost several times more for nothing.
