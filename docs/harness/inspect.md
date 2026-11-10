# inspect_ai

How the design maps onto [inspect_ai](https://inspect.aisi.org.uk). One run of the game is one inspect sample, and one eval plays a model through every scenario.

## The mapping

| Design | inspect | Note |
|---|---|---|
| A [run](../glossary.md) on one seed, scenario and skin | `Sample`, with `scenario`, `seed`, `seed_set`, `skin`, `engine_hash` and `prompt_hash` in `metadata` | The same seeds for every model fall out for free |
| A seed set, see [seeds](../design/scoring.md#seeds) | The dataset: one sample per scenario per seed in the set | The task args in [running](running.md#commands) pick the scenarios, seeds and skin |
| Playing a seed again, see [repeats](../pilot/provider-checks.md#repeats) | `epochs`, reduced by the mean | Repeats of a seed are averaged before any metric sees them, as the [error bars](../design/scoring.md#error-bars) require |
| A [fresh call each round](../design/interface.md#tools) | A custom `@solver` round loop | Not `react` or `basic_agent`. They keep the conversation |
| `submit(bets)` | A `@tool` that raises `ToolError` with the skin's `bad_call` when the engine rejects the bets | The error is the neutral retry. A text reply with no call gets a retry too |
| Game state: the scenario, the seed, the record, the retry counts | A `StoreModel` on the sample, see the [task spec](../specs/harness/task.md#store) | Written to the log, so a run can be replayed from any round. The timeline is rebuilt from the seed, never stored, see [timeline](../specs/engine/timeline.md#interface) |
| A run's output beside its baselines | A custom `@scorer` that records the run's output and the Uniform and Discerning baselines' on the same timeline | The run score is the gain over the gap, see [pooling seeds](../design/scoring.md#pooling-seeds) |
| A run that gives up, see the [retry rule](prompts.md#retry-rule) | The solver returns with `gave_up` in the store and the scorer gives a gain of 0 | Never an error, so an error in a log is infrastructure. `retry_on_error=1` and `fail_on_error=0.1` on the `@task` handle those, set in the task so nobody can forget them |
| Scenario score, error bars, headline, weakest trait | Custom `@metric`s grouped by the `scenario` field, see [metrics](#metrics) | Bootstrap seeds within a scenario, never across |
| Baselines, Jev, Timestral | Custom `ModelAPI` providers | Same solver, same seeds, same logs as an LLM |
| `notes` and `compute`, see [tools](../design/interface.md#tools) | `StoreModel` for notes, an inspect sandbox for compute | The sandbox needs Docker, see [running](running.md#setup) |
| The prompt lint | A pytest over the rendered prompt and tool text | |
| Logs | `.eval` files in `logs/`, browsed with `inspect view` | They hold the full prompt, see [contamination](contamination.md) |

## The round loop

Each round the solver:

1. Renders the system prompt from the skin and the record from the store, see [prompts](prompts.md).
2. Calls `generate` with the `submit`, `notes` and `compute` tools, and a tool choice of `any` where the provider allows it, so the reply must call a tool. Claude takes `any` with thinking off and rejects it with thinking on, so there the choice is `auto` and the prompt says to call `submit`. The solver decides from the model it is given, so nothing on the command line can get it wrong. See [reasoning](models.md#reasoning).
3. Reads the tool call. Bets the engine rejects return a `ToolError` with the skin's `bad_call`, and the model tries again. A reply with no tool call gets a reminder and tries again too. The store counts each retry. After ten tries the solver gives up and the run scores as the Uniform baseline. See the [retry rule](prompts.md#retry-rule).
4. Plays the bets through the engine and appends the readings and output to the record.
5. Repeats until the timeline ends. Nothing from this round's messages survives into the next. The exceptions are the notes file, which comes back next round in the user message below the record, see [tools](../design/interface.md#tools), and the pilot's [rolling conversation](../pilot/provider-checks.md#rolling-conversation) cell, which keeps every message.

## Providers

- **Registered** under the `inspect_ai` entry point in `pyproject.toml`, so `--model baseline/complacent` resolves.
- **Each implements `generate`** and returns a `submit` tool call, never text. The solver cannot tell a provider from an LLM.
- **A provider ignores the messages it is sent** and reads the store instead. The record an LLM sees and the timeline a baseline sees are both on the sample. This leans on inspect's per-sample `store()` being in scope inside `generate`, which is to be confirmed when the harness is built.
- **Baselines** call the [baselines layer](../specs/baselines/README.md)'s policies. The Perfect and Discerning baselines read the timeline. The Complacent baseline reads round 1. The Uniform baseline reads nothing.
- **Jev and Timestral** read the record and call out, see [providers](providers.md).

## Metrics

One eval plays every scenario, so one log holds all a headline needs. Each metric is a custom `@metric` that groups samples by the `scenario` field in metadata.

- **Scenario score** is the model's gain over the Uniform baseline summed over seeds, divided by the Discerning baseline's gain summed over seeds. Not a mean of per-sample ratios, see [scoring](../design/scoring.md#how-we-score). A run that gave up counts as a gain of 0.
- **Error bars** are a percentile bootstrap over seeds within a scenario.
- **Headline** is the plain mean of the scenario scores, bootstrapped by resampling seeds within each scenario. Scenarios are never resampled.
- **Weakest trait** is the lowest scenario score and the name of its trait.
- **Retry share** is the share of rounds that needed a retry, read from the store and reported beside every score.
- **Gaps between models** are paired by seed in the analysis layer, as they need two logs, see [paired gap](../specs/analysis/scores.md#paired-gap).
