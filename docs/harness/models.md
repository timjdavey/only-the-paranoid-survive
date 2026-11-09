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
| `reasoning` | The [reasoning setting](../glossary.md). One value in `poc.toml`, a list in `full.toml` where each value is its own result row |
| `released` | Release date, from Epoch's `date` column. Full study only |
| `eci` | The model's [ECI](../glossary.md), a snapshot from Epoch's [CSV](https://epoch.ai/data/eci_scores.csv). Full study only |
| `notes` | Anything a reader needs, such as a rate limit or an id to verify |

## Reasoning

- **Reasoning is a setting, not a given.** A model with thinking on is a different row from the same model with it off.
- **The proof of concept runs minimal.** Off where the provider allows, the lowest budget where it does not.
- **The full study runs a sweep.** Each model lists every setting it supports from one shared grid, and each one is its own row.

| Setting | Meaning |
|---|---|
| `off` | No thinking |
| `low`, `medium`, `high`, `max` | Effort levels, mapped to the provider's own setting: `reasoning_effort` for OpenAI, `thinking_level` for Gemini, `effort` for Claude, `reasoning` for OpenRouter. Where a model only takes a token budget, the harness picks one per level |
| `on` | Thinking the model won't let us change, such as DeepSeek R1 |

- **`xhigh` is skipped** to keep the grid at five steps.

## Trend plots

The full study plots the headline two ways, one point per model and setting:

- **Against release date** (`released`). Is the trait improving over time?
- **Against [ECI](../glossary.md)** (`eci`). Is it just general capability, or something separate?
- **Settings of one model are joined by a line.** ECI has one score per model, not per setting, so on the ECI plot a model's settings stack in a column. How tall that column is tells you how much reasoning matters.
- **Error bars** come from [scoring](../design/scoring.md#error-bars).
- **ECI is Epoch AI's**, under CC BY 4.0. Credit it on every plot. The analysis can refresh `eci` from the CSV, but it reports the date it read it.

## Keys

inspect reads keys from the environment. Copy `.env.example` to `.env` and fill it in, see [running](running.md).

| Provider | Env var |
|---|---|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Jev | `TYPESAFE_API_KEY` |
| Timestral | None. Runs locally, see [adapters](adapters.md) |
| Baselines | None |

- **A Claude.ai subscription does not work here.** inspect calls the Anthropic API, which needs a key from the console. The proof of concept is small, so it runs on API credits.

## Concurrency and cost

- `--max-connections` per provider, see [running](running.md#cost-guard).
- Tokens per run come from the [pilot](../pilot/checks.md#cost-per-run).
