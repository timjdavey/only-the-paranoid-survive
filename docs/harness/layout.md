# Layout

How the code is arranged. The [design](../README.md#design) pages say why the game is the way it is. This folder says how it is built.

## Six layers

    analysis  →  harness  →  skins, forecasters  →  baselines  →  engine

- **A layer imports only from layers to its right.** The engine knows nothing about inspect_ai. The harness never reaches into the generator's internals.
- **Skins and forecasters sit side by side.** Neither imports the other. A skin is words and a forecaster is numbers.
- **Each layer exports from its `__init__.py` only.** Everything else in the package is private.
- **Tests for a layer need nothing above it.** Engine tests run with no model, no network and no inspect.
- **Enforced in CI** by an `import-linter` layered contract in `pyproject.toml`. A wrong-way import fails the build.

| Layer | Package | Depends on | What it exports |
|---|---|---|---|
| engine | `paranoid.engine` | numpy | `ScenarioConfig`, `SCENARIOS`, `engine_hash`, `make_timeline`, `Timeline`, `Game`, `Record`, `play`, `View`, `Policy`, `split_budget`, see the [engine spec](../specs/engine/README.md#exports) |
| baselines | `paranoid.baselines` | engine | the fixed policies, `HedgeRule`, `ScoutRule`, `POLICIES`, the forecast rules and `FORECAST_RULES`, see the [baselines spec](../specs/baselines/README.md#exports) |
| skins | `paranoid.skins` | engine | `Skin`, `SkinError`, `load_skin`, `load_skins`, `render_system_prompt`, `render_record`, `prompt_hash`, `lint`, `lint_text`, `LintError`, `CANARY` and the lint's word lists, see the [skins spec](../specs/skins/README.md#exports) |
| forecasters | `paranoid.forecasters` | baselines, engine, and torch and Timestral through the `timestral` extra | `Forecaster`, `Forecast`, `ForecastPolicy`, `TIMESTRAL_POLICIES`, see the [forecasters spec](../specs/forecasters/README.md#exports) |
| harness | `paranoid.harness` | skins, forecasters, baselines, engine, inspect_ai | the `paranoid` task, `RunStore`, the round loop solver, the three tools, the providers, the scorer and its five metrics, the models config, the `paranoid` command and the pilot cells, see the [harness spec](../specs/harness/README.md#exports) |
| analysis | `paranoid.analysis` | harness, engine, pandas, matplotlib, scipy | `load_runs`, `ResultKey`, `scenario_scores`, `headlines`, the gaps, `spread`, `switch_kinds`, `noise_threshold`, the writers and plots, `analyse`, see the [analysis spec](../specs/analysis/README.md#exports) |

## What each layer does

- **Engine** turns a scenario and a seed into a [timeline](../design/mechanics.md#generator), takes bets and returns readings, keeps the [record](../design/interface.md#tools), and says what a policy may see. Deterministic. Every number in [mechanics](../design/mechanics.md) is a field on `ScenarioConfig`, and a hash of the config goes into every log.
- **Baselines** hold every [baseline](../design/baselines.md) as a pure function from what it may see to bets, plus the rules that turn a forecast into bets. A new baseline is a file here and a key in `POLICIES`, and the harness plays it as `baseline/<name>` with no change of its own.
- **Skins** dress the engine in a story. A skin is text plus the names of the ten channels. The layer renders the system prompt and the record in the skin's words, and lints both for banned words. Private skins load from a path, see [skins](skins.md).
- **Forecasters** play a [forecaster](../glossary.md#the-study) such as Timestral as a policy: the record in, a forecast, a forecast rule, bets out. The layer hides the model, its weights, the pin and the forecast cache, so `play` runs Timestral with no harness and no skin. It is the only layer that imports torch.
- **Harness** is the inspect_ai layer. One task, one solver, one tool, a provider for every model that cannot place bets, a scorer and metrics. See [inspect](inspect.md).
- **Analysis** reads `.eval` logs and writes the tables and plots in [results](../results/poc.md) and [pilot results](../pilot/results.md). Beside each table it writes the data as a CSV with one row per run: model, skin, scenario, seed set, seed and score. A held-out seed shows its position in the list (0, 1, 2…), never its value, see [contamination](contamination.md#who-can-see-them). It reads a log's scores and metadata and never its messages, see the [analysis spec](../specs/analysis/README.md).

## Repo tree

    README.md  AGENTS.md  TODO.md  CONTRIBUTING.md  LICENSE
    pyproject.toml  .env.example
    .conductor/    settings.toml, the setup script that links .env into a new workspace. See running.md
    configs/
      models/      poc.toml and full.toml. See models.md
      seeds/       public.txt, the one list every scenario plays, once the engine exists. Held-out seeds are private, see contamination.md
      grid.toml    the noise grid and the release name, see docs/specs/harness/task.md
      prices.toml  token prices for the cost table and the date they were read, see docs/specs/analysis/tables.md
    docs/
      design/      why. The decisions
      harness/     how. This folder
      pilot/       checks to run, decisions taken, results
      results/     the headline tables and their CSVs
      prior/       what others have done
      specs/       what each layer must do, written before its code. See docs/specs/README.md
        engine/  baselines/  skins/  forecasters/  harness/  analysis/
      glossary.md
    shapes/        pictures of every shape and a test of each against its purpose, outside the package. See shapes/README.md
    src/paranoid/
      engine/  baselines/  skins/  forecasters/  harness/  analysis/
    tests/         one folder per layer
    logs/          inspect logs, gitignored

## What `pyproject.toml` holds

One file carries a duty for every layer. Each row links to the spec that owns the rule, so this table is the checklist and never the rule.

| Part | What it holds | Owner |
|---|---|---|
| Layer contract | An `import-linter` layered contract over the six packages, a contract that keeps torch and Timestral out of every package but forecasters, one that keeps the skins layer to the engine and the standard library, one that keeps pandas, matplotlib and scipy out of the harness and below, and one that keeps the baselines, skins and forecasters out of the analysis. All run in CI | [Six layers](#six-layers), [analysis modules](../specs/analysis/README.md#modules) |
| Console script | `paranoid`, pointing at the harness's `main` | [command spec](../specs/harness/command.md#subcommands) |
| `inspect_ai` entry point | The module that registers the `baseline`, `jev` and `timestral` providers | [providers spec](../specs/harness/providers.md) |
| `paranoid.commands` entry point | `analyse`, which the harness finds without importing the analysis layer | [analysis command](../specs/analysis/command.md#dispatch) |
| Provider SDKs | `anthropic`, `google-genai` and `openai`, each at the lowest version the pinned inspect accepts. inspect ships none of them, and an `llm` row cannot be called without its provider's | [running](running.md#setup) |
| Extras | `timestral` for torch and Timestral, which only the forecasters layer imports. The Docker sandbox needs no extra, as inspect drives the `docker` command | [running](running.md#setup) |
| Package data | `skins/example.toml` and the harness's `compose.yaml` | [skin spec](../specs/skins/skin.md#the-example-skin), [solver spec](../specs/harness/solver.md#compute) |
| Pins | numpy and pandas to one minor version, scipy to one minor version, matplotlib exactly, as its version is written into every SVG, and the Timestral package to one git commit | [engine hash](../specs/engine/config.md#engine-hash), [plots](../specs/analysis/plots.md#checked), [forecasters spec](../specs/forecasters/timestral.md#pinned) |

## Naming

- **Package** `paranoid`. The repo name stays as it is.
- **Providers** are `baseline/<name>`, `jev/<model>` or `jev/<endpoint>/<model>`, and `timestral/<policy>`, so `--model baseline/complacent` works like `--model anthropic/<model>`.
- **Glossary words in code too**, see [glossary](../glossary.md). A timeline is a timeline, not a tape, a world or a trajectory.
