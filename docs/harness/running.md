# Running

## Setup

    uv sync                      # engine, skins, harness, analysis
    uv sync --extra timestral    # adds torch and Timestral
    uv sync --extra sandbox      # adds the Docker sandbox for the compute tool
    cp .env.example .env         # then fill in keys, see models.md

## Commands

| What | Command |
|---|---|
| One model, one scenario, a few seeds | `inspect eval paranoid -T scenario=down_switch -T seeds=0-4 --model anthropic/claude-haiku-5-5` |
| A baseline | `inspect eval paranoid --model baseline/complacent` |
| Smoke test with no model | `inspect eval paranoid --model mockllm/model --limit 2` |
| The proof of concept list | `uv run paranoid poc`, which reads `configs/models/poc.toml` |
| A pilot cell | `uv run paranoid pilot seeds`, one name per check in [engine checks](../pilot/engine-checks.md) or [provider checks](../pilot/provider-checks.md) |
| Browse logs | `inspect view` |
| Rebuild the results tables and CSVs | `uv run paranoid analyse logs/`, see the [analysis command](../specs/analysis/command.md) |
| Rebuild the pilot results | `uv run paranoid analyse pilot` |
| Tokens and cost per run | `uv run paranoid analyse cost logs/` |
| The gap between two logs, paired by seed | `uv run paranoid analyse gap a.eval b.eval` |

- **Task args:** `scenario`, `seeds`, `skin`, `rounds`, `tools` (none, notes, compute), `inertia`, `warm_up`, `own_scale` and `rolling`, see the [task spec](../specs/harness/task.md). Defaults are the frozen study settings. `scenario` defaults to all eight, so one log holds a headline, see [inspect](inspect.md#metrics). Tool choice is picked from the model, not passed.
- **`seeds`** takes `public`, `held-out`, or a range of positions in the public list such as `0-4`. `held-out` needs `PARANOID_SEEDS` set, see [contamination](contamination.md#two-seed-sets).
- **Every log records** the engine hash, the prompt hash, the harness version, the skin name and the seed set in metadata. A held-out seed is recorded by position, never by value.

## Logs

- Written to `logs/`, gitignored.
- A log holds the full prompt and every reading, so logs from a held-out skin or a held-out seed never leave the machine. See [contamination](contamination.md).
- Published logs come from the example skin on public seeds only and go in `results/logs/`.

## Cost guard

- `--limit` caps samples. Try any new model with `--limit 2` first.
- `--max-connections` per provider. Default 4.
- Token counts per run come from the [pilot](../pilot/provider-checks.md#cost-per-run).
