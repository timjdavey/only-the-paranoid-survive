# Layout

How the code is arranged. The [design](../design/) pages say why the game is the way it is. This folder says how it is built.

## Four layers

    analysis  →  harness  →  skins  →  engine

- **A layer imports only from layers to its right.** The engine knows nothing about inspect_ai. The harness never reaches into the generator's internals.
- **Each layer exports from its `__init__.py` only.** Everything else in the package is private.
- **Tests for a layer need nothing above it.** Engine tests run with no model, no network and no inspect.
- **Enforced in CI** by an `import-linter` layered contract in `pyproject.toml`. A wrong-way import fails the build.

| Layer | Package | Depends on | What it exports |
|---|---|---|---|
| engine | `paranoid.engine` | numpy | `ScenarioConfig`, `SCENARIOS`, `engine_hash`, `make_tape`, `Tape`, `Game`, `Record`, `play`, the fixed policies. Forecast policies come with the Timestral provider, see the [engine spec](../specs/engine/policies.md#parked) |
| skins | `paranoid.skins` | engine | `Skin`, `load_skin`, `load_skins`, `render_system_prompt`, `render_record`, `prompt_hash`, `lint`, `lint_text`, `BANNED_WORDS`, `CANARY`, see the [skins spec](../specs/skins/README.md) |
| harness | `paranoid.harness` | skins, inspect_ai | the `paranoid` task, the round loop solver, the `submit` tool, providers, scorer, metrics, the `paranoid` command |
| analysis | `paranoid.analysis` | harness, pandas | `load_runs`, tables, CSVs, bootstrap, plots |

## What each layer does

- **Engine** turns a scenario and a seed into a [tape](../design/mechanics.md#generator), takes bets and returns readings and output, keeps the [record](../design/interface.md#tools), and holds every [baseline](../design/baselines.md) as a pure function from what it may see to bets. Deterministic. Every number in [mechanics](../design/mechanics.md) is a field on `ScenarioConfig`, and a hash of the config goes into every log.
- **Skins** dress the engine in a story. A skin is text plus the names of the ten channels. The layer renders the system prompt and the record in the skin's words, and lints both for banned words. Private skins load from a path, see [skins](skins.md).
- **Harness** is the inspect_ai layer. One task, one solver, one tool, a provider for every model that cannot place bets, a scorer and metrics. See [inspect](inspect.md).
- **Analysis** reads `.eval` logs and writes the tables and plots in [results](../results/poc.md) and [pilot results](../pilot/results.md). Beside each table it writes the data as a CSV with one row per run: model, skin, scenario, seed set, seed and score. A held-out seed shows its position in the list (0, 1, 2…), never its value, see [contamination](contamination.md#who-can-see-them).

## Repo tree

    README.md  AGENTS.md  TODO.md  CONTRIBUTING.md  LICENSE
    pyproject.toml  .env.example
    configs/
      models/      poc.toml and full.toml. See models.md
      seeds/       public seeds, one file per scenario, once the engine exists. Held-out seeds are private, see contamination.md
    docs/
      design/      why. The decisions
      harness/     how. This folder
      pilot/       checks to run, decisions taken, results
      results/     the headline tables and their CSVs
      prior/       what others have done
      specs/       what each layer must do, written before its code. See docs/specs/README.md
        engine/
      glossary.md
    src/paranoid/
      engine/  skins/  harness/  analysis/
    tests/         one folder per layer
    logs/          inspect logs, gitignored

## Naming

- **Package** `paranoid`. The repo name stays as it is.
- **Providers** are `baseline/<name>`, `jev/<model>` and `timestral/<policy>`, so `--model baseline/complacent` works like `--model anthropic/<model>`.
- **Glossary words in code too**, see [glossary](../glossary.md). A tape is a tape, not a world or a trajectory.
