# Tests

Every test the harness suite runs, in `tests/harness/`. They need no key and no network: LLM calls go through `mockllm/model` with scripted outputs, baselines through the baseline provider, and Jev and Timestral through fakes. Tests marked **sandbox** need Docker and tests marked **timestral** need the extra. Both are skipped by default, run with `-m sandbox` or `-m timestral`. The skins layer's `example` skin is the skin throughout.

## Task

| Id | Test | Page |
|---|---|---|
| K1 | `paranoid()` at the defaults has `8 × len(public seeds)` samples, ids `<scenario>/<position>` in `SCENARIOS` order then file order, and every metadata key in the dataset table | [task](task.md#dataset) |
| K2 | `scenario="one_shock,down_switch"` gives two scenarios' samples. `scenario="nope"` raises `ValueError` naming it | [task](task.md#scenarios-and-config) |
| K3 | `scenario_config("one_shock", rounds=20)` has `rounds == 20` and a different hash from `SCENARIOS["one_shock"]`. `own_scale=2.0` sets `pin_in_level_points` and `inertia=10` sets `inertia_cap`. Each sample's `engine_hash` equals the hash of its resolved config | [task](task.md#scenarios-and-config) |
| K4 | `parse_seeds("0-4", s)` returns positions 0 to 4 with the file's seeds. `"3"` returns one. `"4-2"`, a position past the end, and `"held-out"` with `PARANOID_SEEDS` unset raise `ValueError`, the last naming the variable | [task](task.md#seeds) |
| K5 | A seed file with a comment, a blank line and a repeated seed: the first two are skipped, the third raises `ValueError` | [task](task.md#seeds) |
| K6 | `PARANOID_SEEDS` pointing at a temp folder: `seeds="held-out"` reads it, and metadata has `seed_set == "held-out"` and the right `seed_index` | [task](task.md#seeds) |
| K7 | `skin="nope"` raises `ValueError` listing `example`. `tools="laser"` raises `ValueError` | [task](task.md#task-settings) |
| K8 | The task has `retry_on_error == 1` and `fail_on_error is False`. `sandbox` is set only when `tools` includes `compute` | [task](task.md#task-settings) |
| K9 | `warm_up="complacent:5"` played with `baseline/uniform`: the store has `warm_up_rounds == 5`, the first five rows equal `play(complacent, tape, max_rounds=5)`, and the round 1 user message has six lines. `"complacent:0"`, `"complacent:40"` and `"nope:5"` raise `ValueError` | [task](task.md#warm-up) |
| K10 | `prompt_hash(example)` is 12 lowercase hex characters, equals a pinned string, and changes when `tool_text` changes by one character | [task](task.md#prompt-hash) |
| K11 | `RunStore` has no field whose type is an array or a `Tape`, checked over `model_fields`. `store.tape()` twice is the same object | [task](task.md#store) |
| K12 | `configs/grid.toml` loads to a list of positive floats that includes the default `own_scale` | [task](task.md#scenarios-and-config) |

## Solver

| Id | Test | Page |
|---|---|---|
| S1 | A full run with `baseline/uniform` on one seed: `len(rows) == rounds`, every `tries` entry is 1, and the rows equal `play(uniform, tape)` | [solver](solver.md#each-round) |
| S2 | `mockllm` scripted to a valid call every round: the messages at the start of round 2 are exactly a system and a user message, and the user message is `render_record` of a one-row record | [solver](solver.md#each-round) |
| S3 | `mockllm` scripted to a bad call then a valid one: `bad_calls == 1`, `tries == [2, 1, …]`, the round 1 messages before the valid call hold a tool message with `skin.bad_call`, and the round still played once | [solver](solver.md#tries) |
| S4 | `mockllm` scripted to text with no call then a valid one: `no_calls == 1` and a user message of `skin.no_call` was appended | [solver](solver.md#tries) |
| S5 | A reply with `stop_reason == "max_tokens"` adds one to `cut_offs` and one to `no_calls` | [solver](solver.md#tries) |
| S6 | Ten bad calls in a row raise `RoundError` with `round == 1`, and the store has ten bad calls and no rows | [solver](solver.md#tries) |
| S7 | Bets of `[10.0] × 10` and `["10"] × 10` get `bad_call`. `[10] × 10` plays. The engine's own message appears nowhere in the messages | [solver](solver.md#submit) |
| S8 | Two submit calls in one reply: the first plays, the second gets `bad_call`, `len(rows) == 1` and `bad_calls == 1` | [solver](solver.md#submit) |
| S9 | The tool result on a valid call equals the header and last line of `record.to_csv(skin.channels)` | [solver](solver.md#submit) |
| S10 | `tool_choice="forced"` sets `state.tool_choice` to `ToolFunction(skin.tool_name)`. `"auto"` sets `"auto"`. The submit tool is `state.tools[0]` and carries the skin's name and text | [solver](solver.md#each-round) |
| S11 | `tools="notes"`: a `notes("abc")` call then a valid submit. Round 2's user message has two content blocks, the second `"abc"`. A 3000 character note is stored as 2000. A round that called only `notes` counts a no call | [solver](solver.md#notes) |
| S12 | **sandbox** `tools="compute"`: `compute("print(open('record.csv').read())")` returns the record CSV. `compute("import socket; socket.create_connection(('1.1.1.1', 80))")` returns an error, not a connection. A sleep of 60 seconds returns `timeout` | [solver](solver.md#compute) |
| S13 | `rolling=True`: at round 3 the messages hold every earlier assistant and tool message, and the last user message is the header and one row | [solver](solver.md#rolling) |
| S14 | Replaying `store.rows` as bets with `Game` on `store.tape()` gives equal readings and outputs | [solver](solver.md#invariants) |
| S15 | A lint over every message a `mockllm` run produced finds no banned word, with the example skin | [prompts](../../harness/prompts.md#banned-words) |

## Providers

| Id | Test | Page |
|---|---|---|
| R1 | `get_model("baseline/<name>")` resolves for all six names. `baseline/nope` raises `ValueError` naming the six | [providers](providers.md#registration) |
| R2 | Every provider's `generate` returns one tool call to `tools[0].name` with a `bets` list and `content == ""`. With `tools == []` it raises `RuntimeError` | [providers](providers.md#shared-behaviour) |
| R3 | A full eval of `baseline/<name>` on 5 seeds of Down switch, for each of the six, has rows equal to `play(policy, tape)` | [providers](providers.md#baseline) |
| R4 | `baseline/hedge_rule` with `model_args={"look": "1", "window": "4"}` builds `HedgeRule(look=1, window=4)`. `{"nope": "1"}` and `baseline/uniform` with `{"look": "1"}` raise `ValueError` | [providers](providers.md#baseline) |
| R5 | A fake `JevClient` recording its calls: the state equals the system text, two newlines, the user text. The question and options are the skin's. Probabilities `[0.5, 0.5, 0, …]` give bets `[50, 50, 0, …]`, and `[0.004, 0.996, 0, …]` give `[0, 100, 0, …]`. Nine probabilities raise `ValueError` | [providers](providers.md#jev) |
| R6 | The Jev message's `metadata` holds `probabilities`, `confidence` and `raw` | [providers](providers.md#jev) |
| R7 | A fake `Forecaster` recording its inputs: round 1 bets are `uniform`'s and it is not called. Round 2's `readings` has shape `(1, channels)` with `NaN` nowhere after a uniform round. After a `top-pick` round it has `NaN` on nine channels. `bets` is `None` except for `odds-bet-aware` | [providers](providers.md#timestral) |
| R8 | `TIMESTRAL_POLICIES` on hand-built quantiles: `top-pick` puts 100 on the highest median, `look-2` puts 2 on the rest and 82 on it, `odds` on two channels with equal quantiles gives `50, 50` within 3, and a `NaN` channel gets 0 from every policy | [providers](providers.md#timestral) |
| R9 | The Timestral cache: the same fake forecaster input twice calls the fake once and the message `metadata` has the same `cache_key`. `PARANOID_CACHE` pointing at a temp folder is where the file lands | [providers](providers.md#timestral) |
| R10 | **timestral** The real forecaster on a ten-reading series then thirty `NaN` rows returns widening quantile spreads, and the same input twice is equal | [Timestral checks](../../pilot/provider-checks.md#timestral-checks) |
| R11 | Without the extra, `TimestralAPI("timestral/top-pick")` raises `ImportError` naming `uv sync --extra timestral` | [providers](providers.md#timestral) |

## Scorer

| Id | Test | Page |
|---|---|---|
| O1 | `baseline/uniform` on 5 seeds of every scenario scores `gain == 0`, and `baseline/discerning` scores `gain == gap`, exactly | [scorer](scorer.md#invariants) |
| O2 | A run with `warm_up="complacent:5"`: `output` sums rows 6 on, `rounds == 35`, and every baseline value equals `play(policy, tape, record=warm_up)` summed over the same rows | [scorer](scorer.md#scoring-one-run) |
| O3 | `Score.value` has every key in the table, `retries == sum(tries) − len(tries)`, and `run_score == gain / gap` | [scorer](scorer.md#scoring-one-run) |
| O4 | `pooled_score([880, 220], [1100, 550])` is `0.6666…` and not `0.6`. Empty input and a zero gap sum raise `ValueError` | [scorer](scorer.md#pooling) |
| O5 | `bootstrap` with one seed returns `(score, score)`. Twice with the default rng gives equal bars. With 100 seeds of gains drawn around 0.7 the bar contains 0.7 | [scorer](scorer.md#pooling) |
| O6 | `scenario_score` on hand-built `SampleScore`s for two scenarios returns the pooled score, `lo ≤ score ≤ hi`, `n` and `failed == 0` for each | [scorer](scorer.md#scenario-score) |
| O7 | Missing seeds: `SampleScore`s for seeds at positions 0 and 1 of a 3-seed file give `failed == 1`, and the score equals the pooled score with a third gain of 0 and the gap from the tape | [scorer](scorer.md#missing-seeds) |
| O8 | `headline` on hand-built scores for eight scenarios is their mean, `scenarios == 8`, and `lo ≤ headline ≤ hi`. With three scenarios `scenarios == 3` | [scorer](scorer.md#headline) |
| O9 | `weakest_trait` names the lowest scenario and its trait, and `TRAITS` has the eight pairs | [scorer](scorer.md#weakest-trait) |
| O10 | `retry_share` on a run with `tries == [1, 2, 1, 3]` and 4 rounds is `0.5`, and `cut_off_share` counts `cut_offs` only | [scorer](scorer.md#retry-share) |
| O11 | `Score.answer` equals `store.record().to_csv()` and `Score.metadata` has `scenario`, `seed`, `seed_index` and `engine_hash` | [scorer](scorer.md#interface) |

## Command

| Id | Test | Page |
|---|---|---|
| M1 | `load_models` on `configs/models/poc.toml` and `full.toml` raises nothing, and every row has a `kind` and at least one `reasoning` value | [command](command.md#models-config) |
| M2 | Each validation clause raises `ValueError` naming the row: a bad `kind`, `baseline/x` with `kind = "llm"`, `reasoning = "xhigh"`, a provider row with `reasoning = "low"`, a duplicate `id` and setting, `max_tokens = 0` | [command](command.md#models-config) |
| M3 | `generate_config` for `off`, `on` and `n/a` sets nothing. `high` sets `reasoning_effort="high"` for an `openai/` row and `reasoning_tokens=16384` for a row that takes a budget. `max_tokens` from the row lands in the config. `temperature` is never set | [command](command.md#reasoning) |
| M4 | `tool_choice_for` is `"auto"` for `anthropic/x` at `low` and `"forced"` at `off`, and `"forced"` for `openai/x` at `high` | [command](command.md#tool-choice) |
| M5 | `main(["poc", "--dry-run"])` returns 0, prints one line per row and setting with provider rows first, and calls `eval` zero times | [command](command.md#poc) |
| M6 | `main(["poc", "--only", "baseline/uniform", "--limit", "2"])` runs one eval into a temp log dir whose log has two samples and the metadata keys | [command](command.md#poc) |
| M7 | `main(["nope"])` returns 1 and prints the known subcommands. A fake entry point in `paranoid.commands` is listed and called | [command](command.md#subcommands) |
| M8 | `main(["pilot", "baseline-order", "--out", tmp])` with the seed count cut to 20 by a test hook writes a CSV with the columns in the table and one row per scenario and baseline | [command](command.md#pilot-cells) |
| M9 | Every engine-only pilot cell runs with the network blocked by a socket monkeypatch | [command](command.md#invariants) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| Y1 | For any list of non-negative gains and positive gaps, `pooled_score` lies between the smallest and largest run score |
| Y2 | For any valid split, a scripted `mockllm` call with it plays the round, and the stored row's `None`s match its zeros |
| Y3 | For any probabilities that sum to 1, the Jev bets sum to the budget and have one entry per channel |

## Open

- S12 needs Docker on CI. Until CI has it, the sandbox tests run locally only.
- M8's test hook, a `PARANOID_PILOT_SEEDS` variable that caps the seed count, is the one test-only switch in the harness. Keep it that way.
