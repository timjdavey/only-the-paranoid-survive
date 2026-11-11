"""HK4, HK5, HK12 and HK14's grid half, see docs/specs/harness/tests.md#task."""

import pytest

from paranoid.engine import SCENARIOS
from paranoid.harness import load_grid, load_seeds, parse_seeds, scenario_config


def test_hk4_parse_seeds(configs, monkeypatch):
    configs(seeds=[11, 12, 13, 14, 15, 16])
    assert parse_seeds("0-4") == [(0, 11), (1, 12), (2, 13), (3, 14), (4, 15)]
    assert parse_seeds("3") == [(3, 14)]
    assert parse_seeds("4,0-1") == [(0, 11), (1, 12), (4, 15)]
    assert parse_seeds(["0-1", "4"]) == [(0, 11), (1, 12), (4, 15)]  # as inspect splits -T seeds=0-1,4
    assert parse_seeds("public") == list(enumerate([11, 12, 13, 14, 15, 16]))
    for bad in ("4-2", "1,1", "0-2,2", "6", "x", "-1"):
        with pytest.raises(ValueError):
            parse_seeds(bad)
    with pytest.raises(ValueError, match="PARANOID_SEEDS"):
        parse_seeds("held-out")
    monkeypatch.delenv("PARANOID_SEEDS")
    with pytest.raises(ValueError, match="PARANOID_SEEDS"):
        load_seeds("held-out")


def test_hk5_a_seed_file(tmp_path, monkeypatch):
    monkeypatch.setenv("PARANOID_SEEDS", str(tmp_path))
    (tmp_path / "held-out.txt").write_text("# a comment\n\n 7\n3\n\n")
    assert load_seeds("held-out") == [7, 3]
    assert parse_seeds("held-out") == [(0, 7), (1, 3)]
    (tmp_path / "held-out.txt").write_text("7\n3\n70\n7\n")
    with pytest.raises(ValueError, match="line 4 repeats") as caught:
        load_seeds("held-out")
    assert "70" not in str(caught.value)


def test_the_public_list_is_0_to_999():
    assert load_seeds("public") == list(range(1000))


def test_hk12_the_grid_builds(configs):
    grid = load_grid()
    assert grid.own_scale and all(isinstance(s, float) and s > 0 for s in grid.own_scale)
    assert SCENARIOS["no_change"].own_scale in grid.own_scale
    for name in SCENARIOS:
        for setting in grid.own_scale:
            scenario_config(name, own_scale=setting)
    configs(grid='release = "dev"\nown_scale = [2.0, 0]\n')
    with pytest.raises(ValueError):
        load_grid()


def test_hk14_the_release(configs):
    assert load_grid().release == "dev"
    configs(grid='release = "R 1"\nown_scale = [4.0]\n')
    with pytest.raises(ValueError, match="release"):
        load_grid()
