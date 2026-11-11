"""The repeats cell: the widest spread from the seeds cell, played again at four epochs.

See docs/specs/harness/pilot.md#repeats.
"""

from pathlib import Path

import numpy as np
from inspect_ai.log import list_eval_logs, read_eval_log

from ..models import ModelRow, load_models
from .common import CellArgs
from .evals import cell_eval

PICKS = 10
EPOCHS = 4


def newest_whole_logs(folder: Path) -> list[str]:
    """The seeds logs whose status is success, the newest per model and reasoning, in file order."""
    logs = sorted(info.name for info in list_eval_logs(str(folder))) if folder.is_dir() else []
    newest: dict[tuple, tuple[str, str]] = {}
    for location in logs:
        header = read_eval_log(location, header_only=True)
        if header.status != "success":
            continue
        key = (header.eval.model, (header.eval.metadata or {}).get("reasoning"))
        if key not in newest or header.eval.created > newest[key][0]:
            newest[key] = (header.eval.created, location)
    kept = {location for _, location in newest.values()}
    return [location for location in logs if location in kept]


def widest(args: CellArgs) -> tuple[ModelRow, str, list[int]] | None:
    """The row and scenario with the widest SD of run_score in the seeds logs, and the ten positions picked.

    Only logs that ran whole and are the newest of their model and reasoning count, and only scenarios of ten or
    more scored samples, so the ten picks are ten different seeds.
    """
    best: tuple[float, str, str, list] | None = None
    for location in newest_whole_logs(args.out / "seeds"):
        log = read_eval_log(location)
        by_scenario: dict[str, list] = {}
        for sample in log.samples or []:
            if sample.scores and sample.scores["gain"].value["run_score"] is not None:  # type: ignore[index]
                by_scenario.setdefault(sample.metadata["scenario"], []).append(sample)
        for scenario, samples in by_scenario.items():
            if len(samples) < PICKS:
                continue
            spread = float(np.std([s.scores["gain"].value["run_score"] for s in samples], ddof=1))
            if best is None or spread > best[0]:
                best = (spread, location, scenario, samples)
    if best is None:
        return None
    _, location, scenario, samples = best
    log = read_eval_log(location, header_only=True)
    reasoning = (log.eval.metadata or {}).get("reasoning")
    row = next((r for r in load_models(args.models) if r.id == log.eval.model and reasoning in r.reasoning), None)
    if row is None:
        raise ValueError(f"the seeds log's model {log.eval.model} at {reasoning} is not in {args.models}")
    ranked = sorted(samples, key=lambda s: (s.scores["gain"].value["run_score"], s.metadata["seed_index"]))
    last = len(ranked) - 1
    picks = [ranked[round(last * i / (PICKS - 1))].metadata["seed_index"] for i in range(PICKS)]
    return row, scenario, sorted(picks)


def repeats(args: CellArgs) -> list[Path]:
    found = widest(args)
    if found is None:
        if args.dry_run:
            print("repeats: no seeds log yet, so the eval it would run is not known. Run `paranoid pilot seeds` first")
            return []
        raise ValueError(f"repeats needs the seeds cell's logs in {args.out / 'seeds'}. Run `paranoid pilot seeds` first")
    row, scenario, positions = found
    seeds = ",".join(str(p) for p in positions)
    print(f"repeats: {row.id} at {row.reasoning[0]}, {scenario}, positions {seeds}")
    return cell_eval(args, "repeats", row, {"scenario": scenario, "seeds": seeds}, epochs=EPOCHS)
