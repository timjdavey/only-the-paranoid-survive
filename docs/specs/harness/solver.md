# Solver

## Purpose

`round_loop` plays one run: each round it renders a fresh system prompt and record, asks the model for one call to the skin's tool, plays the bets through the engine and appends the row. `submit` is that tool. The retry rule and the two pilot tools live here too. The design is in [the round loop](../../harness/inspect.md#the-round-loop), [prompts](../../harness/prompts.md) and [tools](../../design/interface.md#tools).

## Interface

```python
class RoundError(RuntimeError):      # max_tries generate calls in one round, none valid
    round: int

@solver
def round_loop(
    skin: Skin,
    tools: str = "none",             # as the task arg
    tool_choice: str = "forced",     # "forced" or "auto"
    max_tries: int = 10,
    notes_cap: int = 2000,           # characters, pilot to confirm
    rolling: bool = False,           # keep the conversation across rounds, pilot only
) -> Solver

@tool
def submit(skin: Skin) -> Tool       # execute(bets: list[int]) -> str
@tool
def notes() -> Tool                  # execute(text: str) -> str
@tool
def compute() -> Tool                # execute(code: str) -> str
```

## Behaviour

### Each round

1. **Fill the store** if `len(store.rows) == 0` and `store.scenario == ""`: copy the metadata in and play the warm up, see [store](task.md#store).
2. **Reset the messages.** `state.messages` becomes exactly: a system message of `render_system_prompt(skin)`, then a user message of `render_record(skin, store.record())`. With `notes` on and `store.notes` non-empty, the user message has a second content block holding the notes, see [notes](#notes). With `rolling` on the messages are not reset, see [rolling](#rolling).
3. **Set the tools.** `state.tools` is `[tool_with(submit(skin), name=skin.tool_name, description=skin.tool_text)]`, then `notes()` and `compute()` when asked for. The submit tool is always first, so a provider finds it at `tools[0]`, see [providers](providers.md#shared-behaviour).
4. **Set the tool choice.** `ToolFunction(name=skin.tool_name)` when `tool_choice` is `"forced"`, `"auto"` otherwise. `"auto"` is for providers that refuse a forced tool with thinking on, see [reasoning](../../harness/models.md#reasoning). The command picks it per model row, see [command](command.md#tool-choice).
5. **Try until the round is played**, see [tries](#tries).
6. **Repeat** until `store.round() > store.config().rounds`. Then return the state.

### Tries

Each try is one `generate(state, tool_calls="single")`, so inspect runs whatever tools the reply called and appends their results. The solver then reads the store.

- **Before the try** the solver sets `store.open = True`. A valid submit sets it back to false, so the solver knows the round was played by the store, not by parsing the reply.
- **A valid call** ends the round. The try count for the round is appended to `store.tries`.
- **A reply with no call to the skin's tool**, whatever else it called or said, is a no call: `store.no_calls += 1` and a user message of `skin.no_call` is appended. A reply whose `stop_reason` is `"max_tokens"` also adds one to `store.cut_offs`, see [sampling](../../harness/models.md#sampling).
- **A call the engine rejected** already carries `skin.bad_call` in its tool message, and the tool counted it, see [submit](#submit). The solver appends nothing more.
- **Within a round the messages grow** with each reply and its retry message, so the model sees what it got wrong. Across rounds nothing survives, see step 2.
- **After `max_tries` tries** with no valid call the solver raises `RoundError(round)`. inspect plays the sample again once, and a second failure leaves the sample with no score, see [task settings](task.md#task-settings). The default is ten, fixed by the [retry rule](../../harness/prompts.md#retry-rule).

### Submit

`submit(skin)` is the engine's `Game.play` behind a tool. The model sees it under the skin's name and text, see [tool text](../../harness/prompts.md#tool-text).

- **`execute(bets)`** reads `store_as(RunStore)`, builds `store.game()`, and calls `game.play(bets)`.
- **The bets go through untouched.** The harness does no coercion. A list of JSON whole numbers passes. `10.0`, `"10"` or `true` fail the engine's `shape` check, see [bets](../engine/game.md#bets).
- **On `BetError`** the tool adds one to `store.bad_calls` and raises `ToolError(skin.bad_call)`. The engine's own message never reaches the model. The round, the record and `store.open` are unchanged.
- **When `store.open` is false** the call raises `ToolError(skin.bad_call)` and counts as a bad call, so a second submit in one reply cannot play two rounds.
- **On success** the tool appends a `StoredRow` from the `Reading`, sets `store.open = False`, and returns the header line and the last line of `store.record().to_csv(skin.channels)`. That is the round just played in the record's own shape, with no words from the harness.

### Notes

Pilot only, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute).

- **`notes(text)`** replaces `store.notes` with the first `notes_cap` characters of `text` and returns the text as stored. Nothing is appended, nothing is kept from an earlier call.
- **Next round** the stored text comes back as a second content block on the user message, after the record, never as an assistant message. A tool message with no tool call before it is rejected by the Anthropic API, and an assistant message would read as the agent's own words.
- **Length is logged** by the store itself, as `len(store.notes)`.
- **A reply that calls `notes` and not the skin's tool is a no call**, see [tries](#tries).

### Compute

Pilot only. Needs `uv sync --extra sandbox` and Docker.

- **Before each round** the solver writes `store.record().to_csv(skin.channels)` to `record.csv` in the sandbox's working directory, so the code sees the record and nothing else.
- **`compute(code)`** runs `python3 -I -c <code>` in the sandbox with a 30 second timeout, and returns stdout then stderr, truncated to 4000 characters. A timeout returns the text `timeout`.
- **The sandbox has no network.** `compose.yaml` sets `network_mode: none` and mounts nothing from the host, so the code can reach neither the engine nor a seed.

### Rolling

Pilot only, see [rolling conversation](../../pilot/provider-checks.md#rolling-conversation).

- **With `rolling` on** step 2 runs on round 1 only. Later rounds append a user message of the new record row, the header line and the last line of the CSV, and keep every earlier message. Nothing is compacted.
- **Everything else is the same**, so the only difference in the log is the message list.

## Invariants

- A round ends only on a valid call to the skin's tool. The harness never places bets for the agent.
- `sum(store.tries) == ` the number of generate calls in the run.
- `len(store.tries) == len(store.rows) − store.warm_up_rounds` when a run ends without error.
- Replaying `store.rows` as bets on `store.tape()` with `Game` gives the same readings and outputs, so the log is enough to check a run.
- With `rolling` off, every round starts with exactly two messages, or two messages with two content blocks on the second when notes are on.
- `store.open` is false whenever the solver is not inside a try.

## Tests

See [tests](tests.md#solver).

## Open

- `notes_cap` is **pilot to confirm**, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute).
- Whether `rolling` runs need their own `max_tokens`, as the conversation grows with the square of the game length, see [rejected](../../design/interface.md#rejected).
