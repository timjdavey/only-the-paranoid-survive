# Task

## Purpose

`paranoid` is the one inspect task. It turns the task args into a dataset of samples, one per scenario per seed, each carrying the scenario, the seed and the knobs in its metadata. `RunStore` is the per-sample state the solver, the tools, the providers and the scorer share. The design is in [inspect](../../harness/inspect.md#the-mapping) and [running](../../harness/running.md#commands). `tool_choice` is decided from the model unless passed, see [each round](solver.md#each-round).

## Interface

```python
@task
def paranoid(
    scenario: str | list[str] = "all",          # a code name, a comma list of them, or "all"
    seeds: str | list[str] = "public",          # "public", "held-out", or positions such as "0-4" or "0-4,7,9"
    skin: str = "example",
    rounds: int | None = None,                  # overrides ScenarioConfig.rounds
    tools: str | list[str] = "notes,compute",   # the headline setting, or "none", "notes", "compute"
    tool_choice: str | None = None,   # "any", "auto", or None to decide from the model, see solver.md
    inertia: int | None = None,       # sets ScenarioConfig.inertia_cap
    warm_up: str | None = None,       # "<baseline>:<rounds>", such as "complacent:5"
    own_scale: float | None = None,   # one noise grid setting. Pins events in level points
    rolling: bool = False,            # keep the conversation across rounds, pilot only, see solver.md
) -> Task

class StoredRow(BaseModel):
    round: int
    bets: list[int]
    readings: list[float | None]      # the three fields of an engine Row. Output is never stored, see game.md

class RunStore(StoreModel):
    scenario: str = ""
    seed_set: str = ""                # "public" or "held-out"
    seed_index: int = 0               # the position in the seed list. Never the held-out value, see below
    skin: str = ""
    rounds: int | None = None
    inertia: int | None = None
    own_scale: float | None = None
    tool_choice: str = ""             # "any" or "auto", as the solver resolved it
    rows: list[StoredRow] = []        # the record so far, warm up rows first
    warm_up_rounds: int = 0
    awaiting_submit: bool = False     # True while a round is waiting for a valid submit
    tries: list[int] = []             # generate calls per round the agent played. 1 means first time
    gave_up: bool = False             # True after max_tries failed tries in one round, see solver.md
    bad_calls: int = 0
    no_calls: int = 0
    cut_offs: int = 0
    notes_rounds: int = 0             # rounds with at least one notes call
    compute_rounds: int = 0           # rounds with at least one compute call
    notes: str = ""
    def seed(self) -> int             # load_seeds(self.seed_set)[self.seed_index]
    def config(self) -> ScenarioConfig
    def timeline(self) -> Timeline    # make_timeline(self.config(), self.seed()), cached by (engine_hash, seed)
    def record(self) -> Record
    def game(self) -> Game            # Game(self.timeline(), self.record())
    def round(self) -> int            # len(rows) + 1

def scenario_config(name: str, *, rounds: int | None = None, inertia: int | None = None,
                    own_scale: float | None = None) -> ScenarioConfig
def load_seeds(seed_set: Literal["public", "held-out"]) -> list[int]
def parse_seeds(arg: str) -> list[tuple[int, int]]   # (position, seed) pairs

@dataclass(frozen=True)
class Grid:
    release: str                      # the release these settings belong to, see Release below
    own_scale: tuple[float, ...]      # the noise grid

def load_grid() -> Grid               # configs/grid.toml
```

## Behaviour

### Scenarios and config

- **`scenario`, `seeds` and `tools` take a list too**, joined with commas first. inspect splits `-T scenario=a,b` into a list before the task sees it, see [checked](#checked).
- **`scenario`** is `"all"`, one code name from `SCENARIOS`, or a comma list such as `"one_shock,down_switch"`. `"all"` is the eight in `SCENARIOS` order. An unknown name raises `ValueError` naming it, before any file is read or path is built.
- **`scenario_config`**, in `config.py`, starts from `SCENARIOS[name]` and applies the knobs with `dataclasses.replace`, so the engine's validation runs again:
  - `rounds` replaces `rounds`.
  - `inertia` replaces `inertia_cap`.
  - `own_scale` replaces `own_scale` and sets `pin_in_level_points` to true, so the reachable gain holds while the noise moves, see [noise threshold](../../design/scoring.md#noise-threshold).
- **The `engine_hash` in the log is of the replaced config**, so a run at `rounds=20` never shares a hash with the frozen study setting.
- **`configs/` is read from the working directory**, as `--models` is, so commands run from the repo root. Tests move the working directory with `monkeypatch.chdir`, and `PARANOID_PILOT_SEEDS` stays the one test hook, see [tests](tests.md).
- **The noise grid lives in `configs/grid.toml`** as `own_scale = [2.0, 3.0, 4.0, 6.0, 8.0]`, **pilot to confirm** by the [noise grid](../../pilot/engine-checks.md#noise-grid) check. `load_grid()` reads it. The task plays one setting per eval. `paranoid run --own-scale grid` plays the list with a model, see [command](command.md#run), and `paranoid pilot noise-grid` plays it with the baselines, see [pilot](pilot.md#noise-grid).
- **Every grid setting must build.** `load_grid()` calls `scenario_config(name, own_scale=s)` for every scenario and setting and lets the engine's `ValueError` through, so a setting the ladder cannot hold fails when the file is read, not half way through a study.

### Release

A [release](../../glossary.md#seeds-and-secrecy) is one frozen set of generator defaults, noise grid and held-out seeds, see [generator](../../design/mechanics.md#generator).

- **`configs/grid.toml` names it**, as `release = "dev"` beside the grid. It is `dev` until the first release is frozen, then a short name such as `r1`. The name matches `[a-z0-9-]+`, else `ValueError`.
- **Every sample's metadata carries it**, see [dataset](#dataset). Held-out seeds are fresh each release and a log holds only a seed's position, so without the name two releases' held-out logs could not be told apart.
- **The analysis never pools two releases.** `release` is a field of its `Setting`, see [runs](../analysis/runs.md#interface).
- **The harness checks nothing else about a release.** What a release must freeze, and how two releases join, is [not decided](#not-decided).

### Seeds

- **One list, every scenario.** There are two seed files, and every scenario plays the same one. Seed *i* is position *i* in all eight scenarios, so twin timelines line up in one log by construction, see [seeds](../../design/scoring.md#seeds). A scenario never has a list of its own.
- **Seed files** hold one seed per line, as a whole number. Blank lines and lines starting with `#` are skipped. A repeated seed raises `ValueError`.
- **Public seeds** are read from `configs/seeds/public.txt`. **Held-out seeds** from `$PARANOID_SEEDS/held-out.txt`. `held-out` with `PARANOID_SEEDS` unset raises `ValueError` that names the variable, see [two seed sets](../../harness/contamination.md#two-seed-sets).
- **`parse_seeds`** returns `(position, seed)` pairs in file order. `"public"` and `"held-out"` give the whole list. A range `"a-b"` gives positions `a` to `b` inclusive of the public list, and `"a"` is `"a-a"`. A comma list such as `"0-4,7,9"` is the union of its parts, in position order. A position past the end of the list, `b < a`, or a position named twice raises `ValueError`. The pilot's `repeats` cell is why a list is allowed, see [pilot](pilot.md#repeats).
- **A position is not a seed value.** Public seeds are 0 up and usually equal their position, but the harness never assumes it. The analysis reports held-out seeds by position, see [layout](../../harness/layout.md#what-each-layer-does).

### Dataset

- **A `MemoryDataset`** with one `Sample` per scenario per seed, scenarios in `SCENARIOS` order, seeds in file order.
- **`Sample.id`** is `f"{scenario}/{position}"`. `Sample.input` is the same string. The solver replaces the messages on every round, so the input is never shown to a model.
- **`Sample.metadata`** holds everything a reader of the log needs and nothing that gives away the timeline:

| Key | Value |
|---|---|
| `scenario` | The code name |
| `seed_set`, `seed_index`, `seeds_arg` | `"public"` or `"held-out"`, the position in that list, and the `seeds` arg as typed |
| `seed` | The seed value, **public seeds only**. A held-out sample has no `seed` key |
| `skin` | The skin name |
| `engine_hash`, `generator_version`, `numpy_version` | From the engine, see [engine hash](../engine/config.md#engine-hash) |
| `prompt_hash` | The skin's hash, from the skins layer, see [names from the skins layer](README.md#names-from-the-skins-layer) |
| `release` | `load_grid().release`, see [release](#release) |
| `harness_version` | The `paranoid` package version, with the short git SHA when run from a checkout, as `0.1.0+2f13c9a`. The two hashes do not cover the solver, so this is what says which round loop played |
| `rounds`, `inertia`, `own_scale`, `tools`, `warm_up`, `rolling` | The knobs, as resolved. `rounds` is the config's final value |
| `tool_choice` | `any` or `auto`. Written by the solver on round 1 into `state.metadata`, not by the dataset, so the analysis reads it without the store, see [each round](solver.md#each-round) |

- **A held-out seed's value is never in the log.** Not in the metadata, not in the store, not in the score. The store holds `seed_set` and `seed_index`, and `seed()` reads the value from the seed file at run time. The engine is public, so one leaked seed is eight leaked worlds, where a leaked record is one run. A held-out log is still as private as its skin, see [contamination](../../harness/contamination.md#public-and-held-out), and the engine spec says the same, see [timeline](../engine/timeline.md#interface).

### Task settings

- **`solver`** is `round_loop(skin, tools, tool_choice=tool_choice, rolling=rolling)`. **`scorer`** is `gain()`. With `tool_choice` unset the solver picks it from the model, see [each round](solver.md#each-round).
- **`fail_on_error=0.1`** on the task, and **`retry_on_error=1`** on every eval `run` and the pilot cells call. `Task` takes no `retry_on_error`, it is an `eval()` argument, see [checked](#checked). Typed by hand, `inspect eval` needs `--retry-on-error 1`. A model that cannot call the tool never raises, it gives up and is scored, see [giving up](scorer.md#giving-up). So an error is infrastructure: a timeout, a rate limit, a provider down. inspect plays the sample again once, and if more than a tenth of samples still error the eval fails, so a half-empty log cannot pass as a result.
- **Epochs** reduce by `"mean"`. Repeats of a seed are averaged before any metric sees them, see [error bars](../../design/scoring.md#error-bars).
- **`sandbox`** is `("docker", <path>)` whenever `tools` includes `compute`, so at the default, else none. The path is the module's own `compose.yaml`, see [compute](solver.md#compute). A headline run therefore needs Docker, see [running](../../harness/running.md#setup).
- **Skins** load with `load_skins()`, which reads `PARANOID_SKINS` when set. A `skin` that is not loaded raises `ValueError` listing the loaded names.
- **The skin must fit the config.** `paranoid()` raises `ValueError` naming the skin and the scenario when `len(skin.channels) != config.channels` for any scenario it will play. An empty record cannot tell them apart, so this is the one place a mismatch can fail before round 2. The skins side of this duty is [what the harness reads](../skins/README.md#what-the-harness-reads).
- **`tools`** is a comma list drawn from `notes` and `compute`, or `none`. **`tool_choice`** is `any`, `auto` or unset. Anything else raises `ValueError`.

### Store

- **The solver fills the store on round 1** from the sample's metadata: `scenario`, `seed_set`, `seed_index`, `skin` and the knobs. Everything else starts empty. The store repeats the metadata because the tools and the providers see the store and not the sample.
- **`seed()`, `config()`, `timeline()`, `record()` and `game()` are derived**, never stored. `timeline()` caches per `(engine_hash, seed)` in a module-level LRU of 1024 timelines, so forty rounds and the scorer build one timeline and a long eval does not grow without bound. The cache holds timelines, not arrays in the store, so nothing on the timeline reaches the log.
- **`rows` is the record.** `record()` builds a `Record` from them in order. `Game(timeline, record)` validates them, see [starting part way](../engine/game.md#starting-part-way).
- **The store is written to the log by inspect**, so a run can be rebuilt from any round by replaying `rows[:r]` against the timeline.

### Warm up

- **`warm_up="<baseline>:<k>"`** plays `k` rounds of the named baseline before the agent's first round: `play(POLICIES[name](), timeline, max_rounds=k)`, see [play](../engine/game.md#play). Its rows go into `rows` and `warm_up_rounds = k`. `name` is a key of the baselines layer's [`POLICIES`](../baselines/policies.md#policies). Every entry is a class, so it is called with no arguments to build the policy at its defaults. `k` must be at least 1 and below the config's `rounds`, else `ValueError`.
- **Under an `inertia` cap the warm up plays with the cap cleared**, on a timeline made from the config with `inertia_cap` set to `None`, as the scorer's baselines do, see [scoring one run](scorer.md#scoring-one-run). The baselines move whole budgets, so under a cap they would raise on their first move. The agent's own rounds keep the cap.
- **The agent then plays rounds `k + 1` to `rounds`.** Its round 1 user message shows `k` rows it did not place, see [user message](../../harness/prompts.md#user-message).
- **Warm up rows score nothing** for the agent, and the baselines it is scored against are summed over the same rounds it played, see [scoring one run](scorer.md#scoring-one-run).
- The warm up check is in [provider checks](../../pilot/provider-checks.md#warm-up).

## Invariants

- The same task args give the same dataset, with the same ids in the same order.
- Every sample's `engine_hash` equals `engine_hash(store.config())` once the store is filled.
- `RunStore` has no field that holds an array, a timeline, a level the agent did not see, or a held-out seed's value.
- `len(store.rows) ≤ store.config().rounds` at all times, and equals it unless the run gave up.
- `store.round() == len(store.rows) + 1`.

## Not decided

- Whether `seeds` should also take a held-out range, such as `held-out:0-4`, for a cheap check on the private set. Not needed for the pilot.
- **What a release freezes beyond its name.** Whether the held-out seed file should name its release so a stale file fails to load, which models are the anchor models, and how the two-setting overlap between adjacent releases is checked, see [noise threshold](../../design/scoring.md#noise-threshold). Decide before the second release, as one release has nothing to join.

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289, with a stub provider and no key.

| Question | Answer |
|---|---|
| Does a solver's write to `state.metadata` land in the log's `sample.metadata` | Yes, beside the keys the dataset set. So the solver writes `tool_choice` there and the task resolves nothing |
| Does `Task` take `retry_on_error` | No. It is an argument of `eval()`, and `Task` drops it with no error. `fail_on_error` is a `Task` argument |
| What `-T scenario=a,b` passes | A list, `["a", "b"]`. inspect splits a comma value before the task sees it |
