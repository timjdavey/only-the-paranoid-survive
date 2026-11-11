Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per release.
- The loading range and the base ladder ranges.
- How often an explore bet reads below 0, from [reading roughness](docs/pilot/engine-checks.md#reading-roughness). A bet is paid its reading, so that is a real loss, and it can move the ladder up.
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
- Add `src/paranoid/skins/example.toml`, the example skin's real words, which are coming. KS2, KR2, KL11 and KL13 wait on it, see the [skins spec](docs/specs/skins/skin.md#the-example-skin).
- Run the [channel order check](docs/pilot/provider-checks.md#channel-order) before any other provider check, as its answer can change the `submit` tool they all play.
- Bring every held-out skin up to the [skin spec](docs/specs/skins/skin.md). Eight keys are wanted: `bets_name`, the names and text of the notes and compute tools, and the three column words, see [skins](docs/harness/skins.md#what-a-skin-file-holds). A skin with an output word drops it, and any wording with two tallies goes, as a bet is paid its reading, see [mechanics](docs/design/mechanics.md#what-the-agent-sees). Each must also call its split percentages, which the lint now checks, see [what every skin must say](docs/harness/prompts.md#what-every-skin-must-say).
- Decide whether the example skin is a money story with channels, then fix [prompts](docs/harness/prompts.md#system-prompt) to match.
  - Its fixed words are budget, spend, fund and channel. A story that spends money on channels can use them as written, and a story that sends people or goods cannot.
  - `prompts.md` brackets the noun once, in "ten [channels]", and writes it out three times: in the two reading sentences and in "in channel order".
  - The draft is a fruit importer that sells through ten wholesale markets on commission. It writes its own noun in all four places and swaps "fund" for a verb of its own. It keeps "budget", "points" and "spend", and "spend" sits oddly on a story that sends goods.
  - So decide whether `prompts.md` brackets the verb as well as the noun, and whether "spend" may move.
  - Its points become percentages, see [interface](docs/design/interface.md#how-the-agent-plays). Its clause for the round hundred can then go.
  - Its `how_points_earn` says a market's figure is what the lots fetched, and promises no average. Its column words become three, see [the figure](docs/harness/writing-a-skin.md#the-figure).
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
