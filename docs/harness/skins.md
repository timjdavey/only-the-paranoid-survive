# Skins

A skin is the story dressed over the engine, see [glossary](../glossary.md). This page is how a skin is written and where it lives. Why skins exist is in the [README](../../README.md#design).

## What a skin file holds

One TOML file per skin. Each field fills a part of the [system prompt](prompts.md#system-prompt) or the [tool text](prompts.md#tool-text).

| Field | What it is |
|---|---|
| `name` | Short id, used in log metadata |
| `channels` | Ten names. Which one leads is drawn per seed by the [ladder](../design/mechanics.md#the-ladder) |
| `intro` | Who the agent is and what it runs |
| `rules` | The budget of 100 points, the ten channels by name, and that points are whole numbers adding up to 100 |
| `how_points_earn` | What a point buys and what a reading means |
| `reading_note` | How a small spend gives a rough reading |
| `ask` | The record is below, place this round's points with the tool |
| `tool_name` | The tool's name as the model sees it |
| `tool_text` | The tool's description |
| `bad_sum` | The retry message for a sum that is not 100, with a `{sum}` slot |
| `no_call` | The retry message for a reply with no tool call |
| `question` | Jev's choice question, see [adapters](adapters.md#jev) |

- **Numbers come from the engine, never the skin.** A skin names things and sets the scene. It never states levels, trends or history.
- **Each skin words the [frame](../glossary.md) its own way.** A held-out skin should read nothing like the example skin, in its rules, ask and tool text as much as its story. The published wording is then only the example skin's, see [contamination](contamination.md#why).
- **One skin per headline.** Skins are never averaged, see [scoring](../design/scoring.md#spread).

## Where skins live

| Skin | Where | Public |
|---|---|---|
| `example` | `src/paranoid/skins/example.toml` | Yes. The one in published logs |
| The held-out skins | A private repo, mounted at `PARANOID_SKINS` | No |

- `load_skins(path)` reads every TOML file in the folder. With `PARANOID_SKINS` unset only `example` loads.
- The private repo holds two folders and nothing else: `skins/`, a plain folder of TOML files, and `seeds/`, the held-out seeds. `PARANOID_SKINS` and `PARANOID_SEEDS` point at them. See [contamination](contamination.md#two-seed-sets).

## Lint

- Every field is linted on load against the [banned words](prompts.md#banned-words).
- Every rendered prompt is checked for the facts in [what every skin must say](prompts.md#what-every-skin-must-say).
- A skin that fails to lint does not load. There is no override flag.
- The test suite renders the full prompt for every loaded skin and lints the result, so the record and tool text are linted too.

## Canary

Every published file that holds prompt text carries the canary GUID, see [contamination](contamination.md#canary). The prompt itself does not, so the model never sees it.
