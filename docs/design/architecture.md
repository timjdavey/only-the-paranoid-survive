# Architecture

## The four layers

Deep-module architecture. Each layer reads only what the one before it writes.

| Layer | What it holds | Reads | Writes |
|---|---|---|---|
| **Engine** | Generator (the four blocks, the weather, the levels and the change), shared luck, game, record, views and bots. Pure Python, no I/O, deterministic from config and seed | Config and seed | A `RunLog` per run |
| **Harness** | The Inspect task, the briefing step, the five tools, the code sandbox, the solver loop and the budget guard | The engine | An Inspect `.eval` log, with the `RunLog` in the sample store |
| **Scoring** | Per run measures: performance, catch, the traits and the scanners | One `RunLog` | One row of `runs.jsonl` |
| **Analysis** | Pooling, bootstrap, plots and metrics across runs. Performance is pooled here. The full study adds the curve fit for discernment from performance pooled by amplitude | `runs.jsonl` and `params.yaml` | A frozen report folder |

The split between scoring and analysis follows METR's `eval-analysis-public`, which keeps wrangling, fitting and plotting apart from the per run scores.

## How a run flows

1. **Brief.** Once per seed, the harness gives the model the record and the briefing prompt, and stores the notes it writes. Bots skip this and start from the standing split.
2. **Play.** The engine plays one seed at one amplitude, or the seed's no-change run, driven either by a bot or by a model through the harness with its notes in context. Either way it ends with a `RunLog`.
3. **Score.** The scorer reads the `RunLog` and writes one row to `runs.jsonl`. Bots write the same rows, with null cost.
4. **Flag.** The scanners add `test_aware`, `tool_misuse` and `steering_text` to the row. Invalidations are listed in a separate file, never made by editing rows.
5. **Analyse.** Analysis keeps rows where `suite == poc`, drops the invalidated ones and writes plots and metrics to the report folder.

## Two artefacts

The Inspect `.eval` log is the transcript, for reading and review. `runs.jsonl` is what analysis reads, one flat row per run:

| Field | What it holds |
|---|---|
| `run_id`, `alias`, `model_id` | Which run, and which model by short name and exact API id |
| `seed`, `amplitude` | The seed, and the fall in points. Null for the no-change run |
| `kind_of_change` | `level` in the proof of concept. `coupling`, `gain` or `observation` on the later rungs. Null for the no-change run |
| `history_style`, `skin_id` | Which record the seed used, steady or jittery, and which skin |
| `task_version`, `config_hash` | The version of what the agent sees, and the hash of the game config |
| `compute_tool` | Whether the run had the `compute` tool. False only for the pilot's diagnostic run |
| `suite` | `pilot`, `poc` or `full`. Only `poc` rows reach the proof of concept report |
| `caught`, `performance` | Whether the switch rule fired with no switch in the seed's no-change run, for the catch rate backup, and the run's expected output minus the no-update bot's on the same seed. Analysis pools it over every run into the headline, and by amplitude into discernment in the full study |
| `gain`, `loss` | The run's gain over the no-update bot, in the gain column for a change run and the loss column for the no-change run. Analysis pools them into the split |
| `output`, `expected_output` | Output with the real dice and weather, and the luck-adjusted total |
| `switch_round` | The switch. Null if it never happened |
| `first_experiment_round` | First doubt, a diagnostic. Null if it never happened |
| `insight_shares`, `insight_notes` | Share of rounds and sides near the end with the largest share on that side's best unit, and whether the rewritten notes state the new rule. Null for the no-change run |
| `paranoia_look`, `paranoia_hedge`, `paranoia_experiment`, `dip_moved`, `dip_switch` | The three paranoia rates, the share moved off the dipping unit during the yoked dip, and whether it switched there. Null for change runs |
| `caution_cusum`, `caution_rounds`, `caution_evidence` | The CUSUM line, rounds from the change start, and the reference bot's odds at the switch. Null for the no-change run and for runs with no switch |
| `conviction` | Share on the unit that rose against the reference bot's after the switch. Null without a switch |
| `notes_rewritten` | How many times the agent called `write_notes`, and the round of the first rewrite |
| `briefing_quality` | Whether the notes name the standing split, the second rate units and the resolved changes |
| `compute_calls` | How many times the agent called `compute`, a diagnostic |
| `cost_usd`, `tokens`, `budget_hit` | Spend, and whether the token limit cut the run short |
| `invalid`, `invalid_reason` | Filled in from `invalidations.yaml` when the report is built |

## Harness

**Decided: Inspect AI with custom tools, one of them a sandboxed code tool.**

| | Inspect AI tools | Pydantic AI tools | CLI in Claude Code or Codex |
|---|---|---|---|
| What it measures | The model | The model | Model, harness and its system prompt |
| Gaming surface | Tool outputs and a sandbox holding only what the agent pastes in | The same | A shell that can read the generator, seeds and logs |
| Transcripts, reasoning, usage | Built in, with a viewer | Build it ourselves | Differs by harness |
| Providers, retries, limits, reasoning effort | Built in | Partly | Differs by harness |
| Used by | METR and UK AISI | Neither | Terminal-bench style evals |
| Cost control | Message and token limits | Build it ourselves | Hard |

The briefing is its own solver step: one model call with `read_record`, `compute` and `write_notes`, run once per seed and cached, so the change run and the no-change run share the notes. The live solver is a custom loop, not the default `react()`. It ends when the game says the horizon is over, and if the model stops calling tools it sends a neutral continue message from `assets/continue.md`. The threshold is stated in the `allocate` tool's description, so it is a rule the agent reads, not a cut-off in the scorer. The CLI form is a later rung on the [realism ladder](future.md): the same engine behind a `paranoid-cli` binary, run inside a coding agent.

We use Inspect's own nouns rather than inventing ours:

| Our idea | Inspect's noun |
|---|---|
| One seed, amplitude, history style and skin | A `Sample`, with those in `metadata` |
| The benchmark | One `Task` |
| Scoring a run | A `Scorer` that reads the `RunLog` from the sample `Store` and returns catch, performance, the traits and output in `Score.value` |
| Repeats | `epochs`, set to 1 since [seeds beat repeats](decisions.md#why-more-seeds-not-repeats) |
| Message and token caps | `message_limit` and `token_limit` |
| A grid of runs | A declarative eval set YAML in `eval_sets/`, one per tier, as in METR's Hawk and its task scaffolder |

The task is packaged the METR way, in `src/paranoid/task/`. The prompts and continue message are files, so the banned word lint runs on files. `task_version` lives in `version.py` and goes into every log and row beside `config_hash`.

## What's in the repo

```
README.md  TODO.md  CANARY
docs/design/  docs/prior/          the design, including this page, and the studies it builds on
pyproject.toml                     uv, ruff, pyright, pytest
configs/
  poc.yaml                         every game parameter in mechanics.md, hashed at freeze
  models.yaml                      one entry per model, fields below
eval_sets/                         declarative grids: pilot.yaml, poc.yaml, full.yaml
seeds/public/                      seed manifests: id, structural params, config hash
skins/                             abstract.yaml, fictional.yaml, plant.yaml, market.yaml
records/                           the frozen records, one per seed and history style, with the bot run that wrote each
src/paranoid/
  engine/     config, generator (inputs, state, coupling, observation), weather, luck, game, record, views (AgentView and RunLog)
  bots/       policy protocol, no_update_bot, fixed bots, reference_bot, retune_bot, dip_only_bot
    disposition/ jumpy, cautious, hedging
    cusum.py  the CUSUM bot behind the caution line, fed the weather model
  task/       task.py, version.py, assets/briefing.md, assets/instructions.md, assets/continue.md
  harness/    tools, compute sandbox, briefing, solver, budget guard
  scoring/    runlog schema, performance, catch, insight, paranoia, caution, conviction, experiment, switch, briefing_quality
    scanners/ test_aware, tool_misuse, steering_text
  analysis/   wrangle, bootstrap, fit, plot, metrics, spreads
  cli.py      paranoid bots | records | run | score | report | freeze
tests/        engine, bots, scoring, harness, leak, skin lint and banned word lint tests
reports/poc/         the frozen report, below
```

Every box has an owner. `engine/` and `bots/` are the engine, `task/` and `harness/` the harness, `scoring/` scoring and `analysis/` analysis.

## Reports are frozen folders

```
reports/poc/
  params.yaml           the analysis plan, committed before any model runs
  invalidations.yaml    run id and reason for each run left out
  data/raw/runs.jsonl   every row, as scored
  data/wrangled/        rows after the suite filter and invalidations
  plots/
  metrics/
```

`params.yaml` holds the grid for the tier, the window for the switch rule, the share thresholds for an experiment and a switch, `volume_per_budget`, `saturation_alpha` and `threshold`, the levels, the weather's memory, spread, loadings and dip settings, the yoked dip's length, which unit falls and which rises, the kind of change, the CUSUM reference statistic behind the caution line, the margin an amplitude must clear to count as worth catching, the window of rounds for insight, the Beta prior on the reference bot's hazard, the sandbox limits on time, memory and output, and the bootstrap scheme. The full study's file adds the curve fit for discernment, its reading levels and whether amplitude enters the fit as points or their log. The bootstrap is two level, seeds first and then runs within a seed, because every run on a seed shares the same luck.

The scorer never refuses a log. Pilot and tuning runs carry `suite: pilot`, stay re-scorable, and the report leaves them out by filter.

## Anti-gaming, built in

| Threat | Defence in the architecture | Test |
|---|---|---|
| Model reads hidden state | Tools render only an `AgentView`, which holds only the funded units' results. The `RunLog`, with the true levels and the weather, never reaches a tool | Every tool output validates against `AgentView` and holds no hidden field |
| Hidden state leaks through an error | Tool errors render through `AgentView` too | Fuzz invalid splits, units and record lengths, then lint every error string |
| Model reads code, seeds or shared luck | No shell and no filesystem. The one code tool is a sandbox that sees only what the agent already saw: no files, no network, no engine import | The harness has exactly [five tools](mechanics.md#tools), and a sandbox test tries to open files, sockets and the engine and must fail |
| Prompt names the move | One renderer for the briefing prompt, the live prompt, the skin, tool docstrings, errors and continue message | Banned word lint (change, probe, commit, explore, exploit, test, benchmark, experiment) over every rendered string |
| A skin leaks information | A skin is a map from abstract names to nouns and a story, and nothing else | Skin lint: every skin renders the same tables and numbers as the abstract skin |
| Fixed strategy scores well | Bots go through the same game and scorer | CI: every fixed bot scores below the reference bot, and the no-update bot catches nothing |
| Learning public seeds | Structure lives in config, not code. Private configs vary the start, the ramp, the dip's length and which unit falls and which rises | Public and private scores reported side by side |
| Learning the record | One frozen record per seed, written by a bot, the same for every model | The record's hash is in the seed manifest |
| Post-hoc tuning | `params.yaml` and `configs/poc.yaml` committed and tagged before any model runs. Every row carries `config_hash` and `task_version` | The report checks every `poc` row's hash against the tag |
| Runs cut short by budget | The token limit is set high and `budget_hit` is recorded | One model is rerun with the limit doubled. The headline must not move. Runs that hit the limit are flagged, not scored as misses |
| Steering or misuse | Scanners write structured flags per run | A planted bad run in tests trips each flag |
| A bug that fails good runs | Before publishing, read each model's worst runs by hand, as METR did when wrapper bugs rejected correct answers | Each review is logged in `invalidations.yaml` or noted as clean |
| Training contamination | Canary GUID in every published file and transcript | Lint checks the canary is present |

The rule, in the terms of METR's Task Standard: the agent sees only what `get_instructions` returns, never what `get_tasks` returns. Here those are `AgentView` and `RunLog`. Why each defence exists is in [Why the game is hard to game](decisions.md#why-the-game-is-hard-to-game).

## Models

`models.yaml` records what Epoch records for each model, since the headline is plotted against release date and anyone rerunning a model needs the same settings.

| Field | What it holds |
|---|---|
| `alias`, `model_id` | Short name, and the exact API id |
| `developer`, `release_date` | Who made it, and when it came out |
| `provider`, `api` | Where it is served, and the endpoint used |
| `reasoning` | Its standard high setting |
| `temperature` | The API default |
| `system_prompt` | Empty |

A budget guard aborts a run or a model past a set dollar cap, and logs usage per run.

## Public and private data

| | Public repo (this one) | Private repo, `paranoid-private` |
|---|---|---|
| Holds | All code, docs, public seeds, public skins, frozen records, bot results and public transcripts | Data only: private seed configs, private skins, private transcripts and raw scores |
| Code | The package | None. It installs the public package and points it at its own `seeds/`, `skins/` and `records/` |
| Published | Any time, since nothing secret is ever in it | Never. Its SHA-256 is published at freeze, so readers can trust it wasn't tuned after results |

- **Transcripts go out from day one.** Public seed transcripts are published with the canary as soon as they exist, not at freeze, as release assets or a Hugging Face dataset.
- **One repo is the alternative.** METR keeps private data in the same repo with DVC and a private remote. We keep two repos because the public one can then never leak.
- **Private seeds still reach providers.** They are sent to model APIs, so we use no-training API terms and rotate private skins each major version.
- **Open: gate the dataset or not.** Epoch puts its log viewer behind a CAPTCHA to keep scrapers out. Whether our Hugging Face dataset is gated is decided before the first upload.

## Maintaining it

1. **`RunLog` is the contract.** Its schema is versioned, and scoring never imports the harness.
2. **Bump `task_version` when anything the agent sees changes.** That covers both prompts, the continue message, tool docstrings, error strings and the skins.
3. **Every open question is a setting.** Volume per budget, saturation, the threshold, the weather, amplitudes, cut-offs and record length live in YAML, so settling an [open question](../../TODO.md#open-questions) needs no code change.
4. **Determinism tests pin the design's numbers.** A drift in code fails against the written design.
5. **Leak and lint tests come before the harness**, so they guard it from day one.
6. **Invalidate, never edit.** A bad run gets a line in `invalidations.yaml` with a reason. Raw rows stay as scored.
7. **`paranoid freeze` does the freeze.** It tags the commit, hashes the configs, the records and the private bundle, and writes the canary.
8. **Records come from the same engine**, run by the damped reference bot through `paranoid records`, so the frozen records and the scored runs share code.
