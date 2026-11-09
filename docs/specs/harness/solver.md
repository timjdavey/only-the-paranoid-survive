# Solver

## Purpose

`round_loop` plays one run: each round it renders a fresh system prompt and record, asks the model for one call to the skin's tool, plays the bets through the engine and appends the row. `submit` is that tool. The retry rule, giving up and the two pilot tools live here too. The design is in [the round loop](../../harness/inspect.md#the-round-loop), [prompts](../../harness/prompts.md) and [tools](../../design/interface.md#tools).

## Interface

```python
@solver
def round_loop(
    skin: Skin,
    tools: str = "none",             # as the task arg
    tool_choice: str | None = None,  # "forced", "auto", or None to decide from the model, see below
    max_tries: int = 10,
    notes_cap: int = 2000,           # characters, pilot to confirm
    rolling: bool = False,           # keep the conversation across rounds, pilot only
) -> Solver

def tool_choice_for(api: str, config: GenerateConfig) -> Literal["forced", "auto"]

@tool
def submit(skin: Skin) -> Tool       # execute(bets: list[int]) -> str
@tool
def notes() -> Tool                  # execute(text: str) -> str
@tool
def compute() -> Tool                # execute(code: str) -> str
```

## Behaviour

### Each round

1. **Fill the store** if `store.scenario == ""`: copy the metadata in and play the warm up, see [store](task.md#store).
2. **Reset the messages.** `state.messages` becomes exactly: a system message of `render_system_prompt(skin)`, then a user message of `render_record(skin, store.record())`. With `notes` on and `store.notes` non-empty, the user message has a second content block holding the notes, see [notes](#notes). With `rolling` on the messages are not reset, see [rolling](#rolling).
3. **Set the tools.** `state.tools` is `[tool_with(submit(skin), name=skin.tool_name, description=skin.tool_text, parameters={"bets": skin.bets_text})]`, then `notes()` and `compute()` when asked for. Every word on the tool is the skin's, see [tool text](../../harness/prompts.md#tool-text). The submit tool is always first, so a provider finds it at `tools[0]`, see [providers](providers.md#shared-behaviour).
4. **Set the tool choice.** `ToolFunction(name=skin.tool_name)` for `"forced"`, `"auto"` otherwise. With `tool_choice=None` the solver calls `tool_choice_for(get_model().api, get_model().config)` on round 1 and stores the answer in `store.tool_choice`, so the log says which it was. The rule: `"auto"` when the api is `"anthropic"` and the config sets `reasoning_effort` or `reasoning_tokens`, else `"forced"`. Claude rejects a forced tool with thinking on, see [reasoning](../../harness/models.md#reasoning). Deciding here, not on the command line, means `inspect eval paranoid --model anthropic/<model>` works as typed.
5. **Try until the round is played**, see [tries](#tries).
6. **Repeat** until `store.round() > store.config().rounds`, or the run gave up. Then return the state.

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

- **`execute(bets)`** reads `store_as(RunStore)`, builds `store.game()`, and calls `game.play(bets)`.
- **The bets go through untouched.** The harness does no coercion. A list of JSON whole numbers passes. `10.0`, `"10"` or `true` fail the engine's `shape` check, see [bets](../engine/game.md#bets).
- **On `BetError`** the tool adds one to `store.bad_calls` and raises `ToolError(skin.bad_call)`. The engine's own message never reaches the model. The round, the record and `store.awaiting_submit` are unchanged.
- **When `store.awaiting_submit` is false** the call raises `ToolError(skin.bad_call)` and counts as a bad call, so a second submit in one reply cannot play two rounds.
- **On success** the tool appends a `StoredRow` from the `Row` the engine returns, sets `store.awaiting_submit = False`, and returns the header line and the last line of `render_record(skin, store.record())`. That is the round just played in the record's own shape, with no words from the harness. The record is rendered by `render_record` everywhere, the user message, this result and the compute file, so they cannot drift apart.

### Notes

Pilot only, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute).

- **`notes(text)`** replaces `store.notes` with the first `notes_cap` characters of `text`, adds one to `store.notes_calls`, and returns the text as stored. Nothing is appended, nothing is kept from an earlier call.
- **Next round** the stored text comes back as a second content block on the user message, after the record, never as an assistant message. A tool message with no tool call before it is rejected by the Anthropic API, and an assistant message would read as the agent's own words.
- **Length is logged** by the store itself, as `len(store.notes)`.
- **A reply that calls `notes` and not the skin's tool is a no call**, see [tries](#tries).

### Compute

Pilot only. Needs `uv sync --extra sandbox` and Docker.

- **Before each round** the solver writes `render_record(skin, store.record())` to `record.csv` in the sandbox's working directory, so the code sees the record and nothing else.
- **`compute(code)`** runs `python3 -I -c <code>` in the sandbox with a 30 second timeout, adds one to `store.compute_calls`, and returns stdout then stderr, truncated to 4000 characters. A timeout returns the text `timeout`. The two counts reach the log through the score, see [scoring one run](scorer.md#scoring-one-run), as the pilot's [notepad check](../../pilot/provider-checks.md#notepad-and-compute) asks how often each tool is used.
- **The sandbox is locked down.** The code is the model's and is untrusted. `compose.yaml` sets `network_mode: none`, mounts nothing from the host, passes no environment, runs the root filesystem read only with a small writable working directory, and caps memory, processes and CPU with `mem_limit`, `pids_limit`, `cpus` and `no-new-privileges`. So the code can reach neither the engine nor a seed, and a memory or fork bomb ends inside the container, not on the machine.
- **The compose file is found from the module**, `Path(__file__).parent / "compose.yaml"`, never from the working directory, and `pyproject.toml` ships it as package data.

### Rolling

Pilot only, see [rolling conversation](../../pilot/provider-checks.md#rolling-conversation).

- **With `rolling` on** step 2 runs on round 1 only. Later rounds append a user message of the new record row, the header line and the last line of `render_record`, and keep every earlier message. Nothing is compacted. `rolling` is a task arg, so the cell runs from the command line, see [task](task.md#interface).
- **Everything else is the same**, so the only difference in the log is the message list.

## Invariants

- A round ends only on a valid call to the skin's tool. The harness never places bets for the agent.
- `sum(store.tries) == ` the number of generate calls in the run, whether or not it gave up.
- `len(store.tries) == len(store.rows) − store.warm_up_rounds`, plus one when the run gave up.
- Replaying `store.rows` as bets on `store.tape()` with `Game` gives the same readings and outputs, so the log is enough to check a run.
- With `rolling` off, every round starts with exactly two messages, or two messages with two content blocks on the second when notes are on.
- `store.awaiting_submit` is false whenever the solver is between rounds, and after a give up.
- The solver raises nothing of its own. An exception in a run comes from inspect, a provider or the network.

## Pilot decides

- `notes_cap`, see [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute).

## Not decided

- Whether `rolling` runs need their own `max_tokens`, as the conversation grows with the square of the game length, see [rejected](../../design/interface.md#rejected). Decide when the rolling cell runs.
- Whether a run needs a try budget on top of the ten a round. A model that needs five tries every round spends two hundred calls a run with no give up. The retry share marks it, and the [cost check](../../pilot/provider-checks.md#cost-per-run) prices it. Decide when the cost check has run.

## Verify before code

- **Which providers refuse a forced tool with thinking on.** Anthropic does, and `tool_choice_for` knows it. Check the other providers in `configs/models/` before the first run and add each that does. `tool_choice_for` waits on it.
