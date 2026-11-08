Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Memory, own-weather spread and shared-factor spread, per scenario.
- The loading range and the base ladder ranges.
- Warm up: one cell starts round 1 with an empty record, one with a record pre-filled by a baseline.

## Code
- Scaffold `src/paranoid/` as in [layout](docs/harness/layout.md), engine first.
- `configs/seeds/` once the engine exists.
- The canary GUID once the example skin exists, see [contamination](docs/harness/contamination.md#canary).
- Verify the model ids in `configs/models/poc.toml` before the first run.
