"""main, the `paranoid` console script: run, pilot, and subcommands from other layers.

See docs/specs/harness/command.md. Other layers plug in through the `paranoid.commands` entry point
group, loaded only when named, so the harness never imports the analysis layer.
"""

import argparse
import math
import sys
from collections.abc import Sequence
from importlib.metadata import entry_points
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from paranoid.forecasters import require_timestral

from .config import loaded_skins
from .evals import EvalCall
from .models import SKIN_READERS, ModelRow, load_models
from .seeds import load_grid

BUILT_IN = ("run", "pilot")


def plugins() -> dict:
    return {ep.name: ep for ep in entry_points(group="paranoid.commands")}


def main(argv: Sequence[str] | None = None) -> int:
    """Returns 0 on success and 1 on a ValueError, whose message it prints."""
    load_dotenv(find_dotenv(usecwd=True), override=False)
    argv = list(sys.argv[1:] if argv is None else argv)
    extra = plugins()
    try:
        command = argv[0] if argv else ""
        if command not in BUILT_IN and command not in extra:
            known = ", ".join([*BUILT_IN, *sorted(extra)])
            raise ValueError(f"unknown subcommand {command!r}. Subcommands: {known}")
        if command not in BUILT_IN:
            return int(extra[command].load()(argv[1:]))
        args = parser().parse_args(argv)
        return args.handler(args)
    except ValueError as error:
        print(error)
        return 1


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(prog="paranoid")
    subcommands = top.add_subparsers(dest="command", required=True)
    run_args = subcommands.add_parser("run", help="play every row of a models config through the task")
    run_args.add_argument("--models", type=Path, default=Path("configs/models/poc.toml"))
    run_args.add_argument("--skins", default="example")
    run_args.add_argument("--seeds", default="public")
    run_args.add_argument("--own-scale", dest="own_scale", default=None)
    run_args.add_argument("--limit", type=int, default=None)
    run_args.add_argument("--log-dir", dest="log_dir", type=Path, default=Path("logs"))
    run_args.add_argument("--only", default=None)
    run_args.add_argument("--dry-run", dest="dry_run", action="store_true")
    run_args.set_defaults(handler=run)
    pilot_args = subcommands.add_parser("pilot", help="run one pilot cell")
    pilot_args.add_argument("check")
    pilot_args.add_argument("--out", type=Path, default=Path("logs/pilot"))
    pilot_args.add_argument("--models", type=Path, default=Path("configs/models/poc.toml"))
    pilot_args.add_argument("--only", default=None)
    pilot_args.add_argument("--seeds", type=int, default=1000)
    pilot_args.add_argument("--workers", type=int, default=1, help="processes an engine cell splits its seeds over")
    pilot_args.add_argument("--dry-run", dest="dry_run", action="store_true")
    pilot_args.set_defaults(handler=pilot)
    return top


def skin_names(arg: str) -> list[str]:
    """Every name loaded and none twice, checked before any eval runs."""
    names = [name.strip() for name in arg.split(",")]
    loaded = loaded_skins()
    for name in names:
        if name not in loaded or names.count(name) > 1:
            what = "is not loaded" if name not in loaded else "is named twice"
            raise ValueError(f"skin {name!r} {what}. Loaded: {', '.join(loaded)}. Held-out skins load from PARANOID_SKINS")
    return names


def own_scales(arg: str | None) -> list[float | None]:
    if arg is None:
        return [None]
    if arg == "grid":
        return list(load_grid().own_scale)
    try:
        value = float(arg)
    except ValueError:
        raise ValueError(f"--own-scale must be a positive number or grid, got {arg!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"--own-scale must be a positive number or grid, got {arg!r}")
    return [value]


def ordered(rows: list[ModelRow], only: str | None) -> list[ModelRow]:
    """Provider rows first, then LLM rows, each in file order."""
    if only is not None:
        rows = [row for row in rows if row.id == only]
        if not rows:
            raise ValueError(f"no row in the models file has id {only!r}")
    return [row for row in rows if row.kind != "llm"] + [row for row in rows if row.kind == "llm"]


def timestral_missing() -> bool:
    try:
        require_timestral()
    except ImportError:
        return True
    return False


def run(args: argparse.Namespace) -> int:
    rows = ordered(load_models(args.models), args.only)
    skins = skin_names(args.skins)
    scales = own_scales(args.own_scale)
    failed = False
    for row in rows:
        if row.kind == "timestral" and timestral_missing():
            print(f"skipping {row.id}: the timestral extra is not installed, run `uv sync --extra timestral`")
            continue
        for reasoning in row.reasoning:
            for skin in skins if row.kind in SKIN_READERS else skins[:1]:
                for scale in scales:
                    task_args = {"skin": skin, "seeds": args.seeds}
                    if scale is not None:
                        task_args["own_scale"] = scale
                    call = EvalCall(row, reasoning, task_args, args.log_dir, limit=args.limit)
                    if args.dry_run:
                        print(call.line())
                        continue
                    failed |= not played(call)
    return 1 if failed else 0


def played(call: EvalCall) -> bool:
    """Runs one eval. A failure is printed and the run carries on to the next."""
    try:
        log = call.run()
    except Exception as error:  # noqa: BLE001, an eval that cannot start is infrastructure
        print(f"{call.row.id} failed: {type(error).__name__}: {error}")
        return False
    if log.status != "success":
        print(f"{call.row.id} ended {log.status}: {log.error.message if log.error else ''}")
        return False
    return True


def pilot(args: argparse.Namespace) -> int:
    from .pilot import CellArgs, run_cell, seed_cap

    cell = CellArgs(
        out=args.out, models=args.models, only=args.only, seeds=seed_cap(args.seeds), dry_run=args.dry_run, workers=args.workers
    )
    for path in run_cell(args.check, cell):
        print(path)
    return 0
