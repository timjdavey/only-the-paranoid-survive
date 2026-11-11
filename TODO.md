Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per release.
- The loading range and the base ladder ranges.
- Whether any reading falls below 0 on the default ladder, from [timeline sanity](docs/pilot/engine-checks.md#timeline-sanity). A bet is paid its reading, so that would be a real loss, and it moves the ladder up.
- The Bayesian baseline's `hazard` and `rule`, from the [Bayesian frontier](docs/pilot/engine-checks.md#bayesian-frontier).

## Code
- Write the baselines from their [spec](docs/specs/baselines/README.md), tests first.
- Write the analysis from its [spec](docs/specs/analysis/README.md), last, once the harness writes logs.
- Add the console script, entry points, extras and package data to `pyproject.toml` with the harness, see [layout](docs/harness/layout.md#what-pyprojecttoml-holds). The scaffold holds only what the engine needs.
- `configs/grid.toml`, the noise grid the `luck`, `timeline-sanity` and `noise-grid` cells read, see the [pilot spec](docs/specs/harness/pilot.md#engine-cells).
- `configs/seeds/` once the engine exists, and the held-out seed lists in the private repo, see [contamination](docs/harness/contamination.md#two-seed-sets).
- Ask each provider in `configs/models/` for zero data retention before the proof of concept, as it plays held-out skins, see [contamination](docs/harness/contamination.md#who-can-see-them).
- Pass the same two held-out skins to `paranoid run --skins` on every proof of concept run, see [running](docs/harness/running.md#commands).
- Before the proof of concept, run `paranoid run --limit 2` on both skins and read `paranoid analyse cost`, so the budget rests on measured tokens and a cached share, see [cost per run](docs/pilot/provider-checks.md#cost-per-run).
- If Claude runs through a subscription, check its data terms, rate limit and cache reads first, see [keys](docs/harness/models.md#keys).
- Run the three checks on cutting the record into content blocks before the pilot, as the prompt structure freezes after it, see the [solver spec](docs/specs/harness/solver.md#verify-before-code).
- Put the canary GUID in `paranoid.skins.canary`, see [contamination](docs/harness/contamination.md#canary).
- Ship `compose.yaml` and the sandbox extra before the first headline run, as the headline needs Docker, see [running](docs/harness/running.md#setup).
- Rerun the word run comparison in the private repo against the example skin, now its real words are in `src/paranoid/skins/example.toml`. No held-out skin may share a run of three words with it, or use `week`, `sent`, `price`, `split` or `send_fruit`, see [reviewing a skin](docs/harness/writing-a-skin.md#reviewing-a-skin-before-you-commit).
- Run the [channel order check](docs/pilot/provider-checks.md#channel-order) before any other provider check, as its answer can change the `submit` tool they all play.
- Bring every held-out skin up to the [skin spec](docs/specs/skins/skin.md). Eight keys are wanted: `bets_name`, the names and text of the notes and compute tools, and the three column words, see [skins](docs/harness/skins.md#what-a-skin-file-holds). A skin with an output word drops it, and any wording with two tallies goes, as a bet is paid its reading, see [mechanics](docs/design/mechanics.md#what-the-agent-sees). Each must also call its split percentages, which the lint now checks, see [what every skin must say](docs/harness/prompts.md#what-every-skin-must-say).
- Decide [banning numbers](docs/specs/skins/lint.md#not-decided) in the skins spec, due now that held-out skins exist.
- Every skin calls its split percentages, which is the first answer to the round hundred. If [recognition](docs/pilot/provider-checks.md#recognition) replies still doubt a skin for it, decide whether a skin may state another number that the tool turns into 100 points, see [writing a skin](docs/harness/writing-a-skin.md#give-every-fixed-fact-a-reason). Not built.
  - Whole points only convert cleanly from a number that divides 100, which makes the smallest bet larger, or from a multiple of 100 placed in fixed lots.
  - It would change the lint's [budget fact](docs/specs/skins/lint.md#frame-facts), the skin spec and the `submit` tool.
- Decide whether the skin names the notes and compute parameters before the first headline run on held-out skins, see the [solver spec](docs/specs/harness/solver.md#not-decided).
- Check the off value for reasoning on every provider in `configs/models/` before the first run, see the [command spec](docs/specs/harness/command.md#verify-before-code).
- Verify the model ids in `configs/models/poc.toml` before the first run.
- Verify every id and every setting marked "to verify" in `configs/models/full.toml` before the first run.
- Run the full study's retiring rows first, or swap them before they go: `claude-haiku-4-5-20251001` (any time now), `gpt-4o-2024-11-20` (2027-01-14), `gpt-5.1` (2027-04-01).
- `google/gemini-2.5-flash` in `configs/models/poc.toml` gets rerouted to `gemini-3.5-flash-lite` on 2026-12-01. Swap it before then.
