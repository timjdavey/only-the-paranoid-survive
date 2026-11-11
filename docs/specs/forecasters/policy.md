# Policy

## Purpose

`ForecastPolicy` turns a forecaster and a [forecast rule](../baselines/forecast.md) into an engine `Policy`. It builds the forecaster's input from the record, caches the forecast on disk, and hands the quantiles to the rule. `TIMESTRAL_POLICIES` holds the six the study plays. The Timestral model itself is on the [timestral](timestral.md) page. What each of the six is there to show is in [baselines](../../design/baselines.md#timestral).

## Interface

```python
class Forecaster(Protocol):
    @property
    def key(self) -> str: ...          # names the model, its weights and its settings, for the cache
    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray: ...
    # readings (rounds, read), NaN for a blank, every column with at least one reading
    # bets the same shape, or None. Returns (read, len(QUANTILE_LEVELS)), next round's quantiles per column

@dataclass(frozen=True, eq=False)
class Forecast:                        # read only array, compared by identity
    quantiles: np.ndarray              # (channels, len(QUANTILE_LEVELS)). A NaN row for a channel never read
    cache_key: str                     # the SHA-256 the forecast is cached under, as hex

@dataclass(frozen=True)
class ForecastPolicy:                  # peeks: ClassVar[bool] = False
    rule: ForecastRule
    with_bets: bool = False            # whether the past bets go to the forecaster
    forecaster: Forecaster = timestral
    def forecast(self, view: View) -> Forecast | None     # None on an empty record
    def rounded_out(self, view: View) -> bool
    def __call__(self, view: View) -> Bets

TIMESTRAL_POLICIES: Mapping[str, ForecastPolicy]          # read only, the six glossary ids
```

## Behaviour

### The policy

- **An empty record gets `uniform`'s split.** With no rows there is nothing to forecast, so the first split is `uniform(view)`, which also reads every channel once. `forecast` returns `None` and the forecaster is not called.
- **Otherwise** the split is `rule(forecast(view).quantiles, view.budget)`. What a rule does with a `NaN` row is the baselines layer's, see [the rules](../baselines/forecast.md#the-rules).
- **A record that is not empty always has a reading.** A split sums to the budget, so every row has a bet above 0 and so a reading. A rule never sees every row `NaN`.

### The arrays

- **`readings`** has shape `(len(rows), channels)`, as float64: each row's readings, with `NaN` where the reading is `None`, which is where the bet was 0.
- **`bets`** has the same shape with each row's bets as float64 when `with_bets` is true, else it is `None`.
- **A channel never read is left out.** A column of `readings` with no finite value is dropped from both arrays before the call, and that channel's quantile row is `NaN`. A warm up record can leave nine channels unread. Timestral forecasts a level of 0 for a series it never saw, and in a joint forecast that series moves the others, see [checked](timestral.md#checked).
- **The forecaster's reply is checked.** It must have shape `(read, len(QUANTILE_LEVELS))` with every value finite, else `ValueError`. Each row is then sorted ascending, as a forecaster can return crossed quantiles and the rules raise on them.
- **`Forecast.quantiles`** is the reply put back in channel order, `(channels, len(QUANTILE_LEVELS))` as float64, and read only.

### The cache

- **Every forecast is cached on disk**, as `<cache>/forecasts/<cache_key>.npy`. `<cache>` is `$PARANOID_CACHE` when set, else `~/.cache/paranoid`.
- **`cache_key`** is the SHA-256 of: `forecaster.key`, the shape of `readings`, its bytes as little-endian float64 in row order, whether `bets` is passed, and its bytes the same way when it is. It is taken before any column is dropped.
- **A hit never calls the forecaster.** So a rerun replays the same bets and never loads the model. `forecast` twice on one view costs one call.
- **A file is written whole.** To a temporary name in the same folder, then moved into place, so a run that stops half way leaves no broken file.
- **The cache is as private as a log.** It holds forecasts of the readings a run saw, so after a held-out run it stays on the machine like the log does, see [contamination](../../harness/contamination.md#public-and-held-out).

### Rounded out

- **`rounded_out(view)`** is true when `rule` is an `Odds` and some channel with a finite quantile row gets a bet of 0 from this view. `Odds` can round a tiny chance to 0, so a channel goes blank that the forecaster had not written off.
- **It is false** for every other rule, which go dark by design, and on an empty record.
- **The pilot counts it**, see [Timestral checks](../../pilot/provider-checks.md#timestral-checks).

### The six policies

| Id | `rule` | `with_bets` | `forecaster` |
|---|---|---|---|
| `top-pick` | `FORECAST_RULES["top-pick"]` | false | `timestral` |
| `odds` | `FORECAST_RULES["odds"]` | false | `timestral` |
| `explore-1`, `explore-2`, `explore-5` | `FORECAST_RULES[id]` | false | `timestral` |
| `odds-bet-aware` | `FORECAST_RULES["odds"]` | true | `Timestral(joint=False)` |

- **The ids are the Timestral ids** in the [glossary](../../glossary.md#the-study) after `timestral/`.
- **`odds-bet-aware` forecasts each channel alone.** A joint forecast cannot tie a row of bets to its channel, see [two shapes](timestral.md#two-shapes).
- **A test swaps the forecaster** with `dataclasses.replace(policy, forecaster=fake)`.

## Invariants

- The forecaster is never called on an empty record, and never sees a column with no reading.
- `policy(view)` twice gives equal splits, and the second call never calls the forecaster.
- `forecast(view).quantiles` has every finite row ascending, so any forecast rule accepts it.
- `TIMESTRAL_POLICIES[id]` has `peeks` false for all six.

## Not decided

- **Whether every row should forecast each channel alone.** `odds-bet-aware` differs from `odds` in two ways today: it is told its bets, and it forecasts each channel alone. Playing `odds` both ways would split the two. Decide at the [Timestral checks](../../pilot/provider-checks.md#timestral-checks), from the gap test on both shapes.
