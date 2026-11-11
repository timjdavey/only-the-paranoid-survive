"""paranoid, the one inspect task, and its dataset. See docs/specs/harness/task.md.

One sample is one run: one scenario, one seed, one skin. A held-out seed's value never reaches the log.
"""

import os
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from inspect_ai import Epochs, Task, task
from inspect_ai.dataset import MemoryDataset, Sample

from paranoid.engine import GENERATOR_VERSION, ScenarioConfig, engine_hash
from paranoid.skins import Skin, prompt_hash

from .config import check_tool_choice, joined, parse_scenarios, parse_tools, parse_warm_up, scenario_config, skin_named
from .scorer import gain
from .seeds import load_grid, parse_seeds, seed_set_of
from .solver import round_loop
from .version import harness_version

COMPOSE = Path(__file__).parent / "compose.yaml"
TRACEBACK_LOCALS = "INSPECT_TRACEBACK_LOCALS"  # inspect prints every local in a traceback when it is 1


@task
def paranoid(
    scenario: str | list[str] = "all",
    seeds: str | list[str] = "public",
    skin: str = "example",
    rounds: int | None = None,
    tools: str | list[str] = "notes,compute",
    tool_choice: str | None = None,
    inertia: int | None = None,
    warm_up: str | None = None,
    own_scale: float | None = None,
    rolling: bool = False,
) -> Task:
    """One sample per scenario per seed. See docs/specs/harness/task.md#interface."""
    names = parse_scenarios(scenario)
    if seed_set_of(seeds) == "held-out" and os.environ.get(TRACEBACK_LOCALS) == "1":
        raise ValueError(f"{TRACEBACK_LOCALS}=1 would print held-out seeds into a traceback. Unset it to play them")
    pilot_tools = parse_tools(tools)
    check_tool_choice(tool_choice)
    the_skin = skin_named(skin)
    configs = {name: scenario_config(name, rounds=rounds, inertia=inertia, own_scale=own_scale) for name in names}
    for name, config in configs.items():
        if len(the_skin.channels) != config.channels:
            raise ValueError(
                f"skin {skin} has {len(the_skin.channels)} channels and scenario {name} has {config.channels}"
            )
        parse_warm_up(warm_up, config.rounds)
    knobs = {
        "inertia": inertia,
        "own_scale": own_scale,
        "tools": ",".join(pilot_tools) or "none",
        "warm_up": warm_up,
        "rolling": rolling,
    }
    samples = dataset(configs, seeds, the_skin, knobs)
    return Task(
        dataset=MemoryDataset(samples, name="paranoid"),
        solver=round_loop(the_skin, knobs["tools"], tool_choice=tool_choice, rolling=rolling),
        scorer=gain(),
        epochs=Epochs(1, "mean"),
        fail_on_error=0.1,
        sandbox=("docker", str(COMPOSE)) if "compute" in pilot_tools else None,
    )


def dataset(
    configs: dict[str, ScenarioConfig], seeds: str | Sequence[str], skin: Skin, knobs: dict[str, object]
) -> list[Sample]:
    """Scenarios in SCENARIOS order, seeds in file order. Every identifier a reader needs is in the metadata."""
    seed_set = seed_set_of(seeds)
    pairs = parse_seeds(seeds)
    shared = {
        "seed_set": seed_set,
        "seeds_arg": joined(seeds),
        "skin": skin.name,
        "generator_version": GENERATOR_VERSION,
        "numpy_version": np.__version__,
        "prompt_hash": prompt_hash(skin),
        "release": load_grid().release,
        "harness_version": harness_version(),
        **knobs,
    }
    samples = []
    for name, config in configs.items():
        for position, seed in pairs:
            metadata = {"scenario": name, "seed_index": position, **shared}
            metadata |= {"engine_hash": engine_hash(config), "rounds": config.rounds}
            if seed_set == "public":
                metadata["seed"] = seed
            sample_id = f"{name}/{position}"
            samples.append(Sample(id=sample_id, input=sample_id, metadata=metadata))
    return samples
