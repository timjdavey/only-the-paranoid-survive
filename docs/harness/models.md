# Models

Which models run, and with what settings. The lists live in `configs/models/` so the harness reads the same file you do. This page explains the columns and the choices.

## Two lists

| List | File | When |
|---|---|---|
| Proof of concept | [`poc.toml`](../../configs/models/poc.toml) | Now. Cheap models, two held-out skins, enough to check the harness and the baseline order and to put a first number on [skin sensitivity](../design/scoring.md#spread) |
| Full study | [`full.toml`](../../configs/models/full.toml) | When budget lands. The wider array for the headline |

- **Only a row that reads the skin plays every skin.** LLM rows read the whole prompt and Jev reads the skin's question, so both play each skin. Timestral and the fixed baselines read numbers only, see [baselines](../design/baselines.md#timestral), so they play the first skin and no more, see the [command spec](../specs/harness/command.md#run).

## Columns

| Column | Meaning |
|---|---|
| `id` | The inspect model string, such as `anthropic/claude-haiku-5-5` or `baseline/complacent` |
| `kind` | `llm`, `baseline`, `jev` or `timestral`. Tells the analysis which rows are floors and ceilings |
| `reasoning` | The [reasoning setting](../glossary.md). One value in `poc.toml`, a list in `full.toml` where each value is its own result row |
| `reasoning_kind` | `effort` or `budget`: whether the provider takes an effort name or a token budget. Optional. The harness guesses from the id's prefix, so set it only for an exception such as `claude-haiku-4-5`, see the [command spec](../specs/harness/command.md#reasoning) |
| `released` | Release date, from Epoch's `date` column. Full study only |
| `eci` | The model's [ECI](../glossary.md), a snapshot from Epoch's [CSV](https://epoch.ai/data/eci_scores.csv). Full study only |
| `max_tokens` | The model's own output limit, set only where the provider's default is lower, see [sampling](#sampling). Optional |
| `notes` | Anything a reader needs, such as a rate limit or an id to verify |

## Reasoning

- **Reasoning is a setting, not a given.** A model with thinking on is a different row from the same model with it off.
- **The proof of concept runs minimal.** Off where the provider allows, the lowest budget where it does not.
- **The full study runs a sweep.** Each model lists every setting it supports from one shared grid, and each one is its own row.

| Setting | Meaning |
|---|---|
| `off` | No thinking. The harness sends the provider's explicit off, never its default, see the [command spec](../specs/harness/command.md#reasoning) |
| `low`, `medium`, `high`, `max` | Effort levels, mapped to the provider's own setting: `reasoning_effort` for OpenAI, `thinking_level` for Gemini, `effort` for Claude, `reasoning` for OpenRouter. Where a model only takes a token budget, the harness picks one per level |
| `on` | Thinking the model won't let us change, such as DeepSeek R1 |

- **A model that cannot turn thinking off does not list `off`.** Its row lists its lowest setting, or `on` when nothing can be set. Otherwise a model that thinks by default would play its `off` row with thinking on.
- **`xhigh` is skipped** to keep the grid at five steps.
- **Tool choice follows the reasoning setting on Anthropic.** With thinking on, Claude takes only `auto`, so the solver uses it there and `any` elsewhere, see [each round](../specs/harness/solver.md#each-round). The value is in every sample's metadata and in the result row's `Setting`, and the [tool choice](../pilot/provider-checks.md#tool-choice) check prices the difference.
- **What a model keeps of its reasoning across turns is the provider's choice.** In the [rolling conversation](../pilot/provider-checks.md#rolling-conversation) check every provider keeps the text and the tool calls, but whether the model reads its own earlier reasoning next turn varies by provider and model. So that check is read per model, and the row's `notes` says what its provider keeps.

## Sampling

- **Temperature is the provider's default.** We never set it. It is the setting people deploy with, and some reasoning models refuse any other value. inspect writes the generate config into every log, so the value used is on record.
- **Max tokens is the model's own output limit.** There is no standard number across evals. The usual practice is a cap high enough that it never binds, so the cap can't make a choice for the model. Where a provider's default is lower, the harness sets `max_tokens` to the model's limit.
- **A reply cut off by the limit is a retry**, see the [retry rule](prompts.md#retry-rule). It is counted apart from other retries, so a cap problem can't pass as a model problem.
- **Cost is guarded elsewhere**, by `--limit` and the [cost per run](../pilot/provider-checks.md#cost-per-run) check, not by a low cap.

## Prompt caching

- **On by default and never switched off.** inspect marks the system prompt, the tools and the end of the prompt for Anthropic's cache, and OpenAI caches a repeated start of a prompt on its own. The harness never sets `cache_prompt`, see the [command spec](../specs/harness/command.md#reasoning).
- **It changes the bill, never the prompt.** A cached token is the same token at a lower price, so no score depends on it.
- **A fresh call each round is why it pays.** Round 20's prompt is round 19's plus one row, so all but the newest row can come from the cache. The notes sit below the record, so a changed note never spoils the rows above it.
- **Anthropic caches by content block.** A record sent as one growing block would only ever hit on the system prompt, and the record would be billed in full every round. So the solver sends the record one block per line to Anthropic models, see the [solver spec](../specs/harness/solver.md#each-round). Other providers match the start of the prompt whatever its blocks, so they get one block.
- **Cached tokens are counted apart.** inspect leaves them out of its input count, so the [cost table](../specs/analysis/tables.md#cost) prices them on their own and the [cost per run](../pilot/provider-checks.md#cost-per-run) check reports each model's cached share.
- **Batches do not fit.** A batch costs half as much, but each round needs the last round's reply, so a run is forty calls in a row and cannot be queued as one.
- **To verify:** whether Google caches a repeated start on the models in `configs/models/`.

## Trend plots

The full study plots the headline two ways, one point per model and setting:

- **Against release date** (`released`). Is the trait improving over time?
- **Against [ECI](../glossary.md)** (`eci`). Is it just general capability, or something separate?
- **Settings of one model are joined by a line.** ECI has one score per model, not per setting, so on the ECI plot a model's settings stack in a column. How tall that column is tells you how much reasoning matters.
- **Error bars** come from [scoring](../design/scoring.md#error-bars).
- **ECI is Epoch AI's**, under CC BY 4.0. Credit it on every plot. The values are typed into the models file by hand from the CSV, and the date they were read is passed to `paranoid analyse --eci-read-on` for the credit. The analysis never fetches them, see the [analysis command](../specs/analysis/command.md#results).

## Keys

inspect reads keys from the environment. Copy `.env.example` to `.env` and fill it in, see [running](running.md).

| Provider | Env var |
|---|---|
| Anthropic | `ANTHROPIC_API_KEY`, or `ANTHROPIC_AUTH_TOKEN` for an OAuth token |
| OpenAI | `OPENAI_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Jev | `TYPESAFE_API_KEY` |
| Timestral | None. Runs locally, see [providers](providers.md#timestral) |
| Baselines | None |

- **A Claude subscription works only if the plan gives API access.** inspect calls the Anthropic API with a console key, or with an OAuth token in `ANTHROPIC_AUTH_TOKEN`, which wins when both are set. A chat-only plan has neither.
- **Check a subscription before a held-out skin goes through it.** Three things, none verified yet:
  - That the plan neither keeps prompts nor trains on them. A held-out skin a provider trains on is no longer held out, see [who can see them](contamination.md#who-can-see-them).
  - That its rate limit covers the run. At twenty seeds and two skins a Claude row is 320 runs of at least forty calls each, so about 13,000 calls.
  - That a `--limit 2` run completes and its cost table shows cache reads, see [prompt caching](#prompt-caching).

## Concurrency and cost

- `--max-connections` per provider, see [running](running.md#cost-guard).
- Tokens per run come from the [pilot](../pilot/provider-checks.md#cost-per-run).
