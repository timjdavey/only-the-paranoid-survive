# Skins spec

The skins layer dresses the engine in a story. A skin is one TOML file: the names of the ten channels and the text that words the [frame](../../glossary.md) for the agent. The layer loads skins, renders the system prompt and the record in a skin's words, hashes the result, and lints everything the model will read. It imports the engine and the standard library only, and knows nothing about inspect_ai or any model. Why skins exist is in the [README](../../../README.md#design), how they are written is in [skins](../../harness/skins.md), and what every prompt must say is in [prompts](../../harness/prompts.md).

## Pages

| Page | What it specifies |
|---|---|
| [skin](skin.md) | `Skin`, its fields and validation, the TOML file, `load_skin`, `load_skins`, where the example skin lives |
| [render](render.md) | `render_system_prompt`, `render_record`, `prompt_hash`, `RENDER_VERSION` |
| [lint](lint.md) | `BANNED_WORDS`, `PREFIXES`, `WHOLE_NUMBER_PHRASES`, `lint_text`, `lint`, `LintError`, the frame facts, `CANARY` |
| [tests](tests.md) | Every test the skins suite runs, with the page it checks |

## Exports

`paranoid.skins` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#four-layers).

| Name | Kind | Page |
|---|---|---|
| `Skin`, `SkinError` | Frozen dataclass and the error its construction and loading raise | [skin](skin.md) |
| `load_skin`, `load_skins` | `(Path) -> Skin` and `(Path | None) -> Mapping[str, Skin]` | [skin](skin.md) |
| `render_system_prompt`, `render_record` | `(Skin) -> str` and `(Skin, Record) -> str` | [render](render.md) |
| `prompt_hash`, `RENDER_VERSION` | `(Skin) -> str`, the hash a log carries, and the layout version it covers | [render](render.md) |
| `lint`, `lint_text`, `LintError` | The lint and its error, a `SkinError` | [lint](lint.md) |
| `BANNED_WORDS`, `PREFIXES`, `WHOLE_NUMBER_PHRASES` | The lint's word lists, pinned by the test suite | [lint](lint.md) |
| `CANARY` | The canary line, as a string | [lint](lint.md#canary) |

## Modules

    src/paranoid/skins/
      __init__.py    the exports above, nothing else
      skin.py        Skin, SkinError
      load.py        load_skin, load_skins
      render.py      RENDER_VERSION, render_system_prompt, render_record, prompt_hash
      lint.py        BANNED_WORDS, PREFIXES, WHOLE_NUMBER_PHRASES, LintError, lint_text, lint
      canary.py      CANARY
      example.toml   the example skin, shipped as package data

- **Loading is its own module** so the imports run one way: `load` imports `lint`, `lint` imports `render`, `render` imports `skin`. `skin.py` imports nothing of its own layer.
- Nothing outside `__init__.py` is public. Tests import from `paranoid.skins` only, plus `paranoid.engine` for records.
- The only imports are `paranoid.engine` and the standard library. TOML is read with `tomllib`. `import-linter` enforces it, see [layout](../../harness/layout.md#four-layers).

## What the harness reads

The harness takes a `Skin` from `load_skins` and uses it in five places, see [inspect](../../harness/inspect.md#the-round-loop).

| Harness part | Reads |
|---|---|
| System prompt | `render_system_prompt(skin)` |
| User message | `render_record(skin, record)` |
| The `submit` tool | `skin.tool_name`, `skin.tool_text`, `skin.bad_call`, `skin.no_call` |
| The Jev provider | `skin.question`, with `skin.channels` as the options, see [providers](../../harness/providers.md#jev) |
| Log metadata | `skin.name`, `prompt_hash(skin)` |

- **The harness checks `len(skin.channels) == config.channels` before round 1.** A skin always has ten names and the default config ten channels, but a pilot config can have fewer. An empty record cannot tell, so without the check a mismatch fails at round 2, see [record](render.md#record).

## Conventions

- **Channel names are in channel index order.** Channel `c` is `skin.channels[c]` in every prompt, header and tool call. Which index leads is drawn per seed by the [ladder](../engine/tape.md#the-ladder), so a skin never knows its leader.
- **A skin holds words, never numbers from the engine.** No level, trend, onset or history. The number 100 and the count of ten are the frame's, see [skins](../../harness/skins.md#what-a-skin-file-holds).
- **Text is stored stripped, in NFC, with `\n` newlines.** Rendering adds only the joins on the [render](render.md) page, so the same file hashes the same on every machine.
- **Everything the model reads passes through `lint`.** A skin that fails to lint does not load, and there is no override, see [lint](lint.md).
- **The skin is private, the layer is public.** The code, the example skin and these pages are published. Held-out skins live in the private repo, see [contamination](../../harness/contamination.md).
