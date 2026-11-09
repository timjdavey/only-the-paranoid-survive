# inspect_ai

How the design maps onto [inspect_ai](https://inspect.aisi.org.uk). One run of the game is one inspect sample.

## The mapping

| Design | inspect | Note |
|---|---|---|
| A [run](../glossary.md) on one seed, scenario and skin | `Sample`, with `scenario`, `seed`, `seed_set`, `skin`, `engine_hash` and `prompt_hash` in `metadata` | The same seeds for every model falls out for free |
| Playing a seed again, see [repeats](../pilot/provider-checks.md#repeats) | `epochs` | Built in |
| A [fresh call each round](../design/interface.md#tools) | A custom `@solver` round loop | Not `react` or `basic_agent`. They keep the conversation |
| `submit(bets)` | A `@tool` that raises `ToolError` when the sum is off | The error is the neutral retry. A text reply with no call gets a retry too |
| Game state, the tape, output so far, the record | A `StoreModel` on the sample | Written to the log, so a run can be replayed from any round |
| A run's output beside its baselines | A custom `@scorer` that records the run's output and the Uniform and Discerning baselines' on the same tape | Three numbers per sample. The run score is their ratio |
| Scenario score | A custom `@metric` per scenario: summed gain over summed gap | Not a mean of per-sample ratios, see [scoring](../design/scoring.md#how-we-score) |
| Error bars and the headline | Custom `@metric`s | Bootstrap seeds within a scenario, never across |
| Baselines, Jev, Timestral | Custom `ModelAPI` providers | Same solver, same seeds, same logs as an LLM |
| `notes` and `compute`, pilot only | `StoreModel` for notes, an inspect sandbox for compute | The sandbox is an optional extra |
| The prompt lint | A pytest over the rendered prompt and tool text | |
| Logs | `.eval` files in `logs/`, browsed with `inspect view` | They hold the full prompt, see [contamination](contamination.md) |

## The round loop

Each round the solver:

1. Renders the system prompt from the skin and the record from the store, see [prompts](prompts.md).
2. Calls `generate` with the `submit` tool. Forced where the provider allows it. Current Claude models reject a forced tool, so there the choice is `auto` and the prompt says to call the tool.
3. Reads the tool call. A bad sum returns a `ToolError` and the model tries again. A reply with no tool call gets a reminder and tries again too. The store counts each retry. After ten tries the solver raises an error, and `--retry-on-error 1` plays the seed again once. See the [retry rule](prompts.md#retry-rule).
4. Plays the bets through the engine and appends the readings and output to the record.
5. Repeats until the tape ends. Nothing from this round's messages survives into the next.

## Providers

- **Registered** under the `inspect_ai` entry point in `pyproject.toml`, so `--model baseline/complacent` resolves.
- **Each implements `generate`** and returns a `submit` tool call, never text. The solver cannot tell a provider from an LLM.
- **Baselines** read the store, which holds the tape and the record, and call the engine's policy functions. The Perfect and Discerning baselines read the tape. The Complacent baseline reads round 1. The Uniform baseline reads nothing.
- **Jev and Timestral** read the record and call out, see [adapters](adapters.md).

## Metrics

- **Scenario score** is a custom metric per scenario: the model's gain over the Uniform baseline summed over seeds, divided by the Discerning baseline's gain summed over seeds. Not a mean of per-sample ratios.
- **Error bars** are a custom metric: percentile bootstrap over seeds within a scenario.
- **Headline** is a custom metric: the plain mean of the scenario scores, bootstrapped by resampling seeds within each scenario.
- **Weakest trait** is a custom metric: the lowest scenario score and the name of its trait.
- **Gaps between models** are paired by seed in the [analysis](layout.md) layer, as they need two logs.
