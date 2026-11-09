# Task

## Purpose

`paranoid` is the one inspect task. It turns the task args into a dataset of samples, one per scenario per seed, each carrying the scenario, the seed and the knobs in its metadata. `RunStore` is the per-sample state the solver, the tools, the providers and the scorer share. The design is in [inspect](../../harness/inspect.md#the-mapping) and [running](../../harness/running.md#commands).

## Interface

```python
@task
def paranoid(
    scenario: str = "all",            # a code name, a comma list of them, or "all"
    seeds: str = "public",            # "public", "held-out", or a range of positions such as "0-4"
    skin: str = "example",
    rounds: int | None = None,        # overrides ScenarioConfig.rounds
    tools: str = "none",              # "none", "notes", "compute" or "notes,compute"
    inertia: int | None = None,       # sets ScenarioConfig.inertia_cap
    warm_up: str | None = None,       # "<baseline>:<rounds>", such as "complacent:5"
    own_scale: float | None = None,   # one noise grid setting. Pins events in level points
    tool_choice: str = "forced",      # "forced" or "auto", see solver.md
) -> Task

class StoredRow(BaseModel):
    round: int
    bets: list[int]
    readings: list[float | None]
    output: float

class RunStore(StoreModel):
    scenario: str = ""
    seed: int = 0
    skin: str = ""
    rounds: int | None = None
    inertia: int | None = None
    own_scale: float | None = None
    rows: list[StoredRow] = []        # the record so far, warm up rows first
    warm_up_rounds: int = 0
    open: bool = False                # True while a round is waiting for a valid submit
    tries: list[int] = []             # generate calls per round the agent played. 1 means first time
    bad_calls: int = 0
    no_calls: int = 0
    cut_offs: int = 0
    notes: str = ""
    def config(self) -> ScenarioConfig
    def tape(self) -> Tape            # make_tape(self.config(), self.seed), cached by (engine_hash, seed)
    def record(self) -> Record
    def game(self) -> Game            # Game(self.tape(), self.record())
    def round(self) -> int            # len(rows) + 1

def scenario_config(name: str, *, rounds: int | None = None, inertia: int | None = None,
                    own_scale: float | None = None) -> ScenarioConfig
def load_seeds(scenario: str, seed_set: Literal["public", "held-out"]) -> list[int]
def parse_seeds(arg: str, scenario: str) -> list[tuple[int, int]]   # (position, seed) pairs
def prompt_hash(skin: Skin) -> str
```

## Behaviour

### Scenarios and config

- **`scenario`** is `"all"`, one code name from `SCENARIOS`, or a comma list such as `"one_shock,down_switch"`. `"all"` is the eight in `SCENARIOS` order. An unknown name raises `ValueError` naming it.
- **`scenario_config`** starts from `SCENARIOS[name]` and applies the knobs with `dataclasses.replace`, so the engine's validation runs again:
  - `rounds` replaces `rounds`.
  - `inertia` replaces `inertia_cap`.
  - `own_scale` replaces `own_scale` and sets `pin_in_level_points` to true, so the prize holds while the noise moves, see [noise threshold](../../design/scoring.md#noise-threshold).
- **The `engine_hash` in the log is of the replaced config**, so a run at `rounds=20` never shares a hash with the frozen study setting.
- **The noise grid lives in `configs/grid.toml`** as `own_scale = [2.0, 3.0, 4.0, 6.0, 8.0]`, **pilot to confirm** by the [noise grid](../../pilot/engine-checks.md#noise-grid) check. The task plays one setting per eval. `paranoid pilot noise-grid` plays the list, see [command](command.md#pilot-cells).

### Seeds

- **Seed files** hold one seed per line, as a whole number. Blank lines and lines starting with `#` are skipped. A repeated seed raises `ValueError`.
- **Public seeds** are read from `configs/seeds/<scenario>.txt`. **Held-out seeds** from `$PARANOID_SEEDS/<scenario>.txt`. `held-out` with `PARANOID_SEEDS` unset raises `ValueError` that names the variable, see [two seed sets](../../harness/contamination.md#two-seed-sets).
- **`parse_seeds`** returns `(position, seed)` pairs in file order. `"public"` and `"held-out"` give the whole list. A range `"a-b"` gives positions `a` to `b` inclusive of the public list, and `"a"` is `"a-a"`. A position past the end of the list, or `b < a`, raises `ValueError`.
- **A position is not a seed value.** Public seeds are 0 up and usually equal their position, but the harness never assumes it. The analysis reports held-out seeds by position, see [layout](../../harness/layout.md#what-each-layer-does).
- **One seed set per eval.** The eight scenarios share one `seeds` arg, so twin tapes line up across scenarios in one log, see [seeds](../../design/scoring.md#seeds).

### Dataset

- **A `MemoryDataset`** with one `Sample` per scenario per seed, scenarios in `SCENARIOS` order, seeds in file order.
- **`Sample.id`** is `f"{scenario}/{position}"`. `Sample.input` is the same string. The solver replaces the messages on every round, so the input is never shown to a model.
- **`Sample.metadata`** holds everything a reader of the log needs and nothing that gives away the tape:

| Key | Value |
|---|---|
| `scenario` | The code name |
| `seed`, `seed_index` | The seed value and its position in its list |
| `seed_set`, `seeds_arg` | `"public"` or `"held-out"`, and the `seeds` arg as typed |
| `skin` | The skin name |
| `engine_hash`, `generator_version`, `numpy_version` | From the engine, see [engine hash](../engine/config.md#engine-hash) |
| `prompt_hash` | See below |
| `rounds`, `inertia`, `own_scale`, `tools`, `warm_up`, `tool_choice` | The knobs, as resolved. `rounds` is the config's final value |

- **The seed value is in the metadata.** A log from a held-out seed holds the full prompt anyway, so it never leaves the machine, see [contamination](../../harness/contamination.md#public-and-held-out). The analysis layer, not the log, keeps held-out seeds to positions.

### Task settings

- **`solver`** is `round_loop(skin, tools, tool_choice)`. **`scorer`** is `gain()`.
- **`retry_on_error=1`** and **`fail_on_error=False`**, set here and never on the command line, see [retry rule](../../harness/prompts.md#retry-rule). A sample that errors twice has no score, and the metrics count it as a gain of 0, see [missing seeds](scorer.md#missing-seeds).
- **Epochs** reduce by `"mean"`. Repeats of a seed are averaged before any metric sees them, see [error bars](../../design/scoring.md#error-bars).
- **`sandbox`** is `("docker", "src/paranoid/harness/compose.yaml")` only when `tools` includes `compute`, else none, see [compute](solver.md#compute).
- **Skins** load with `load_skins()`, which reads `PARANOID_SKINS` when set. A `skin` that is not loaded raises `ValueError` listing the loaded names.
- **`tools`** is a comma list drawn from `notes` and `compute`, or `none`. Anything else raises `ValueError`.

### Store

- **The solver fills the store on round 1** from the sample's metadata: `scenario`, `seed`, `skin` and the knobs. Everything else starts empty.
- **`config()`, `tape()`, `record()` and `game()` are derived**, never stored. `tape()` caches per `(engine_hash, seed)` in a module-level dict, so forty rounds and the scorer build one tape. The cache holds tapes, not arrays in the store, so nothing on the tape reaches the log.
- **`rows` is the record.** `record()` builds a `Record` from them in order. `Game(tape, record)` validates them, see [starting part way](../engine/game.md#starting-part-way).
- **The store is written to the log by inspect**, so a run can be rebuilt from any round by replaying `rows[:r]` against the tape.

### Warm up

- **`warm_up="<baseline>:<k>"`** plays `k` rounds of the named baseline before the agent's first round: `play(POLICIES[name], tape, max_rounds=k)`, see [play](../engine/game.md#play). Its rows go into `rows` and `warm_up_rounds = k`. `name` is a key of [`POLICIES`](providers.md#baseline). `k` must be at least 1 and below the config's `rounds`, else `ValueError`.
- **The agent then plays rounds `k + 1` to `rounds`.** Its round 1 user message shows `k` rows it did not place, see [user message](../../harness/prompts.md#user-message).
- **Warm up rows score nothing** for the agent, and the baselines it is scored against are summed over the same rounds it played, see [scoring one run](scorer.md#scoring-one-run).
- The warm up cell is in [decisions](../../pilot/decisions.md#provider-checks) as "Warm up: empty record or pre-filled".

### Prompt hash

- **`prompt_hash(skin)`** is the first 12 hex characters of the SHA-256 of `render_system_prompt(skin)`, the skin's `tool_text`, `bad_call` and `no_call`, joined by `"\n"` and encoded as UTF-8.
- **It covers the fixed text only.** The user message grows every round and is the record, which the store already holds.
- **Changing a word changes the hash**, see [prompts](../../harness/prompts.md). The same skin gives the same hash on every machine.

## Invariants

- The same task args give the same dataset, with the same ids in the same order.
- Every sample's `engine_hash` equals `engine_hash(store.config())` once the store is filled.
- `RunStore` has no field that holds an array, a tape or a level the agent did not see.
- `len(store.rows) ≤ store.config().rounds` at all times, and equals it when a run ends without error.
- `store.round() == len(store.rows) + 1`.

## Tests

See [tests](tests.md#task).

## Open

- Whether `seeds` should also take a held-out range, such as `held-out:0-4`, for a cheap check on the private set. Not needed for the pilot.
- `inspect_ai`'s `retry_on_error` plays an errored sample again once. Confirm it does not also retry a `RoundError` inside the same sample, which would give a round more than ten tries.
