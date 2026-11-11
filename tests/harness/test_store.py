"""HK3's config half and HK11, see docs/specs/harness/tests.md#task."""

import typing

import numpy as np
from inspect_ai.util import Store

from paranoid.engine import SCENARIOS, Timeline, engine_hash
from paranoid.harness import RunStore, StoredRow, scenario_config


def test_hk3_scenario_config():
    twenty = scenario_config("one_shock", rounds=20)
    assert twenty.rounds == 20
    assert engine_hash(twenty) != engine_hash(SCENARIOS["one_shock"])
    pinned = scenario_config("one_shock", own_scale=2.0)
    assert pinned.own_scale == 2.0 and pinned.pin_in_level_points
    assert scenario_config("one_shock", inertia=10).inertia_cap == 10
    assert scenario_config("one_shock") == SCENARIOS["one_shock"]


def types_in(annotation) -> set:
    found = {annotation}
    for arg in typing.get_args(annotation):
        found |= types_in(arg)
    return found


def test_hk11_nothing_on_the_timeline_is_stored():
    assert "seed" not in RunStore.model_fields
    for name, field in RunStore.model_fields.items():
        found = types_in(field.annotation)
        assert np.ndarray not in found and Timeline not in found, name
    store = RunStore(store=Store())
    store.scenario, store.seed_set = "down_switch", "public"
    assert store.timeline() is store.timeline()
    assert store.round() == 1
    store.rows = [StoredRow(round=1, bets=[10] * 10, readings=[50.0] * 10)]
    assert store.round() == 2 and len(store.record()) == 1
