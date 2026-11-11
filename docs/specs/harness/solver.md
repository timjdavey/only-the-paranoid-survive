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

def tool_choice_for(api: str, config: GenerateConfig) -> Literal["any", "auto"]   # api as ModelName(model).api

BLOCK_CACHE_APIS: tuple[str, ...] = ()   # apis whose prompt cache matches by content block. Off until checked
def record_blocks(text: str) -> list[str]   # the record cut after every line end

def submit(skin: Skin) -> Tool                     # one parameter, named skin.bets_name, a list of ints. Returns str
def notes(skin: Skin, cap: int = 2000) -> Tool     # one parameter, named skin.notes_param, a str. Returns str
def compute(skin: Skin) -> Tool                    # one parameter, named skin.compute_param, a str. Returns str
                                                   # each parameter's description is the skin's, see Notes below
```

## Behaviour

### Each round

1. **Fill the store** if `store.scenario == ""`: copy the metadata in and play the warm up, see [store](task.md#store).
2. **Reset the messages.** `state.messages` becomes exactly: a system message of `render_system_prompt(skin)`, then a user message of `render_record(skin, store.record())`, as one content block or cut by [record blocks](#record-blocks). With `notes` on and `store.notes` non-empty, the user message has one more content block after the record, holding the notes, see [notes](#notes). With `rolling` on the messages are not reset, see [rolling](#rolling).
3. **Set the tools.** `state.tools` is `[submit(skin)]`, which carries the skin's `tool_name`, `tool_text`, `bets_name` and `bets_text`, see [submit](#submit), then `notes(skin)` as `skin.notes_name` with `skin.notes_text` and one parameter named `skin.notes_param` and described by `skin.notes_param_text`, and `compute(skin)` as `skin.compute_name` with `skin.compute_text` and one parameter named `skin.compute_param` and described by `skin.compute_param_text`, when `tools` asks for them. Every word on every tool is the skin's, see [tool text](../../harness/prompts.md#tool-text). The submit tool is always first, so a provider finds it at `tools[0]`, see [providers](providers.md#shared-behaviour).
4. **Set the tool choice.** `"any"` for `"any"`, so the reply must call some tool, and `"auto"` otherwise. A `ToolFunction` naming the skin's tool is never used: it would stop the model calling notes or compute first. With `tool_choice=None` the solver calls `tool_choice_for(ModelName(get_model()).api, get_model().config)` on round 1. `Model.api` is the provider object, not its name, so the name comes from `ModelName`, see [checked](#checked) and writes the answer to `store.tool_choice` and to `state.metadata["tool_choice"]`, so the log says which it was and the analysis reads it without the store, see [result key](../analysis/runs.md#result-key). The rule: `"auto"` when the api is `"anthropic"` and the config asks for thinking, which is a `reasoning_effort` other than `"none"` or any `reasoning_tokens`, else `"any"`. With thinking on, `any` never reaches Claude as asked: inspect drops it, turns it into `auto`, or sends it and the model skips its thinking, see [checked](#checked) and [reasoning](../../harness/models.md#reasoning). Deciding here, not on the command line, means `inspect eval paranoid/paranoid --model anthropic/<model>` works as typed.
5. **Try until the round is played**, see [tries](#tries).
6. **Repeat** until `store.round() > store.config().rounds`, or the run gave up. Then return the state.

### Record blocks

How the record is cut into content blocks, and nothing else. The text is the same either way, so this moves the bill and never the prompt, see [prompt caching](../../harness/models.md#prompt-caching).

- **`record_blocks(text)`** cuts the record after every line end and returns the pieces in order: the header line, then one piece per row. Nothing is added, dropped or stripped.
- **Used when `ModelName(get_model()).api` is in `BLOCK_CACHE_APIS`.** Each piece is one text block of the user message. Any other api gets the record as one block.
- **`BLOCK_CACHE_APIS` ships empty**, so every api gets one block until both Anthropic checks in [verify before code](#verify-before-code) pass. Then it becomes `("anthropic",)`, and nothing else changes.
- **Why.** Anthropic's cache matches by content block, and a record sent as one growing block never matches, see [prompt caching](../../harness/models.md#prompt-caching).
- **The notes block stays last**, after every record block, so a changed note leaves the rows above it cached.
- **inspect places the cache marks.** The solver sets none, and `cache_prompt` stays at inspect's default, see [reasoning](command.md#reasoning). Where the marks fall is in [checked](#checked).
- **With `rolling` on** every user message that holds the record is cut the same way.

### Tries

Each try is one `generate(state, tool_calls="single")`, so inspect runs whatever tools the reply called and appends their results. The solver then reads the store.

- **Before the try** the solver sets `store.awaiting_submit = True`. A valid submit sets it back to false, so the solver knows the round was played by the store, not by parsing the reply.
- **A valid call** ends the round. The try count for the round is appended to `store.tries`.
- **A reply with no call to the skin's tool**, whatever else it called or said, is a no call: `store.no_calls += 1` and a user message of `skin.no_call` is appended. A reply whose `stop_reason` is `"max_tokens"` also adds one to `store.cut_offs`, see [sampling](../../harness/models.md#sampling).
- **A call the engine rejected** already carries `skin.bad_call` in its tool message, and the tool counted it, see [submit](#submit). The solver appends nothing more.
- **A call inspect refused** never ran the tool. The solver puts the skin's words on its tool message and counts it, see [refused calls](#refused-calls).
- **Within a round the messages grow** with each reply and its retry message, so the model sees what it got wrong. Across rounds nothing survives, see step 2.
- **After `max_tries` tries** with no valid call the solver gives up: it appends the try count to `store.tries`, sets `store.gave_up = True` and `store.awaiting_submit = False`, and returns the state with the rounds left unplayed. The sample is still scored, as the Uniform baseline on that seed, see [giving up](scorer.md#giving-up). Nothing is raised, so an error in the log always means infrastructure, never the model. The default is ten, fixed by the [retry rule](../../harness/prompts.md#retry-rule).

### Submit

`submit(skin)` is the engine's `Game.play` behind a tool. The model sees it under the skin's name and text, see [tool text](../../harness/prompts.md#tool-text).

- **The tool is built from the skin**, as a `ToolDef` with explicit `ToolParams`, never with `@tool`, which would rename it after its factory, see [checked](#checked). Its name is `skin.tool_name`, its description `skin.tool_text`, and it has one required parameter named `skin.bets_name`, an array of integers, described by `skin.bets_text`. So no word on the tool is the harness's, and no two skins need share one, see [contamination](../../harness/contamination.md#why).
- **`execute`** takes that one argument by the skin's name, reads `store_as(RunStore)`, builds `store.game()`, and calls `game.play(bets)`. A call with any other argument name, or with more than one, never reaches it, see [refused calls](#refused-calls).
- **The bets go through untouched.** The harness does no coercion. A list of JSON whole numbers passes. `10.0` reaches the engine as a float and fails its `shape` check, see [bets](../engine/game.md#bets). `"10"`, `true` and `10.5` are [refused](#refused-calls) before the tool runs.
- **On `BetError`** the tool adds one to `store.bad_calls` and returns `skin.bad_call` as its result. The engine's own message never reaches the model. The round, the record and `store.awaiting_submit` are unchanged.
- **It never raises `ToolError`.** Providers built on OpenAI's chat completions, OpenRouter among them, put `Error: ` before a tool error's message, and Anthropic does not. A plain result reads the same on every provider and holds no word of inspect's, see [checked](#checked).
- **When `store.awaiting_submit` is false** the call returns `skin.bad_call` and counts as a bad call, so a second submit in one reply cannot play two rounds.
- **On success** the tool appends `StoredRow(round, bets, readings)` from the `Row` the engine returns, sets `store.awaiting_submit = False`, and returns the header line and the last line of `render_record(skin, store.record())`. That is the round just played in the record's own shape, with no words from the harness. The record is rendered by `render_record` everywhere, the user message, this result and the compute file, so they cannot drift apart.

### Refused calls

inspect checks every tool call against its tool's schema before the tool runs, see [checked](#checked).

- **A refused call** is one whose arguments do not fit the schema, one to a tool that does not exist, or one whose JSON did not parse. Its tool message has `error.type == "parsing"` and a message in inspect's own English. No tool ran, so no tool counted it.
- **After each try the solver rewrites every refused call of that try.** It sets the tool message's `content` and clears its `error`, so the next call reads a plain result.
- **A refused call to the skin's tool** gets `skin.bad_call` and adds one to `store.bad_calls`, as a call the engine rejected does.
- **Any other refused call** gets `skin.no_call`. The reply is then a no call like any other with no call to the skin's tool, see [tries](#tries).
- **So the model reads the skin's words and nobody else's**, the same on every provider.

### Notes

In the headline, see [tools](../../design/interface.md#tools). What it costs or adds is the [bare harness](../../pilot/provider-checks.md#bare-harness) check's to measure.

- **The notes tool takes one string**, under the skin's `notes_param`, built as [`submit`](#submit) is. It replaces `store.notes` with the first `notes_cap` characters of the string and returns the text as stored. Nothing is appended, nothing is kept from an earlier call.
- **Next round** the stored text comes back as a second content block on the user message, after the record, never as an assistant message. A tool message with no tool call before it is rejected by the Anthropic API, and an assistant message would read as the agent's own words.
- **Length is logged** by the store itself, as `len(store.notes)`.
- **The first `notes` call in a round adds one to `store.notes_rounds`.** Later calls in the same round add nothing, so the count is rounds, not calls. The solver counts it at the end of the round, from the tool messages of calls that ran, so a refused call saves nothing and counts nothing.
- **A reply that calls `notes` and not the skin's tool is a no call**, see [tries](#tries).
- **Each parameter is described by the skin**, in `skin.notes_param_text` and `skin.compute_param_text`, as `bets_text` describes `submit`'s. inspect will not build a tool whose parameter has no description, and the harness writes no words of its own. Decided on 2026-11-11, before the pilot, as the prompt structure freezes after it: a parameter that repeated its tool's text made the model read one sentence twice, in every skin alike.

### Compute

In the headline, so a default run needs Docker, see [running](../../harness/running.md#setup). inspect's Docker sandbox needs no Python package beyond inspect itself, so there is no extra to install.

- **Before each round**, and only when `compute` is on, the solver writes `render_record(skin, store.record())` to `record.csv` in the sandbox's working directory, so the code sees the record and nothing else. With `compute` off there is no sandbox to write to.
- **The compute tool takes one string**, under the skin's `compute_param`, and runs `python3 -I -c <string>` in the sandbox with a 30 second timeout and `timeout_retry=False`, and returns stdout then stderr, truncated to 4000 characters. A timeout returns the text `timeout`. inspect retries a timed out command twice by default, which would run the model's code three times.
- **The code runs as `nobody`** on Docker, and `record.csv` is written as root. So the code can read the record and cannot change it. Any other sandbox runs it as the sandbox's own user.
- **The sandbox is locked down.** The code is the model's and is untrusted. `compose.yaml` sets `network_mode: none`, mounts nothing from the host, passes no environment, runs the root filesystem read only with small `tmpfs` mounts as the only writable places, and caps memory, processes and CPU with `mem_limit`, `memswap_limit`, `pids_limit`, `cpus`, `shm_size`, `ipc: private`, `cap_drop: [ALL]` and `no-new-privileges`. The image tag is pinned to one Debian release. So the code can reach neither the engine nor a seed, and a memory or fork bomb ends inside the container, not on the machine.
- **Nothing crosses a round.** Before writing `record.csv`, the solver resets the sandbox when the round before ran a `compute` call, which is when `store.compute_rounds` went up. A round with no `compute` call left nothing to clear, so it costs nothing. So the model cannot leave itself a note in the sandbox, and the [notes tool](#notes) stays the only memory across rounds.
  - **On Docker the reset restarts the container**, with `docker compose restart --timeout 0`. The root is read only and every writable mount is `tmpfs`, so a restart clears files, `/dev/shm`, left running processes and SysV shared memory at once. Wiping in place would have to list every place state can hide, and would miss some.
  - **On any other sandbox** it empties the working directory, by relative paths only, so it is safe on the host's temp folder the tests use.
  - **A failed reset raises `RuntimeError`**, so the sample errors as infrastructure and is never played on a dirty sandbox.
  - **Known limits.** State persists within a round, so a second `compute` call reads what the first left. Host wide `/proc` counters, such as uptime and load, stay readable.
  - **The restart uses inspect internals**, `compose_command`, `DockerSandboxEnvironment` and its `_project` and `_service`. `pyproject.toml` pins inspect, and HS21 fails loudly if they move.
- **Code that eats memory reads Python's own `MemoryError`.** `ulimits` sets `data` to 384 MB, below the 512 MB `mem_limit`, so Python fails to grow and raises. Past `mem_limit` the kernel kills the process with no output, and the model would read an empty result and no reason, see [checked](#checked).
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
- The solver raises nothing of its own bar a failed [sandbox reset](#compute). An exception in a run comes from inspect, a provider, the network or the sandbox, so it always means infrastructure.
- When a call is made, no tool message from an earlier try holds an `error`. Every one holds a row of the record, a skin's words, the saved note or compute's output.

## Pilot decides

- `notes_cap`, see [bare harness](../../pilot/provider-checks.md#bare-harness).
- **Whether `submit` keeps one list in channel order.** A list makes the model count to the right place, and a miscount is a valid call. If the [channel order check](../../pilot/provider-checks.md#channel-order) finds slips, the tool takes one number per channel by name, and this page, [tool text](../../harness/prompts.md#tool-text) and the skin's `bets_name` change with it.

## Not decided

- Whether `rolling` runs need their own `max_tokens`, as the conversation grows with the square of the game length, see [rejected](../../design/interface.md#rejected). inspect records usage per call, so input tokens per round are read from the log, and the rolling check reports them. Decide when the rolling cell runs.
- Whether a run needs a try budget on top of the ten a round. A model that needs five tries every round spends two hundred calls a run with no give up. The retry share marks it, and the [cost check](../../pilot/provider-checks.md#cost-per-run) prices it. Decide when the cost check has run.

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289, and read from its provider source. No key was used, so no provider was called.

| Question | Answer |
|---|---|
| Can a tool's parameter be named at run time | Yes. A `ToolDef` with explicit `ToolParams` and an `execute(**kwargs)` puts the given name in the schema, with `additionalProperties` false, and the call comes back under that name |
| Does a parameter need a description | Yes. A `ToolDef` raises on a parameter with none, or with an empty one |
| Does every call reach the tool | No. inspect checks the arguments against the schema first. Another argument name, an extra argument, `"10"`, `true` or `10.5` in a list of integers, a tool that does not exist and JSON that did not parse all come back with `error.type` of `parsing` and inspect's own message. `10.0` passes as an integer and reaches the tool as a float |
| What the model reads for a tool error | The error's message. Providers built on OpenAI's chat completions put `Error: ` in front. Anthropic, Google and OpenAI's responses API send it as it is |
| Can a solver change a tool message before the next call | Yes. A message whose `error` was replaced reached the next `generate` as changed, and the log holds it as changed |
| Does inspect send each text block of a user message to Anthropic as its own block | Yes. A user message of `ContentText` blocks goes out block for block, with no text added or joined. A plain string goes out as a string |
| Where inspect puts the cache marks | On the system prompt, on the last tool, on the second to last block of the messages, and one automatic mark for the end of the prompt. So with a saved note the last row carries a mark, and with none the row before it does |
| `any` on Claude with a thinking budget | inspect leaves `tool_choice` out of the request, so it plays as `auto` |
| `any` on Claude with adaptive thinking | Sent. inspect's source says the model then skips its thinking on that turn |
| `any` on Fable 5.1, Opus 5.5 and Sonnet 5.5 | These refuse a required call at any setting. inspect sends `auto`, warns once, and writes `tool_choice_degraded` on the reply's metadata |
| `any` on DeepSeek and Kimi, through inspect's own providers | Both refuse it while thinking, and inspect sends `auto`. Through OpenRouter inspect changes nothing |
| Does inspect send a model its earlier reasoning | Yes by default. `GenerateConfig.reasoning_history` is `auto`, which replays reasoning blocks. What the model reads of them is the provider's |
| What `get_model().api` is | The `ModelAPI` object, not a string. `ModelName(model).api` is the provider's name, such as `anthropic`, with the package prefix stripped |
| What `sandbox.exec(timeout=...)` does on a timeout | Raises `TimeoutError`, after two retries unless `timeout_retry=False` |
| Does `@tool` keep a `ToolDef`'s name | No. It tags the tool it returns with its factory's name, so the tools are plain functions returning `ToolDef(...).as_tool()` |
| What Docker needs from Python | Nothing beyond inspect_ai. Its Docker sandbox drives the `docker` command line |
| Does `compose.yaml` run, read-only root and all | Yes. HS12 passes on Docker 29.5 under Colima, run on 2026-11-11. inspect writes `record.csv` to the `tmpfs` working directory, the code reads it, the network is unreachable and no key is in the environment |
| Does a restart clear the sandbox | Yes. HS21 passes on Docker 29.5 under Colima, run on 2026-11-11. A file in `/work`, `/tmp` and `/dev/shm`, a SysV segment and a listening process all survive a second call in the round and are gone the next round. One `docker compose restart --timeout 0` took 0.13 seconds |
| What a memory bomb returns under `mem_limit` alone | Nothing. The kernel kills Python with exit code 137 and no output. With `ulimits` `data` below `mem_limit` it returns a `MemoryError` traceback |

- **So the rule above stands for Claude**, for a wider reason than a refused call: `auto` is the only choice that leaves thinking on.
- **A Claude that thinks with nothing set** still gets `any`, as the rule reads the config and not the model. Every Anthropic row in `configs/models/` sets its reasoning, so no row of the study plays that way.

## Verify before code

Each needs a key, so none was run.

- **Which OpenRouter models refuse `any` while thinking.** For every `openrouter/` row in `configs/models/` at a setting above `off`, one `generate` with the [`submit`](#submit) tool and `tool_choice="any"`. A 400, or a reply with no reasoning, means `tool_choice_for` returns `auto` for that model, and it then takes the model name as well as the api. DeepSeek and Kimi are the likely ones, see [checked](#checked). The same call on one OpenAI and one Google row. `tool_choice_for` waits on it.
- **That `any` with adaptive thinking skips the thinking.** One call on `claude-haiku-5-5` at `low` with `any` and one with `auto`. If the `any` reply thinks as much, the rule could send `any` there. Nothing waits on it.
- **That cutting the record changes the bill and nothing else.** Two checks left of three, on one Anthropic model. `BLOCK_CACHE_APIS` ships empty, so `record_blocks` is used only once both pass and the constant becomes `("anthropic",)`. If one fails, it stays empty and the record stays one block.
  - Anthropic's token count for the prompt is the same cut or whole, so no separator reaches the model. `count_tokens` on a forty row record both ways.
  - In a three round run the log's cache read tokens grow each round, and by round 3 cover the system prompt and the first rows. A prompt under the model's cache minimum reads nothing, so use a record long enough to clear it. Anthropic's docs put the minimum at 512 tokens on Claude 5.5 models, read on 2026-11-11.
- **Which models read their own earlier reasoning on a later turn**, and which get it summarised or empty. From each provider's docs, noted in the row's `notes`. Done for the three `llm` rows of `poc.toml` on 2026-11-11: all three read it when the blocks are sent back as they came. The rows of `full.toml` are left. The per-model reading of the rolling cell waits on it, see [rolling](#rolling).
