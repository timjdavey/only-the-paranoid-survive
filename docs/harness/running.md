# Running

## Setup

    uv sync                      # engine, skins, harness, analysis
    uv sync --extra timestral    # adds torch and Timestral
    uv sync --extra sandbox      # adds the Docker sandbox for the compute tool
    cp .env.example .env         # then fill in keys, see models.md

## Commands

| What | Command |
|---|---|
| One model, one scenario, a few seeds | `inspect eval paranoid -T scenario=switch -T seeds=0-4 --model anthropic/claude-haiku-5-5` |
| A baseline | `inspect eval paranoid --model baseline/stale` |
| Smoke test with no model | `inspect eval paranoid --model mockllm/model --limit 2` |
| The proof of concept list | `uv run paranoid poc`, which reads `configs/models/poc.toml` |
| A pilot cell | `uv run paranoid pilot seeds`, one name per check in [checks](../pilot/checks.md) |
| Browse logs | `inspect view` |
| Rebuild the results tables | `uv run paranoid analyse logs/` |

- **Task args:** `scenario`, `seeds`, `skin`, `rounds`, `tools` (none, notes, compute) and `inertia`. Defaults are the frozen study settings.
- **Every log records** the engine hash, the prompt hash and the skin name in metadata.

## Logs

- Written to `logs/`, gitignored.
- A log holds the full prompt, so logs from a private skin never leave the machine. See [privacy](../privacy.md).
- Published logs come from the public skin only and go in `results/logs/`.

## Cost guard

- `--limit` caps samples. Try any new model with `--limit 2` first.
- `--max-connections` per provider. Default 4.
- Token counts per run come from the [pilot](../pilot/checks.md#cost-per-run).
