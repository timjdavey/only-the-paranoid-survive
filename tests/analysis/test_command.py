"""AM1 to AM8: the command and the exports. See docs/specs/analysis/tests.md#command."""

import re
import socket
from pathlib import Path

import pandas as pd
import pytest

import paranoid.analysis as analysis
from paranoid.analysis import analyse
from paranoid.harness import main

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def offline(monkeypatch):
    """No network and no key, for every subcommand, see AM5."""

    def blocked(*args, **kwargs):
        raise OSError("the network is blocked in the analysis tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)  # outbound only, as asyncio's own socket pair needs no connect
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "TYPESAFE_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def files_under(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*") if p.is_file()) if folder.exists() else []


def test_am1_dry_run_through_main(logs, tmp_path, capsys, offline, monkeypatch):
    before = files_under(ROOT / "docs")
    assert main(["analyse", "--dry-run", str(logs.folder), "--out", str(tmp_path / "out")]) == 0
    printed = capsys.readouterr().out
    assert "Read 4 logs" in printed and "Would write:" in printed and str(tmp_path / "out" / "poc.md") in printed
    assert not (tmp_path / "out").exists() and files_under(ROOT / "docs") == before


def test_am2_results_is_the_default(logs, tmp_path, offline):
    out = tmp_path / "out"
    assert analyse([str(logs.folder), "--out", str(out), "--name", "t"]) == 0
    assert [p.name for p in files_under(out)] == ["t.csv", "t.md"]


def test_am3_gap(logs, tmp_path, capsys, offline, helpers):
    assert analyse(["gap", str(logs.discerning), str(logs.uniform)]) == 0
    printed = capsys.readouterr().out
    rows = [line.split() for line in printed.splitlines() if line.split()[:1] and line.split()[0] in ("no_change", "one_shock", "headline")]
    assert rows and all(float(row[1]) == 1 for row in rows)
    both = tmp_path / "both"
    helpers.edit(logs.uniform, both / "a.eval")
    helpers.edit(logs.complacent, both / "b.eval")
    assert analyse(["gap", str(both), str(logs.uniform)]) == 1
    assert str(both) in capsys.readouterr().out
    copy = helpers.edit(logs.uniform, tmp_path / "copy.eval")
    assert analyse(["gap", str(copy), str(logs.uniform)]) == 1
    assert "baseline/uniform" in capsys.readouterr().out


def test_am4_cost(logs, tmp_path, capsys, offline, monkeypatch):
    assert not (ROOT / "configs" / "prices.toml").exists()
    assert analyse(["cost", str(logs.folder)]) == 0
    printed = capsys.readouterr().out
    assert "cached_share" in printed and " cost" not in printed.split("cached_share")[1].splitlines()[0]
    assert "No prices at configs/prices.toml" in printed
    assert analyse(["cost", str(logs.folder), "--prices", "/nope"]) == 1
    assert analyse(["results", "/nope"]) == 1
    assert "/nope" in capsys.readouterr().out


def test_am5_every_subcommand_offline(logs, tmp_path, offline):
    out = str(tmp_path / "out")
    assert analyse(["results", str(logs.folder), "--out", out, "--name", "t"]) == 0
    assert analyse(["pilot", "--logs", str(tmp_path / "none"), "--out", out]) == 0
    assert analyse(["cost", str(logs.folder)]) == 0
    assert analyse(["gap", str(logs.discerning), str(logs.uniform)]) == 0


def test_am6_bad_names_and_the_eci_date(logs, tmp_path, offline, models_file):
    out = tmp_path / "out"
    assert analyse([str(logs.folder), "--out", str(out), "--name", "../x"]) == 1
    eci = models_file(tmp_path, {"id": "mockllm/model", "kind": "llm", "reasoning": "off", "eci": 120.5})
    assert analyse([str(logs.folder), "--out", str(out), "--plots", "--models", str(eci)]) == 1
    assert not out.exists() and not (tmp_path / "x.md").exists()


def test_am7_pilot(tmp_path, capsys, offline):
    logs, out = tmp_path / "logs", tmp_path / "out"
    logs.mkdir()
    rows = [{"scenario": "down_switch", "kind": "fall", "baseline": b, "seed": s, "output": o, "move_round": 0}
            for s in (0, 1) for b, o in (("uniform", 100), ("discerning", 200), ("complacent", 150))]  # fmt: skip
    pd.DataFrame(rows).to_csv(logs / "baseline-order.csv", index=False)
    assert analyse(["pilot", "--logs", str(logs), "--out", str(out), "--dry-run"]) == 0
    would = capsys.readouterr().out
    assert not out.exists()
    assert analyse(["pilot", "--logs", str(logs), "--out", str(out)]) == 0
    wrote = capsys.readouterr().out
    assert would.replace("Would write:", "Wrote:") == wrote
    names = [p.name for p in files_under(out)]
    assert "results.md" in names and "baseline-order-outputs.csv" in names and "reachable-gain-gains.csv" in names


def test_am8_the_exports_are_the_spec_table():
    page = (ROOT / "docs" / "specs" / "analysis" / "README.md").read_text()
    table = page.split("## Exports")[1].split("## ")[0]
    names = {name for row in re.findall(r"^\| ([^|]+) \|", table, re.M) for name in re.findall(r"`(\w+)`", row)}
    assert set(analysis.__all__) == names and len(analysis.__all__) == len(names)
