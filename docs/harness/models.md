# Models

Which models run, and with what settings. The lists live in `configs/models/` so the harness reads the same file you do. This page explains the columns and the choices.

## Two lists

| List | File | When |
|---|---|---|
| Proof of concept | [`poc.toml`](../../configs/models/poc.toml) | Now. Cheap models, one skin, enough to check the harness and the baseline order |
| Full study | [`full.toml`](../../configs/models/full.toml) | When budget lands. The wider array for the headline |

## Columns

| Column | Meaning |
|---|---|
| `id` | The inspect model string, such as `anthropic/claude-haiku-5-5` or `baseline/stale` |
| `kind` | `llm`, `baseline`, `jev` or `timestral`. Tells the analysis which rows are floors and ceilings |
| `reasoning` | `off`, `min`, or a token budget. Reported beside the score |
| `notes` | Anything a reader needs, such as a rate limit or an id to verify |

## Reasoning

- **Reasoning is a setting, not a given.** A model with thinking on is a different row from the same model with it off.
- **The proof of concept runs minimal.** Off where the provider allows, the lowest budget where it does not.
- **The full study runs both** for any model that offers it, as separate rows.

## Keys

inspect reads keys from the environment. Copy `.env.example` to `.env` and fill it in, see [running](running.md).

| Provider | Env var |
|---|---|
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Jev | `TYPESAFE_API_KEY` |
| Timestral | None. Runs locally, see [adapters](adapters.md) |
| Baselines | None |

- **A Claude.ai subscription does not work here.** inspect calls the Anthropic API, which needs a key from the console. The proof of concept is small, so it runs on API credits.

## Concurrency and cost

- `--max-connections` per provider, see [running](running.md#cost-guard).
- Tokens per run come from the [pilot](../pilot/checks.md#cost-per-run).
