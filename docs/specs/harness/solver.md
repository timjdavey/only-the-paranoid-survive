# Solver

## Purpose

`round_loop` plays one run: each round it renders a fresh system prompt and record, asks the model for one call to the skin's tool, plays the bets through the engine and appends the row. `submit` is that tool. The retry rule, giving up, the notes and compute tools and the pilot's rolling conversation live here too. The design is in [the round loop](../../harness/inspect.md#the-round-loop), [prompts](../../harness/prompts.md) and [tools](../../design/interface.md#tools).

## Interface

```python
@solver
def round_loop(
    skin: Skin,
    tools: str = "notes,compute",    # as the task arg
    tool_choice: str | None = None,  # "any", "auto", or None to decide from the model, see below
    max_tries: int = 10,
    notes_cap: int = 2000,           # characters, pilot to confirm
    rolling: bool = False,           # keep the conversation across rounds, pilot only
) -> Solver

def tool_choice_for(api: str, config: GenerateConfig) -> Literal["any", "auto"]

BLOCK_CACHE_APIS = ("anthropic",)    # apis whose prompt cache matches by content block
def record_blocks(text: str) -> list[str]   # the record cut after every line end

@tool
def submit(skin: Skin) -> Tool       # one parameter, named skin.bets_name, a list of ints. Returns str
@tool
def notes() -> Tool                  # execute(text: str) -> str
@tool
def compute() -> Tool                # execute(code: str) -> str
```

## Behaviour

### Each round

1. **Fill the store** if `store.scenario == ""`: copy the metadata in and play the warm up, see [store](task.md#store).
2. **Reset the messages.** `state.messages` becomes exactly: a system message of `render_system_prompt(skin)`, then a user message of `render_record(skin, store.record())`, as one content block or cut by [record blocks](#record-blocks). With `notes` on and `store.notes` non-empty, the user message has one more content block after the record, holding the notes, see [notes](#notes). With `rolling` on the messages are not reset, see [rolling](#rolling).
3. **Set the tools.** `state.tools` is `[submit(skin)]`, which carries the skin's `tool_name`, `tool_text`, `bets_name` and `bets_text`, see [submit](#submit), then `notes()` as `skin.notes_name` with `skin.notes_text` and `compute()` as `skin.compute_name` with `skin.compute_text`, when `tools` asks for them. Every word on every tool is the skin's, see [tool text](../../harness/prompts.md#tool-text). The submit tool is always first, so a provider finds it at `tools[0]`, see [providers](providers.md#shared-behaviour).
4. **Set the tool choice.** `"any"` for `"any"`, so the reply must call some tool, and `"auto"` otherwise. A `ToolFunction` naming the skin's tool is never used: it would stop the model calling notes or compute first. With `tool_choice=None` the solver calls `tool_choice_for(get_model().api, get_model().config)` on round 1 and writes the answer to `store.tool_choice` and to `state.metadata["tool_choice"]`, so the log says which it was and the analysis reads it without the store, see [result key](../analysis/runs.md#result-key). The rule: `"auto"` when the api is `"anthropic"` and the config sets `reasoning_effort` or `reasoning_tokens`, else `"any"`. Claude rejects `any` with thinking on, see [reasoning](../../harness/models.md#reasoning). Deciding here, not on the command line, means `inspect eval paranoid --model anthropic/<model>` works as typed.
5. **Try until the round is played**, see [tries](#tries).
6. **Repeat** until `store.round() > store.config().rounds`, or the run gave up. Then return the state.

### Record blocks

How the record is cut into content blocks, and nothing else. The text is the same either way, so this moves the bill and never the prompt, see [prompt caching](../../harness/models.md#prompt-caching).

- **`record_blocks(text)`** cuts the record after every line end and returns the pieces in order: the header line, then one piece per row. Nothing is added, dropped or stripped.
- **Used when `get_model().api` is in `BLOCK_CACHE_APIS`.** Each piece is one text block of the user message. Any other api gets the record as one block.
- **Why.** Anthropic's cache matches by content block, and a record sent as one growing block never matches, see [prompt caching](../../harness/models.md#prompt-caching).
- **The notes block stays last**, after every record block, so a changed note leaves the rows above it cached.
- **inspect places the cache marks.** The solver sets none, and `cache_prompt` stays at inspect's default, see [reasoning](command.md#reasoning).
- **With `rolling` on** every user message that holds the record is cut the same way.

### Tries

Each try is one `generate(state, tool_calls="single")`, so inspect runs whatever tools the reply called and appends their results. The solver then reads the store.

- **Before the try** the solver sets `store.awaiting_submit = True`. A valid submit sets it back to false, so the solver knows the round was played by the store, not by parsing the reply.
- **A valid call** ends the round. The try count for the round is appended to `store.tries`.
- **A reply with no call to the skin's tool**, whatever else it called or said, is a no call: `store.no_calls += 1` and a user message of `skin.no_call` is appended. A reply whose `stop_reason` is `"max_tokens"` also adds one to `store.cut_offs`, see [sampling](../../harness/models.md#sampling).
- **A call the engine rejected** already carries `skin.bad_call` in its tool message, and the tool counted it, see [submit](#submit). The solver appends nothing more.
- **Within a round the messages grow** with each reply and its retry message, so the model sees what it got wrong. Across rounds nothing survives, see step 2.
- **After `max_tries` tries** with no valid call the solver gives up: it appends the try count to `store.tries`, sets `store.gave_up = True` and `store.awaiting_submit = False`, and returns the state with the rounds left unplayed. The sample is still scored, as the Uniform baseline on that seed, see [giving up](scorer.md#giving-up). Nothing is raised, so an error in the log always means infrastructure, never the model. The default is ten, fixed by the [retry rule](../../harness/prompts.md#retry-rule).

### Submit

`submit(skin)` is the engine's `Game.play` behind a tool. The model sees it under the skin's name and text, see [tool text](../../harness/prompts.md#tool-text).

- **The tool is built from the skin.** Its name is `skin.tool_name`, its description `skin.tool_text`, and it has one required parameter named `skin.bets_name`, an array of integers, described by `skin.bets_text`. So no word on the tool is the harness's, and no two skins need share one, see [contamination](../../harness/contamination.md#why).
- **`execute`** takes that one argument by the skin's name, reads `store_as(RunStore)`, builds `store.game()`, and calls `game.play(bets)`. A call with any other argument name, or with more than one, is a bad call.
- **The bets go through untouched.** The harness does no coercion. A list of JSON whole numbers passes. `10.0`, `"10"` or `true` fail the engine's `shape` check, see [bets](../engine/game.md#bets).
- **On `BetError`** the tool adds one to `store.bad_calls` and raises `ToolError(skin.bad_call)`. The engine's own message never reaches the model. The round, the record and `store.awaiting_submit` are unchanged.
- **When `store.awaiting_submit` is false** the call raises `ToolError(skin.bad_call)` and counts as a bad call, so a second submit in one reply cannot play two rounds.
- **On success** the tool appends `StoredRow(round, bets, readings)` from the `Row` the engine returns, sets `store.awaiting_submit = False`, and returns the header line and the last line of `render_record(skin, store.record())`. That is the round just played in the record's own shape, with no words from the harness. The record is rendered by `render_record` everywhere, the user message, this result and the compute file, so they cannot drift apart.

### Notes

In the headline, see [tools](../../design/interface.md#tools). What it costs or adds is the [bare harness](../../pilot/provider-checks.md#bare-harness) check's to measure.

- **`notes(text)`** replaces `store.notes` with the first `notes_cap` characters of `text` and returns the text as stored. Nothing is appended, nothing is kept from an earlier call.
- **Next round** the stored text comes back as a second content block on the user message, after the record, never as an assistant message. A tool message with no tool call before it is rejected by the Anthropic API, and an assistant message would read as the agent's own words.
- **Length is logged** by the store itself, as `len(store.notes)`.
- **The first `notes` call in a round adds one to `store.notes_rounds`.** Later calls in the same round add nothing, so the count is rounds, not calls.
- **A reply that calls `notes` and not the skin's tool is a no call**, see [tries](#tries).

### Compute

In the headline, so a default run needs `uv sync --extra sandbox` and Docker, see [running](../../harness/running.md#setup).

- **Before each round** the solver writes `render_record(skin, store.record())` to `record.csv` in the sandbox's working directory, so the code sees the record and nothing else.
- **`compute(code)`** runs `python3 -I -c <code>` in the sandbox with a 30 second timeout, and returns stdout then stderr, truncated to 4000 characters. A timeout returns the text `timeout`.
- **The sandbox is locked down.** The code is the model's and is untrusted. `compose.yaml` sets `network_mode: none`, mounts nothing from the host, passes no environment, runs the root filesystem read only with a small writable working directory, and caps memory, processes and CPU with `mem_limit`, `pids_limit`, `cpus` and `no-new-privileges`. So the code can reach neither the engine nor a seed, and a memory or fork bomb ends inside the container, not on the machine.
- **The first `compute` call in a round adds one to `store.compute_rounds`**, as for notes.
- **The compose file is found from the module**, `Path(__file__).parent / "compose.yaml"`, never from the working directory, and `pyproject.toml` ships it as package data.

### Rolling

Pilot only, see [rolling conversation](../../pilot/provider-checks.md#rolling-conversation).

- **With `rolling` on** step 2 runs on round 1 only. Later rounds append a user message of `render_record(skin, store.record())`, the same user message a fresh call would send, and keep every earlier message. Nothing is compacted. The record the model reads is the same in both modes, so the one thing rolling changes is that the earlier replies, tool messages and retry messages stay. `rolling` is a task arg, so the cell runs from the command line, see [task](task.md#interface).
- **Everything else is the same**, so the only difference in the log is the message list.
- **What carries over is the provider's**, see [reasoning](../../harness/models.md#reasoning), so the rolling gap is read per model, see [rolling conversation](../../pilot/provider-checks.md#rolling-conversation).

## Invariants

- A round ends only on a valid call to the skin's tool. The harness never places bets for the agent.
- `sum(store.tries) == ` the number of generate calls in the run, whether or not it gave up.
- `len(store.tries) == len(store.rows) − store.warm_up_rounds`, plus one when the run gave up.
- Replaying `store.rows` as bets on `store.timeline()` with `Game` gives the same readings, and so the same `row.output`, so the log is enough to check a run.
- With `rolling` off, every round starts with exactly two messages. The second holds the record, as one content block or as `record_blocks` cuts it, then one more block when a note is saved.
- `"".join(record_blocks(text)) == text` for any text, so the model reads the same record however it is cut.
- `state.tool_choice` is `"any"` or `"auto"`, never a `ToolFunction`.
- `store.notes_rounds ≤ len(store.tries)` and `store.compute_rounds ≤ len(store.tries)`.
- With `rolling` on, round `n` starts with the two messages a fresh call would send, then every reply, tool message and retry message of rounds 1 to `n − 1` in order, then the user message a fresh call would send for round `n`. So the last user message is the same with `rolling` on or off.
- `store.awaiting_submit` is false whenever the solver is between rounds, and after a give up.
- The solver raises nothing of its own. An exception in a run comes from inspect, a provider or the network.

## Pilot decides

- `notes_cap`, see [bare harness](../../pilot/provider-checks.md#bare-harness).
- **Whether `submit` keeps one list in channel order.** A list makes the model count to the right place, and a miscount is a valid call. If the [channel order check](../../pilot/provider-checks.md#channel-order) finds slips, the tool takes one number per channel by name, and this page, [tool text](../../harness/prompts.md#tool-text) and the skin's `bets_name` change with it.

## Not decided

- Whether `rolling` runs need their own `max_tokens`, as the conversation grows with the square of the game length, see [rejected](../../design/interface.md#rejected). inspect records usage per call, so input tokens per round are read from the log, and the rolling check reports them. Decide when the rolling cell runs.
- **Whether the skin should name the parameters of notes and compute.** They are `text` and `code` in every skin, the two words on any tool the harness still writes. Both are as plain as a parameter name gets, so they mark little, but they are shared. Each would be one more skin field, as `bets_name` is. Decide before the first headline run on held-out skins, as the prompt freezes there.
- Whether a run needs a try budget on top of the ten a round. A model that needs five tries every round spends two hundred calls a run with no give up. The retry share marks it, and the [cost check](../../pilot/provider-checks.md#cost-per-run) prices it. Decide when the cost check has run.

## Verify before code

- **Which providers refuse `any` with thinking on.** Anthropic does, and `tool_choice_for` knows it. Check the other providers in `configs/models/` before the first run and add each that does. `tool_choice_for` waits on it.
- **That cutting the record changes the bill and nothing else.** Three checks on one Anthropic model, and `record_blocks` is used only once all three pass. If one fails, `BLOCK_CACHE_APIS` is empty and the record stays one block.
  - inspect sends each text block of a user message to Anthropic as its own block, and does not join them.
  - Anthropic's token count for the prompt is the same cut or whole, so no separator reaches the model.
  - In a three round run the log's cache read tokens grow each round, and by round 3 cover the system prompt and the first rows.
- **That inspect lets a tool's parameter be named at run time.** `submit` needs a parameter whose name comes from the skin, which a plain `@tool` function with a fixed argument cannot give. Check that a `ToolDef` with explicit `ToolParams` and an `execute(**kwargs)` sends the skin's name in the schema and passes the call back under it. If it cannot, the parameter stays `bets` in every skin and `bets_name` is dropped from the skin. `submit` waits on it.
- **Which providers let a model read its own earlier reasoning on a later turn**, and which return it summarised or empty. The per-model reading of the rolling cell waits on it, see [rolling](#rolling).
