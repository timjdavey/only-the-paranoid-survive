# inspect_ai

How the design maps onto [inspect_ai](https://inspect.aisi.org.uk). One run of the game is one inspect sample.

## The mapping

| Design | inspect | Note |
|---|---|---|
| A [run](../glossary.md) on one seed, scenario and skin | `Sample`, with `scenario`, `seed`, `skin`, `engine_hash` and `prompt_hash` in `metadata` | The same seeds for every model falls out for free |
| Playing a seed again, see [repeats](../pilot/checks.md#repeats) | `epochs` | Built in |
| A [fresh call each round](../design/interface.md#tools) | A custom `@solver` round loop | Not `react` or `basic_agent`. They keep the conversation |
| `submit(bets)` | A `@tool` that raises `ToolError` when the sum is off | The error is the neutral retry. A text reply with no call is a miss |
| Game state, the tape, output so far, the record | A `StoreModel` on the sample | Written to the log, so a run can be replayed from any round |
| Fraction of the oracle | A custom `@scorer` that runs the oracle on the same tape | One number per sample, 0 to 1 |
| Mean per scenario | `grouped(mean(), "scenario")` | See [scoring](../design/scoring.md) |
| Error bars and the headline | Custom `@metric`s | Bootstrap seeds within a scenario, never across |
| Baselines, Jev, Timestral | Custom `ModelAPI` providers | Same solver, same seeds, same logs as an LLM |
| `notes` and `compute`, pilot only | `StoreModel` for notes, an inspect sandbox for compute | The sandbox is an optional extra |
| The prompt lint | A pytest over the rendered prompt and tool text | |
| Logs | `.eval` files in `logs/`, browsed with `inspect view` | They hold the full prompt, see [contamination](contamination.md) |

## The round loop

Each round the solver:

1. Renders the system prompt from the skin and the record from the store, see [prompts](prompts.md).
2. Calls `generate` with the `submit` tool. Forced where the provider allows it. Current Claude models reject a forced tool, so there the choice is `auto` and the prompt says to call `submit`.
3. Reads the tool call. A bad sum returns a `ToolError` and the model tries again. A reply with no tool call is a miss too. Three misses and the round holds last round's bets and the store flags it.
4. Plays the bets through the engine and appends the readings and output to the record.
5. Repeats until the tape ends. Nothing from this round's messages survives into the next.

## Providers

- **Registered** under the `inspect_ai` entry point in `pyproject.toml`, so `--model baseline/stale` resolves.
- **Each implements `generate`** and returns a `submit` tool call, never text. The solver cannot tell a provider from an LLM.
- **Baselines** read the store, which holds the tape and the record, and call the engine's policy functions. Oracle and steady read the tape. Stale reads round 1. Uniform reads nothing.
- **Jev and Timestral** read the record and call out, see [adapters](adapters.md).

## Metrics

- **Scenario score** is `grouped(mean(), "scenario")`.
- **Error bars** are a custom metric: percentile bootstrap over seeds within a scenario.
- **Headline** is a custom metric: geometric mean of the scenario means, bootstrapped by resampling seeds within each scenario.
- **Gaps between models** are paired by seed in the [analysis](layout.md) layer, as they need two logs.
