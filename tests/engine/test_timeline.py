"""ET1 to ET5, ET8, ET25, ET28 and ET37, see docs/specs/engine/tests.md#timeline."""

import dataclasses
import hashlib
import subprocess
import sys

import numpy as np
import pytest

from paranoid.engine import SCENARIOS, engine_hash, make_timeline

ARRAYS = ("levels", "base", "weather", "factor", "loadings", "impulse", "read_noise_z")
SEEDS = range(200)


def fingerprint(timeline) -> str:
    digest = hashlib.sha256()
    for name in ARRAYS:
        digest.update(getattr(timeline, name).tobytes())
    digest.update(repr(timeline.events).encode())
    return digest.hexdigest()


def test_et1_same_config_and_seed_same_timeline():
    config = SCENARIOS["shock_then_switch"]
    a, b = make_timeline(config, 7), make_timeline(config, 7)
    for name in ARRAYS:
        assert np.array_equal(getattr(a, name), getattr(b, name)), name
    assert a.events == b.events
    assert a.engine_hash == b.engine_hash == engine_hash(config)
    script = (
        "import hashlib\n"
        "from paranoid.engine import SCENARIOS, make_timeline\n"
        "t = make_timeline(SCENARIOS['shock_then_switch'], 7)\n"
        "d = hashlib.sha256()\n"
        f"for name in {ARRAYS!r}:\n"
        "    d.update(getattr(t, name).tobytes())\n"
        "d.update(repr(t.events).encode())\n"
        "print(d.hexdigest(), t.engine_hash)\n"
    )
    out = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
    assert out.stdout.split() == [fingerprint(a), a.engine_hash]


@pytest.mark.parametrize("name", SCENARIOS)
def test_et2_shapes(name):
    config = SCENARIOS[name]
    timeline = make_timeline(config, 3)
    for array in ("levels", "base", "weather", "loadings", "impulse", "read_noise_z"):
        assert getattr(timeline, array).shape == (config.rounds, config.channels), array
    assert timeline.factor.shape == (config.rounds,)


@pytest.mark.parametrize("name", SCENARIOS)
def test_et3_levels_add_up(name):
    t = make_timeline(SCENARIOS[name], 5)
    total = t.base + t.weather + t.loadings * t.factor[:, None] + t.impulse
    assert np.allclose(t.levels, total, rtol=0, atol=1e-9)


def test_et4_ladder():
    config = SCENARIOS["no_change"]
    for seed in SEEDS:
        t = make_timeline(config, seed)
        assert len({t.leader, t.runner_up, t.hedge}) == 3
        assert len(t.field) == config.channels - 2
        assert t.hedge in t.field
        assert set(t.field) | {t.leader, t.runner_up} == set(range(config.channels))
        row = t.base[0]
        others = [c for c in range(config.channels) if c not in (t.leader, t.runner_up)]
        assert row[t.leader] > row[t.runner_up] > max(row[c] for c in others)
        assert row[t.hedge] == row.min()
        for c in t.field:
            if c != t.hedge:
                assert row[c] <= row[t.runner_up] - config.field_headroom


def test_et5_loadings():
    config = SCENARIOS["no_change"]
    for seed in SEEDS:
        t = make_timeline(config, seed)
        for c, loading in enumerate(t.loadings[0]):
            low, high = config.hedge_loading if c == t.hedge else config.loading
            assert low <= loading <= high


def test_et8_onset():
    low, high = SCENARIOS["one_shock"].onset
    for seed in SEEDS:
        shock = make_timeline(SCENARIOS["one_shock"], seed).events[0].onset
        switch = make_timeline(SCENARIOS["down_switch"], seed).events[0].onset
        assert low <= shock <= high
        assert shock == switch


def test_et25_seed_bounds():
    config = SCENARIOS["one_shock"]
    make_timeline(config, 0)
    make_timeline(config, 2**64 - 1)
    with pytest.raises(ValueError):
        make_timeline(config, 2**64)
    with pytest.raises(ValueError):
        make_timeline(config, -1)
    with pytest.raises(TypeError):
        make_timeline(config, 1.0)


def test_et28_arrays_are_read_only():
    t = make_timeline(SCENARIOS["one_shock"], 0)
    for name in ARRAYS:
        with pytest.raises(ValueError):
            getattr(t, name)[0, ...] = 0.0


def test_et38_climate_leader_rejects_a_round_outside_the_run():
    t = make_timeline(SCENARIOS["no_change"], 0)
    assert t.climate_leader(1) == t.leader
    for round in (0, t.config.rounds + 1):
        with pytest.raises(ValueError):
            t.climate_leader(round)


@pytest.mark.parametrize("name", SCENARIOS)
def test_et37_inertia_cap_changes_the_hash_not_the_arrays(name):
    config = SCENARIOS[name]
    capped = dataclasses.replace(config, inertia_cap=20)
    assert engine_hash(capped) != engine_hash(config)
    for seed in range(20):
        a, b = make_timeline(config, seed), make_timeline(capped, seed)
        assert fingerprint(a) == fingerprint(b)
