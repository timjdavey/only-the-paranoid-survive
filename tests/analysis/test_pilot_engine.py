"""AI1, AI2, AI4, AI7, AI8 and AI10 to AI16, and AI23: the page and the engine sections, on hand-built CSVs.

See docs/specs/analysis/tests.md#pilot.
"""

import re
from pathlib import Path

import pandas as pd
import pytest

from paranoid.analysis import SECTIONS, signal_points, write_pilot
from paranoid.harness import scenario_config

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "specs" / "harness" / "pilot.md"
NOT_RUN = "_Not run yet._"


def written_columns() -> dict[str, list[str]]:
    """Each CSV's columns, from the harness pilot spec's Writes lines, as the harness suite reads them."""
    found = re.findall(r"\*\*(?:Also )?[Ww]rites\*\* `([a-z-]+)\.csv`[^`]*`([^`]+)`", SPEC.read_text())
    return {name: [c.strip() for c in columns.split(",")] for name, columns in found}


def csv(folder: Path, name: str, rows: list[dict]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.csv"
    pd.DataFrame(rows, columns=written_columns()[name]).to_csv(path, index=False)
    return path


def section_of(text: str, heading: str) -> str:
    rest = text.split(f"## {heading}\n", 1)[1]
    return rest.split("\n## ", 1)[0]


def table(out: Path, section: str, name: str) -> pd.DataFrame:
    return pd.read_csv(out / "results" / f"{section}-{name}.csv")


def test_ai1_an_empty_folder(tmp_path):
    out = tmp_path / "out"
    assert write_pilot(tmp_path / "logs", out, dry_run=True) == [out / "results.md"] and not out.exists()
    write_pilot(tmp_path / "logs", out)
    text = (out / "results.md").read_text()
    assert re.findall(r"^## (.+)$", text, re.M) == list(SECTIONS)
    assert all(section_of(text, h).strip() == NOT_RUN for h in SECTIONS)
    assert [p.name for p in out.rglob("*")] == ["results.md"]
    page = (ROOT / "docs" / "pilot" / "results.md").read_text()
    assert re.findall(r"^## (.+)$", page, re.M) == list(SECTIONS)


def order_rows(scores: dict[str, dict[str, float]], seeds=(0, 1), kinds=None, moves=None) -> list[dict]:
    """baseline-order rows whose pooled scores are `scores`: uniform 100, discerning 200 on every seed."""
    rows = []
    for scenario, players in scores.items():
        for seed in seeds:
            for name, score in {"uniform": 0.0, "discerning": 1.0, **players}.items():
                move = (moves or {}).get((scenario, name, seed), 0)
                kind = (kinds or {}).get(scenario, "none")
                rows.append({"scenario": scenario, "kind": kind, "baseline": name, "seed": seed, "output": 100 + 100 * score, "move_round": move})
    return rows


def test_ai2_baseline_order(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    down = {"perfect": 1.2, "hedge_rule": 0.8, "complacent": 0.5}
    calm = {"complacent": 1.0, "hedge_rule": 0.5}  # the planted break: the hedge rule far below the other two
    csv(logs, "baseline-order", order_rows({"down_switch": down, "no_change": calm}, kinds={"down_switch": "fall"}))
    paths = write_pilot(logs, out)
    text = (out / "results.md").read_text()
    outputs = table(out, "baseline-order", "outputs")
    assert len(outputs) == 5 + 4  # one row per scenario and baseline
    orders = table(out, "baseline-order", "orders")["order"].tolist()
    assert orders[0] == "Down switch: Perfect > Discerning > hedge rule > Complacent > Uniform, holds"
    assert orders[1].startswith("**No change: ") and orders[1].endswith(", breaks**")
    names = sorted(p.name for p in paths if p.parent.name == "results" and p.name.startswith("baseline-order"))
    assert names == ["baseline-order-orders.csv", "baseline-order-outputs.csv"]
    for heading in SECTIONS:
        if heading not in ("Baseline order", "Reachable gain"):
            assert section_of(text, heading).strip() == NOT_RUN, heading


def test_ai4_a_renamed_heading(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    page = (ROOT / "docs" / "pilot" / "results.md").read_text().replace("## Noise\n", "## Noisy\n")
    (out / "results.md").write_text(page)
    with pytest.raises(ValueError, match="Noisy"):
        write_pilot(tmp_path / "logs", out)
    assert (out / "results.md").read_text() == page


def test_ai7_reachable_gain(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    scores = {s: {"complacent": 0.5, "bayesian": 0.9} for s in ("shock_then_switch", "slow_drift", "switch_then_shock")}
    scores |= {"up_switch": {"complacent": 0.8, "bayesian": 0.95}, "down_switch": {"complacent": 0.5, "bayesian": 0.7}}
    scores |= {"up_switch_then_down_switch": {"complacent": 0.9, "stayer": 0.5, "bayesian": 0.9}}
    moves = {("up_switch_then_down_switch", "bayesian", seed): 12 for seed in (0, 1)}
    csv(logs, "baseline-order", order_rows(scores, seeds=range(5), moves=moves))
    write_pilot(logs, out)
    gains = table(out, "reachable-gain", "gains").set_index("scenario")
    assert len(gains) == 6
    assert gains.loc["up_switch", "reachable_gain"] == pytest.approx(0.2)
    assert gains.loc["down_switch", "bayesian_gain_percentage"] == pytest.approx(40)
    assert gains.loc["up_switch_then_down_switch", "reachable_gain"] == pytest.approx(0.5)
    assert gains.loc["up_switch_then_down_switch", "bayesian_move_share"] == pytest.approx(0.4)
    broken = [line for line in table(out, "reachable-gain", "lines")["line"] if line.startswith("**")]
    assert len(broken) == 3
    assert any("Up switch: reachable gain" in b for b in broken) and any("Down switch: Bayesian gain percentage" in b for b in broken)
    assert any("Up switch then down switch: the Bayesian baseline moves" in b for b in broken)


def test_ai8_weather(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    falls = [(2, 2)] * 8 + [(2, 1), (0, 0)]
    rows = [{"factor_scale": 3.0, "loading_low": 0.3, "scenario": "one_shock", "seed": seed, "onset": 10, "fall_rounds": f,
             "tell_rounds": t, "move_round": 0, "held": 1, "field_together_rounds": 0} for seed, (f, t) in enumerate(falls)]  # fmt: skip
    csv(logs, "tell", rows)
    csv(logs, "luck", [{"setting": 2.0, "seed": 0, "perfect": 130, "discerning": 120, "uniform": 100}])
    write_pilot(logs, out)
    (tell,) = table(out, "weather", "tell").itertuples()
    assert tell.hit_rate == pytest.approx(8 / 9) and tell.never_fired_one_shock == pytest.approx(0.1)
    assert table(out, "weather", "luck")["luck_share"].tolist() == [0.5]


def test_ai10_noise(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    rows = [{"setting": 4.0, "scenario": "down_switch", "baseline": name, "seed": seed, "output": output}
            for seed in (0, 1) for name, output in (("uniform", 100), ("discerning", 200), ("complacent", 150))]  # fmt: skip
    csv(logs, "noise-grid", rows)
    write_pilot(logs, out)
    scores = table(out, "noise", "scores").set_index("baseline")
    assert scores.loc["complacent", "score"] == 0.5
    assert scores.loc["complacent", "snr"] == signal_points(scenario_config("down_switch")) / 4.0


def test_ai11_game_length(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    rows = []
    for seed, clear in enumerate([12, 14, 16, 0]):
        for name in ("uniform", "discerning", "complacent", "hedge_rule", "scout_rule"):
            rows.append({"rounds": 40, "onset_low": 8, "onset_high": 12, "scenario": "down_switch", "seed": seed, "onset_1": 10,
                         "last_end": 14, "baseline": name, "output": 100.0, "output_window_1": 50.0, "move_round": 11,
                         "clear_round_1": clear if name == "discerning" else None})  # fmt: skip
    csv(logs, "game-length", rows)
    write_pilot(logs, out)
    (row,) = table(out, "game-length-and-switch-round", "length").itertuples()
    assert row.window_1_rounds_to_clear == 4 and row.window_1_never_clear == 0.25


def test_ai12_reading_roughness(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    rows = [{"setting": 8.0, "scenario": "no_change", "baseline": "complacent", "seed": s, "output": 500, "move_round": 0} for s in (0, 1)]
    rows += [{"setting": 8.0, "scenario": "no_change", "baseline": "hedge_rule", "parameter": 2, "scout_rounds": 1, "seed": s,
              "output": o, "move_round": 0} for s, o in ((0, 480), (1, 470))]  # fmt: skip
    csv(logs, "reading-roughness", rows)
    write_pilot(logs, out)
    (row,) = table(out, "reading-roughness", "roughness").itertuples()
    assert row.explore_cost == 50


def test_ai13_up_and_down(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    kinds = ["fall", "fall", "fall", "fall_and_rise"]
    rows = [{"setting": 1.0, "scenario": "down_switch", "kind": kind, "baseline": name, "seed": seed, "onset": 10, "output": output,
             "move_round": 0} for seed, kind in enumerate(kinds)
            for name, output in (("uniform", 100), ("discerning", 200), ("complacent", 140))]  # fmt: skip
    csv(logs, "up-and-down", rows)
    write_pilot(logs, out)
    kinds_table = table(out, "up-and-down", "kinds")
    complacent = kinds_table[kinds_table["player"] == "complacent"].set_index("kind")
    assert complacent["seeds"].to_dict() == {"fall": 3, "fall_and_rise": 1}
    assert complacent["reachable_score"].tolist() == pytest.approx([1 - 0.4, 1 - 0.4])


def test_ai14_bayesian_frontier(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    rows = []
    for seed in (0, 1, 500, 501):
        for scenario in ("down_switch", "no_change"):
            players = {"uniform": 100, "discerning": 200, "bayesian a": 190 if seed < 500 else 170, "bayesian b": 150}
            for name, output in players.items():
                baseline, _, hazard = name.partition(" ")
                rows.append({"scenario": scenario, "baseline": baseline, "hazard": hazard or None, "rule": "r" if hazard else None,
                             "seed": seed, "output": output})  # fmt: skip
    csv(logs, "bayesian-frontier", rows)
    write_pilot(logs, out)
    (pick,) = table(out, "bayesian-frontier", "pick").itertuples()
    assert pick.player == "bayesian a r" and pick.irreducible_lag == pytest.approx(1 - 0.7)


def test_ai15_jev_rounding(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    csv(logs, "jev", [{"model": "jev/x", "scenario": "no_change", "seed_index": 0, "round": r, "rounded_out": 2 if r < 3 else 0}
                      for r in range(10)])  # fmt: skip
    write_pilot(logs, out)
    (row,) = table(out, "jev-checks", "rounding").itertuples()
    assert row.mean_rounded_out == pytest.approx(0.6) and row.rounded_share == pytest.approx(0.3)


def test_ai16_timestral(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    csv(logs, "timestral", [{"probe": "gap", "joint": 1, "gap": 1, "channel": 0, "spread": 4.0},
                            {"probe": "determinism", "joint": 1, "equal": 0}])  # fmt: skip
    grid = [{"setting": 4.0, "scenario": "down_switch", "baseline": n, "seed": 0, "output": o}
            for n, o in (("uniform", 100), ("discerning", 200), ("hedge_rule", 170), ("complacent", 150))]  # fmt: skip
    csv(logs, "noise-grid", grid)
    csv(logs, "timestral-grid", [{"setting": 4.0, "scenario": "down_switch", "model": "timestral/odds", "seed": 0, "output": 160}])
    write_pilot(logs, out)
    gap_test = table(out, "timestral-checks", "gap-test")
    assert gap_test[gap_test["probe"] == "determinism"]["equal"].tolist() == [0]
    scores = table(out, "timestral-checks", "grid").set_index("baseline")["score"]
    assert scores.to_dict() | {} == pytest.approx({"uniform": 0.0, "discerning": 1.0, "hedge_rule": 0.7, "complacent": 0.5, "timestral/odds": 0.6})


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
