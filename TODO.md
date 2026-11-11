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
- **Bayesian run time.** About 46 ms a run, down from 103, now the filter's states are cached by the record's rows, and 204 ms with `lookahead`, down from 265, see [the cache](docs/specs/baselines/bayesian.md#the-cache). Every engine cell wrote the same bytes before and after. Measured on eight cores:
  - `baseline-order` on 1000 seeds takes about 8 minutes on one core and 97 seconds with `--workers 8`.
  - `game-length` on 50 seeds takes 83 seconds with `--workers 8`, so about 27 minutes on 1000. Pass `--seeds 200` while a knob is still moving.
  - `bayesian-frontier` takes 15 seconds, as it now plays three players on ten seeds, see [Bayesian frontier](docs/pilot/engine-checks.md#bayesian-frontier).

First numbers from the forecasters layer, on the real Timestral at its [pins](docs/specs/forecasters/timestral.md#pinned), for the [Timestral checks](docs/pilot/provider-checks.md#timestral-checks):
- **Gap test.** Ten readings then blanks, on seed 0 of One shock. After thirty blanks the spread is wider on every channel: 2.1 to 3.0 times with the channels joint, 2.0 to 6.9 times with each alone. It does not widen round by round. Joint, the mean spread falls from 44 to 40 points over the first ten blanks, then grows to 107. Alone it grows from 43 to 198. Decide whether that is widening enough for Timestral odds.
- **Determinism.** The same input twice is equal, on one thread or four, so the cache keys on the inputs alone.
- **Rounding.** `rounded_out` was true on every round of every Timestral odds run, 468 of 468, so a yes or no measured nothing. `rounded_out` is now a count of channels, see [rounded out](docs/specs/forecasters/policy.md#rounded-out). Its mean a round was 6.4 for odds and 6.8 for odds alone and bet aware. Odds kept a bet on 3.6 of the ten channels a round, with 79 points on its top one.
- **On the grid.** Seeds 0 to 3 only, at the defaults, so a smoke test and not a measure. Mean score over One shock, Down switch and Up switch: top pick 0.85, explore 1 0.84, odds 0.80, odds alone 0.80, bet aware 0.79, explore 2 0.76, explore 5 0.48, beside the hedge rule's 0.88 and the Complacent baseline's 0.84. Top pick never moved on Up switch. Explore 1, 2 and 5 ended where the Discerning baseline did on 12 of 12. Odds alone moved no scenario by more than 0.03 from odds, and bet aware none by more than 0.01 from odds alone, so on four seeds neither the shape nor the bets shows.
- **Run time.** About 115 ms a forecast on CPU, so 5 seconds a run and half an hour a grid setting for the `timestral` cell. The thread count makes no difference.

## Code
- Compare one plot's SVG hash from CI with one made on a Mac before a results page is rebuilt on a second machine. Equal bytes are checked on one machine only, see [plots](docs/specs/analysis/plots.md#verify-before-code).
- Add the full study's rows to `configs/prices.toml` once their ids are verified. It holds the three `llm` rows of `poc.toml`, read on 2026-11-11, so read them again if weeks pass before the cost check, see [cost](docs/specs/analysis/tables.md#cost).
- The held-out seed lists in the private repo, see [contamination](docs/harness/contamination.md#two-seed-sets). The public list, 0 to 999, is in `configs/seeds/public.txt`.
- Ask each provider in `configs/models/` for zero data retention before the pilot's `recognition` and `channel-order` cells, as both send every held-out skin's prompt to every `llm` row, see [contamination](docs/harness/contamination.md#who-can-see-them). The proof of concept plays held-out skins too.
- Pass the same two held-out skins to `paranoid run --skins` on every proof of concept run, see [running](docs/harness/running.md#commands).
- Before the proof of concept, run `paranoid run --limit 2` on both skins and read `paranoid analyse cost`, so the budget rests on measured tokens and a cached share, see [cost per run](docs/pilot/provider-checks.md#cost-per-run).
- If Claude runs through a subscription, check its rate limit and cache reads first, and play no held-out skin through it: Anthropic's Free, Pro and Max plans are outside zero data retention, see [keys](docs/harness/models.md#keys).
- Pass `--seeds` to every proof of concept run. A bare `--seeds public` is the whole public list, 1000 seeds of eight scenarios, so 8000 runs a skin, see [running](docs/harness/running.md#commands).
- Run the [channel order check](docs/pilot/provider-checks.md#channel-order) before any other provider check, as its answer can change the `submit` tool they all play.
- Rule on the six pass names in the held-out skin `indigo` that sit one letter from a real place, before `indigo` is called done and before [recognition](docs/pilot/provider-checks.md#recognition) reads it. The search and its findings are in the private repo's `skins/README.md`.
- Every skin calls its split percentages, which is the first answer to the round hundred. If [recognition](docs/pilot/provider-checks.md#recognition) replies still doubt a skin for it, decide whether a skin may state another number that the tool turns into 100 points, see [writing a skin](docs/harness/writing-a-skin.md#give-every-fixed-fact-a-reason). Not built.
  - Whole points only convert cleanly from a number that divides 100, which makes the smallest bet larger, or from a multiple of 100 placed in fixed lots.
  - It would change the lint's [budget fact](docs/specs/skins/lint.md#frame-facts), the skin spec and the `submit` tool.
- Pin the sandbox image in `compose.yaml` by digest as well as by tag, so a rebuilt `python:3.12-slim-bookworm` cannot change what compute runs on, see [compute](docs/specs/harness/solver.md#compute).
- Code killed past `mem_limit` returns `""` to the model, with no reason. Decide whether compute should return a word of the skin's on exit code 137 instead, see [compute](docs/specs/harness/solver.md#checked).
- Two specs disagree, so choose one:
  - The tie rule for the weakest trait, see [the scores table](docs/specs/analysis/tables.md#the-scores-table) and [scoring](docs/design/scoring.md).
  - Whether "rounds to pull clear" is `clear_round − onset` or one more, see [reading the inputs](docs/specs/analysis/pilot.md#reading-the-inputs) and [game length](docs/specs/harness/pilot.md#game-length).
  - Whether a Down switch seed that never pulls clear is `0` or empty, same two pages.
- Design choices the review left open:
  - One cross setting table that raises stops the whole results page, see [the cross setting tables](docs/specs/analysis/tables.md#the-cross-setting-tables). It could skip that table and say so.
  - `move_round` misses a scout round when two channels tie for the largest bet, see [baseline order](docs/specs/harness/pilot.md#baseline-order).
  - The Up switch order in the up and down tables, and Up switch seeds whose sleeper stops short, see [sections](docs/specs/analysis/pilot.md#sections).
  - The cost table's `projected` column, see [cost](docs/specs/analysis/tables.md#cost).
  - The Sensitivity table's Headline cell drops the flags the scores table shows, see [the cross setting tables](docs/specs/analysis/tables.md#the-cross-setting-tables).
- Tidy ups: delete plot SVGs a rebuild no longer writes, move `matplotlib.use("Agg")` out of import time in `paranoid.analysis.plots`, and read a log's header alone where the samples are not needed, see [plots](docs/specs/analysis/plots.md#every-plot) and [runs](docs/specs/analysis/runs.md).
- Run the full study's retiring rows first, or swap them before they go: `claude-haiku-4-5-20251001` (any time now), `gpt-4o-2024-11-20` (2027-01-14), `gpt-5.1` (2027-04-01).

## Needs a key
Every other "Verify before code" item on a harness or analysis page is closed, see its "Checked" section, bar equal plot bytes across machines, see [code](#code). These call a provider, so they wait for a workspace with a `.env`. Each spec bullet says the exact call. The `.env` lives outside any workspace and is linked in, see [keys](docs/harness/running.md#keys).
- **Each provider takes what inspect sends.** One small call per `llm` row and reasoning setting in `configs/models/`, see the [command spec](docs/specs/harness/command.md#verify-before-code). It checks every model id and every setting marked "to verify" in `full.toml` on the way.
- **`off` is off.** No reasoning tokens on any `off` row, same page. `poc.toml` has no `off` row today, so run the check at `off` on all three of its `llm` rows. Anthropic's docs say Haiku 5.5 can turn thinking off, inspect sends `between_tools` for Sonnet 5.5, and Google's docs list no off for `gemini-3.5-flash-lite`. A row that passes moves to `off`, as the proof of concept runs minimal, see [reasoning](docs/harness/models.md#reasoning).
- **Which OpenRouter models refuse a required tool call while thinking**, see the [solver spec](docs/specs/harness/solver.md#verify-before-code). DeepSeek and Kimi are the likely ones.
- **Cutting the record into content blocks changes the bill and not the prompt.** Two checks left of three, on one Anthropic model, same page. Run them before the pilot, as the prompt structure freezes after it. Once both pass, set `BLOCK_CACHE_APIS = ("anthropic",)` in `src/paranoid/harness/solver.py`, which ships empty. Anthropic's docs put the cache minimum at 512 tokens on Claude 5.5 models, so a `uniform` warm up of thirty rounds clears it.
- **One live Jev reply holds a probability for every option**, see the [providers spec](docs/specs/harness/providers.md#verify-before-code).
- **Which models read their own earlier reasoning on a later turn**, from provider docs, same solver page, for the rows of `full.toml`. The three `llm` rows of `poc.toml` say it in their `notes`. Only the rolling cell reads it.
