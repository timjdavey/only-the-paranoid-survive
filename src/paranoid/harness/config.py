"""scenario_config, and the checks on the task args. See docs/specs/harness/task.md#scenarios-and-config.

Its own module, as the store needs it and the task needs the store.
"""

from collections.abc import Sequence
from dataclasses import replace

from paranoid.baselines import POLICIES
from paranoid.engine import SCENARIOS, ScenarioConfig

TOOLS = ("notes", "compute")
TOOL_CHOICES = ("any", "auto")


def joined(arg: str | Sequence[str]) -> str:
    """A comma list as one string. inspect splits `-T scenario=a,b` into a list before the task sees it."""
    return arg if isinstance(arg, str) else ",".join(str(part) for part in arg)


def check_scenario(name: str) -> None:
    if name not in SCENARIOS:
        raise ValueError(f"unknown scenario {name!r}, the known ones are {', '.join(SCENARIOS)}")


def scenario_config(
    name: str, *, rounds: int | None = None, inertia: int | None = None, own_scale: float | None = None
) -> ScenarioConfig:
    """`SCENARIOS[name]` with the knobs replaced, so the engine's validation runs again."""
    check_scenario(name)
    changes: dict[str, object] = {}
    if rounds is not None:
        changes["rounds"] = rounds
    if inertia is not None:
        changes["inertia_cap"] = inertia
    if own_scale is not None:
        changes |= {"own_scale": own_scale, "pin_in_level_points": True}
    return replace(SCENARIOS[name], **changes)


def parse_scenarios(arg: str | Sequence[str]) -> list[str]:
    """`all`, or the names given, each checked. Always in SCENARIOS order."""
    text = joined(arg)
    if text == "all":
        return list(SCENARIOS)
    names = [name.strip() for name in text.split(",")]
    for name in names:
        check_scenario(name)
    return [name for name in SCENARIOS if name in names]


def parse_tools(arg: str | Sequence[str]) -> tuple[str, ...]:
    """The pilot tools asked for, in TOOLS order. `none` is the empty tuple."""
    text = joined(arg)
    if text == "none":
        return ()
    names = [name.strip() for name in text.split(",")]
    for name in names:
        if name not in TOOLS:
            raise ValueError(f"unknown tool {name!r}, tools is a comma list of {' and '.join(TOOLS)}, or none")
    return tuple(name for name in TOOLS if name in names)


def check_tool_choice(tool_choice: str | None) -> None:
    if tool_choice is not None and tool_choice not in TOOL_CHOICES:
        raise ValueError(f"tool_choice must be any, auto or unset, got {tool_choice!r}")


def parse_warm_up(arg: str | None, rounds: int) -> tuple[str, int] | None:
    """`<baseline>:<k>`, a key of POLICIES and 1 ≤ k < rounds. None when unset."""
    if arg is None:
        return None
    name, colon, count = arg.partition(":")
    if not colon or name not in POLICIES:
        raise ValueError(f"warm_up must be <baseline>:<rounds>, the baseline one of {', '.join(POLICIES)}")
    try:
        k = int(count)
    except ValueError:
        raise ValueError(f"warm_up rounds must be a whole number, got {count!r}") from None
    if not 1 <= k < rounds:
        raise ValueError(f"warm_up rounds must be at least 1 and below {rounds}, got {k}")
    return name, k
