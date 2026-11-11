Keep a running list of TODOs in here.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Persistence, own-weather scale and shared-factor scale, per release.
- The loading range and the base ladder ranges.
- Whether any reading falls below 0 on the default ladder, from [timeline sanity](docs/pilot/engine-checks.md#timeline-sanity). A bet is paid its reading, so that would be a real loss, and it moves the ladder up.
- The Bayesian baseline's `hazard` and `rule`, from the [Bayesian frontier](docs/pilot/engine-checks.md#bayesian-frontier).

First numbers from the baselines layer at its defaults, on seeds 0 to 49, for the checks that set them:
- **[The tell](docs/pilot/engine-checks.md#the-tell).** The hedge rule false alarms a lot. Weather alone made it scout on 14 of 50 No change seeds. On One shock it never scouted on only 16 of 50, though it ended on the leader on 43. The fall test fired in 87 hold rounds there and the tell stopped 52. Look at `fall_points`, `window` and `tell_points`.
- **[Up and down](docs/pilot/engine-checks.md#up-and-down).** The hedge rule ended off the leader on 6 of 50 Up switch seeds, 5 of them on the sleeper. The Scout rule went to the sleeper and back on 41 of 50 Up switch then down switch seeds.
- **[Bayesian frontier](docs/pilot/engine-checks.md#bayesian-frontier).** At the defaults it beat the Complacent baseline on 46 of 50 Down switch seeds and ended on the leader on 49 of 50 One shock seeds. A near zero hazard top pick played No change as the Complacent baseline on 47 of 50.
- **[Reachable gain](docs/pilot/engine-checks.md#reachable-gain).** On 200 seeds per scenario at the defaults, three of six scenarios fail. Against the Stayer in Up switch then down switch, against the Complacent baseline elsewhere:

  | Scenario | Reachable gain | Bayesian gain | Bayesian gain percentage | Passes |
  |---|---|---|---|---|
  | Down switch | 0.38 | 0.29 | 76% | Yes |
  | Up switch | 0.14 | 0.08 | 62% | No |
  | Shock then switch | 0.20 | 0.10 | 53% | No |
  | Slow drift | 0.12 | 0.05 | 40% | No |
  | Switch then shock | 0.39 | 0.29 | 74% | Yes |
  | Up switch then down switch | 0.36 | 0.29 | 80% | Yes |

  Never moving scored 0.84 on the headline and the Bayesian baseline 0.93. The explore cost was 0.05 for the Bayesian baseline, 0.05 for the hedge rule and 0.11 for the Scout rule. The Bayesian baseline moved off the leader on 191 of 200 Up switch then down switch seeds, so that line holds. A rough sweep: an onset of 8 to 12 with switch sizes of 2 to 4 sigmas clears every scenario but Up switch, which needed a rise of 3 to 5 sigmas.
- **Bayesian run time.** About 90 ms a run, 240 ms with `lookahead`, so the frontier's 240,000 runs take 6 to 16 hours on one core. A cache on the record's rows should about halve it. Add it with the frontier's pilot cell.

First numbers from the forecasters layer, on the real Timestral at its [pins](docs/specs/forecasters/timestral.md#pinned), for the [Timestral checks](docs/pilot/provider-checks.md#timestral-checks):
- **Gap test.** Ten readings then blanks, on seed 0 of One shock. After thirty blanks the spread is wider on every channel: 2.1 to 3.0 times with the channels joint, 2.0 to 6.9 times with each alone. It does not widen round by round. Joint, the mean spread falls from 44 to 40 points over the first ten blanks, then grows to 107. Alone it grows from 43 to 198. Decide whether that is widening enough for Timestral odds.
- **Determinism.** The same input twice is equal, on one thread or four, so the cache keys on the inputs alone.
- **Rounding.** `rounded_out` was true on every round of every Timestral odds run, 468 of 468, so as defined it measures nothing. Odds kept a bet on 3.6 of the ten channels a round, with 79 points on its top one. Count the channels rounded out instead, or drop the measure.
- **On the grid.** Seeds 0 to 3 only, at the defaults, so a smoke test and not a measure. Mean score over One shock, Down switch and Up switch: top pick 0.85, explore 1 0.84, odds 0.80, bet aware 0.79, explore 2 0.76, explore 5 0.48, beside the hedge rule's 0.88 and the Complacent baseline's 0.84. Top pick never moved on Up switch. Explore 1, 2 and 5 ended where the Discerning baseline did on 12 of 12.
- **Run time.** About 115 ms a forecast on CPU, so 5 seconds a run and half an hour a grid setting for the `timestral` cell. The thread count makes no difference.

## Code
- Decide whether every Timestral row forecasts each channel alone, as Timestral odds, bet aware must, see [not decided](docs/specs/forecasters/policy.md#not-decided).
- Write the analysis from its [spec](docs/specs/analysis/README.md), last, once the harness writes logs.
- Add the console script, entry points, the sandbox extra and package data to `pyproject.toml` with the harness. The `timestral` extra is in, see [layout](docs/harness/layout.md#what-pyprojecttoml-holds). The scaffold holds only what the engine needs.
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
