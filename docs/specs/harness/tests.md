# Tests

Every test the harness suite runs, in `tests/harness/`. Ids start `H` for the harness, then the page's letter, see [test ids](../README.md#rules). They need no key and no network: LLM calls go through `mockllm/model` with scripted outputs, baselines through the baseline provider, and Jev and Timestral through fakes. The forecast rules themselves are tested in the [baselines suite](../baselines/tests.md#forecast). Tests marked **sandbox** need Docker and tests marked **timestral** need the extra. Both are skipped by default, run with `-m sandbox` or `-m timestral`. The skins layer's `example` skin is the skin throughout.

- **One test-only switch.** `PARANOID_PILOT_SEEDS` caps the seed count a pilot cell runs, for HM8. It is the only test hook in the harness. Keep it that way.

## Task

| Id | Test | Page |
|---|---|---|
| HK1 | `paranoid()` at the defaults has `8 × len(public seeds)` samples, ids `<scenario>/<position>` in `SCENARIOS` order then file order, and every metadata key in the dataset table | [task](task.md#dataset) |
| HK2 | `scenario="one_shock,down_switch"` gives two scenarios' samples. `scenario="nope"` raises `ValueError` naming it | [task](task.md#scenarios-and-config) |
| HK3 | `scenario_config("one_shock", rounds=20)` has `rounds == 20` and a different hash from `SCENARIOS["one_shock"]`. `own_scale=2.0` sets `pin_in_level_points` and `inertia=10` sets `inertia_cap`. Each sample's `engine_hash` equals the hash of its resolved config | [task](task.md#scenarios-and-config) |
| HK4 | `parse_seeds("0-4")` returns positions 0 to 4 with the file's seeds. `"3"` returns one. `"4-2"`, a position past the end, and `"held-out"` with `PARANOID_SEEDS` unset raise `ValueError`, the last naming the variable | [task](task.md#seeds) |
| HK5 | A seed file with a comment, a blank line and a repeated seed: the first two are skipped, the third raises `ValueError` | [task](task.md#seeds) |
| HK6 | `PARANOID_SEEDS` pointing at a temp folder with a `held-out.txt`: `seeds="held-out"` reads it, metadata has `seed_set == "held-out"` and the right `seed_index` and no `seed` key, and the seed value appears nowhere in the log. Every scenario's sample at position `i` plays the same seed | [task](task.md#seeds) |
| HK7 | `skin="nope"` raises `ValueError` listing `example`. `tools="laser"` raises `ValueError`. `scenario="../x"` raises before any path is built | [task](task.md#task-settings) |
| HK8 | The task has `retry_on_error == 1` and `fail_on_error == 0.1`. `sandbox` is set only when `tools` includes `compute`, and its path exists | [task](task.md#task-settings) |
| HK9 | `warm_up="complacent:5"` played with `baseline/uniform`: the store has `warm_up_rounds == 5`, the first five rows equal `play(complacent, tape, max_rounds=5)`, and the round 1 user message has six lines. `"complacent:0"`, `"complacent:40"` and `"nope:5"` raise `ValueError` | [task](task.md#warm-up) |
| HK10 | Every sample's `prompt_hash` equals the skins layer's `prompt_hash(skin)`, and `harness_version` is a non-empty string | [task](task.md#dataset) |
| HK11 | `RunStore` has no field whose type is an array or a `Tape`, and no `seed` field, checked over `model_fields`. `store.tape()` twice is the same object | [task](task.md#store) |
| HK12 | `configs/grid.toml` loads to a list of positive floats that includes the default `own_scale` | [task](task.md#scenarios-and-config) |
| HK13 | With `PARANOID_SKINS` pointing at a folder holding a clean four-name skin, `paranoid(skin=<its name>)` raises `ValueError` naming the skin and a scenario, before any sample is built | [task](task.md#task-settings) |

## Solver

| Id | Test | Page |
|---|---|---|
| HS1 | A full run with `baseline/uniform` on one seed: `len(rows) == rounds`, every `tries` entry is 1, and the rows equal `play(uniform, tape)` | [solver](solver.md#each-round) |
| HS2 | `mockllm` scripted to a valid call every round: the messages at the start of round 2 are exactly a system and a user message, and the user message is `render_record` of a one-row record | [solver](solver.md#each-round) |
| HS3 | `mockllm` scripted to a bad call then a valid one: `bad_calls == 1`, `tries == [2, 1, …]`, the round 1 messages before the valid call hold a tool message with `skin.bad_call`, and the round still played once | [solver](solver.md#tries) |
| HS4 | `mockllm` scripted to text with no call then a valid one: `no_calls == 1` and a user message of `skin.no_call` was appended | [solver](solver.md#tries) |
| HS5 | A reply with `stop_reason == "max_tokens"` adds one to `cut_offs` and one to `no_calls` | [solver](solver.md#tries) |
| HS6 | Ten bad calls in a row: the solver returns with `gave_up` true, `tries == [10]`, ten bad calls, no rows, `awaiting_submit` false, and the sample has a score | [solver](solver.md#tries) |
| HS7 | Bets of `[10.0] × 10` and `["10"] × 10` get `bad_call`. `[10] × 10` plays. The engine's own message appears nowhere in the messages | [solver](solver.md#submit) |
| HS8 | Two submit calls in one reply: the first plays, the second gets `bad_call`, `len(rows) == 1` and `bad_calls == 1` | [solver](solver.md#submit) |
| HS9 | The tool result on a valid call equals the header and last line of `render_record(skin, record)` | [solver](solver.md#submit) |
| HS10 | `tool_choice="forced"` sets `state.tool_choice` to `ToolFunction(skin.tool_name)`. `"auto"` sets `"auto"`. With `None`, `store.tool_choice` holds the resolved value. The submit tool is `state.tools[0]` and carries the skin's name, text and parameter text | [solver](solver.md#each-round) |
| HS11 | `tools="notes"`: a `notes("abc")` call then a valid submit. Round 2's user message has two content blocks, the second `"abc"`. A 3000 character note is stored as 2000. A round that called only `notes` counts a no call | [solver](solver.md#notes) |
| HS12 | **sandbox** `tools="compute"`: `compute("print(open('record.csv').read())")` returns the record CSV. `compute("import socket; socket.create_connection(('1.1.1.1', 80))")` returns an error, not a connection. A sleep of 60 seconds returns `timeout`. A loop that appends to a list forever ends with an error inside the timeout, and `os.environ` holds no key | [solver](solver.md#compute) |
| HS13 | `rolling=True`: at round 3 the messages hold every earlier assistant and tool message, and the last user message is the header and one row | [solver](solver.md#rolling) |
| HS14 | Replaying `store.rows` as bets with `Game` on `store.tape()` gives equal readings and outputs | [solver](solver.md#invariants) |
| HS15 | A lint over every message a `mockllm` run produced finds no banned word, with the example skin | [prompts](../../harness/prompts.md#banned-words) |
| HS16 | `tool_choice_for("anthropic", GenerateConfig(reasoning_effort="low"))` is `"auto"`. `("anthropic", GenerateConfig())` and `("openai", GenerateConfig(reasoning_effort="high"))` are `"forced"` | [solver](solver.md#each-round) |

## Providers

| Id | Test | Page |
|---|---|---|
| HR1 | `get_model("baseline/<name>")` resolves for all six names. `baseline/nope` raises `ValueError` naming the six | [providers](providers.md#registration) |
| HR2 | Every provider's `generate` returns one tool call to `tools[0].name` with a `bets` list and `content == ""`, its `id` is `<model name>-<round>`, and its usage is zero tokens. With `tools == []` it raises `RuntimeError` | [providers](providers.md#shared-behaviour) |
| HR3 | A full eval of `baseline/<name>` on 5 seeds of Down switch, for each of the six, has rows equal to `play(policy, tape)` | [providers](providers.md#baseline) |
| HR4 | `baseline/hedge_rule` with `model_args={"explore": "1", "window": "4"}` builds `HedgeRule(explore=1, window=4)`, the strings cast. `{"nope": "1"}` and `baseline/uniform` with `{"explore": "1"}` raise `ValueError` | [providers](providers.md#baseline) |
| HR5 | A fake async `JevClient` recording its calls: the state equals the system text, two newlines, the user text. The question and options are the skin's. Probabilities `[0.5, 0.5, 0, …]` give bets `[50, 50, 0, …]`, and `[0.004, 0.996, 0, …]` give `[0, 100, 0, …]`. Nine probabilities raise `ValueError` | [providers](providers.md#jev) |
| HR6 | The Jev message's `metadata` holds `probabilities`, `confidence` and `raw` | [providers](providers.md#jev) |
| HR7 | A fake `Forecaster` recording its inputs: round 1 bets are `uniform`'s and it is not called. Round 2's `readings` has shape `(1, channels)` with `NaN` nowhere after a uniform round. After a `top-pick` round it has `NaN` on nine channels. `bets` is `None` except for `odds-bet-aware`. A fake that returns one row with its quantiles reversed gives the same bets as the sorted row | [providers](providers.md#timestral) |
| HR8 | `TIMESTRAL_POLICIES` has the six glossary ids, `odds-bet-aware` maps to `FORECAST_RULES["odds"]` with the flag on, every other id to `FORECAST_RULES[id]` with it off | [providers](providers.md#timestral) |
| HR9 | The Timestral cache: the same fake forecaster input twice calls the fake once and the message `metadata` has the same `cache_key`. `PARANOID_CACHE` pointing at a temp folder is where the file lands | [providers](providers.md#timestral) |
| HR10 | **timestral** The real forecaster on a ten-reading series then thirty `NaN` rows returns widening quantile spreads, and the same input twice is equal | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| HR11 | Without the extra, `TimestralAPI("timestral/top-pick")` raises `ImportError` naming `uv sync --extra timestral` | [providers](providers.md#timestral) |
| HR12 | `BaselineAPI` reports `max_connections` of 32, a `JevAPI` with a fake client 4, and a `TimestralAPI` with a fake forecaster 1 | [providers](providers.md#shared-behaviour) |

## Scorer

| Id | Test | Page |
|---|---|---|
| HO1 | `baseline/uniform` on 5 seeds of every scenario scores `gain == 0`, and `baseline/discerning` scores `gain == gap`, exactly | [scorer](scorer.md#invariants) |
| HO2 | A run with `warm_up="complacent:5"`: `output` sums rows 6 on, `rounds == 35`, and every baseline value equals `play(policy, tape, record=warm_up)` summed over the same rows | [scorer](scorer.md#scoring-one-run) |
| HO3 | `Score.value` has every key in the table, `retries == sum(tries) − len(tries)`, `gave_up == 0` and `run_score == gain / gap` | [scorer](scorer.md#scoring-one-run) |
| HO4 | `pooled_score([880, 220], [1100, 550])` is `0.6666…` and not `0.6`. Empty input and a zero gap sum raise `ValueError` | [scorer](scorer.md#pooling) |
| HO5 | `bootstrap` with one seed returns `(score, score)`. Twice with the default rng gives equal bars. With 100 seeds of gains drawn around 0.7 the bar contains 0.7 | [scorer](scorer.md#pooling) |
| HO6 | `scenario_score` on hand-built `SampleScore`s for two scenarios returns the pooled score, `lo ≤ score ≤ hi`, `n` and `failed == 0` for each | [scorer](scorer.md#scenario-score) |
| HO7 | A run that gave up at round 3: `gave_up == 1`, `gain == 0`, `run_score == 0`, `output` is the two rows' sum, `rounds == 3`, and the baselines are summed to the end of the run. `scenario_score` over it and two scored seeds has `failed == 1`, `n == 3`, and equals the pooled score with its gain at 0 | [scorer](scorer.md#giving-up) |
| HO8 | `headline` on hand-built scores for eight scenarios is their mean, `scenarios == 8`, and `lo ≤ headline ≤ hi`. With three scenarios `scenarios == 3` | [scorer](scorer.md#headline) |
| HO9 | `weakest_trait` names the lowest scenario and its trait, and `TRAITS` has the eight pairs | [scorer](scorer.md#weakest-trait) |
| HO10 | `retry_share` on a run with `tries == [1, 2, 1, 3]` and 4 rounds is `0.5`, a run that gave up with `tries == [1, 1, 10]` is `1/3`, and `cut_off_share` counts `cut_offs` only | [scorer](scorer.md#retry-share) |
| HO11 | `Score.answer` equals `render_record(skin, store.record())` and `Score.metadata` has `scenario`, `seed_set`, `seed_index` and `engine_hash`, with `seed` on a public sample only | [scorer](scorer.md#interface) |
| HO12 | The metrics on a log give the same numbers with `PARANOID_SEEDS` unset and the public seed file moved away | [scorer](scorer.md#giving-up) |

## Command

| Id | Test | Page |
|---|---|---|
| HM1 | `load_models` on `configs/models/poc.toml` and `full.toml` raises nothing, and every row has a `kind`, a `reasoning_kind` and at least one `reasoning` value | [command](command.md#models-config) |
| HM2 | Each validation clause raises `ValueError` naming the row: a bad `kind`, `baseline/x` with `kind = "llm"`, `reasoning = "xhigh"`, a provider row with `reasoning = "low"`, `reasoning_kind = "lots"`, a duplicate `id` and setting, `max_tokens = 0` | [command](command.md#models-config) |
| HM3 | `generate_config` for `off`, `on` and `n/a` sets nothing. `high` sets `reasoning_effort="high"` for an `openai/` row and `reasoning_tokens=16384` for a row with `reasoning_kind = "budget"`. `max_tokens` from the row lands in the config. `temperature` is never set | [command](command.md#reasoning) |
| HM4 | `reasoning_kind` defaults to `effort` for `anthropic/x` and `budget` for `together/x`, and the file's column wins over the prefix | [command](command.md#models-config) |
| HM5 | `main(["poc", "--dry-run"])` returns 0, prints one line per row and setting with provider rows first, and calls `eval` zero times | [command](command.md#poc) |
| HM6 | `main(["poc", "--models", <a temp file with one baseline/uniform row>, "--limit", "2"])` runs one eval into a temp log dir whose log has two samples and the metadata keys | [command](command.md#poc) |
| HM7 | `main(["nope"])` returns 1 and prints the known subcommands. A fake entry point in `paranoid.commands` is listed and called | [command](command.md#subcommands) |
| HM8 | `main(["pilot", "baseline-order", "--out", tmp])` with the seed count cut to 20 by a test hook writes a CSV with the columns in the table and one row per scenario and baseline | [command](command.md#pilot-cells) |
| HM9 | Every engine-only pilot cell runs with the network blocked by a socket monkeypatch | [command](command.md#invariants) |
| HM10 | `main(["poc", "--only", "baseline/uniform", "--dry-run"])` on a two-row file prints that row's line only | [command](command.md#poc) |
| HM11 | Without the timestral extra, a models file with a `timestral/top-pick` row then a `baseline/uniform` row: `poc` prints one line saying the Timestral row is skipped, runs the baseline eval, and returns 0 | [command](command.md#poc) |
| HM12 | A models file with an `llm` row whose `id` names a provider inspect cannot resolve, then a `baseline/uniform` row: `poc` runs the baseline eval anyway and returns 1 | [command](command.md#poc) |
| HM13 | The log HM6 writes has `eval.metadata["reasoning"] == "n/a"` and `eval.metadata["kind"] == "baseline"` | [command](command.md#poc) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| HY1 | For any list of non-negative gains and positive gaps, `pooled_score` lies between the smallest and largest run score |
| HY2 | For any valid split, a scripted `mockllm` call with it plays the round, and the stored row's `None`s match its zeros |
| HY3 | For any probabilities that sum to 1, the Jev bets sum to the budget and have one entry per channel |

## Not decided

- HS12 needs Docker on CI. Until CI has it, the sandbox tests run locally only. Decide when CI is set up.
