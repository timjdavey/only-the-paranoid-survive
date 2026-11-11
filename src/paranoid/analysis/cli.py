"""analyse, the `paranoid analyse` subcommand: results, pilot, cost and gap. See docs/specs/analysis/command.md.

The harness's `main` finds it through the `paranoid.commands` entry point and passes the arguments after `analyse`.
"""

import argparse
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pandas as pd

from .cost import write_cost
from .gaps import paired_gap
from .keys import keys_in, label
from .pilot import write_pilot
from .runs import load_runs, mean_over_epochs, report_lines
from .scores import load_recognition
from .tables import write_results

SUBCOMMANDS = ("results", "pilot", "cost", "gap")
DEFAULT_MODELS = Path("configs/models/poc.toml")
DEFAULT_PRICES = Path("configs/prices.toml")


def analyse(argv: Sequence[str]) -> int:
    """Returns 0 on success and 1 on a ValueError, whose message it prints."""
    argv = list(argv)
    if not argv or argv[0] not in SUBCOMMANDS:
        argv = ["results", *argv]  # a first argument that is not a subcommand is a path
    try:
        args = parser().parse_args(argv)
        return args.handler(args)
    except ValueError as error:
        print(error)
        return 1


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(prog="paranoid analyse")
    commands = top.add_subparsers(dest="command", required=True)
    results = commands.add_parser("results", help="write the results page, its CSV and plots")
    results.add_argument("logs", nargs="*", type=Path, default=[Path("logs")])
    results.add_argument("--out", type=Path, default=Path("docs/results"))
    results.add_argument("--name", default="poc")
    results.add_argument("--models", type=Path, default=None)
    results.add_argument("--recognition", type=Path, default=Path("logs/pilot/recognition.csv"))
    results.add_argument("--plots", action="store_true")
    results.add_argument("--eci-read-on", dest="eci_read_on", type=date.fromisoformat, default=None)
    results.add_argument("--dry-run", dest="dry_run", action="store_true")
    results.set_defaults(handler=run_results)
    pilot = commands.add_parser("pilot", help="write pilot results from the pilot cells")
    pilot.add_argument("--logs", type=Path, default=Path("logs/pilot"))
    pilot.add_argument("--out", type=Path, default=Path("docs/pilot"))
    pilot.add_argument("--main", type=Path, default=None)
    pilot.add_argument("--dry-run", dest="dry_run", action="store_true")
    pilot.set_defaults(handler=run_pilot)
    cost = commands.add_parser("cost", help="print tokens per run and what the full study would cost")
    cost.add_argument("logs", nargs="*", type=Path, default=[Path("logs")])
    cost.add_argument("--models", type=Path, default=None)
    cost.add_argument("--seeds", type=int, default=None)
    cost.add_argument("--prices", type=Path, default=None)
    cost.set_defaults(handler=run_cost)
    gap = commands.add_parser("gap", help="print the paired gap between two logs")
    gap.add_argument("a", type=Path)
    gap.add_argument("b", type=Path)
    gap.set_defaults(handler=run_gap)
    return top


def models_of(given: Path | None) -> Path | None:
    """The models file typed, which must exist, else the default when it is there."""
    if given is not None:
        if not given.exists():
            raise ValueError(f"no models file at {given}")
        return given
    return DEFAULT_MODELS if DEFAULT_MODELS.exists() else None


def loaded(paths: Sequence[Path]) -> pd.DataFrame:
    runs = load_runs(paths)
    print("\n".join(report_lines(runs.attrs["report"])))
    return runs


def run_results(args: argparse.Namespace) -> int:
    runs = loaded(args.logs)
    recognition = load_recognition(args.recognition) if args.recognition.exists() else None
    paths = write_results(
        runs,
        args.out,
        args.name,
        models=models_of(args.models),
        recognition=recognition,
        plots=args.plots,
        eci_read_on=args.eci_read_on,
        dry_run=args.dry_run,
    )
    print(("Would write:" if args.dry_run else "Wrote:") + "".join(f"\n  {path}" for path in paths))
    return 0


def run_pilot(args: argparse.Namespace) -> int:
    paths = write_pilot(args.logs, args.out, main=args.main, dry_run=args.dry_run)
    print(("Would write:" if args.dry_run else "Wrote:") + "".join(f"\n  {path}" for path in paths))
    return 0


def run_cost(args: argparse.Namespace) -> int:
    prices = args.prices
    if prices is None:
        prices = DEFAULT_PRICES if DEFAULT_PRICES.exists() else None
        if prices is None:
            print(f"No prices at {DEFAULT_PRICES}, so the table has no cost column.")
    elif not prices.exists():
        raise ValueError(f"no prices file at {prices}")
    table = write_cost(loaded(args.logs), models=models_of(args.models), seeds=args.seeds, prices=prices)
    print(table.to_string(index=False))
    if "read_on" in table.attrs:
        print(f"Prices read on {table.attrs['read_on']}.")
    return 0


def run_gap(args: argparse.Namespace) -> int:
    keys = []
    for path in (args.a, args.b):
        found = keys_in(load_runs([path]))
        if len(found) != 1:
            raise ValueError(
                f"{path} holds {len(found)} result rows, {', '.join(map(label, found)) or 'none'}, and a gap needs one"
            )
        keys.append(found[0])
    if keys[0] == keys[1]:
        raise ValueError(f"both logs are {label(keys[0])} on one setting, so the gap would be a row against itself")
    runs = mean_over_epochs(loaded([args.a, args.b]))
    print(paired_gap(runs, keys[0], keys[1]).to_string(index=False))
    return 0
