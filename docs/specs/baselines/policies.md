# Policies

## Purpose

The four fixed baselines with no parameters, and `POLICIES`, the mapping from the seven `baseline/<name>` names in [fixed baselines](../../design/baselines.md#fixed-baselines) to the policy each plays. The harness wraps each in a provider so `--model baseline/complacent` plays like a model, see [baseline](../harness/providers.md#baseline), and the engine checks run them on thousands of timelines with no model, see [engine checks](../../pilot/engine-checks.md). The baselines with parameters are on [rules](rules.md) and [bayesian](bayesian.md).

## Interface

```python
@dataclass(frozen=True)
class Uniform: ...                          # peeks: ClassVar[bool] = False
@dataclass(frozen=True)
class Discerning: ...                       # peeks: ClassVar[bool] = True
@dataclass(frozen=True)
class Complacent: ...                       # peeks: ClassVar[bool] = False
@dataclass(frozen=True)
class Perfect: ...                          # peeks: ClassVar[bool] = True

uniform, discerning, complacent, perfect: Policy   # one instance of each

POLICIES: Mapping[str, Callable[..., Policy]]
# the seven baseline/<name> names to the seven classes, so POLICIES[name](**args) builds any baseline
```

- The four classes have no fields, so one instance of each is exported by name and the classes are not exported. `POLICIES` carries them, see [conventions](README.md#conventions).
- `POLICIES` has exactly seven keys, the names in the [glossary](../../glossary.md#the-study) after `baseline/`. Assigning to it raises `TypeError`.

## Behaviour

### The four fixed baselines

| Policy | Peeks | Split each round |
|---|---|---|
| `uniform` | No | `split_budget([1] × channels, budget)`. 10 each at the defaults |
| `discerning` | Yes | `budget` on `timeline.climate_leader(round)`, the highest base level this round. Ties go to the lowest index. So it holds on a short Up switch seed, and in the Up switch then down switch scenario it moves to the sleeper and back |
| `complacent` | No | `budget` on `start.leader`, every round. Equals the Discerning baseline's round 1 split |
| `perfect` | Yes | `budget` on the channel with the highest `timeline.levels[round−1]`. Ties go to the lowest index |

- **`uniform` ignores the view entirely.** It is the floor, see [scoring](../../design/scoring.md#why-these-two-baselines).
- **`discerning` is the yardstick.** It reads the timeline so the score is the same whatever the agent chose to explore. Nothing else on this page or [rules](rules.md) may be the denominator, see [players may read their own record](../../design/baselines.md#fixed-baselines).
- **`complacent` needs `start`**, the ladder at round 1, which the view carries for every policy, see [view](../engine/view.md#view).

### `POLICIES`

- **Every entry is a class.** `Uniform`, `Discerning`, `Complacent`, `Perfect`, `HedgeRule`, `ScoutRule` and `Bayesian`, under the glossary names. So the harness builds any baseline the same way, `POLICIES[name](**args)`, and never asks which kind of entry it holds.
- **Built with no arguments, every entry equals its exported instance.** `POLICIES["hedge_rule"]() == hedge_rule`, `POLICIES["bayesian"]() == bayesian` and `POLICIES["uniform"]() == uniform`.
- **Parameters come as strings.** inspect passes `-M explore=1` as `{"explore": "1"}`. The harness casts each value to the dataclass field's type and calls the class, see [baseline](../harness/providers.md#baseline). A field the class does not have raises `TypeError` from the dataclass, which is how a class with no fields rejects any argument at all. What the harness tells the user is its rule, not this layer's.
- **Every entry is a `Policy`** once built, with `peeks` and `__call__`, see [conventions](README.md#conventions).

## Invariants

- Every entry in `POLICIES`, built at its defaults, returns a valid split for every view: `channels` ints, none negative, summing to `budget`.
- `complacent` on round 1 equals `discerning` on round 1, on every timeline.
- `discerning` and `complacent` are equal on every round of a No change timeline.
- `perfect`'s output is at least `discerning`'s on every seed of every scenario.
- `uniform` returns the same split for any view.
- Every key in `POLICIES` is a glossary name and every glossary `baseline/<name>` is a key.
