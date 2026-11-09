# Render

## Purpose

`render_system_prompt` and `render_record` turn a skin and a record into the two texts the harness sends each round, see [placement](../../harness/prompts.md#placement). `prompt_hash` fingerprints every word the model reads from a skin, and the layout it reads them in, so a log can prove which wording it played. The renderer joins, it never writes a word of its own.

## Interface

```python
RENDER_VERSION: int = 1                     # goes up by one when the layout of either text changes

def render_system_prompt(skin: Skin) -> str
def render_record(skin: Skin, record: Record) -> str
def prompt_hash(skin: Skin) -> str
```

## Behaviour

### System prompt

Four parts, in this order, each one skin field, see [system prompt](../../harness/prompts.md#system-prompt).

| Part | Text |
|---|---|
| Intro | `skin.intro` |
| Rules | `skin.rules` |
| How points earn | `skin.how_points_earn` |
| Ask | `skin.ask` |

- **Parts are joined by one blank line**, `"\n\n"`. There is no leading or trailing newline. Fields are already stripped, see [skin](skin.md#validation-on-construction), so the join is the only whitespace the renderer adds.
- **Nothing is substituted.** The skin's text already holds the ten names, the number 100 and the tool name. The [lint](lint.md#frame-facts) checks they are there.
- **The same skin renders the same string on every call**, on every machine. The prompt is stable across rounds, which is why it is the system prompt, see [placement](../../harness/prompts.md#placement).

### Record

- **`render_record(skin, record)`** returns `record.to_csv(skin.channels)`, see [record](../engine/game.md#record). The header is `round,<name>_bet × 10,<name>_level × 10,output` with the skin's names in channel index order, and one row per round played.
- **Round 1 is the header alone**, as the record is empty. A record a baseline pre-filled renders the same way, see [starting part way](../engine/game.md#starting-part-way).
- **A record whose rows do not fit ten channels** raises `ValueError` from the engine. The skins layer adds no check of its own. An empty record cannot tell, so the harness checks the skin against the config before round 1, see [what the harness reads](README.md#what-the-harness-reads).
- **The CSV is the whole user message.** The harness sends it as is, see [user message](../../harness/prompts.md#user-message).

### Prompt hash

- **`prompt_hash(skin)`** is the first 12 hex characters of the SHA-256 of a canonical JSON string: an object with the keys `render_version`, `system`, `channels`, `tool_name`, `tool_text`, `bad_call`, `no_call` and `question`, sorted keys, no whitespace, `ensure_ascii` off, UTF-8. `render_version` is `RENDER_VERSION`, `system` is `render_system_prompt(skin)`, `channels` is the list of names, the rest are the fields of the same name.
- **It covers every word the model can read from a skin** and nothing else. `name` is not in it, so renaming a file does not change the hash, and the record is not in it, as the record changes every round and the log holds it anyway.
- **`RENDER_VERSION` covers the layout.** It goes up by one whenever the joins on this page, the columns or decimals of `to_csv`, or the shape of either text change. So a hash change always means the model read something different, even when no skin word moved, and `engine_hash` stays about the world.
- **Same skin, same hash**, across Python versions and machines. Two skins that differ in any covered field differ in hash.
- **The harness logs it as `prompt_hash`** beside `engine_hash`, see [prompts](../../harness/prompts.md) and [inspect](../../harness/inspect.md#the-mapping). Changing a word changes the study, and the hash is how a reader can tell.

## Invariants

- `render_system_prompt(skin)` equals `intro`, `rules`, `how_points_earn` and `ask` joined by `"\n\n"`, in that order, and holds no other field.
- `render_system_prompt(skin).count("\n\n") >= 3` and the string neither starts nor ends with whitespace.
- `render_record(skin, record).count("\n") == len(record) + 1`.
- `render_record(skin, Record())` is one line, and the line holds each channel name twice.
- `prompt_hash(skin)` is 12 lowercase hex characters and is equal for equal skins.

## Tests

See [tests](tests.md#render).

## Open

- **The record's column words are a fingerprint.** `round`, `_bet`, `_level` and `output` head every skin's record, whatever its story, and `level` and `output` are engine words. [Contamination](../../harness/contamination.md#why) holds that shared frame text lets a model spot the benchmark under any story. The fix is four more skin fields that `to_csv` takes as its column words, hashed with the rest, which is an engine spec change too. Decide before the first held-out skin is written.
- **Whether a second skin field should go in the user message.** Today the user message is the CSV and nothing else. The notepad pilot cell appends a tool message, not skin text, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute). If a cell ever needs skin words there, this page gets a `render_user_message` and the hash covers it.
