"""EC1 to EC9, see docs/specs/engine/tests.md#config."""

import dataclasses
import hashlib
import json
import math
import re

import numpy as np
import pytest

from paranoid.engine import (
    GENERATOR_VERSION,
    SCENARIOS,
    DriftSpec,
    ScenarioConfig,
    ShockSpec,
    SwitchSpec,
    engine_hash,
)

SCENARIO_ORDER = [
    "no_change",
    "one_shock",
    "down_switch",
    "up_switch",
    "shock_then_switch",
    "slow_drift",
    "switch_then_shock",
    "up_switch_then_down_switch",
]

# Pinned. Changing it is a reviewed change, see EC3.
NO_CHANGE_HASH = "PINNED_IN_STEP_6"


def config(**fields) -> ScenarioConfig:
    return ScenarioConfig(name="test", **fields)


def test_ec1_scenarios_are_the_eight_in_order():
    assert list(SCENARIOS) == SCENARIO_ORDER
    for name, scenario in SCENARIOS.items():
        assert scenario.name == name
    with pytest.raises(TypeError):
        SCENARIOS["no_change"] = SCENARIOS["one_shock"]


BAD_CONFIGS = {
    "channels below 4": dict(channels=3),
    "rounds below 1": dict(rounds=0, onset=(2, 2)),
    "budget below channels": dict(budget=9),
    "range low above high": dict(leader_base=(70.0, 60.0)),
    "int range low above high": dict(onset=(20, 12)),
    "persistence of 1": dict(persistence=1.0),
    "persistence below 0": dict(persistence=-0.1),
    "own_scale of 0": dict(own_scale=0.0),
    "factor_scale of 0": dict(factor_scale=0.0),
    "read_noise_k of 0": dict(read_noise_k=0.0),
    "field_headroom of 0": dict(field_headroom=0.0),
    "hedge_margin_points of 0": dict(hedge_margin_points=0.0),
    "infinite own_scale": dict(own_scale=math.inf),
    "nan in a range": dict(leader_base=(math.nan, 70.0)),
    "loading low of 0": dict(loading=(0.0, 1.0)),
    "hedge_loading high of 0": dict(hedge_loading=(-0.6, 0.0)),
    "runner_up_gap_sigmas low of 0": dict(runner_up_gap_sigmas=(0.0, 4.0)),
    "runner_up_gap_points low of 0": dict(runner_up_gap_points=(0.0, 16.0)),
    "onset low of 0": dict(onset=(0, 5)),
    "onset low of 1": dict(onset=(1, 5)),
    "onset high above rounds": dict(onset=(12, 41)),
    "negative inertia_cap": dict(inertia_cap=-1),
    "hedge_base not below field_base": dict(hedge_base=(20.0, 30.0)),
    "field_base too high for the ladder": dict(field_base=(45.0, 55.0)),
    "riser_share above 1": lambda: dict(events=(SwitchSpec(riser_share=1.5),)),
    "short_share below 0": lambda: dict(events=(SwitchSpec(kind="rise", short_share=-0.1),)),
    "gap low of 0": lambda: dict(events=(ShockSpec(gap=(0, 4)),)),
    "ramp low of 0": lambda: dict(events=(SwitchSpec(ramp=(0, 5)),)),
    "half_life low of 0": lambda: dict(events=(ShockSpec(half_life=(0, 4)),)),
    "length low of 0": lambda: dict(events=(DriftSpec(length=(0, 25)),)),
    "size_sigmas low of 0": lambda: dict(events=(SwitchSpec(size_sigmas=(0.0, 3.0)),)),
    "depth_points low of 0": lambda: dict(events=(ShockSpec(depth_points=(0.0, 32.0)),)),
    "unknown kind": lambda: dict(events=(SwitchSpec(kind="leap"),)),
    "unknown shock profile": lambda: dict(events=(ShockSpec(profile="slow"),)),
    "unknown drift profile": lambda: dict(events=(DriftSpec(profile="sharp"),)),
    "short_share on a draw switch": lambda: dict(events=(SwitchSpec(kind="draw", short_share=0.5),)),
    "short_level low of 0": lambda: dict(events=(SwitchSpec(kind="rise", short_level=(0.0, 0.5)),)),
    "short_level high of 1": lambda: dict(events=(SwitchSpec(kind="rise", short_level=(0.5, 1.0)),)),
    "undo first": lambda: dict(events=(SwitchSpec(kind="undo"),)),
    "undo after a fall": lambda: dict(events=(SwitchSpec(kind="fall"), SwitchSpec(kind="undo"))),
    "undo after a draw": lambda: dict(events=(SwitchSpec(kind="draw"), SwitchSpec(kind="undo"))),
}


@pytest.mark.parametrize("fields", BAD_CONFIGS.values(), ids=BAD_CONFIGS.keys())
def test_ec2_validation(fields):
    with pytest.raises(ValueError):
        config(**(fields() if callable(fields) else fields))


def test_ec2_undo_after_a_rise_through_a_shock_builds():
    config(events=(SwitchSpec(kind="rise"), ShockSpec(), SwitchSpec(kind="undo")))


def test_ec3_pinned_hash():
    digest = engine_hash(SCENARIOS["no_change"])
    assert re.fullmatch(r"[0-9a-f]{12}", digest)
    assert digest == NO_CHANGE_HASH


# A different valid value for every field, for EC4.
OTHER_VALUES = {
    "name": "other",
    "channels": 11,
    "rounds": 39,
    "budget": 101,
    "leader_base": (61.0, 70.0),
    "runner_up_gap_sigmas": (2.0, 3.5),
    "runner_up_gap_points": (8.0, 15.0),
    "field_base": (31.0, 55.0),
    "field_headroom": 5.0,
    "hedge_base": (21.0, 28.0),
    "own_scale": 3.0,
    "persistence": 0.7,
    "factor_scale": 2.0,
    "loading": (0.4, 1.0),
    "hedge_loading": (-0.5, -0.3),
    "read_noise_k": 9.0,
    "events": (ShockSpec(),),
    "onset": (12, 19),
    "pin_in_level_points": True,
    "hedge_margin_points": 5.0,
    "hedge_may_overtake": True,
    "one_channel_shock": True,
    "inertia_cap": 20,
}


def test_ec4_every_field_changes_the_hash():
    base = SCENARIOS["no_change"]
    names = [f.name for f in dataclasses.fields(ScenarioConfig)]
    assert sorted(names) == sorted(OTHER_VALUES)
    for name in names:
        same = dataclasses.replace(base, **{name: getattr(base, name)})
        assert engine_hash(same) == engine_hash(base), name
        other = dataclasses.replace(base, **{name: OTHER_VALUES[name]})
        assert engine_hash(other) != engine_hash(base), name


def test_ec4_every_event_field_changes_the_hash():
    for spec in (ShockSpec(), SwitchSpec(kind="rise"), DriftSpec()):
        base = config(events=(spec,))
        for field in dataclasses.fields(spec):
            value = getattr(spec, field.name)
            if isinstance(value, tuple):
                other = (value[0], value[1] + (1 if isinstance(value[1], int) else 0.1))
            elif field.name == "kind":
                other = "draw"
            elif field.name == "profile":
                other = "sharp" if isinstance(spec, ShockSpec) else "linear"
            else:
                other = value / 2 if value else 0.5
            changed = config(events=(dataclasses.replace(spec, **{field.name: other}),))
            assert engine_hash(changed) != engine_hash(base), field.name


def test_ec5_points_defaults_agree_with_sigmas():
    defaults = config()
    scale = defaults.own_scale
    assert defaults.runner_up_gap_points == tuple(x * scale for x in defaults.runner_up_gap_sigmas)
    pairs = [
        (ShockSpec(), "depth"),
        (SwitchSpec(), "size"),
        (SwitchSpec(), "rise"),
        (DriftSpec(), "size"),
    ]
    for spec, stem in pairs:
        sigmas = getattr(spec, f"{stem}_sigmas")
        assert getattr(spec, f"{stem}_points") == tuple(x * scale for x in sigmas), stem


def test_ec6_int_and_float_ranges_are_one_config():
    from paranoid.engine import make_timeline

    as_ints = config(leader_base=(60, 70))
    as_floats = config(leader_base=(60.0, 70.0))
    assert as_ints == as_floats
    assert engine_hash(as_ints) == engine_hash(as_floats)
    a, b = make_timeline(as_ints, 0), make_timeline(as_floats, 0)
    assert np.array_equal(a.levels, b.levels)
    assert np.array_equal(a.base, b.base)


def canonical(config: ScenarioConfig) -> str:
    shapes = {ShockSpec: "shock", SwitchSpec: "switch", DriftSpec: "drift"}
    d = dataclasses.asdict(config)
    for event_dict, spec in zip(d["events"], config.events):
        event_dict["shape"] = shapes[type(spec)]
    d["generator_version"] = GENERATOR_VERSION
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def test_ec7_canonical_json_has_the_shape_keys():
    one_shock = canonical(SCENARIOS["one_shock"])
    digest = hashlib.sha256(one_shock.encode("utf-8")).hexdigest()
    assert digest[:12] == engine_hash(SCENARIOS["one_shock"])
    events = json.loads(one_shock)["events"]
    assert [e["shape"] for e in events] == ["shock"]
    assert '"shape":"shock"' in one_shock
    both = json.loads(canonical(SCENARIOS["shock_then_switch"]))
    assert [e["shape"] for e in both["events"]] == ["shock", "switch"]


@pytest.mark.parametrize("name", SCENARIO_ORDER)
def test_ec8_noise_grid_settings(name):
    from paranoid.engine import make_timeline

    pinned = dataclasses.replace(SCENARIOS[name], own_scale=8.0, pin_in_level_points=True)
    make_timeline(pinned, 0)
    with pytest.raises(ValueError):
        dataclasses.replace(SCENARIOS[name], own_scale=8.0, pin_in_level_points=False)
    with pytest.raises(ValueError):
        dataclasses.replace(pinned, runner_up_gap_points=(8.0, 30.0))


BAD_TYPES = {
    "string in a range": dict(leader_base=("60", 70.0)),
    "bool in a range": dict(leader_base=(True, 70.0)),
    "float in an int range": dict(onset=(12.5, 20)),
    "float whole number in an int range": dict(onset=(12.0, 20)),
    "float int field": dict(channels=10.0),
    "bool int field": dict(rounds=True),
    "string float field": dict(own_scale="4"),
    "int for a bool field": dict(pin_in_level_points=1),
    "a range of three": dict(leader_base=(60.0, 65.0, 70.0)),
    "not an event spec": lambda: dict(events=("shock",)),
    "float in an event int range": lambda: dict(events=(ShockSpec(gap=(8.5, 12)),)),
}


@pytest.mark.parametrize("fields", BAD_TYPES.values(), ids=BAD_TYPES.keys())
def test_ec9_bad_types(fields):
    with pytest.raises(TypeError):
        config(**(fields() if callable(fields) else fields))


def test_ec9_whole_floats_are_cast():
    assert config(own_scale=4) == config(own_scale=4.0)
    assert engine_hash(config(own_scale=4)) == engine_hash(config(own_scale=4.0))
    assert isinstance(config(own_scale=4).own_scale, float)
    assert config(events=[ShockSpec()]).events == (ShockSpec(),)
    assert ShockSpec(gap=(np.int64(8), 12)).gap == (8, 12)
