# Skins

A skin is the story dressed over the engine, see [glossary](../glossary.md). This page is how a skin is written and where it lives. Why skins exist is in the [README](../../README.md#design).

## What a skin file holds

One TOML file per skin. Each field fills a bracket in the [system prompt](prompts.md#system-prompt-skeleton).

| Field | What it is |
|---|---|
| `name` | Short id, used in log metadata |
| `channels` | Ten names. Which one leads is drawn per seed by the [ladder](../design/mechanics.md#the-ladder) |
| `intro` | Who the agent is and what it runs |
| `how_points_earn` | What a point buys and what a reading means |
| `reading_note` | How a small spend gives a rough reading |
| `question` | Jev's choice question, see [adapters](adapters.md#jev) |

- **Numbers come from the engine, never the skin.** A skin names things and sets the scene. It never states levels, trends or history.
- **One skin per headline.** Skins are never averaged, see [scoring](../design/scoring.md#spread).

## Where skins live

| Skin | Where | Public |
|---|---|---|
| `example` | `src/paranoid/skins/example.toml` | Yes. The one in published logs |
| The held-out skins | A private repo, mounted at `PARANOID_SKINS` | No |

- `load_skins(path)` reads every TOML file in the folder. With `PARANOID_SKINS` unset only `example` loads.
- The private repo is a plain folder of TOML files and nothing else.

## Lint

- Every field is linted on load against the [banned words](prompts.md#banned-words).
- A skin that fails to lint does not load. There is no override flag.
- The test suite renders the full prompt for every loaded skin and lints the result, so the fixed text is linted too.

## Canary

Every published file that holds prompt text carries the canary GUID, see [privacy](../privacy.md#canary). The prompt itself does not, so the model never sees it.
