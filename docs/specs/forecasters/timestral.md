# Timestral

## Purpose

`Timestral` is the default [forecaster](policy.md#interface): Mistral's [Timestral](https://github.com/mistralai/timestral) model, run in this process on CPU. This page says how it is pinned, loaded and called, and what was checked on the real model before the code was written. Everything here is hidden behind a [`ForecastPolicy`](policy.md).

## Interface

```python
TIMESTRAL_MODEL = "mistralai/Timestral-209M"
TIMESTRAL_REVISION = "9874d252ab0aae16f7f7c999f98f98d6ad7d8365"     # the weights, on the Hugging Face Hub

@dataclass(frozen=True)
class Timestral:                       # a Forecaster
    joint: bool = True                 # the channels as one series, or each alone
    model: str = TIMESTRAL_MODEL
    revision: str = TIMESTRAL_REVISION
    @property
    def key(self) -> str               # "<model>@<revision>/joint" or ".../separate"
    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray

timestral: Forecaster                  # Timestral() at the defaults

def require_timestral() -> None        # ImportError naming the extra when torch or Timestral is missing
```

## Behaviour

### Pinned

- **The package is pinned to one git commit**, `a534bdbd244d64f3d9d743f46c7bf6fc330ed4ff`, as a direct reference in the `timestral` extra in `pyproject.toml`. So no installer ever resolves the name from an index. An unpinned git install is a supply chain risk and a reproducibility hole at once.
- **The weights are pinned to `TIMESTRAL_REVISION`**, passed to the loader, so a rerun loads the same code and the same weights.
- **The revision is in `key`**, so new weights never read an old forecast from the [cache](policy.md#the-cache). The package commit is not, so empty the cache folder when the pin moves.

### Loading

- **Nothing is imported until a forecast is needed.** torch and Timestral are imported inside the loader, so importing `paranoid.forecasters` never imports either.
- **`require_timestral()`** raises `ImportError` naming `uv sync --extra timestral` when either package cannot be found. It imports neither. `Timestral.__call__` calls it first.
- **One model per process.** `TimestralForecaster.from_pretrained(model, device="cpu", revision=revision)`, loaded on the first call and kept, one per `(model, revision)`. It takes about a second once the weights are on disk. The first load downloads them, about 840 MB.
- **The quantile levels are checked on load.** The model's `quantile_levels` must equal `QUANTILE_LEVELS`, else `ValueError`. They do at the pin.
- **CPU.** Documented and tested upstream. Apple MPS is not, so we do not rely on it.

### Two shapes

Timestral takes `(series, variates, time)` and forecasts the variates of one series jointly. So the ten channels can go in two ways.

| `joint` | Context | Bets | What it means |
|---|---|---|---|
| true | `(1, read, rounds)` | Must be `None` | One series with a variate per channel. A dark channel's forecast can lean on the channels still read |
| false | `(read, 1, rounds)` | `(read, 1, rounds)` as `past_covariates` | A series per channel, each forecast alone, each with its own row of bets |

- **A joint forecast cannot be told its bets.** Timestral's covariate rows belong to the series, not to a variate, so nothing ties bet row `c` to channel `c`. `Timestral(joint=True)` called with `bets` raises `ValueError`, before anything is loaded.
- **`readings` and `bets` arrive as `(rounds, read)`**, so each is transposed into place.

### The call

- **One call a forecast:** `forecast(context, prediction_length=1, past_covariates=...)`, every other argument at the package's default. So its symmetric averaging and its clamp at 0 for a series with no negative reading both stay on.
- **`NaN` is a blank.** Timestral masks it and carries the last reading forward.
- **The reply** is `.quantiles`, a float32 tensor `(series, variates, 1, 21)`. The horizon axis is dropped and the rest reshaped to `(read, 21)` as float64 numpy.
- **No seed and no thread setting.** The model draws nothing, see [checked](#checked).

## Checked

Read from the package source and run on the real model on 2026-11-11, at the pins above, with torch 2.15.0 and numpy 2.5.4 on an Apple silicon CPU. `FT4` to `FT6` rerun the ones that matter, see [tests](tests.md#timestral).

| Question | Answer |
|---|---|
| Quantile levels | The 21 in `QUANTILE_LEVELS`, read from the checkpoint's `config.json` |
| Reply | A torch float32 tensor, already ascending along the quantile axis |
| The same input twice | Equal, bit for bit |
| One thread against four | Equal, bit for bit |
| A different `torch.manual_seed` | Equal, so the model draws nothing |
| One forecast, one thread | 110 to 135 ms from 10 to 39 rounds, either shape |
| A channel never read | A forecast of 0, with quantiles from −0.01 to 0.01. In a joint forecast it also moves the other channels |
| Bets in a joint forecast, rows reversed | No change at all, so the rows are not tied to channels |
| Bets with each channel alone | They move the forecast |
| torch against `numpy~=2.5.0` | Imports and runs |

- **The gap test's first numbers** are in [TODO](../../../TODO.md#pilot). The decision is the pilot's.

## Invariants

- `Timestral()(readings, None)` twice gives equal arrays.
- Importing `paranoid.forecasters` adds neither `torch` nor `timestral` to `sys.modules`.
