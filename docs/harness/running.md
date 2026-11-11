# Running

## Setup

    uv sync                      # engine, skins, harness, analysis
    uv sync --extra timestral    # adds torch and Timestral
    cp .env.example .env         # then fill in keys, see models.md

- **Python 3.12 or later.** `uv` installs the version in `.python-version` for you.
- **`uv sync` installs the provider SDKs too.** inspect calls Anthropic, Google, OpenAI and OpenRouter through `anthropic`, `google-genai` and `openai`, ships none of them, and raises on the first call without one. All three are default dependencies, so there is nothing more to install.
- **Check a change** with `uv run pytest` and `uv run lint-imports`, the two things CI runs. Slow tests are skipped unless you add `-m slow`, see the [engine tests](../specs/engine/tests.md).
- **Tests run in parallel**, one worker per core, through `pytest-xdist`. Add `-n 0` to run them in one process, for example to read a test's output in order.
- **Sweeps** play a baseline on a thousand seeds and take about two minutes. CI skips them, so run `uv run pytest -m sweep` by hand after changing a baseline or the engine, see the [baselines tests](../specs/baselines/tests.md#three-sizes).
- **Timestral's own tests** load the real model, so they run by hand with `uv run pytest -m timestral` once the extra is installed. The first run downloads about 840 MB of weights, see the [forecasters tests](../specs/forecasters/tests.md).
- **The headline needs Docker.** The `compute` tool runs in a sandbox, see [tools](../design/interface.md#tools), so a running Docker is needed for any run at the default `tools`. inspect drives Docker itself, so there is nothing more to install. Pass `-T tools=none` to run without, as the smoke test does.

## Commands

| What | Command |
|---|---|
| One model, one scenario, a few seeds | `inspect eval paranoid/paranoid -T scenario=down_switch -T seeds=0-4 --model anthropic/claude-haiku-5-5` |
| A baseline | `inspect eval paranoid/paranoid --model baseline/complacent` |
| Smoke test with no model or Docker | `inspect eval paranoid/paranoid --model mockllm/model -T tools=none --limit 2` |
| The proof of concept list | `uv run paranoid run --skins <a>,<b> --seeds 0-19`, which reads `configs/models/poc.toml` and plays the two held-out skins named, so it needs `PARANOID_SKINS`. Without `--skins` it plays the example skin |
| The full study | `uv run paranoid run --models configs/models/full.toml --skins <a>,<b> --seeds held-out --own-scale grid`, which plays every setting of the [noise grid](../pilot/engine-checks.md#noise-grid) in `configs/grid.toml`, see the [command spec](../specs/harness/command.md#run) |
| One noise setting | Add `--own-scale 6` to `paranoid run`, or `-T own_scale=6` to `inspect eval paranoid/paranoid` |
| A pilot cell | `uv run paranoid pilot seeds`, one name per check in [engine checks](../pilot/engine-checks.md) or [provider checks](../pilot/provider-checks.md). What each writes is in the [pilot spec](../specs/harness/pilot.md). Add `--workers 8` to split an engine cell's seeds over eight processes, which writes the same file sooner |
| Browse logs | `inspect view` |
| Rebuild the results tables and CSVs | `uv run paranoid analyse logs/`, see the [analysis command](../specs/analysis/command.md) |
| Rebuild the pilot results | `uv run paranoid analyse pilot` |
| Tokens and cost per run | `uv run paranoid analyse cost logs/` |
| The gap between two logs, paired by seed | `uv run paranoid analyse gap a.eval b.eval` |

- **The task is `paranoid/paranoid`** to inspect, as it comes from an installed package, see the [harness spec](../specs/harness/README.md#modules). A hand-typed `inspect eval` should add `--retry-on-error 1`, which `paranoid run` passes for you.
- **Run from the repo root.** `configs/` is read from the working directory, as `--models` is.
- **Task args:** `scenario`, `seeds`, `skin`, `rounds`, `tools` (`notes,compute` by default, or `none`, `notes`, `compute`), `tool_choice`, `inertia`, `warm_up`, `own_scale` and `rolling`, see the [task spec](../specs/harness/task.md). Defaults are the frozen study settings. `scenario` defaults to all eight, so one log holds a headline, see [inspect](inspect.md#metrics). `tool_choice` is picked from the model unless passed, see the [solver spec](../specs/harness/solver.md#each-round).
- **`seeds`** takes `public`, `held-out`, or a range of positions in the public list such as `0-4`. `held-out` needs `PARANOID_SEEDS` set, see [contamination](contamination.md#two-seed-sets).
- **Every log records** the engine hash, the prompt hash, the harness version, the [release](../glossary.md#seeds-and-secrecy), the skin name and the seed set in metadata. A held-out seed is recorded by position, never by value.

## Logs

- Written to `logs/`, gitignored.
- A log holds the full prompt and every reading, so logs from a held-out skin or a held-out seed never leave the machine. See [contamination](contamination.md).
- Published logs come from the example skin on public seeds only and go in `results/logs/`. The proof of concept plays held-out skins, so none of its logs is published.

## Cost guard

- `--limit` caps samples. Try any new model with `--limit 2` first, then read `uv run paranoid analyse cost logs/` before the full run.
- `--max-connections` per provider. Default 4.
- Token counts per run come from the [pilot](../pilot/provider-checks.md#cost-per-run).
