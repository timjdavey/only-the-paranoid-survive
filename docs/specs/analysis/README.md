# Analysis spec

The analysis is the top layer. It reads `.eval` logs and writes the tables, CSVs and plots in [results](../../results/poc.md) and [pilot results](../../pilot/results.md): the scenario scores with their bars, the headline and weakest trait, the marks the fixed baselines put on every bar, the gaps between models paired by seed, the spread, the public gap and the noise threshold. It reads a log's scores and metadata and never its messages, and it never serialises a timeline. It imports the harness, the engine, inspect_ai's log reader, pandas, matplotlib and scipy, and nothing in it is read by a model. Why each number is reported is in [scoring](../../design/scoring.md), [models](../../harness/models.md#trend-plots) and [contamination](../../harness/contamination.md).

## Pages

| Page | What it specifies |
|---|---|
| [runs](runs.md) | `load_runs`, the run table with one row per run, `Setting` and `ResultKey`, how a log is read and what is never read |
| [scores](scores.md) | Scenario scores, headlines, marks and flags, paired gaps, the public gap, spread and sampling share, switch kinds, the noise threshold |
| [tables](tables.md) | The results page, the run CSV and the cost table |
| [plots](plots.md) | The strip, profile, trend and noise plots |
| [pilot](pilot.md) | What `write_pilot` writes for each section of pilot results |
| [command](command.md) | `paranoid analyse` and its subcommands |
| [tests](tests.md) | Every test the analysis suite runs, with the page it checks |

## Exports

`paranoid.analysis` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#six-layers).

| Name | Kind | Page |
|---|---|---|
| `load_runs`, `mean_over_epochs`, `RUN_COLUMNS` | Logs to the run table, epochs to one row per seed, and the column names | [runs](runs.md) |
| `Setting`, `ResultKey`, `result_key` | What was played, who played it, and a log's key | [runs](runs.md) |
| `scenario_scores`, `headlines`, `load_recognition`, `RETRY_FLAG`, `RECOGNITION_FLAG` | The pooled scores, bars, marks and flags per result row, and the two flag marks | [scores](scores.md) |
| `paired_gap`, `scenario_gap`, `public_gap`, `GAP_COLUMNS` | Gaps between two rows, two scenarios, two seed sets | [scores](scores.md) |
| `spread`, `sampling_share` | The SD and 10th percentile of run scores, and the model's share of it | [scores](scores.md) |
| `switch_kinds` | Which kind of switch each seed drew | [scores](scores.md) |
| `noise_threshold`, `Threshold`, `signal_points` | The full study headline and its axis | [scores](scores.md) |
| `write_results`, `write_run_csv`, `write_cost`, `CSV_COLUMNS` | The results page, its CSV and the cost table | [tables](tables.md) |
| `strip_plot`, `profile_plot`, `trend_plot`, `noise_plot` | The four plots | [plots](plots.md) |
| `write_pilot`, `SECTIONS` | Pilot results from the pilot cells' CSVs and logs, and the page's headings | [pilot](pilot.md) |
| `analyse` | The `paranoid analyse` entry point | [command](command.md) |

## Names from the harness

The analysis imports these from `paranoid.harness`. Their behaviour is in the [harness spec](../harness/README.md#exports), and the harness's side of this boundary is [what the analysis layer reads](../harness/README.md#what-the-analysis-layer-reads).

| Name | What the analysis uses it for |
|---|---|
| `pooled_score`, `bootstrap`, `BOOTSTRAP_DRAWS`, `BOOTSTRAP_SEED` | Every pooled score and bar, so a table equals the log's own metric, see [pooling](scores.md#pooling) |
| `TRAITS` | Scenario to trait, for the weakest trait and the table headers |
| `load_models`, `ModelRow`, `REASONING` | Row order, `kind`, `released` and `eci` for the tables and trend plots, and the reasoning grid a log's setting is read back onto, see [reasoning](runs.md#reasoning) |
| `scenario_config`, `load_seeds` | The config and seed that rebuild one timeline for [switch kinds](scores.md#switch-kinds) and the signal in [noise threshold](scores.md#noise-threshold) |

The one third-party reader is inspect_ai's `read_eval_log`, see [runs](runs.md#checked).

## Names from the engine

The analysis imports these from `paranoid.engine`. The engine's side of this boundary is [what the layers above read](../engine/README.md#what-the-layers-above-read).

| Name | What the analysis uses it for |
|---|---|
| `SCENARIOS` | The scenario names a log may claim, see [guards](runs.md#guards) |
| `make_timeline`, `Timeline`, `Event` | One timeline per seed, read for its first switch's `kind` and `short` draws and then dropped, see [switch kinds](scores.md#switch-kinds) |
| `SwitchSpec` | The `size_points` range behind `signal_points`, see [noise threshold](scores.md#noise-threshold) |

- **Nothing from the baselines layer.** The baselines' outputs are already in every `Score.value`, see [scoring one run](../harness/scorer.md#scoring-one-run).
- **Nothing from the skins layer.** A skin is its name in the metadata. No skin text is read or written.

## Modules

    src/paranoid/analysis/
      __init__.py    the exports above, nothing else
      runs.py        load_runs, mean_over_epochs, RUN_COLUMNS, Setting, ResultKey, result_key
      scores.py      scenario_scores, headlines, load_recognition, the gaps, spread, sampling_share, switch_kinds, noise_threshold
      tables.py      write_results, write_run_csv, write_cost
      plots.py       the four plots
      pilot.py       write_pilot
      cli.py         analyse

- Nothing outside `__init__.py` is public. Tests import from `paranoid.analysis` only, plus `paranoid.harness` to make logs.
- Third-party imports are inspect_ai, pandas, matplotlib, scipy and numpy. `import-linter` enforces the layer rule, see [layout](../../harness/layout.md#six-layers).
- `pyproject.toml` registers `analyse = "paranoid.analysis.cli:analyse"` in the `paranoid.commands` entry point group, see [subcommands](../harness/command.md#subcommands).

## Conventions

- **One run is one row** of the run table, see [runs](runs.md). One result row is one `ResultKey`: a model at one reasoning setting on one `Setting`, which is the skin, seed set, noise setting, knobs and versions that fix what it played. The `engine_hash` is per scenario, so it is a row's, not a key's.
- **`Score.value` is the source of every number.** The metrics on the log are a check, not a source: a table must equal them on a one-epoch log, and a test says so. Nothing is rebuilt from a timeline but the switch kind.
- **Pooled, never averaged.** Every score over seeds goes through the harness's `pooled_score`, see [pooling seeds](../../design/scoring.md#pooling-seeds). The plain mean appears once, across scenarios in the headline.
- **A written file is deterministic.** The same logs give the same bytes, so a results page diff is a results diff.
- **Everything written is publishable**, so the secrecy rules are invariants here, not options: a held-out seed is its position, a timeline never reaches a file, a message is never read, a skin is its name, see [what never reaches a log or a prompt](../README.md#what-never-reaches-a-log-or-a-prompt).
- **Marks and flags differ.** A mark is a fixed baseline's pooled score on the bar. A flag is a symbol beside a score that says a run gave up, retries ran high, or the model recognised the prompt or finished the canary. A flag never drops a row, see the [retry rule](../../harness/prompts.md#retry-rule).
- **A log is not trusted to name things.** The scenario, skin and model strings a log claims are checked before they reach a table cell or a file name, see [guards](runs.md#guards).
- **Rounds, seeds and scenarios** keep the harness's names: `seed_index` is a position, `scenario` a code name, see [dataset](../harness/task.md#dataset).

## Invariants

- No function in the layer reads `sample.messages` or `sample.store`, or calls `make_timeline` outside `switch_kinds`.
- No written file holds a held-out seed's value, an array, a message, a recognition reply or a word of any skin but its name.
- `load_runs` then `write_results` on the same logs twice gives byte-identical files, whatever was in the output folder before.
- Every path the layer writes is under the `out` it was given.
