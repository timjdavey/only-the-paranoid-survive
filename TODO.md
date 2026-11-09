Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per release.
- The loading range and the base ladder ranges.
- Warm up: one cell starts round 1 with an empty record, one with a record pre-filled by a baseline.

## Code
- Write the engine from its [spec](docs/specs/engine/README.md), tests first, then the baselines from [theirs](docs/specs/baselines/README.md).
- Write the analysis from its [spec](docs/specs/analysis/README.md), last, once the harness writes logs.
- Scaffold `src/paranoid/` as in [layout](docs/harness/layout.md), engine first, baselines second.
- `configs/grid.toml`, the noise grid the `luck`, `tape-sanity` and `noise-grid` cells read, see the [pilot spec](docs/specs/harness/pilot.md#engine-cells).
- `configs/seeds/` once the engine exists, and the held-out seed lists in the private repo, see [contamination](docs/harness/contamination.md#two-seed-sets).
- Ask each provider in `configs/models/` for zero data retention before a held-out run.
- Put the canary GUID in `paranoid.skins.canary`, see [contamination](docs/harness/contamination.md#canary).
- Decide the two skins spec Open items that were due before the first held-out skin, as held-out skins now exist: the [record column words](docs/specs/skins/render.md#open) and [banning numbers](docs/specs/skins/lint.md#open).
- Verify the model ids in `configs/models/poc.toml` before the first run.
- Verify every id and every setting marked "to verify" in `configs/models/full.toml` before the first run.
- Run the full study's retiring rows first, or swap them before they go: `claude-haiku-4-5-20251001` (any time now), `gpt-4o-2024-11-20` (2027-01-14), `gpt-5.1` (2027-04-01).
- `google/gemini-2.5-flash` in `configs/models/poc.toml` gets rerouted to `gemini-3.5-flash-lite` on 2026-12-01. Swap it before then.
