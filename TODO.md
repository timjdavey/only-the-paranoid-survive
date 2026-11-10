Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per release.
- The loading range and the base ladder ranges.
- The Bayesian baseline's `hazard` and `rule`, from the [Bayesian frontier](docs/pilot/engine-checks.md#bayesian-frontier).

## Code
- Write the engine from its [spec](docs/specs/engine/README.md), tests first, then the baselines from [theirs](docs/specs/baselines/README.md).
- Write the analysis from its [spec](docs/specs/analysis/README.md), last, once the harness writes logs.
- Scaffold `src/paranoid/` as in [layout](docs/harness/layout.md), engine first, baselines second.
- `configs/seeds/` once the engine exists, and the held-out seed lists in the private repo, see [contamination](docs/harness/contamination.md#two-seed-sets).
- Ask each provider in `configs/models/` for zero data retention before the proof of concept, as it plays held-out skins, see [contamination](docs/harness/contamination.md#who-can-see-them).
- Pass the same two held-out skins to `paranoid run --skins` on every proof of concept run, see [running](docs/harness/running.md#commands).
- Before the proof of concept, run `paranoid run --limit 2` on both skins and read `paranoid analyse cost`, so the budget rests on measured tokens and a cached share, see [cost per run](docs/pilot/provider-checks.md#cost-per-run).
- If Claude runs through a subscription, check its data terms, rate limit and cache reads first, see [keys](docs/harness/models.md#keys).
- Run the three checks on cutting the record into content blocks before the pilot, as the prompt structure freezes after it, see the [solver spec](docs/specs/harness/solver.md#verify-before-code).
- Put the canary GUID in `paranoid.skins.canary`, see [contamination](docs/harness/contamination.md#canary).
- Ship `compose.yaml` and the sandbox extra before the first headline run, as the headline needs Docker, see [running](docs/harness/running.md#setup).
- Decide the two skins spec Open items that were due before the first held-out skin, as held-out skins now exist: the [record column words](docs/specs/skins/render.md#open) and [banning numbers](docs/specs/skins/lint.md#open).
- Verify the model ids in `configs/models/poc.toml` before the first run.
- Verify every id and every setting marked "to verify" in `configs/models/full.toml` before the first run.
- Run the full study's retiring rows first, or swap them before they go: `claude-haiku-4-5-20251001` (any time now), `gpt-4o-2024-11-20` (2027-01-14), `gpt-5.1` (2027-04-01).
- `google/gemini-2.5-flash` in `configs/models/poc.toml` gets rerouted to `gemini-3.5-flash-lite` on 2026-12-01. Swap it before then.
