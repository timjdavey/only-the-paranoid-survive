# Running

## Setup

    uv sync                      # engine, skins, harness, analysis
    uv sync --extra timestral    # adds torch and Timestral
    uv sync --extra sandbox      # adds the Docker sandbox for the compute tool
    cp .env.example .env         # then fill in keys, see models.md

- **The headline needs Docker.** The `compute` tool runs in a sandbox, see [tools](../design/interface.md#tools), so the sandbox extra and a running Docker are needed for any run at the default `tools`. Pass `-T tools=none` to run without, as the smoke test does.

## Commands

| What | Command |
|---|---|
| One model, one scenario, a few seeds | `inspect eval paranoid -T scenario=down_switch -T seeds=0-4 --model anthropic/claude-haiku-5-5` |
| A baseline | `inspect eval paranoid --model baseline/complacent` |
| Smoke test with no model or Docker | `inspect eval paranoid --model mockllm/model -T tools=none --limit 2` |
| The proof of concept list | `uv run paranoid run --skins <a>,<b>`, which reads `configs/models/poc.toml` and plays the two held-out skins named, so it needs `PARANOID_SKINS`. Without `--skins` it plays the example skin |
| The full study | `uv run paranoid run --models configs/models/full.toml --skins <a>,<b> --seeds held-out --own-scale grid`, which plays every setting of the [noise grid](../pilot/engine-checks.md#noise-grid) in `configs/grid.toml`, see the [command spec](../specs/harness/command.md#run) |
| One noise setting | Add `--own-scale 6` to `paranoid run`, or `-T own_scale=6` to `inspect eval paranoid` |
| A pilot cell | `uv run paranoid pilot seeds`, one name per check in [engine checks](../pilot/engine-checks.md) or [provider checks](../pilot/provider-checks.md). What each writes is in the [pilot spec](../specs/harness/pilot.md) |
| Browse logs | `inspect view` |
| Rebuild the results tables and CSVs | `uv run paranoid analyse logs/`, see the [analysis command](../specs/analysis/command.md) |
| Rebuild the pilot results | `uv run paranoid analyse pilot` |
| Tokens and cost per run | `uv run paranoid analyse cost logs/` |
| The gap between two logs, paired by seed | `uv run paranoid analyse gap a.eval b.eval` |

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
