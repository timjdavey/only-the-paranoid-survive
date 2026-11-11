"""The provider cells that are plain evals: seeds, up-against-down, jev, bare, tool-choice, rolling and warm-up.

See docs/specs/harness/pilot.md#provider-cells. Every eval goes through the one call `run` uses,
plays `seeds="0-19"` and the example skin, and logs to `<out>/<cell>/`.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from inspect_ai.event import ModelEvent
from inspect_ai.log import read_eval_log
from inspect_ai.util import Store

from ..evals import EvalCall
from ..models import ModelRow, generate_config, load_models
from ..solver import tool_choice_for
from ..store import RunStore
from .common import CellArgs, write_csv

PILOT_SEEDS = "0-19"  # so every pilot log pairs by seed with every other


def rows_of(args: CellArgs, kind: str, *, first: bool = False) -> list[ModelRow]:
    """The models file's rows of one kind, narrowed by --only, or the first one when `first`."""
    rows = [row for row in load_models(args.models) if row.kind == kind]
    if args.only is not None:
        rows = [row for row in rows if row.id == args.only]
        if not rows:
            raise ValueError(f"--only {args.only!r} names no {kind} row in {args.models}")
    return rows[:1] if first else rows


def cell_eval(args: CellArgs, cell: str, row: ModelRow, task_args: dict[str, Any], **extra: Any) -> list[Path]:
    """One eval into `<out>/<cell>/`, or one printed line on a dry run."""
    call = EvalCall(row, row.reasoning[0], {"seeds": PILOT_SEEDS} | task_args, args.out / cell, **extra)
    if args.dry_run:
        print(call.line())
        return []
    return [Path(call.run().location)]


def each_llm(cell: str, scenario: str, settings: list[dict[str, Any]], *, first: bool = False) -> Callable:
    """A cell that plays every llm row, or the first, once per setting of the task args."""

    def run(args: CellArgs) -> list[Path]:
        paths: list[Path] = []
        for row in rows_of(args, "llm", first=first):
            for setting in settings:
                paths += cell_eval(args, cell, row, {"scenario": scenario} | setting)
        return paths

    return run


TOKEN_COLUMNS = (
    "model", "rolling", "scenario", "seed_index", "round", "input_tokens", "cache_read_tokens", "cache_write_tokens",
)  # fmt: skip
USAGE = ("input_tokens", "input_tokens_cache_read", "input_tokens_cache_write")  # inspect's names for the three


def with_tokens(cell: str, play: Callable) -> Callable:
    """A cell that also writes `<cell>-tokens.csv`, see docs/specs/harness/pilot.md#token-files."""

    def run(args: CellArgs) -> list[Path]:
        paths = play(args)
        return paths + write_csv(args, f"{cell}-tokens", TOKEN_COLUMNS, lambda: token_rows(paths))

    return run


def token_rows(paths: list[Path]):
    """One row per round the agent played, its tries' usage summed. Nothing but the usage is read."""
    for path in paths:
        log = read_eval_log(str(path))
        for sample in log.samples or []:
            if "gain" not in (sample.scores or {}):
                continue
            store = RunStore(store=Store(sample.store))
            events = iter(event for event in sample.events if isinstance(event, ModelEvent))
            for played, tries in enumerate(store.tries, start=store.warm_up_rounds + 1):
                usage = [event.output.usage for event in (next(events) for _ in range(tries))]
                totals = [sum((getattr(u, field) or 0) for u in usage if u is not None) for field in USAGE]
                meta = sample.metadata
                yield log.eval.model, int(bool(meta["rolling"])), meta["scenario"], meta["seed_index"], played, *totals


seeds = with_tokens("seeds", each_llm("seeds", "one_shock,up_switch", [{}]))
up_against_down = each_llm(
    "up-against-down", "no_change,down_switch,up_switch,up_switch_then_down_switch,switch_then_shock", [{}], first=True
)
bare = each_llm("bare", "one_shock,down_switch", [{"tools": t} for t in ("notes,compute", "notes", "compute", "none")])
rolling = with_tokens(
    "rolling", each_llm("rolling", "no_change,one_shock,down_switch", [{"rolling": False}, {"rolling": True}])
)
warm_up = each_llm("warm-up", "no_change,down_switch", [{}, {"warm_up": "complacent:5"}])


def tool_choice(args: CellArgs) -> list[Path]:
    """Both choices for every llm row that resolves to any. The api is the id's prefix, so no key is needed."""
    paths: list[Path] = []
    for row in rows_of(args, "llm"):
        api = row.id.split("/")[0]
        if tool_choice_for(api, generate_config(row, row.reasoning[0])) != "any":
            print(f"skipping {row.id}: it resolves to auto, so it cannot be asked for any")
            continue
        for choice in ("any", "auto"):
            paths += cell_eval(args, "tool-choice", row, {"scenario": "one_shock,down_switch", "tool_choice": choice})
    return paths


def jev(args: CellArgs) -> list[Path]:
    """One eval per jev row, then jev.csv: rounded_out per round, read from each reply's metadata."""
    paths: list[Path] = []
    for row in rows_of(args, "jev"):
        paths += cell_eval(args, "jev", row, {"scenario": "no_change,down_switch"})

    def rows():
        for path in paths:
            log = read_eval_log(str(path))
            for sample in log.samples or []:
                for event in sample.events:
                    if type(event).__name__ != "ModelEvent" or not event.output.message.tool_calls:
                        continue
                    played = int(event.output.message.tool_calls[0].id.rsplit("-", 1)[1])
                    rounded_out = (event.output.message.metadata or {}).get("rounded_out")
                    yield log.eval.model, sample.metadata["scenario"], sample.metadata["seed_index"], played, rounded_out

    columns = ("model", "scenario", "seed_index", "round", "rounded_out")
    return paths + write_csv(args, "jev", columns, rows)
