# Policies

## Purpose

The four fixed baselines with no parameters, and `POLICIES`, the mapping from the six `baseline/<name>` names in [fixed baselines](../../design/baselines.md#fixed-baselines) to the policy each plays. The harness wraps each in a provider so `--model baseline/complacent` plays like a model, see [baseline](../harness/providers.md#baseline), and the engine checks run them on thousands of tapes with no model, see [engine checks](../../pilot/engine-checks.md). The two baselines with parameters are on [rules](rules.md).

## Interface

```python
uniform: Policy        # peeks = False
discerning: Policy     # peeks = True
complacent: Policy     # peeks = False
perfect: Policy        # peeks = True

POLICIES: Mapping[str, Policy | type[Policy]]
# uniform, discerning, complacent, perfect as instances. hedge_rule and scout_rule as HedgeRule and ScoutRule
```

- Each of the four is an instance of a frozen dataclass with no fields, see [conventions](README.md#conventions).
- `POLICIES` has exactly six keys, the names in the [glossary](../../glossary.md#the-study) after `baseline/`. Assigning to it raises `TypeError`.

## Behaviour

### The four fixed baselines

| Policy | Peeks | Split each round |
|---|---|---|
| `uniform` | No | `split_budget([1] × channels, budget)`. 10 each at the defaults |
| `discerning` | Yes | `budget` on `tape.climate_leader(round)`, the highest base level this round. Ties go to the lowest index. So it holds on a short Up switch seed, and in the Up switch then down switch scenario it moves to the sleeper and back |
| `complacent` | No | `budget` on `start.leader`, every round. Equals the Discerning baseline's round 1 split |
| `perfect` | Yes | `budget` on the channel with the highest `tape.levels[round−1]`. Ties go to the lowest index |

- **`uniform` ignores the view entirely.** It is the floor, see [scoring](../../design/scoring.md#why-these-two-baselines).
- **`discerning` is the yardstick.** It reads the tape so the score is the same whatever the agent chose to look at. Nothing else on this page or [rules](rules.md) may be the denominator, see [players may read their own record](../../design/baselines.md#fixed-baselines).
- **`complacent` needs `start`**, the ladder at round 1, which the view carries for every policy, see [view](../engine/view.md#view).

### `POLICIES`

- **Instances and classes.** `uniform`, `discerning`, `complacent` and `perfect` map to the instances above. `hedge_rule` and `scout_rule` map to the classes `HedgeRule` and `ScoutRule`, so a caller can build one with parameters.
- **Parameters come as strings.** inspect passes `-M look=1` as `{"look": "1"}`, so the harness builds a class entry with `POLICIES[name](**args)` after casting each value to the dataclass field's type, see [baseline](../harness/providers.md#baseline). The cast is the harness's. The errors are this layer's:
  - An unknown field raises `TypeError` from the dataclass, which the harness reports as `ValueError` naming the known fields.
  - A class entry with no arguments is the engine's default instance: `POLICIES["hedge_rule"]() == hedge_rule`.
  - An instance entry takes no arguments. The harness raises `ValueError` if any are given.
- **Every entry is a `Policy`** once built, with `peeks` and `__call__`, see [conventions](README.md#conventions).

## Invariants

- `complacent` on round 1 equals `discerning` on round 1, on every tape.
- `discerning` and `complacent` are equal on every round of a No change tape.
- `perfect`'s output is at least `discerning`'s on every seed of every scenario.
- `uniform` returns the same split for any view.
- Every key in `POLICIES` is a glossary name and every glossary `baseline/<name>` is a key.
