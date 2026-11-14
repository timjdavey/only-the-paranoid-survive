# Tests

Every test the harness suite runs, in `tests/harness/`. Ids start `H` for the harness, then the page's letter, see [test ids](../README.md#rules). They need no key and no network: LLM calls go through `mockllm/model` with scripted outputs, baselines through the baseline provider, and Jev and Timestral through fakes. The forecast rules themselves are tested in the [baselines suite](../baselines/tests.md#forecast), and the forecast policies and the real Timestral in the [forecasters suite](../forecasters/tests.md). Tests marked **sandbox** need Docker. They are skipped by default, run with `-m sandbox`. The skins layer's `example` skin is the skin throughout, bar HM14, which copies it under two more names. Every `mockllm` test passes `tools="none"` unless marked **sandbox**, so the suite needs no Docker. HM6, HM11 to HM14, HP5, HP7 and HP15 run evals at the default tools, as `run` and the cells do, so a fixture wraps `inspect_ai.eval` to add `sandbox="local"` to them. Tests that read `configs/` move the working directory with `monkeypatch.chdir`.

- **One test-only switch.** `PARANOID_PILOT_SEEDS` caps the seed count a pilot cell runs, for the pilot tests below. It is the only test hook in the harness. Keep it that way.

## Task

| Id | Test | Page |
|---|---|---|
| HK1 | `paranoid()` at the defaults has `8 × len(public seeds)` samples, ids `<scenario>/<position>` in `SCENARIOS` order then file order, and every metadata key in the dataset table | [task](task.md#dataset) |
| HK2 | `scenario="one_shock,down_switch"` gives two scenarios' samples. `scenario="nope"` raises `ValueError` naming it | [task](task.md#scenarios-and-config) |
| HK3 | `scenario_config("one_shock", rounds=20)` has `rounds == 20` and a different hash from `SCENARIOS["one_shock"]`. `own_scale=2.0` sets `pin_in_level_points` and `inertia=10` sets `inertia_cap`. Each sample's `engine_hash` equals the hash of its resolved config | [task](task.md#scenarios-and-config) |
| HK4 | `parse_seeds("0-4")` returns positions 0 to 4 with the file's seeds. `"3"` returns one. `"0-1,4"` returns three in position order. `"4-2"`, `"1,1"`, a position past the end, and `"held-out"` with `PARANOID_SEEDS` unset raise `ValueError`, the last naming the variable | [task](task.md#seeds) |
| HK5 | A seed file with a comment, a blank line and a repeated seed: the first two are skipped, the third raises `ValueError` | [task](task.md#seeds) |
| HK6 | `PARANOID_SEEDS` pointing at a temp folder with a `held-out.txt`: `seeds="held-out"` reads it, metadata has `seed_set == "held-out"` and the right `seed_index` and no `seed` key, and the seed value appears nowhere in the log. Every scenario's sample at position `i` plays the same seed | [task](task.md#seeds) |
| HK7 | `skin="nope"` raises `ValueError` listing `example`. `tools="laser"` and `tool_choice="laser"` each raise `ValueError`. `scenario="../x"` raises before any path is built | [task](task.md#task-settings) |
| HK8 | The task has `fail_on_error == 0.1`, and the eval call `run` and the cells share passes `retry_on_error=1`. The default `tools` is `notes,compute`. `sandbox` is set at the default and whenever `tools` includes `compute`, not at `tools="none"`, and its path exists | [task](task.md#task-settings) |
| HK9 | `warm_up="complacent:5"` played with `baseline/uniform`: the store has `warm_up_rounds == 5`, the first five rows equal `play(complacent, timeline, max_rounds=5)`, and the round 1 user message has six lines. `"complacent:0"`, `"complacent:40"` and `"nope:5"` raise `ValueError` | [task](task.md#warm-up) |
| HK10 | Every sample's `prompt_hash` equals the skins layer's `prompt_hash(skin)`, and `harness_version` is a non-empty string | [task](task.md#dataset) |
| HK11 | `RunStore` has no field whose type is an array or a `Timeline`, and no `seed` field, checked over `model_fields`. `store.timeline()` twice is the same object | [task](task.md#store) |
| HK12 | `load_grid()` on `configs/grid.toml` gives positive floats in `own_scale` that include the default, and `scenario_config(name, own_scale=s)` raises nothing for every scenario and every setting. A temp grid with a setting of 0 raises `ValueError` | [task](task.md#scenarios-and-config) |
| HK13 | With `PARANOID_SKINS` pointing at a folder holding a clean four-name skin, `paranoid(skin=<its name>)` raises `ValueError` naming the skin and a scenario, before any sample is built | [task](task.md#task-settings) |
| HK14 | Every sample's `release` equals `load_grid().release`, which is `dev` in this repo. A temp grid whose `release` is `R 1` raises `ValueError` | [task](task.md#release) |
| HK15 | `paranoid(seeds=3)` plays position 3, as `seeds="3"` does, and `scenario` and `tools` given as one-item lists work too | [task](task.md#scenarios-and-config) |
| HK16 | With `subprocess.run` patched, `harness_version()` is `<version>+<sha>` when `git status --porcelain -- src/paranoid` prints nothing and `<version>+<sha>.dirty` when it prints a line | [task](task.md#dataset) |
| HK17 | With `INSPECT_TRACEBACK_LOCALS=1`, `paranoid(seeds="held-out")` raises `ValueError` naming the variable, and `paranoid(seeds="0")` does not | [task](task.md#dataset) |

## Solver

| Id | Test | Page |
|---|---|---|
| HS1 | A full run with `baseline/uniform` on one seed: `len(rows) == rounds`, every `tries` entry is 1, and the rows equal `play(uniform, timeline)` | [solver](solver.md#each-round) |
| HS2 | `mockllm` scripted to a valid call every round: the messages at the start of round 2 are exactly a system and a user message, and the user message is `render_record` of a one-row record | [solver](solver.md#each-round) |
| HS3 | `mockllm` scripted to a bad call then a valid one: `bad_calls == 1`, `tries == [2, 1, …]`, the round 1 messages before the valid call hold a tool message with `skin.bad_call`, and the round still played once | [solver](solver.md#tries) |
| HS4 | `mockllm` scripted to text with no call then a valid one: `no_calls == 1` and a user message of `skin.no_call` was appended | [solver](solver.md#tries) |
| HS5 | A reply with `stop_reason == "max_tokens"` adds one to `cut_offs` and one to `no_calls` | [solver](solver.md#tries) |
| HS6 | Ten bad calls in a row: the solver returns with `gave_up` true, `tries == [10]`, ten bad calls, no rows, `awaiting_submit` false, and the sample has a score | [solver](solver.md#tries) |
| HS7 | Bets of `[10.0] × 10` and `["10"] × 10` get `bad_call` as the tool message's `content`, with no `error`, and each adds one to `bad_calls`. `[10] × 10` plays. A call to a tool that does not exist gets `no_call`. Neither the engine's own message nor inspect's appears anywhere in the messages | [solver](solver.md#submit) |
| HS8 | Two submit calls in one reply: the first plays, the second gets `bad_call`, `len(rows) == 1` and `bad_calls == 1` | [solver](solver.md#submit) |
| HS9 | The tool result on a valid call equals the header and last line of `render_record(skin, record)` | [solver](solver.md#submit) |
| HS10 | `tool_choice="any"` sets `state.tool_choice` to `"any"`, never a `ToolFunction`. `"auto"` sets `"auto"`. With `None`, `store.tool_choice` and `state.metadata["tool_choice"]` hold the resolved value, and it is in the log's sample metadata. The submit tool is `state.tools[0]` and carries the skin's name, text and parameter text | [solver](solver.md#each-round) |
| HS11 | `tools="notes"`: a call to the notes tool with `"abc"` under `skin.notes_param`, then a valid submit. Round 2's user message has two content blocks, the second `"abc"`. A 3000 character note is stored as 2000. A round that called only `notes` counts a no call. Two `notes` calls in round 1 and one in round 2 give `notes_rounds == 2` | [solver](solver.md#notes) |
| HS12 | **sandbox** `tools="compute"`, every call under `skin.compute_param`: `print(open('record.csv').read())` returns the record CSV. `import socket; socket.create_connection(('1.1.1.1', 80))` returns an error, not a connection. A sleep of 60 seconds returns `timeout`. A loop that appends to a list forever ends with Python's `MemoryError` inside the timeout, and `os.environ` holds only the names the image sets itself, so nothing from the host and no key. Two `compute` calls in one round give `compute_rounds == 1` | [solver](solver.md#compute) |
| HS13 | `rolling=True`: at round 3 the messages hold every earlier assistant and tool message in order, the first two messages equal a fresh call's, and the last user message equals `render_record` of the two-row record, as HS2's would | [solver](solver.md#rolling) |
| HS14 | Replaying `store.rows` as bets with `Game` on `store.timeline()` gives equal readings, and so an equal `row.output` on every row | [solver](solver.md#invariants) |
| HS15 | A lint over every message a `mockllm` run produced finds no banned word, with the example skin | [prompts](../../harness/prompts.md#banned-words) |
| HS16 | `tool_choice_for("anthropic", GenerateConfig(reasoning_effort="low"))` is `"auto"`. `("anthropic", GenerateConfig(reasoning_tokens=1024))` is too. `("anthropic", GenerateConfig())`, `("anthropic", GenerateConfig(reasoning_effort="none"))` and `("openai", GenerateConfig(reasoning_effort="high"))` are `"any"` | [solver](solver.md#each-round) |
| HS17 | `record_blocks` on `render_record` of a three-row record returns four pieces, the header line then one per row, that join back to the same string. `BLOCK_CACHE_APIS` is `("anthropic",)`, and a `mockllm` run sends the record as one content block. With `BLOCK_CACHE_APIS` patched to `("mockllm",)`, the round 3 user message has three record blocks, and four content blocks once a note is saved, the note last | [solver](solver.md#record-blocks) |
| HS18 | With a copy of the example skin whose `bets_name` is `amounts`, the tool the model is offered has one required parameter named `amounts`, an array of integers, described by `bets_text`. A call of `{"amounts": [10] × 10}` plays the round. A call of `{"bets": [10] × 10}` gets `bad_call` and plays nothing. With `notes_param` of `memo` and `compute_param` of `script`, the other two tools each offer one required string parameter of that name, described by `notes_param_text` and `compute_param_text`, and the tool itself by `notes_text` and `compute_text` | [solver](solver.md#submit) |
| HS19 | `compute(skin)` on inspect's `local` sandbox, so it runs without Docker: `print(1 + 1)` returns `2`, code that raises returns its traceback, a sleep past a patched one second timeout returns `timeout`, and output past 4000 characters is cut to 4000. Two calls in one round give `compute_rounds == 1`, and the round's `record.csv` holds `render_record` of the record | [solver](solver.md#compute) |
| HS20 | Compute on the `local` sandbox, so it runs without Docker. Round 1's first call writes `mem.txt`, `.mem` and `d/f`, and a second call in round 1 still lists them. Round 2 lists only `record.csv`. A reset whose sandbox command fails raises `RuntimeError` | [solver](solver.md#compute) |
| HS21 | **sandbox** Round 1 plants a file in `/work`, `/tmp` and `/dev/shm`, a SysV shared memory segment and a detached process listening on `127.0.0.1`. A second call in round 1 finds all five, so the plants worked. Round 2 finds none of them, `os.getuid()` is 65534, and opening `record.csv` to write raises | [solver](solver.md#compute) |
| HS22 | Compute on a fake sandbox whose `exec` raises `PermissionError` with a path in its message: the sample errors with a `RuntimeError` naming the tool and `permission`, and the path is not in the error. Unpatched, code that writes bytes that are not UTF-8 returns text and the sample succeeds | [solver](solver.md#refused-calls) |
| HS23 | `record_blocks` on text holding `\x0b` and U+2028 cuts at `\n` alone, and the pieces join back to the text. Text with no last `\n` keeps its last piece | [solver](solver.md#record-blocks) |
| HS24 | A reply with `stop_reason == "model_length"` adds one to `cut_offs` and one to `no_calls`, as HS5's `max_tokens` does | [solver](solver.md#tries) |

## Providers

| Id | Test | Page |
|---|---|---|
| HR1 | `get_model("baseline/<name>")` resolves for all seven names. `baseline/nope` raises `ValueError` naming the seven | [providers](providers.md#registration) |
| HR2 | Every provider's `generate` returns one tool call to `tools[0].name` whose one argument is a list of bets under the skin's `bets_name`, and `content == ""`, its `id` is `<model name>-<round>`, and its usage is zero tokens. With `tools == []` it raises `RuntimeError` | [providers](providers.md#shared-behaviour) |
| HR3 | A full eval of `baseline/<name>` on 5 seeds of Down switch, for each of the seven, has rows equal to `play(policy, timeline)` | [providers](providers.md#baseline) |
| HR4 | `baseline/hedge_rule` with `model_args={"explore": "1", "window": "4"}` builds `HedgeRule(explore=1, window=4)`, the strings cast. `{"nope": "1"}` and `baseline/uniform` with `{"explore": "1"}` raise `ValueError` | [providers](providers.md#baseline) |
| HR5 | A fake async `JevClient` recording its calls: the state equals the system text, two newlines, the user text. The question and options are the skin's. Probabilities `[0.5, 0.5, 0, …]` give bets `[50, 50, 0, …]`, and `[0.004, 0.996, 0, …]` give `[0, 100, 0, …]`. Nine probabilities raise `ValueError` | [providers](providers.md#jev) |
| HR6 | The Jev message's `metadata` holds `probabilities`, `confidence` and `raw` | [providers](providers.md#jev) |
| HR7 | A full eval of `timestral/<id>` with a fake `Forecaster`, for each of the seven, on 3 seeds of Down switch: its rows equal `play(replace(TIMESTRAL_POLICIES[id], forecaster=fake), timeline)`. Every message's `metadata` holds `quantiles`, `cache_key` and `rounded_out`, with `quantiles` and `cache_key` `None` on round 1. `timestral/nope` raises `ValueError` naming the seven | [providers](providers.md#timestral) |
| HR8 | Without the extra, `TimestralAPI("top-pick")` raises `ImportError` naming `uv sync --extra timestral`, and with a fake `Forecaster` passed it does not | [providers](providers.md#timestral) |
| HR9 | `BaselineAPI` reports `max_connections` of 32, a `JevAPI` with a fake client 4, and a `TimestralAPI` with a fake forecaster 1 | [providers](providers.md#shared-behaviour) |
| HR10 | A policy that bets 110 in all, patched into the baseline provider's copy of `POLICIES`, which is read only: an eval of it errors the sample with a `RuntimeError` naming the model and round 1. `gave_up` is unset and `bad_calls` is 0 | [providers](providers.md#shared-behaviour) |
| HR11 | `endpoint_of("decisionmodels/s1-fast-2")` is `(ENDPOINTS["decisionmodels"], "s1-fast-2")` and `endpoint_of("jev-latest")` is `(TYPESAFE, "jev-latest")`. `JevAPI("nope/x", client=FakeJev())` raises `ValueError` naming `decisionmodels` | [providers](providers.md#jev) |
| HR12 | With `TYPESAFE_API_KEY` set and `DECISIONMODELS_API_KEY` unset, a `TypesafeClient` for `ENDPOINTS["decisionmodels"]` raises `ValueError` naming `DECISIONMODELS_API_KEY` on `ask`. With both set and `TYPESAFE_BASE_URL` set too, the SDK client its `sdk()` builds has Decision Models' base URL and key and the `S1-Region: eu` header. Nothing is sent | [providers](providers.md#jev) |

## Scorer

| Id | Test | Page |
|---|---|---|
| HO1 | `baseline/uniform` on 5 seeds of every scenario scores `gain == 0`, and `baseline/discerning` scores `gain == gap`, exactly | [scorer](scorer.md#invariants) |
| HO2 | A run with `warm_up="complacent:5"`: `output` sums rows 6 on, `rounds == 35`, and every baseline value equals `play(policy, timeline, record=warm_up)` summed over the same rows. `warm_up_kept` is 1 when the agent's first split is row 5's and 0 when it is not, and `None` on a run with no warm up | [scorer](scorer.md#scoring-one-run) |
| HO3 | `Score.value` has every key in the table, `retries == sum(tries) − len(tries)`, `gave_up == 0` and `run_score == gain / gap`. On a `baseline/uniform` run of Down switch `explore_points == 90`, `sleeper_round` is the switch's onset on a seed whose `kind` is `fall_and_rise` and empty on a `fall` seed, and `notes_rounds == compute_rounds == 0` | [scorer](scorer.md#scoring-one-run) |
| HO4 | `pooled_score([880, 220], [1100, 550])` is `0.6666…` and not `0.6`. Empty input and a zero gap sum raise `ValueError` | [scorer](scorer.md#pooling) |
| HO5 | `bootstrap` with one seed returns `(score, score)`. Twice with the default rng gives equal bars. With 100 seeds of gains drawn around 0.7 the bar contains 0.7. `draws_of` with a fresh `default_rng(BOOTSTRAP_SEED)` returns `BOOTSTRAP_DRAWS` values whose 2.5th and 97.5th percentiles are that bar | [scorer](scorer.md#pooling) |
| HO6 | `scenario_score` on hand-built `SampleScore`s for two scenarios returns the pooled score, `lo ≤ score ≤ hi`, `n` and `failed == 0` for each | [scorer](scorer.md#scenario-score) |
| HO7 | A run that gave up at round 3: `gave_up == 1`, `gain == 0`, `run_score == 0`, `output` is the two rows' sum, `rounds == 3`, and the baselines are summed to the end of the run. `scenario_score` over it and two scored seeds has `failed == 1`, `n == 3`, and equals the pooled score with its gain at 0 | [scorer](scorer.md#giving-up) |
| HO8 | `headline` on hand-built scores for eight scenarios is their mean, `scenarios == 8`, and `lo ≤ headline ≤ hi`. With three scenarios `scenarios == 3` | [scorer](scorer.md#headline) |
| HO9 | `weakest_trait` returns one key, the lowest scenario's trait, holding its score, and `TRAITS` has the eight pairs | [scorer](scorer.md#weakest-trait) |
| HO10 | `retry_share` on a run with `tries == [1, 2, 1, 3]` and 4 rounds is `0.5`, a run that gave up with `tries == [1, 1, 10]` is `1/3`, and `cut_off_share` counts `cut_offs` only | [scorer](scorer.md#retry-share) |
| HO11 | `Score.answer` equals `render_record(skin, store.record())` and `Score.metadata` has `scenario`, `seed_set`, `seed_index` and `engine_hash`, with `seed` on a public sample only | [scorer](scorer.md#interface) |
| HO12 | The metrics on a log give the same numbers with `PARANOID_SEEDS` unset and the public seed file moved away | [scorer](scorer.md#giving-up) |
| HO13 | `tool_use_share` on hand-built scores with `notes_rounds` 4 and 0 and `compute_rounds` 0 and 0 over `rounds` 40 and 40 is `{"notes": 0.05, "compute": 0}` | [scorer](scorer.md#tool-use-share) |

## Command

| Id | Test | Page |
|---|---|---|
| HM1 | `load_models` on `configs/models/poc.toml` and `full.toml` raises nothing, and every row has a `kind`, a `reasoning_kind` and at least one `reasoning` value | [command](command.md#models-config) |
| HM2 | Each validation clause raises `ValueError` naming the row: a bad `kind`, `baseline/x` with `kind = "llm"`, `reasoning = "xhigh"`, a provider row with `reasoning = "low"`, `reasoning_kind = "lots"`, a duplicate `id` and setting, `max_tokens = 0`, `pilot = "no"` | [command](command.md#models-config) |
| HM3 | `generate_config` for `on` and `n/a` sets nothing. `off` sets `reasoning_effort="none"` and no `reasoning_tokens`, for an `openai/` row and for a row with `reasoning_kind = "budget"`, so on any `llm` row no two settings give equal configs. `high` sets `reasoning_effort="high"` for an `openai/` row and `reasoning_tokens` of `BUDGETS["high"]`, 16384, for a row with `reasoning_kind = "budget"`. `max` sets `reasoning_effort="max"` for an `anthropic/` row, never `"xhigh"`. `max_tokens` from the row lands in the config. `temperature` and `cache_prompt` are never set | [command](command.md#reasoning) |
| HM4 | `reasoning_kind` defaults to `effort` for `anthropic/x` and `budget` for `together/x`, and the file's column wins over the prefix | [command](command.md#models-config) |
| HM5 | `main(["run", "--dry-run"])` returns 0, prints one line per row and setting with provider rows first, and calls `eval` zero times | [command](command.md#run) |
| HM6 | `main(["run", "--models", <a temp file with one baseline/uniform row>, "--limit", "2"])` runs one eval into a temp log dir whose log has two samples and the metadata keys | [command](command.md#run) |
| HM7 | `main(["nope"])` returns 1 and prints the known subcommands. A fake entry point in `paranoid.commands` is listed and called | [command](command.md#subcommands) |
| HM8 | `main(["pilot", "baseline-order", "--out", tmp, "--seeds", "5"])` calls `run_cell` with a `CellArgs` holding those values and returns 0. `main(["pilot", "nope"])` returns 1 and prints the twenty-one names | [command](command.md#pilot) |
| HM10 | `main(["run", "--only", "baseline/uniform", "--dry-run"])` on a two-row file prints that row's line only | [command](command.md#run) |
| HM11 | Without the timestral extra, a models file with a `timestral/top-pick` row then a `baseline/uniform` row: `run` prints one line saying the Timestral row is skipped, runs the baseline eval, and returns 0 | [command](command.md#run) |
| HM12 | A models file with an `llm` row whose `id` names a provider inspect cannot resolve, then a `baseline/uniform` row: `run` runs the baseline eval anyway and returns 1 | [command](command.md#run) |
| HM13 | The log HM6 writes has `eval.metadata["reasoning"] == "n/a"` and `eval.metadata["kind"] == "baseline"` | [command](command.md#run) |
| HM14 | With `PARANOID_SKINS` at a temp folder holding `example.toml` copied to `a.toml` and `b.toml`, and a models file with a `baseline/uniform` row then an `llm` row: `main(["run", "--skins", "a,b", "--dry-run"])` prints the baseline row once, on `a`, then the LLM row on `a` and on `b` in that order. Without `--dry-run` and with the baseline row alone, the one log's samples have `skin == "a"` | [command](command.md#run) |
| HM15 | `main(["run", "--skins", "nope"])` and `main(["run", "--skins", "example,example"])` each return 1, print the loaded names and `PARANOID_SKINS`, and call `eval` zero times | [command](command.md#run) |
| HM16 | With a temp grid of two settings, `main(["run", "--own-scale", "grid", "--dry-run"])` on a one-row file prints two eval calls, one per setting in file order, each with that `own_scale` in its task args. `--own-scale 6` prints one. `--own-scale 0` and `--own-scale lots` each return 1 and call `eval` zero times | [command](command.md#run) |

## Pilot

Every cell runs with `PARANOID_PILOT_SEEDS=5` into a temp `out`, so the fixture seeds are positions 0 to 4.

| Id | Test | Page |
|---|---|---|
| HP1 | Each engine cell writes its CSV with exactly the columns in its Writes line, in order, and one row per seed per setting per scenario per baseline as its Runs line says. `timeline-sanity` also writes the sparklines file with one row per scenario and round. The network is blocked by a socket monkeypatch throughout. `bayesian-frontier` has a row per seed, scenario and each of its five players and five fixed baselines. The `game-length` case is **slow**, as it takes a minute at five seeds | [pilot](pilot.md#engine-cells) |
| HP2 | `CELLS` has the twenty-one names in page order. `run_cell("nope", args)` raises `ValueError` listing them | [pilot](pilot.md#invariants) |
| HP3 | `seeds=20` against a public seed file of ten raises `ValueError` naming `PARANOID_PILOT_SEEDS` | [pilot](pilot.md#shared-rules) |
| HP4 | In `baseline-order.csv`, `kind` on every Down switch row equals the word `make_timeline` gives by hand, `discerning`'s `move_round` lies within the switch's ramp, from its onset to `onset + ramp − 1`, on every Down switch seed, as its base falls past the next one's during the ramp, and is `0` on every No change seed, and `complacent`'s `move_round` is `0` everywhere | [pilot](pilot.md#words-the-columns-use) |
| HP5 | `seeds` with a models file whose one `llm` row is `mockllm/model` writes one log under `out/seeds/` with twenty `one_shock` and twenty `up_switch` samples and `reasoning` and `kind` in the eval metadata. `repeats` then writes a log under `out/repeats/` with ten sample ids of one scenario at four epochs each and prints the row, the scenario and the ten positions. `repeats` with no `seeds` log raises `ValueError` naming `seeds` | [pilot](pilot.md#provider-cells) |
| HP6 | `recognition` with `mockllm/model` scripted to three replies, one holding a banned word and one the GUID, writes a CSV with the six columns and three rows per model and skin, `lint_hits` of 1 on the first, `canary_finished` of 1 on the canary row only, and the GUID appears in no message the fake received. With two `llm` rows in the models file the CSV has both models' rows, and `--only` runs one and keeps the other's rows, see HP17 | [pilot](pilot.md#recognition) |
| HP7 | `jev` with a fake client that answers `[0.004, 0.996, 0, …]` on round 3 writes a log and a `jev.csv` whose round 3 rows have `rounded_out` 1 and every other row 0 | [pilot](pilot.md#jev) |
| HP8 | `timestral` with a fake forecaster writes `timestral.csv` with thirty `gap` rows per channel and shape, `spread` non-decreasing in `gap` when the fake widens with the gap, and one `determinism` row per shape with `equal` 1. `timestral-grid.csv` has one row per row, setting, scenario and seed, and `timestral-rounding.csv` one per round of each. It writes no eval log | [pilot](pilot.md#timestral) |
| HP9 | `dry_run=True` on every cell writes nothing under `out` and prints one line per eval call or CSV | [pilot](pilot.md#shared-rules) |
| HP10 | `channel-order` with `mockllm/model` scripted to send the split asked for on every probe but three, one `one` probe with its 100 a place late, one split summing to 90 and one reply with no call, writes a CSV with the ten columns and thirty rows per model and skin. `matched` is 1 on twenty-seven rows, `slipped` is 1 on the late row only, the split of 90 has `called` 1 and `valid` 0, the reply with no call has `called` 0, and `matched`, `slipped` and `sent` are empty on both. Each request the fake received names its channels in the order the shape's table gives, and no channel name is in the file | [pilot](pilot.md#channel-order) |
| HP11 | In `baseline-order.csv`, `stayer` rows appear only in the Up switch then down switch scenario, one per seed. On every such seed its `move_round` equals `discerning`'s, and its last round's largest bet is on the sleeper. On every seed whose undo ends before the last round, `discerning`'s is back on the leader | [pilot](pilot.md#shared-rules) |
| HP12 | In `tell.csv`, `tell_rounds ≤ fall_rounds` on every row, and both are empty on No change. On every row whose `move_round` is at or after its `onset`, `fall_rounds` is above `tell_rounds`, as the rule only scouts on a fall the tell did not stop | [pilot](pilot.md#tell) |
| HP13 | In `game-length.csv`, `clear_round_1` is set on `discerning` rows only, lies from `onset_1` to the window's end or is `0`, and on a seed where it is above 0 the Discerning baseline's output summed from `onset_1` is above the Complacent baseline's in every round from it to the window's end, played by hand | [pilot](pilot.md#game-length) |
| HP14 | In `reading-roughness.csv` there is one `complacent` row per setting, scenario and seed, with `parameter` and `scout_rounds` empty and `move_round` of `0` | [pilot](pilot.md#reading-roughness) |
| HP15 | `seeds` with `mockllm/model` scripted to one reply with no call writes `seeds-tokens.csv` with the eight columns and one row per round of every sample. The round that took two tries has the sum of two events' `input_tokens`, and every row's `rolling` is 0. `rolling` writes `rolling-tokens.csv` with rows at both values | [pilot](pilot.md#token-files) |
| HP16 | `luck` and `baseline-order` each write the same bytes at `workers=2` as at `workers=1`. `workers=0` raises `ValueError` | [pilot](pilot.md#shared-rules) |
| HP17 | `write_csv` with `--only b` on a file holding rows of models `a` and `b` keeps `a`'s rows and replaces `b`'s. Without `--only` it replaces the file. With `--only` and a file whose header differs it raises `ValueError` | [pilot](pilot.md#shared-rules) |
| HP18 | `write_csv` whose `rows()` raises part way leaves the old file byte for byte, and no temp file beside it | [pilot](pilot.md#shared-rules) |
| HP19 | `widest` over fake seeds logs: a log whose status is `error` is skipped, an older log of the same model and reasoning is skipped for the newer one, and a scenario of five scored samples is skipped, however wide its spread | [pilot](pilot.md#repeats) |
| HP20 | `recognition` on a models file of two `llm` rows, the second with `pilot = false`, calls and writes the first row only. `--only` naming the second raises `ValueError` naming it | [pilot](pilot.md#shared-rules) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| HY1 | For any list of non-negative gains and positive gaps, `pooled_score` lies between the smallest and largest run score |
| HY2 | For any valid split, a scripted `mockllm` call with it plays the round, and the stored row's `None`s match its zeros |
| HY3 | For any probabilities that sum to 1, the Jev bets sum to the budget and have one entry per channel |

## Not decided

- HS12 and HS21 need Docker on CI. Until CI has it, the sandbox tests run locally only. Decide when CI is set up.
