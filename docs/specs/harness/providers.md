# Providers

## Purpose

A provider plays a model that cannot call a tool through the same solver, engine and score as an LLM. `StoreAPI` is the shared base: it ignores the messages, reads the store, and answers with one call to the skin's tool. The baselines, Jev and Timestral each subclass it. The design is in [providers](../../harness/inspect.md#providers) and [providers for Jev and Timestral](../../harness/providers.md).

## Interface

```python
class StoreAPI(ModelAPI):
    def __init__(self, model_name: str, base_url: str | None = None, api_key: str | None = None,
                 config: GenerateConfig = GenerateConfig(), **model_args: Any)
    def bets(self, store: RunStore, input: list[ChatMessage]) -> Bets      # subclasses implement
    async def generate(self, input: list[ChatMessage], tools: list[ToolInfo],
                       tool_choice: ToolChoice, config: GenerateConfig) -> ModelOutput
    def max_connections(self) -> int                                       # 32 for baselines, 4 otherwise

class BaselineAPI(StoreAPI): ...     # "baseline/<name>". model_args are the policy's parameters
class JevAPI(StoreAPI): ...          # "jev/<model>"
class TimestralAPI(StoreAPI): ...    # "timestral/<policy>"

POLICIES: Mapping[str, Policy | type[Policy]]   # uniform, discerning, complacent, perfect as instances,
                                                # hedge_rule and scout_rule as HedgeRule and ScoutRule

@dataclass(frozen=True)
class JevAnswer:
    probabilities: tuple[float, ...]            # one per option, in option order
    confidence: float | None
    raw: Mapping[str, Any]                      # the SDK's reply as returned

class JevClient(Protocol):
    def ask(self, state: str, question: str, options: Sequence[str]) -> JevAnswer: ...

class Forecaster(Protocol):
    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray: ...
    # readings (rounds, channels) with NaN for blanks. bets the same shape or None. Returns (channels, 21)

TIMESTRAL_POLICIES: Mapping[str, Callable[[np.ndarray, int], Bets]]   # id -> (quantiles, budget) -> bets
```

## Behaviour

### Registration

- **`providers/__init__.py`** registers `baseline`, `jev` and `timestral` with `@modelapi(name=...)`, each returning its class. `pyproject.toml` lists the module under the `inspect_ai` entry point, so `--model baseline/complacent` resolves with no import by the caller, see [naming](../../harness/layout.md#naming).
- **The model name after the slash** picks the policy, the Jev model or the Timestral policy. An unknown one raises `ValueError` on construction, naming the known ones.
- **No key is read** by the baseline and Timestral providers. Jev reads `TYPESAFE_API_KEY`, see [keys](../../harness/models.md#keys).

### Shared behaviour

- **`generate` reads the store**, `store_as(RunStore)`, and calls `self.bets(store, input)`. inspect's per-sample store is in scope inside `generate` because the model call is awaited in the sample's own task, see [Open](#open).
- **It answers with one tool call and no text.** `ModelOutput` with one `ChatMessageAssistant` whose `content` is `""` and whose `tool_calls` is one `ToolCall` with `id` `f"{self.model_name}-{store.round()}"`, `function` `tools[0].name` and `arguments` `{"bets": list(bets)}`. `stop_reason` is `"tool_calls"`. The submit tool is always first, see [each round](solver.md#each-round).
- **`tools` is never empty.** If it is, `generate` raises `RuntimeError`, as the solver is not the one calling.
- **A provider that cannot produce bets raises.** A baseline that bets badly is a bug and the sample errors, see [play](../engine/game.md#play). Providers never retry.
- **Usage is zero tokens.** The scorer and the [cost check](../../pilot/provider-checks.md#cost-per-run) can tell a provider row from an LLM row by `kind` in the models config, not by usage.
- **Extra information goes on the message.** Jev's probabilities and Timestral's quantiles are set on `ChatMessageAssistant.metadata`, so they sit beside the bets in the log.

### Baseline

- **`POLICIES`** maps the six names in [baselines](../../design/baselines.md#fixed-baselines) to the engine's exports: `uniform`, `discerning`, `complacent`, `perfect` to the instances, `hedge_rule` to `HedgeRule` and `scout_rule` to `ScoutRule`.
- **Model args are policy parameters.** `--model baseline/hedge_rule -M look=1 -M window=4` builds `HedgeRule(look=1, window=4)`. inspect passes `-M` values as strings, so each is cast to the dataclass field's type. A model arg on a baseline that takes none, or an unknown field, raises `ValueError` on construction. With no model args the two parameterised baselines are `HedgeRule()` and `ScoutRule()`, equal to the engine's `hedge_rule` and `scout_rule`.
- **`bets`** is `policy(store.game().view(policy.peeks))`, see [view](../engine/game.md#view). The peeking baselines get the tape, the rest get `None`.
- **The same rounds as a model.** A baseline run through the provider has the same `rows` as `play(policy, tape)`, warm up included, so the scorer's own baseline sums agree with the provider's run to the last decimal, see [scorer invariants](scorer.md#invariants).
- **`max_connections`** is 32. A baseline does no I/O, so the cap only bounds concurrency.

### Jev

- **`JevAPI`** takes a `client: JevClient`. The default is `TypesafeClient`, a thin wrapper over `typesafe-sdk` that is imported lazily, so the default install needs the package only when Jev runs. Tests pass a fake.
- **State** is the text of the system message and the text of the user message in `input`, joined by two newlines. That is exactly what an LLM sees this round, notes included when the pilot turns them on.
- **Question and options** are the skin's `question` and `channels`, in channel index order. The provider loads the skin by `store.skin` from `load_skins()`, called once per process and kept.
- **Bets** are `split_budget(answer.probabilities, budget)`, see [`split_budget`](../engine/policies.md#split_budget). A probability under 0.005 of the budget gets 0 unless a leftover point falls to it. An answer with the wrong number of probabilities, a negative one, or all zeros raises `ValueError`.
- **Logged** on the message's `metadata`: `probabilities`, `confidence` and `raw`.
- **No memory.** The client is called once a round with the state as given. Nothing is kept between rounds, see [Jev](../../harness/providers.md#jev).

### Timestral

- **`TimestralAPI`** takes a `forecaster: Forecaster`. The default loads `mistralai/Timestral-209M` on CPU, imported lazily from the `timestral` extra. Without the extra, construction raises `ImportError` that names `uv sync --extra timestral`. Tests pass a fake.
- **Pinned.** `pyproject.toml` pins the Timestral package to one git commit, and the loader passes a weights `revision`, so a rerun loads the same code and the same weights. Both are named in the row's `notes` in the models config. An unpinned git install is a supply chain risk and a reproducibility hole at once.
- **Input** is `readings`, shape `(len(rows), channels)`, each row's readings with `NaN` where the bet was 0. For `odds-bet-aware`, `bets` is the same shape with the past bets, else `None`, see [Timestral](../../harness/providers.md#timestral).
- **Round 1 is `uniform`.** With no rows there is nothing to forecast, so the first split is `uniform`'s, which also reads every channel once.
- **Output** is `(channels, 21)` quantiles for next round, in ascending quantile order. Index 10 is the median. The levels are the ones the Timestral package reports, see [Open](#open).
- **Determinism and cache.** `torch.set_num_threads(1)` once and `torch.manual_seed(0)` before each forecast, as CPU inference can differ across thread counts. The result is cached under `$PARANOID_CACHE`, default `~/.cache/paranoid/timestral/`, keyed by the SHA-256 of the model id, the weights revision, the input arrays' bytes and shapes, and whether `bets` was passed. A cache hit never calls the model, so a rerun replays the same bets. The key is logged on the message's `metadata` as `cache_key`, with the quantiles.
- **The cache is as private as a log.** It holds forecasts of the readings a run saw, so after a held-out run it stays on the machine like the log does, see [contamination](../../harness/contamination.md#public-and-held-out).
- **`TIMESTRAL_POLICIES`** turns quantiles into bets, one entry per id in the [glossary](../../glossary.md#the-study):

| Id | Bets |
|---|---|
| `top-pick` | `budget` on the channel with the highest median. Ties to the lowest index |
| `odds` | `split_budget(p, budget)` where `p[c]` is the share of 1000 draws in which channel `c` is highest. Each draw takes one value per channel from its quantile function by linear interpolation, with `default_rng(0)` |
| `look-1`, `look-2`, `look-5` | 1, 2 or 5 on every channel but the top pick, the rest on it |
| `odds-bet-aware` | As `odds`. The difference is the `bets` input |

- **A channel with no reading yet** has a `NaN` median. `top-pick` treats it as lowest. `odds` gives it no draws.
- **These rules move to the engine** as `Policy`s whose `View` carries the forecast, once the Bayesian baseline needs them, see [parked](../engine/policies.md#parked). The table here is the contract until then.

## Invariants

- `generate` on any provider returns exactly one tool call to `tools[0].name` and no text.
- `BaselineAPI("baseline/<name>")` plays the same `rows` as `play(POLICIES[name], tape)` on the same tape and warm up.
- A provider never writes to the store. Only the solver and the tools do.
- A fake `JevClient` or `Forecaster` is enough to run a whole eval with no network.

## Tests

See [tests](tests.md#providers).

## Open

- **Store in scope.** `store_as` inside `generate` relies on inspect's sample context reaching the model call. Confirm on the first run. If it does not, the solver sets a `ContextVar` holding the store before each generate and the base reads that instead.
- **Timestral's quantile levels and call signature** are read from the package when the extra is first installed. The 21 levels are assumed to be evenly spaced from 0.05 to 0.95 until then.
- **`typesafe-sdk`'s call shape.** `JevClient` is the seam, so only `TypesafeClient` changes if the SDK differs.
