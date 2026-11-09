# Render

## Purpose

`render_system_prompt` and `render_record` turn a skin and a record into the two texts the harness sends each round, see [placement](../../harness/prompts.md#placement). `prompt_hash` fingerprints every word the model reads from a skin, so a log can prove which wording it played. The renderer joins, it never writes a word of its own.

## Interface

```python
def render_system_prompt(skin: Skin) -> str
def render_record(skin: Skin, record: Record) -> str
def prompt_hash(skin: Skin) -> str
```

## Behaviour

### System prompt

Four parts, in this order, each a skin field, see [system prompt](../../harness/prompts.md#system-prompt).

| Part | Text |
|---|---|
| Intro | `skin.intro` |
| Rules | `skin.rules` |
| How points earn | `skin.how_points_earn`, one space, `skin.reading_note` |
| Ask | `skin.ask` |

- **Parts are joined by one blank line**, `"\n\n"`. There is no leading or trailing newline. Fields are already stripped, see [skin](skin.md#validation-on-construction), so the join is the only whitespace the renderer adds.
- **Nothing is substituted.** The skin's text already holds the ten names, the number 100 and the tool name. The [lint](lint.md#frame-facts) checks they are there.
- **The same skin renders the same string on every call**, on every machine. The prompt is stable across rounds, which is why it is the system prompt, see [placement](../../harness/prompts.md#placement).

### Record

- **`render_record(skin, record)`** returns `record.to_csv(skin.channels)`, see [record](../engine/game.md#record). The header is `round,<name>_bet × 10,<name>_level × 10,output` with the skin's names in channel index order, and one row per round played.
- **Round 1 is the header alone**, as the record is empty. A record a baseline pre-filled renders the same way, see [starting part way](../engine/game.md#starting-part-way).
- **A record whose rows do not fit ten channels** raises `ValueError` from the engine. The skins layer adds no check of its own.
- **The CSV is the whole user message.** The harness sends it as is, see [user message](../../harness/prompts.md#user-message).

### Prompt hash

- **`prompt_hash(skin)`** is the first 12 hex characters of the SHA-256 of a canonical JSON string: an object with the keys `system`, `channels`, `tool_name`, `tool_text`, `bad_call`, `no_call` and `question`, sorted keys, no whitespace, `ensure_ascii` off, UTF-8. `system` is `render_system_prompt(skin)`, `channels` is the list of names, the rest are the fields of the same name.
- **It covers every word the model can read from a skin** and nothing else. `name` is not in it, so renaming a file does not change the hash, and the record is not in it, as the record changes every round and the log holds it anyway.
- **Same skin, same hash**, across Python versions and machines. Two skins that differ in any covered field differ in hash.
- **The harness logs it as `prompt_hash`** beside `engine_hash`, see [prompts](../../harness/prompts.md) and [inspect](../../harness/inspect.md#the-mapping). Changing a word changes the study, and the hash is how a reader can tell.

## Invariants

- `render_system_prompt(skin)` contains `intro`, `rules`, `how_points_earn`, `reading_note` and `ask`, each exactly once, in that order, and no other field.
- `render_system_prompt(skin).count("\n\n") >= 3` and the string neither starts nor ends with whitespace.
- `render_record(skin, record).count("\n") == len(record) + 1`.
- `render_record(skin, Record())` is one line, and the line holds each channel name twice.
- `prompt_hash(skin)` is 12 lowercase hex characters and is equal for equal skins.

## Tests

See [tests](tests.md#render).

## Open

- **Whether a second skin field should go in the user message.** Today the user message is the CSV and nothing else. The notepad pilot cell appends a tool message, not skin text, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute). If a cell ever needs skin words there, this page gets a `render_user_message` and the hash covers it.
