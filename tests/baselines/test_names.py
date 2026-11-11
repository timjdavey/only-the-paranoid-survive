"""BP1, BP6 and BP9 over every entry in POLICIES, BP11, BP12 and the exports table.

See docs/specs/baselines/tests.md#policies. BP1 for the four fixed baselines on 50 seeds is in test_policies.py.
"""

import dataclasses
import re
import subprocess
import sys
from pathlib import Path

import pytest

import paranoid.baselines as baselines
from paranoid.baselines import POLICIES, bayesian, complacent, discerning, hedge_rule, perfect, scout_rule, uniform
from paranoid.engine import SCENARIOS, make_timeline, play

INSTANCES = {
    "uniform": uniform,
    "discerning": discerning,
    "complacent": complacent,
    "perfect": perfect,
    "hedge_rule": hedge_rule,
    "scout_rule": scout_rule,
    "bayesian": bayesian,
}
WITH_PARAMETERS = ["hedge_rule", "scout_rule", "bayesian"]
DOCS = Path(__file__).parents[2] / "docs"


@pytest.mark.parametrize("name", list(SCENARIOS))
@pytest.mark.parametrize("key", WITH_PARAMETERS)
def test_bp1_players_with_parameters_play_valid_splits(key, name, check_split):
    for seed in range(3):
        for r in play(POLICIES[key](), make_timeline(SCENARIOS[name], seed)).rows:
            check_split(r.bets)


@pytest.mark.parametrize("key", [k for k, policy in INSTANCES.items() if not policy.peeks])
def test_bp6_non_peeking_ignore_the_timeline(key, view_of):
    policy = POLICIES[key]()
    t = make_timeline(SCENARIOS["shock_then_switch"], 5)
    record = play(policy, t)
    for k in range(0, len(record), 3):
        rows = record.rows[:k]
        assert policy(view_of(t, rows, peeks=False)) == policy(view_of(t, rows, peeks=True))


@pytest.mark.parametrize("key", list(INSTANCES))
def test_bp9_every_policy_has_peeks_as_a_class_var(key):
    policy = INSTANCES[key]
    assert isinstance(policy.peeks, bool) and callable(policy)
    assert "peeks" not in {f.name for f in dataclasses.fields(policy)}
    assert type(policy).__dataclass_params__.frozen


def test_bp9_only_the_yardstick_peeks():
    assert {key for key, policy in INSTANCES.items() if policy.peeks} == {"discerning", "perfect"}


def test_bp11_the_seven_keys():
    glossary = (DOCS / "glossary.md").read_text()
    assert set(POLICIES) == set(re.findall(r"`baseline/(\w+)` in code", glossary)) == set(INSTANCES)
    assert len(POLICIES) == 7
    with pytest.raises(TypeError):
        POLICIES["uniform"] = uniform
    for key, policy in INSTANCES.items():
        assert POLICIES[key]() == policy
        assert isinstance(POLICIES[key], type)


def test_bp11_an_unknown_field_raises():
    with pytest.raises(TypeError):
        POLICIES["hedge_rule"](nope=1)
    with pytest.raises(TypeError):
        POLICIES["uniform"](explore=1)


def test_bp11_parameters_build_a_player():
    assert POLICIES["hedge_rule"](explore=1) == baselines.HedgeRule(explore=1)
    assert POLICIES["bayesian"](hazard=0.1, rule="lookahead").rule == "lookahead"


def top_level_modules(imports: str) -> set[str]:
    code = f"import sys, {imports}; print(' '.join({{m.split('.')[0] for m in sys.modules}}))"
    return set(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout.split())


def test_bp12_imports_only_numpy_and_the_standard_library():
    """What the layer adds beyond numpy.random, which loads numpy's Cython runtime, and the venv's startup hook."""
    added = top_level_modules("numpy.random, paranoid.baselines") - top_level_modules("numpy.random")
    assert sorted(added - sys.stdlib_module_names) == ["paranoid"]


def test_the_exports_are_the_spec_table():
    table = (DOCS / "specs" / "baselines" / "README.md").read_text().split("## Exports")[1].split("## ")[0]
    names = {name for cell in re.findall(r"^\| ([^|]+) \|", table, re.M) for name in re.findall(r"`(\w+)`", cell)}
    assert set(baselines.__all__) == names
    assert len(baselines.__all__) == len(names)
