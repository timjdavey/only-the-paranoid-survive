Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per scenario.
- The loading range and the base ladder ranges.
- Warm up: one cell starts round 1 with an empty record, one with a record pre-filled by a baseline.

## Code
- Scaffold `src/paranoid/` as in [layout](docs/harness/layout.md), engine first.
- `configs/seeds/` once the engine exists, and the held-out seed lists in the private repo, see [contamination](docs/harness/contamination.md#two-seed-sets).
- Ask each provider in `configs/models/` for zero data retention before a held-out run.
- The canary GUID once the example skin exists, see [contamination](docs/harness/contamination.md#canary).
- Verify the model ids in `configs/models/poc.toml` before the first run.
- Verify every id and every setting marked "to verify" in `configs/models/full.toml` before the first run.
- Run the full study's retiring rows first, or swap them before they go: `claude-haiku-4-5-20251001` (any time now), `gpt-4o-2024-11-20` (2027-01-14), `gpt-5.1` (2027-04-01).
- `google/gemini-2.5-flash` in `configs/models/poc.toml` gets rerouted to `gemini-3.5-flash-lite` on 2026-12-01. Swap it before then.
