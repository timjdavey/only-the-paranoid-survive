"""HP1, HP3, HP4, HP9, HP11, HP12 to HP14 and HP16: the engine cells. See docs/specs/harness/tests.md#pilot.

Every cell runs with PARANOID_PILOT_SEEDS=5 into a temp `out`. The columns are read from the pilot spec's
Writes lines, so the CSV and the page cannot drift apart.
"""

import csv
import re
import socket
from dataclasses import replace
from pathlib import Path

import pytest

from paranoid.baselines import complacent, discerning
from paranoid.engine import SCENARIOS, Game, make_timeline, play
from paranoid.harness import CELLS, CellArgs, load_grid, load_seeds, run_cell

SPEC = Path(__file__).parents[2] / "docs" / "specs" / "harness" / "pilot.md"
SEEDS, GRID = 5, len(load_grid().own_scale)
POLICIES, SCENARIO_COUNT = 7, 8
ROWS = {  # one row per seed per setting per scenario per baseline, as each Runs line says
    "streaks": 4 * 2 * SEEDS,
    "tell": (4 * 2 + 27) * 3 * SEEDS,
    "luck": GRID * SEEDS,
    "timeline-sanity": GRID * SCENARIO_COUNT * SEEDS,
    "timeline-sanity-sparklines": SCENARIO_COUNT * 40,
    "noise-grid": GRID * 3 * POLICIES * SEEDS,
    "game-length": 9 * (4 + 3 * 3) * POLICIES * SEEDS + 9 * 3 * SEEDS,
    "reading-roughness": 3 * (9 * 2 + 3 * 2 + 3) * SEEDS,
    "up-and-down": 3 * 3 * 9 * SEEDS,
    "bayesian-frontier": SCENARIO_COUNT * (3 + 5) * SEEDS,  # three players and five fixed baselines
    "baseline-order": SCENARIO_COUNT * POLICIES * SEEDS + SEEDS,
}
ENGINE = ["streaks", "tell", "luck", "timeline-sanity", "noise-grid", "game-length", "reading-roughness"]
ENGINE += ["up-and-down", "bayesian-frontier", "baseline-order"]
SLOW = ("game-length",)


def written_columns() -> dict[str, list[str]]:
    """Each CSV's columns, from the spec's `Writes` and `Also writes` lines."""
    found = re.findall(r"\*\*(?:Also )?[Ww]rites\*\* `([a-z-]+)\.csv`[^`]*`([^`]+)`", SPEC.read_text())
    return {name: [c.strip() for c in columns.split(",")] for name, columns in found}


def read(path: Path) -> list[dict]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    monkeypatch.setenv("PARANOID_PILOT_SEEDS", str(SEEDS))

    def no_network(*args, **kwargs):
        raise OSError("the network is blocked in the pilot tests")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    return CellArgs(out=tmp_path / "out")


@pytest.mark.parametrize("cell", [pytest.param(c, marks=pytest.mark.slow) if c in SLOW else c for c in ENGINE])
def test_hp1_each_engine_cell(cell, pilot):
    paths = run_cell(cell, pilot)
    columns = written_columns()
    assert paths and all(path.parent == pilot.out for path in paths)
    for path in paths:
        name = path.stem
        with path.open(newline="") as file:
            header = next(csv.reader(file))
        assert header == columns[name], name
        assert len(read(path)) == ROWS[name], name


def test_hp3_too_few_public_seeds(configs, pilot, monkeypatch):
    configs(seeds=list(range(10)))
    monkeypatch.delenv("PARANOID_PILOT_SEEDS")
    with pytest.raises(ValueError, match="PARANOID_PILOT_SEEDS"):
        run_cell("luck", CellArgs(out=pilot.out, seeds=20))


@pytest.fixture
def order(pilot) -> list[dict]:
    (path,) = run_cell("baseline-order", pilot)
    return read(path)


def timeline(row):
    return make_timeline(SCENARIOS[row["scenario"]], int(row["seed"]))


def test_hp4_baseline_order_words(order):
    for row in order:
        t = timeline(row)
        if row["scenario"] == "down_switch":
            assert row["kind"] == t.events[0].numbers["kind"]
            if row["baseline"] == "discerning":
                switch = t.events[0]
                assert switch.onset <= int(row["move_round"]) <= switch.onset + switch.numbers["ramp"] - 1
        if row["scenario"] == "no_change" and row["baseline"] == "discerning":
            assert row["move_round"] == "0"
        if row["baseline"] == "complacent":
            assert row["move_round"] == "0"


def test_hp11_the_stayer(order):
    stayers = [row for row in order if row["baseline"] == "stayer"]
    assert {row["scenario"] for row in stayers} == {"up_switch_then_down_switch"}
    assert sorted(int(row["seed"]) for row in stayers) == load_seeds("public")[:SEEDS]
    discerning = {row["seed"]: row for row in order if row["baseline"] == "discerning" and row["scenario"] == "up_switch_then_down_switch"}
    for row in stayers:
        t = timeline(row)
        assert row["move_round"] == discerning[row["seed"]]["move_round"]
        undo = t.events[-1]
        assert t.climate_leader(undo.onset - 1) == t.sleeper
        rounds = t.config.rounds
        held = sum(r.output for r in held_record(t).rows)
        assert float(row["output"]) == pytest.approx(held)
        if undo.onset + int(undo.numbers["ramp"]) - 1 < rounds:
            assert t.climate_leader(rounds) == t.leader


def held_record(t):
    """The Stayer's record, built here from its rule: discerning until the last event begins, then hold."""
    game = Game(t)
    while not game.done:
        held = t.climate_leader(min(game.round, t.events[-1].onset - 1))
        game.play([100 if c == held else 0 for c in range(t.config.channels)])
    return game.record


def test_hp9_a_dry_run_writes_nothing(pilot, capsys):
    for cell in ENGINE:
        assert run_cell(cell, CellArgs(out=pilot.out, dry_run=True)) == []
    assert not pilot.out.exists()
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == len(ENGINE) + 1  # timeline-sanity writes two files
    assert all(": " in line and line.split(": ")[0].endswith(".csv") for line in lines)
    assert set(ENGINE) <= set(CELLS)


def test_hp12_fall_and_tell_rounds(pilot):
    (path,) = run_cell("tell", pilot)
    rows = read(path)
    for row in rows:
        if row["scenario"] == "no_change":
            assert row["fall_rounds"] == row["tell_rounds"] == ""
            continue
        falls, tells = int(row["fall_rounds"]), int(row["tell_rounds"])
        assert 0 <= tells <= falls
        if int(row["move_round"]) >= int(row["onset"]):
            assert falls > tells, row
    assert any(int(row["tell_rounds"] or 0) > 0 for row in rows)


def test_hp13_clear_rounds(pilot, monkeypatch):
    two = [("discerning", discerning), ("complacent", complacent)]  # the two clear_round reads, so the cell is quick
    monkeypatch.setattr("paranoid.harness.pilot.sweeps.defaults", lambda: two)
    (path,) = run_cell("game-length", pilot)
    rows = read(path)
    assert {row["baseline"] for row in rows if row["clear_round_1"]} == {"discerning"}
    checked = 0
    for row in rows:
        if row["baseline"] != "discerning" or row["scenario"] != "down_switch" or row["clear_round_1"] == "0":
            continue
        onset = (int(row["onset_low"]), int(row["onset_high"]))
        config = replace(SCENARIOS["down_switch"], rounds=int(row["rounds"]), onset=onset)
        t = make_timeline(config, int(row["seed"]))
        clear, start = int(row["clear_round_1"]), int(row["onset_1"])
        assert start <= clear <= config.rounds
        ahead, behind = play(discerning, t).rows, play(complacent, t).rows
        for r in range(clear, config.rounds + 1):
            assert sum(ahead[k - 1].output - behind[k - 1].output for k in range(start, r + 1)) > 0
        checked += 1
    assert checked


def test_hp14_complacent_rows(pilot):
    (path,) = run_cell("reading-roughness", pilot)
    base = [row for row in read(path) if row["baseline"] == "complacent"]
    assert len(base) == 3 * 3 * SEEDS
    assert len({(row["setting"], row["scenario"], row["seed"]) for row in base}) == len(base)
    assert all(row["parameter"] == row["scout_rounds"] == "" and row["move_round"] == "0" for row in base)


@pytest.mark.parametrize("cell", ["luck", "baseline-order"])
def test_hp16_workers_write_the_same_bytes(cell, tmp_path, monkeypatch):
    monkeypatch.setenv("PARANOID_PILOT_SEEDS", "3")
    (one,) = run_cell(cell, CellArgs(out=tmp_path / "one"))
    (two,) = run_cell(cell, CellArgs(out=tmp_path / "two", workers=2))
    assert one.read_bytes() == two.read_bytes()


def test_hp16_workers_below_one(pilot):
    with pytest.raises(ValueError, match="workers"):
        run_cell("luck", replace(pilot, workers=0))
