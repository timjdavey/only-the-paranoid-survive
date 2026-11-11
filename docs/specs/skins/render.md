# Render

## Purpose

`render_system_prompt` and `render_record` turn a skin and a record into the two texts the harness sends each round, see [placement](../../harness/prompts.md#placement). `prompt_hash` fingerprints every word the model reads from a skin, and the layout it reads them in, so a log can prove which wording it played. The renderer joins, it never writes a word of its own. `render_record` is the one place the record becomes text, so no engine word reaches a model.

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
- **Nothing is substituted.** The skin's text already holds the channel names, the number 100 and the tool name. The [lint](lint.md#frame-facts) checks they are there.
- **The same skin renders the same string on every call**, on every machine. The prompt is stable across rounds, which is why it is the system prompt, see [placement](../../harness/prompts.md#placement).

### Record

`render_record(skin, record)` writes the record as CSV. The engine holds the rows and renders nothing, see [record](../engine/game.md#record). The CSV is the whole user message, which the harness sends as is, see [user message](../../harness/prompts.md#user-message).

- **The header** is `{round_word},{name}_{bet_word} × channels,{name}_{reading_word} × channels`, with the skin's channel names in channel index order. With the example skin's words that reads `week,<name>_sent…,<name>_price…`.
- **One row per round played**, in round order: the round as an int, each bet as an int, then each reading with exactly one decimal and a `None` reading as an empty field. There is no output column, as a bet is paid its reading and the agent can add them up, see [what the agent sees](../../design/mechanics.md#what-the-agent-sees). A value that rounds to zero from below is written `0.0`, never `-0.0`.
- **Rows end with `\n`**, the last included. An empty record renders the header line only, which is what round 1 sends. A record a baseline pre-filled renders the same way, see [starting part way](../engine/game.md#starting-part-way).
- **Example**, a four-channel skin with the example words: `week,a_sent,b_sent,c_sent,d_sent,a_price,b_price,c_price,d_price\n1,100,0,0,0,61.2,,,\n`.
- **A row whose bets do not fit the skin's channels** raises `ValueError`. An empty record cannot tell, so the harness checks the skin against the config when the task is built, see [task settings](../harness/task.md#task-settings).
- **The column words are the skin's.** `round`, `bet` and `reading` are engine words, and a header every skin shared would mark the benchmark under any story, see [why](../../harness/contamination.md#why). So each skin picks its own, the lint checks them, and `prompt_hash` covers them.

### Prompt hash

- **`prompt_hash(skin)`** is the first 12 hex characters of the SHA-256 of a canonical JSON string: an object with the keys `render_version`, `system`, `channels`, `tool_name`, `tool_text`, `bets_name`, `bets_text`, `bad_call`, `no_call`, `notes_name`, `notes_text`, `notes_param`, `compute_name`, `compute_text`, `compute_param`, `question`, `round_word`, `bet_word` and `reading_word`, sorted keys, no whitespace, `ensure_ascii` off, UTF-8. `render_version` is `RENDER_VERSION`, `system` is `render_system_prompt(skin)`, `channels` is the list of names, the rest are the fields of the same name.
- **It covers every word the model can read from a skin** and nothing else. `name` is not in it, so renaming a file does not change the hash, and the record is not in it, as the record changes every round and the log holds it anyway.
- **`RENDER_VERSION` covers the layout.** It goes up by one whenever the joins on this page, the columns or decimals of the record, or the shape of either text change. So a hash change always means the model read something different, even when no skin word moved, and `engine_hash` stays about the world.
- **Same skin, same hash**, across Python versions and machines. Two skins that differ in any covered field differ in hash.
- **The harness logs it as `prompt_hash`** beside `engine_hash`, see [prompts](../../harness/prompts.md) and [inspect](../../harness/inspect.md#the-mapping). Changing a word changes the study, and the hash is how a reader can tell.

## Invariants

- `render_system_prompt(skin)` equals `intro`, `rules`, `how_points_earn` and `ask` joined by `"\n\n"`, in that order, and holds no other field.
- `render_system_prompt(skin).count("\n\n") >= 3` and the string neither starts nor ends with whitespace.
- `render_record(skin, record).count("\n") == len(record) + 1`.
- `render_record(skin, Record())` is one line, and the line holds each channel name twice and each column word.
- `render_record` writes no word that is not a skin field, a digit, a separator or a newline.
- `prompt_hash(skin)` is 12 lowercase hex characters and is equal for equal skins.

## Not decided

- **Whether a second skin field should go in the user message.** Today the user message is the CSV and nothing else. A saved note is appended as a second content block of the user message, the agent's own text and not the skin's, see [notes](../harness/solver.md#notes). If a cell ever needs skin words there, this page gets a `render_user_message` and the hash covers it.
