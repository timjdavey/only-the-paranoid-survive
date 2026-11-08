# Contributing

## Setup

See [running](docs/harness/running.md). `uv sync`, copy `.env.example` to `.env`, then run the smoke test with `mockllm`.

## Before you change anything

- **Read the layer rule** in [layout](docs/harness/layout.md). Code imports only from the layer below it. CI checks this.
- **Use glossary words** in code and prose, see [glossary](docs/glossary.md). Add a word there before using it anywhere else.
- **Commit before every major change.** If the working tree has uncommitted work, commit it first, then start the change.

## Be reader friendly

This matters most.

- Every file must be skimmable, clear and concise. Use bullets where you can.
- Name things so they explain themselves.
- Keep files under 300 lines. Use links over re-explaining.
- Talk to the reader, not to yourself. Assume they've never seen the study, and be friendly and clear.

## Adding things

| To add | Where | Then |
|---|---|---|
| A scenario | An events list in `paranoid.engine`, a row in [scenarios](docs/design/scenarios.md) | Tie it to a failure mode and test its reverse |
| A skin | A TOML file, see [skins](docs/harness/skins.md) | It must pass the lint. Held-out skins go in the private repo |
| A baseline | A pure policy in `paranoid.engine`, a provider in `paranoid.harness`, a row in [baselines](docs/design/baselines.md) | Check the [baseline order](docs/pilot/checks.md#baseline-order) still holds |
| A model | A row in `configs/models/` | Say its reasoning setting |
| A pilot check | A section in [checks](docs/pilot/checks.md) and a row in [decisions](docs/pilot/decisions.md) | |

## What never changes without a new pilot

- The prompt text in [prompts](docs/harness/prompts.md).
- Any number in [decisions](docs/pilot/decisions.md) once filled.
- The seed lists in `configs/seeds/`.
