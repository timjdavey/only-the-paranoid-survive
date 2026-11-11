# Skins

A skin is the story dressed over the engine, see [glossary](../glossary.md). This page is what a skin file holds and where it lives. How to write a good one is in [writing a skin](writing-a-skin.md). Why skins exist is in the [README](../../README.md#design). What the code must do with one is in the [skins spec](../specs/skins/README.md).

## What a skin file holds

One TOML file per skin. Each field fills a part of the [system prompt](prompts.md#system-prompt) or the [tool text](prompts.md#tool-text).

| Field | What it is |
|---|---|
| `name` | Short id, the file stem, used in log metadata. Results tables publish it, so a held-out skin's name is opaque, never a word from its story |
| `channels` | One name per channel, ten in the study. Which one leads is drawn per seed by the [ladder](../design/mechanics.md#the-ladder) |
| `intro` | Who the agent is and what it runs |
| `rules` | The ten channels by name, and that the split is in whole percentages adding up to 100 |
| `how_points_earn` | What a percent of the budget buys, what a reading means, and that a small spend gives a rough reading |
| `ask` | The record is below, place this round's points with the tool |
| `tool_name` | The tool's name as the model sees it |
| `tool_text` | The tool's description |
| `bets_name` | The name of the tool's one parameter as the model sees it. `bets` in the example skin. Each skin picks its own, so no parameter name is shared across skins |
| `bets_text` | The description of that parameter, the ten whole percentages in channel order |
| `bad_call` | The retry message for any bets the engine rejects. One generic message, no slots |
| `no_call` | The retry message for a reply with no tool call |
| `notes_name`, `notes_text` | The notes tool's name and description, see [tool text](prompts.md#tool-text) |
| `compute_name`, `compute_text` | The compute tool's name and description |
| `question` | Jev's choice question, see [providers](providers.md#jev). Linted like every other skin field |
| `round_word`, `bet_word`, `level_word`, `output_word` | The four words that head the [record](prompts.md#user-message): the round column, the suffix of each bet column, the suffix of each level column, the output column. `round`, `bet`, `level` and `output` in the example skin. Each skin picks its own, so no header is shared across skins, see [contamination](contamination.md#why) |

- **Numbers come from the engine, never the skin.** A skin names things and sets the scene. It never states levels, trends or history.
- **Each skin words the [frame](../glossary.md) its own way.** A held-out skin should read nothing like the example skin, in its rules, ask, tool text and column words as much as its story. The published wording is then only the example skin's, see [contamination](contamination.md#why).
- **One skin per headline.** Skins are never averaged, see [scoring](../design/scoring.md#spread).

## Where skins live

| Skin | Where | Public |
|---|---|---|
| `example` | `src/paranoid/skins/example.toml` | Yes. The one in published logs |
| The held-out skins | A private repo, mounted at `PARANOID_SKINS` | No |

- `load_skins(path)` reads every TOML file in the folder, and `load_skin(path)` reads one. With `PARANOID_SKINS` unset only `example` loads. See [skin](../specs/skins/skin.md#load_skins).
- The private repo holds two folders and nothing else: `skins/`, a plain folder of TOML files, and `seeds/`, the held-out seeds. `PARANOID_SKINS` and `PARANOID_SEEDS` point at them. See [contamination](contamination.md#two-seed-sets).

## Lint

- Every field the model reads is linted on load against the [banned words](prompts.md#banned-words). `name` is the one field it never reads, so it is the one field not linted.
- Every rendered prompt is checked for the facts in [what every skin must say](prompts.md#what-every-skin-must-say).
- A skin that fails to lint does not load. There is no override flag.
- The test suite renders the full prompt for every loaded skin and lints the result, so the record and tool text are linted too.

## Canary

Every published file that holds prompt text carries the canary GUID, see [contamination](contamination.md#canary). Held-out skins carry it too, so a file that ever leaks is filtered. The prompt itself does not, so the model never sees it.
