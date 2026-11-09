# Contributing

## Setup

See [running](docs/harness/running.md). `uv sync`, copy `.env.example` to `.env`, then run the smoke test with `mockllm`.

## Before you change anything

- **Read the layer rule** in [layout](docs/harness/layout.md). Code imports only from the layer below it. CI checks this.
- **Read the layer's spec** in [specs](docs/specs/README.md). Code is written from its spec and tested against it. If the code has to differ, change the spec in the same PR.
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
| A skin | A TOML file, see [skins](docs/harness/skins.md) and [writing a skin](docs/harness/writing-a-skin.md) | It must pass the lint. Held-out skins go in the private repo |
| A baseline | A pure policy in `paranoid.baselines` and a key in its `POLICIES`, see the [baselines spec](docs/specs/baselines/README.md), a row in [baselines](docs/design/baselines.md). The harness then plays it as `baseline/<name>` with no change | Check the [baseline order](docs/pilot/engine-checks.md#baseline-order) still holds |
| Seeds | Public seeds in `configs/seeds/public.txt`, held-out seeds in the private repo's `held-out.txt`. One list for every scenario, see [contamination](docs/harness/contamination.md#two-seed-sets) | Never publish a held-out seed, its tape or a log that played it |
| A model | A row in `configs/models/` | Say its reasoning setting |
| A pilot check | A section in [engine checks](docs/pilot/engine-checks.md) if it needs no model, else in [provider checks](docs/pilot/provider-checks.md), and a row in [decisions](docs/pilot/decisions.md) | |

## What never changes without a new pilot

- The frame and prompt structure in [prompts](docs/harness/prompts.md).
- A skin's text, once a headline run has played it.
- Any number in [decisions](docs/pilot/decisions.md) once filled.
- The public seed lists in `configs/seeds/`.
- The held-out seed lists. They change only with a new release, see [contamination](docs/harness/contamination.md#who-can-see-them).
