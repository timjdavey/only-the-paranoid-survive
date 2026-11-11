# Forecasters spec

The forecasters layer plays a [forecaster](../../glossary.md#the-study) as a policy. A forecaster guesses each channel's level next round and places no bets, so this layer reads the record, asks for a forecast, hands it to a [forecast rule](../baselines/forecast.md) and returns the split. Its whole interface is the engine's `Policy`, so `play(TIMESTRAL_POLICIES["top-pick"], timeline)` runs Timestral with no harness, no skin and no Docker. The model, its weights, the pin and the forecast cache are hidden behind it. It imports the baselines layer, the engine and numpy, and torch and Timestral lazily. It knows nothing about skins or inspect_ai. Why Timestral is in the study lives in [baselines](../../design/baselines.md#timestral).

## Pages

| Page | What it specifies |
|---|---|
| [policy](policy.md) | `Forecaster`, `Forecast`, `ForecastPolicy`, the forecast cache and `TIMESTRAL_POLICIES`, the seven ids the harness plays |
| [timestral](timestral.md) | `Timestral`, the default forecaster: the pin, the load, the two input shapes, and what was checked on the real model |
| [tests](tests.md) | Every test the forecasters suite runs, with the page it checks |

## Exports

`paranoid.forecasters` exports these names from its `__init__.py` and nothing else, see [layout](../../harness/layout.md#six-layers).

| Name | Kind | Page |
|---|---|---|
| `Forecaster` | The protocol a forecaster meets, and the seam a test fakes | [policy](policy.md) |
| `Forecast` | One round's quantiles and the key they are cached under | [policy](policy.md) |
| `ForecastPolicy` | A frozen dataclass that is an engine `Policy`: a forecaster through a forecast rule | [policy](policy.md) |
| `TIMESTRAL_POLICIES` | Read only `Mapping[str, ForecastPolicy]`, the seven `timestral/<id>` ids to their policies | [policy](policy.md) |
| `Timestral`, `timestral` | The Timestral forecaster's class, and `Timestral()` at the defaults | [timestral](timestral.md) |
| `TIMESTRAL_MODEL`, `TIMESTRAL_REVISION` | The checkpoint and the weights revision every run loads | [timestral](timestral.md) |
| `require_timestral` | Raises `ImportError` naming the extra when it is missing | [timestral](timestral.md) |

## Names from the engine

The forecasters layer imports these from `paranoid.engine`. Their behaviour is in the [engine spec](../engine/README.md#exports), and the engine's side of this boundary is [what the layers above read](../engine/README.md#what-the-layers-above-read).

| Name | What the forecasters layer uses it for |
|---|---|
| `View`, `Bets` | What a policy takes and returns, see [view](../engine/view.md) |
| `play`, `make_timeline`, `SCENARIOS`, `Game`, `Record`, `Row` | Whole runs, and views built from hand-written rows, for the test suite only, see [tests](tests.md) |

## Names from the baselines layer

The forecasters layer imports these from `paranoid.baselines`. Their behaviour is in the [baselines spec](../baselines/README.md#exports), and that layer's side of this boundary is [what the layers above read](../baselines/README.md#what-the-layers-above-read).

| Name | What the forecasters layer uses it for |
|---|---|
| `ForecastRule`, `FORECAST_RULES`, `QUANTILE_LEVELS` | The rule a forecast goes through, the five rule ids, and the grid a forecast must be on, see [forecast](../baselines/forecast.md) |
| `Odds` | To tell which rule can round a channel out, see [rounded out](policy.md#rounded-out) |
| `uniform` | The split on an empty record, see [the policy](policy.md#the-policy) |
| `complacent` | Warm up records for the test suite only, see [tests](tests.md) |

## What the layers above read

What the harness takes from this layer is listed on its README, so the boundary is written on both sides, see [specs](../README.md#rules).

| Layer | Its list |
|---|---|
| harness | [Names from the forecasters layer](../harness/README.md#names-from-the-forecasters-layer): `TIMESTRAL_POLICIES` and `require_timestral` for the Timestral provider, `Forecaster` for its tests' fake, and `Timestral` and `timestral` for the pilot cell's probes |

- **Skins and forecasters never meet.** They sit side by side under the harness, and neither imports the other, see [layout](../../harness/layout.md#six-layers).

## Modules

    src/paranoid/forecasters/
      __init__.py    the exports above, nothing else
      policy.py      Forecaster, Forecast, ForecastPolicy, TIMESTRAL_POLICIES
      cache.py       private: the forecast cache on disk
      timestral.py   Timestral, timestral, TIMESTRAL_MODEL, TIMESTRAL_REVISION, require_timestral

- Nothing outside `__init__.py` is public. Tests import from `paranoid.forecasters` only, plus `paranoid.engine` and `paranoid.baselines` for timelines, records and rules.
- Third-party imports are numpy, plus torch and Timestral inside `timestral.py`, imported inside the function that loads the model. So importing the layer never imports torch, and the default install runs without the extra.
- **This is the only layer that imports torch or Timestral.** `import-linter` enforces it with a forbidden contract on every other package, see [layout](../../harness/layout.md#what-pyprojecttoml-holds).

## Conventions

- **A forecast policy is a policy like any baseline.** A frozen dataclass with `__call__` and `peeks` declared `ClassVar[bool]`, false. It reads `view.record`, `view.channels` and `view.budget`, and never the timeline, the start or the dials. So it knows nothing a model does not, see [baselines conventions](../baselines/README.md#conventions).
- **State is derived, never kept.** Each call rebuilds its arrays from the record. The cache is keyed on those arrays, so it changes how long a call takes and never what it returns.
- **A forecaster that fails raises.** A wrong shape, a `NaN` or a missing extra is an error and the run stops. Nothing here retries.
- **The layer writes no text.** Nothing here renders a prompt or a log. The harness logs what `forecast` returns.

## Invariants

- A forecast policy returns a valid split for every view: `channels` whole numbers, none negative, summing to `budget`.
- A forecast policy returns the same split whether `view.timeline` is the timeline or `None`.
- No policy edits the view or the record.
