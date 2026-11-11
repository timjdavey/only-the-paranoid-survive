"""AI15, AI16, AI23, AI24 and AI26: the Jev, Timestral and Up and down sections, and every cell's columns,
on hand-built CSVs.

See docs/specs/analysis/tests.md#pilot.
"""

import re
from pathlib import Path

import pandas as pd
import pytest

from paranoid.analysis import write_pilot

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "specs" / "harness" / "pilot.md"


def written_columns() -> dict[str, list[str]]:
    """Each CSV's columns, from the harness pilot spec's Writes lines, as the harness suite reads them."""
    found = re.findall(r"\*\*(?:Also )?[Ww]rites\*\* `([a-z-]+)\.csv`[^`]*`([^`]+)`", SPEC.read_text())
    return {name: [c.strip() for c in columns.split(",")] for name, columns in found}


def csv(folder: Path, name: str, rows: list[dict]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.csv"
    pd.DataFrame(rows, columns=written_columns()[name]).to_csv(path, index=False)
    return path


def table(out: Path, section: str, name: str) -> pd.DataFrame:
    return pd.read_csv(out / "results" / f"{section}-{name}.csv")


def test_ai15_jev_rounding(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    csv(
        logs,
        "jev",
        [
            {"model": "jev/x", "scenario": "no_change", "seed_index": 0, "round": r, "rounded_out": 2 if r < 3 else 0}
            for r in range(10)
        ],
    )
    write_pilot(logs, out)
    (row,) = table(out, "jev-checks", "rounding").itertuples()
    assert row.mean_rounded_out == pytest.approx(0.6) and row.rounded_share == pytest.approx(0.3)


def test_ai16_timestral(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    csv(
        logs,
        "timestral",
        [{"probe": "gap", "joint": 1, "gap": 1, "channel": 0, "spread": 4.0}, {"probe": "determinism", "joint": 1, "equal": 0}],
    )
    grid = [
        {"setting": 4.0, "scenario": "down_switch", "baseline": n, "seed": 0, "output": o}
        for n, o in (("uniform", 100), ("discerning", 200), ("hedge_rule", 170), ("complacent", 150))
    ]
    csv(logs, "noise-grid", grid)
    csv(
        logs, "timestral-grid", [{"setting": 4.0, "scenario": "down_switch", "model": "timestral/odds", "seed": 0, "output": 160}]
    )
    write_pilot(logs, out)
    gap_test = table(out, "timestral-checks", "gap-test")
    assert gap_test[gap_test["probe"] == "determinism"]["equal"].tolist() == [0]
    scores = table(out, "timestral-checks", "grid").set_index("baseline")["score"]
    assert scores.to_dict() | {} == pytest.approx(
        {"uniform": 0.0, "discerning": 1.0, "hedge_rule": 0.7, "complacent": 0.5, "timestral/odds": 0.6}
    )


@pytest.mark.parametrize("cell", list(written_columns()))
def test_ai23_every_column_read_is_a_column_written(cell, tmp_path):
    columns = written_columns()[cell]
    for name, header in (("extra", [*columns, "odd_one"]), ("short", columns[:-1])):
        logs = tmp_path / name
        logs.mkdir()
        pd.DataFrame(columns=header).to_csv(logs / f"{cell}.csv", index=False)
        odd = "odd_one" if name == "extra" else columns[-1]
        if cell == "recognition":
            odd = ""  # its header is held whole, so the message names the header it found
        with pytest.raises(ValueError, match=rf"{cell}\.csv.*{odd}"):
            write_pilot(logs, tmp_path / f"{name}-out")


def test_ai24_timestral_marks_on_the_seeds_it_played(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    outputs = {"uniform": (100, 100), "discerning": (200, 200), "hedge_rule": (170, 200), "complacent": (150, 100)}
    grid = [
        {"setting": 4.0, "scenario": "down_switch", "baseline": name, "seed": seed, "output": pair[seed >= 20]}
        for seed in range(30)
        for name, pair in outputs.items()
    ]  # pooled on all 30 seeds, the hedge rule's mark would be 0.8 and the Complacent baseline's 1/3
    csv(logs, "noise-grid", grid)
    played = [{"setting": 4.0, "scenario": "down_switch", "model": "timestral/odds", "seed": s, "output": 160} for s in range(20)]
    csv(logs, "timestral-grid", played)
    write_pilot(logs, out)
    rows = table(out, "timestral-checks", "grid").set_index("baseline")
    assert rows["seeds"].to_dict() == {name: 20 for name in [*outputs, "timestral/odds"]}
    assert rows.loc["hedge_rule", "score"] == pytest.approx(0.7) and rows.loc["complacent", "score"] == pytest.approx(0.5)


def test_ai26_a_move_round_of_0_is_never(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    moves = {"uniform": (0, 0, 0), "discerning": (0, 4, 8), "complacent": (0, 0, 0)}
    rows = [
        {
            "setting": 1.0,
            "scenario": "down_switch",
            "kind": "fall",
            "baseline": name,
            "seed": seed,
            "onset": 10,
            "output": {"uniform": 100, "discerning": 200, "complacent": 140}[name],
            "move_round": rounds[seed],
        }
        for name, rounds in moves.items()
        for seed in range(3)
    ]
    csv(logs, "up-and-down", rows)
    write_pilot(logs, out)
    median = table(out, "up-and-down", "kinds").set_index("player")["median_move_round"]
    assert median["discerning"] == 6 and pd.isna(median["complacent"])
