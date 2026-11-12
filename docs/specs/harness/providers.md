# Providers

## Purpose

A provider plays a model that cannot call a tool through the same solver, engine and score as an LLM. `StoreAPI` is the shared base: it ignores the messages, reads the store, and answers with one call to the skin's tool. The baselines, Jev and Timestral each subclass it. The Timestral provider only plays a policy from the [forecasters layer](../forecasters/README.md), which owns the model. The design is in [providers](../../harness/inspect.md#providers) and [providers for Jev and Timestral](../../harness/providers.md).

## Interface

```python
class StoreAPI(ModelAPI):
    def __init__(self, model_name: str, base_url: str | None = None, api_key: str | None = None,
                 config: GenerateConfig = GenerateConfig(), **model_args: Any)
    async def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets   # subclasses implement
    async def answer(self, store: RunStore, input: list[ChatMessage]) -> tuple[Bets, dict | None]
                                                                      # the bets and what to log beside them
    async def generate(self, input: list[ChatMessage], tools: list[ToolInfo],
                       tool_choice: ToolChoice, config: GenerateConfig) -> ModelOutput
    def max_connections(self) -> int                                       # 32 for baselines, 4 for Jev, 1 for Timestral

class BaselineAPI(StoreAPI): ...     # "baseline/<name>". model_args are the policy's parameters
class JevAPI(StoreAPI): ...          # "jev/<model>" on TypeSafe, or "jev/<endpoint>/<model>"
class TimestralAPI(StoreAPI): ...    # "timestral/<policy>". Plays a forecasters layer policy

@dataclass(frozen=True)
class JevAnswer:
    probabilities: tuple[float, ...]            # one per option, in option order
    confidence: float | None
    raw: Mapping[str, Any]                      # the SDK's reply as returned

class JevClient(Protocol):
    async def ask(self, state: str, question: str, options: Sequence[str]) -> JevAnswer: ...

@dataclass(frozen=True)
class Endpoint:                                 # a Jev-compatible API
    base_url: str | None                        # None: the SDK's own default, TypeSafe
    key_env: str | None                         # None: the SDK reads TYPESAFE_API_KEY itself
    headers: Mapping[str, str]                  # sent on every call

TYPESAFE = Endpoint(None, None, {})
ENDPOINTS = {"decisionmodels": Endpoint("https://api.decisionmodels.io", "DECISIONMODELS_API_KEY",
                                        {"S1-Region": "eu"})}

def endpoint_of(model_name: str) -> tuple[Endpoint, str]   # the endpoint and the model id it takes
```

## Behaviour

### Registration

- **`providers/__init__.py`** registers `baseline`, `jev` and `timestral` with `@modelapi(name=...)`, each returning its class. `pyproject.toml` lists the module under the `inspect_ai` entry point, so `--model baseline/complacent` resolves with no import by the caller, see [naming](../../harness/layout.md#naming).
- **The model name after the slash** picks the policy, the Jev model or the Timestral policy. inspect builds the provider with that bare name, so `--model timestral/top-pick` builds `TimestralAPI("top-pick")`. An unknown one raises `ValueError` on construction, naming the known ones.
- **No key is read** by the baseline and Timestral providers. A `jev` row reads its endpoint's key, `TYPESAFE_API_KEY` or `DECISIONMODELS_API_KEY`, see [keys](../../harness/models.md#keys).

### Shared behaviour

- **`generate` reads the store**, `store_as(RunStore)`, and awaits `self.bets(store, input)`. inspect's per-sample store is in scope inside `generate` because the model call is awaited in the sample's own task, see [checked](#checked).
- **It answers with one tool call and no text.** `ModelOutput` with one `ChatMessageAssistant` whose `content` is `""` and whose `tool_calls` is one `ToolCall` with `id` `f"{self.model_name}-{store.round()}"`, `function` `tools[0].name` and `arguments` `{name: list(bets)}`, where `name` is the one key of `tools[0].parameters.properties`. That is the skin's `bets_name`, so a provider plays any skin, see [submit](solver.md#submit). `stop_reason` is `"tool_calls"`. The submit tool is always first, see [each round](solver.md#each-round).
- **I/O is awaited, compute is serialised.** `JevClient.ask` is async, so a network call never stalls the other samples. A Timestral forecast is CPU bound, so `TimestralAPI.max_connections` is 1 and the forecast runs on the loop. Two at once would stall the loop for no gain, see [Timestral](#timestral).
- **`tools` is never empty.** If it is, `generate` raises `RuntimeError`, as the solver is not the one calling.
- **A provider that cannot produce bets raises.** A baseline that bets badly is a bug and the sample errors, see [play](../engine/game.md#play). Providers never retry.
- **`generate` checks the bets before it answers**, with `store.game().check(bets)`, and sends the checked split. A `BetError` becomes a `RuntimeError` naming the provider and the round, so the sample errors. Otherwise the bad split would reach `submit` as a model's bad call, and ten of them would end in a give up scored as the Uniform baseline.
- **Usage is zero tokens.** The scorer and the [cost check](../../pilot/provider-checks.md#cost-per-run) can tell a provider row from an LLM row by `kind` in the models config, not by usage.
- **Extra information goes on the message.** Jev's probabilities and Timestral's quantiles are set on `ChatMessageAssistant.metadata`, so they sit beside the bets in the log. `generate` calls `answer`, which by default is `bets` with nothing logged, and Jev and Timestral override it.

### Baseline

- **The name after the slash is a key of [`POLICIES`](../baselines/policies.md#policies)**, from the baselines layer, and the policy is `POLICIES[name](**args)` with the model args cast.
- **Model args are policy parameters.** `--model baseline/hedge_rule -M explore=1 -M window=4` builds `HedgeRule(explore=1, window=4)`. inspect passes `-M` values as strings, so each is cast to the dataclass field's type, read from `dataclasses.fields`. A model arg that is not a field of the class, which for the four fixed baselines is any model arg at all, raises `ValueError` on construction naming the known fields. With no model args every entry is built at its defaults, so it equals the layer's instance of the same name.
- **`bets`** is `policy(store.game().view(policy.peeks))`, see [view](../engine/game.md#view). The peeking baselines get the timeline, the rest get `None`.
- **The same rounds as a model.** A baseline run through the provider has the same `rows` as `play(policy, timeline)`, warm up included, so the scorer's own baseline sums agree with the provider's run exactly, as both sum `row.output` over the same rows, see [scorer invariants](scorer.md#invariants).
- **`max_connections`** is 32. A baseline does no I/O, so the cap only bounds concurrency.

### Jev

- **`JevAPI`** takes a `client: JevClient`. The default is `TypesafeClient`, a thin wrapper over `typesafe-sdk`. The package is a default dependency and is imported lazily, inside `TypesafeClient`, so nothing but a Jev run loads it. Its module is `typesafe_sdk`. Tests pass a fake.
- **The endpoint is named in the id.** Other APIs take Jev's request shape, so one provider plays them all. `endpoint_of` splits the name inspect passes at its first slash. With no slash it is TypeSafe's model, so `jev/jev-latest` is `(TYPESAFE, "jev-latest")`. With one, the part before it is a key of `ENDPOINTS`, so `jev/decisionmodels/s1-pro-5` is `(ENDPOINTS["decisionmodels"], "s1-pro-5")`. An unknown key raises `ValueError` naming the known ones. `JevAPI` calls it on construction, fake client or not.
- **Decision Models runs in its EU tier only.** The `S1-Region: eu` header keeps a call off its peer-to-peer network, out of its logs and out of training, see [who can see them](../../harness/contamination.md#who-can-see-them). Its rows name pinned ids, as an alias such as `s1-pro` can change model between calls and the SDK drops the `model_version` that would show it.
- **`TypesafeClient(model, endpoint)`** builds one `AsyncTypeSafeClient(model=model, base_url=endpoint.base_url, api_key=key, headers=endpoint.headers)` in `sdk()`, on its first ask, and keeps it. For TypeSafe `key` is `None` and the SDK reads `TYPESAFE_API_KEY` itself. For any other endpoint `key` is `os.environ[endpoint.key_env]`, and a missing or blank one raises `ValueError` naming the variable before any call, so a run never sends one provider's key to another. An explicit `base_url` also wins over `TYPESAFE_BASE_URL`.
- **`TypesafeClient.ask`** awaits `client.system_one(state=state, questions={"channel": Choice(instructions=question, criteria={option: None for option in options})})`. The answer is `response.choices["channel"]`. Its `probabilities` is a dict keyed by option, so `JevAnswer.probabilities` reads it in option order, and an option the reply leaves out raises `ValueError` naming the model. `confidence` is the answer's own, and `raw` is `response.model_dump()`. The shape is in [checked](#checked).
- **State** is the text of the system message and the text of the user message in `input`, joined by two newlines. That is exactly what an LLM sees this round, notes included when the pilot turns them on.
- **Question and options** are the skin's `question` and `channels`, in channel index order. The provider loads the skin by `store.skin` from `load_skins()`, called once per process and kept.
- **Bets** are `split_budget(answer.probabilities, budget)`, see [`split_budget`](../engine/view.md#split_budget). A probability under 0.005 of the budget gets 0 unless a leftover point falls to it. An answer with the wrong number of probabilities, a negative one, or all zeros raises `ValueError` naming the model.
- **Logged** on the message's `metadata`: `probabilities`, `confidence`, `raw` and `rounded_out`, which is how many options have a probability above 0 and a bet of 0, so the [Jev rounding check](../../pilot/provider-checks.md#jev-checks) can count the channels that fell out of view. It is a count for the reason Timestral's is, see [rounded out](../forecasters/policy.md#rounded-out). The `jev` cell reads it from the log, see [pilot](pilot.md#jev).
- **No memory.** The client is awaited once a round with the state as given. Nothing is kept between rounds, see [Jev](../../harness/providers.md#jev).

### Timestral

- **The name after the slash is a key of [`TIMESTRAL_POLICIES`](../forecasters/policy.md#the-policies)**, from the forecasters layer. The provider holds that policy and nothing else. The model, its pin, its input and its cache are that layer's, see the [forecasters spec](../forecasters/README.md).
- **`TimestralAPI`** takes a `forecaster: Forecaster | None`. With one, the policy is `dataclasses.replace(policy, forecaster=forecaster)`, which is how tests pass a fake. With none it calls [`require_timestral()`](../forecasters/timestral.md#loading), so without the extra construction raises `ImportError` naming `uv sync --extra timestral`.
- **`bets`** is `policy(view)` with `view = store.game().view(False)`, as a baseline's is, see [baseline](#baseline). Round 1, a blank, a channel never read and crossed quantiles are all the policy's to handle.
- **The same rounds as `play`.** A Timestral run through the provider has the same `rows` as `play(policy, timeline)`, warm up included. So anything `play` shows about a policy holds for its row in a log.
- **Logged** on the message's `metadata`: `quantiles` and `cache_key` from `policy.forecast(view)`, and `rounded_out` from `policy.rounded_out(view)`, see [rounded out](../forecasters/policy.md#rounded-out). Both read the [cache](../forecasters/policy.md#the-cache), so logging costs no forecast. `quantiles` is a list per channel, `None` for a channel never read. On an empty record `quantiles` and `cache_key` are `None`.
- **`max_connections`** is 1, see [shared behaviour](#shared-behaviour).

## Invariants

- `generate` on any provider returns exactly one tool call to `tools[0].name` and no text.
- `BaselineAPI("baseline/<name>")` plays the same `rows` as `play(POLICIES[name](), timeline)` on the same timeline and warm up.
- A provider never writes to the store. Only the solver and the tools do.
- A fake `JevClient` or `Forecaster` is enough to run a whole eval with no network.
- The harness never imports torch or Timestral. `import-linter` enforces it, see [layout](../../harness/layout.md#what-pyprojecttoml-holds).

## Checked

Run on 2026-11-11 against inspect_ai 0.3.289 and read from `typesafe-sdk` 0.7.5. No key was used, so nothing here called Jev. The Decision Models rows were read from its [llms.txt](https://decisionmodels.io/llms.txt), [model registry](https://api.decisionmodels.io/v1/models) and [migration checklist](https://decisionmodels.io/jev-migration-checklist) on 2026-11-12, and called live the same day.

| Question | Answer |
|---|---|
| Is the sample's store in scope inside `ModelAPI.generate` | Yes. A stub provider read `store_as(RunStore)` in `generate` and saw rounds 0, 1 and 2 of its own sample, on eight samples run at once |
| Does a provider see the tool's parameter name | Yes. `tools[0].parameters.properties` has the one key the solver gave it, and a `ToolCall` with that key in `arguments` reaches the tool |
| `typesafe-sdk`'s async call | `AsyncTypeSafeClient.system_one(state, questions)`, where `state` is text and `questions` maps a name to a `Choice(instructions, criteria)`. `criteria` maps each label to a description or `None` |
| Its reply | `SystemOneResponse.choices[<name>]` is a `ChoiceAnswer` with `choice`, `confidence` from 0 to 1, and `probabilities`, a dict keyed by label that sums to about 1 |
| Its key, model and timeout | `TYPESAFE_API_KEY`, `jev-latest` by default, 10 seconds a call, with its own retries |
| Its usage | The reply holds `usage.input_tokens`, which Jev bills. It lands in `raw`, so the log has it, and the provider still reports zero tokens to inspect |
| The SDK's request | `POST {base_url}/v1/systemone` with `Authorization: Bearer <key>`, and it reads the reply's `answers`. It takes `base_url`, `api_key` and `headers` as arguments |
| Decision Models' API | The same path, auth and reply, at `https://api.decisionmodels.io`. `S1-Region: eu` picks the EU tier. One question a call on `s1-fast`, three on `s1-pro`, and we send one |
| Decision Models' limits | `s1-pro-5` (mammoth-1 27B, EU only) and `reax-1-20261021` 8,192 input tokens, and `s1-pro-5` 64 options. `s1-pro-3` (vLLM-SR d3 26B, kept to at least 2027-01-27) 16,384. `s1-fast-2` (Blink v0.3 26B-A4B) 16,192 and 16 options, on a batched engine, so one request twice can differ slightly. `reax-1.3` (EU only) 28,672, and it counts a prompt twice. A prompt over the limit is a 400, never cut |
| A live reply, 2026-11-12 | One call to each of the five rows with a round 40 Uniform record on the example skin: all ten probabilities back, summing to 1, in under 2 seconds. About 3,850 input tokens, or 7,700 on `reax-1.3`, so every row has at least twice the room it needs. Then one full run of each through `paranoid run --skins example --limit 1`, with no errors. `s1-vision-2` gave `s1-fast-2`'s answer to the digit, so it is the same model and has no row |

## Verify before code

- **That a live Jev reply holds a probability for every option.** The types say `probabilities` is keyed by label, and only a call can show that all ten come back and none is renamed. One `system_one` call with the example skin's `question` and `channels`, and `TYPESAFE_API_KEY` set. Only the first eval of a `jev` row waits on it, as `TypesafeClient` raises on a missing option either way.
