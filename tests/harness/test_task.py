"""HK1, HK2, HK3's sample half, HK6 to HK8, HK10 and HK13, see docs/specs/harness/tests.md#task.

Task tests build the task and read its dataset. The ones that need a log play mockllm's default
text reply, which gives up on round 1 after ten tries: cheap, and enough to read the metadata.
"""

from pathlib import Path

import pytest
from inspect_ai.model import get_model

from paranoid.engine import SCENARIOS, engine_hash
from paranoid.harness import load_grid, load_seeds, paranoid, scenario_config
from paranoid.skins import prompt_hash

KEYS = {
    "scenario", "seed_set", "seed_index", "seeds_arg", "seed", "skin", "engine_hash", "generator_version",
    "numpy_version", "prompt_hash", "release", "harness_version", "rounds", "inertia", "own_scale", "tools",
    "warm_up", "rolling",
}  # fmt: skip
HELD_OUT = [7340591, 2280417, 9135562]


def test_hk1_the_default_dataset():
    samples = list(paranoid().dataset)
    seeds = load_seeds("public")
    assert len(samples) == 8 * len(seeds)
    assert [s.id for s in samples[: len(seeds)]] == [f"no_change/{i}" for i in range(len(seeds))]
    assert [s.id.split("/")[0] for s in samples[:: len(seeds)]] == list(SCENARIOS)
    for sample in samples[:3]:
        assert set(sample.metadata) == KEYS and sample.input == sample.id
    assert samples[5].metadata["seed"] == seeds[5] and samples[5].metadata["tools"] == "notes,compute"


def test_hk2_scenarios():
    task = paranoid(scenario="down_switch,one_shock", seeds="0-1")
    assert [s.id for s in task.dataset] == ["one_shock/0", "one_shock/1", "down_switch/0", "down_switch/1"]
    assert [s.id for s in paranoid(scenario=["down_switch", "one_shock"], seeds="0").dataset][0] == "one_shock/0"
    with pytest.raises(ValueError, match="nope"):
        paranoid(scenario="nope")


def test_hk3_each_sample_has_its_config_hash():
    task = paranoid(scenario="one_shock,down_switch", seeds="0", rounds=20, inertia=10, own_scale=2.0)
    for sample in task.dataset:
        config = scenario_config(sample.metadata["scenario"], rounds=20, inertia=10, own_scale=2.0)
        assert sample.metadata["engine_hash"] == engine_hash(config) and sample.metadata["rounds"] == 20


def test_hk6_held_out_seeds(tmp_path, monkeypatch, helpers):
    monkeypatch.setenv("PARANOID_SEEDS", str(tmp_path))
    (tmp_path / "held-out.txt").write_text("".join(f"{s}\n" for s in HELD_OUT))
    log = helpers.run(get_model("mockllm/model"), scenario="no_change,one_shock", seeds="held-out")
    assert len(log.samples) == 6
    for sample in log.samples:
        assert sample.metadata["seed_set"] == "held-out" and "seed" not in sample.metadata
        assert sample.id == f"{sample.metadata['scenario']}/{sample.metadata['seed_index']}"
        assert helpers.store_of(sample).seed() == HELD_OUT[sample.metadata["seed_index"]]
        assert "seed" not in sample.scores["gain"].metadata
    text = log.model_dump_json()
    assert not any(str(seed) in text for seed in HELD_OUT)
    for path in Path(log.location).parent.iterdir():
        assert not any(str(seed).encode() in path.read_bytes() for seed in HELD_OUT)


def test_hk7_bad_settings():
    with pytest.raises(ValueError, match="example"):
        paranoid(skin="nope")
    for bad in ({"tools": "laser"}, {"tool_choice": "laser"}, {"warm_up": "nope:5"}):
        with pytest.raises(ValueError):
            paranoid(seeds="0", **bad)
    with pytest.raises(ValueError, match="scenario"):
        paranoid(scenario="../x", seeds="../x")


def test_hk8_task_settings():
    task = paranoid(seeds="0")
    assert task.fail_on_error == 0.1
    assert task.sandbox is not None and task.sandbox.type == "docker" and Path(task.sandbox.config).exists()
    assert paranoid(seeds="0", tools="compute").sandbox is not None
    assert paranoid(seeds="0", tools="notes").sandbox is None
    assert paranoid(seeds="0", tools="none").sandbox is None
    assert [s.metadata["tools"] for s in paranoid(seeds="0", tools="compute,notes").dataset][0] == "notes,compute"


def test_hk10_hashes_and_version(example):
    for sample in paranoid(scenario="one_shock", seeds="0-2").dataset:
        assert sample.metadata["prompt_hash"] == prompt_hash(example)
        assert isinstance(sample.metadata["harness_version"], str) and sample.metadata["harness_version"]
        assert sample.metadata["release"] == load_grid().release == "dev"


def test_hk13_a_skin_that_does_not_fit(tmp_path, monkeypatch, skin_file):
    skin_file(tmp_path / "four.toml", channels=["Ashford", "Brill", "Corran", "Dunmore"])
    monkeypatch.setenv("PARANOID_SKINS", str(tmp_path))
    with pytest.raises(ValueError, match="four.*no_change"):
        paranoid(skin="four")
