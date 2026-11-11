"""HP17 to HP19: how a cell writes its CSV and which seeds logs repeats reads. See docs/specs/harness/tests.md#pilot."""

import importlib
from types import SimpleNamespace

import pytest

from paranoid.harness import CellArgs
from paranoid.harness.pilot.common import write_csv
from paranoid.harness.pilot.repeats import widest

COLUMNS = ("model", "seed", "output")
OLD = "model,seed,output\na,0,1.5\nb,0,2.5\na,1,3.5\n"


def test_hp17_only_keeps_the_other_models_rows(tmp_path):
    path = tmp_path / "cell.csv"
    path.write_text(OLD)
    write_csv(CellArgs(out=tmp_path, only="b"), "cell", COLUMNS, lambda: [("b", 0, 9.5), ("b", 1, None)])
    assert path.read_text() == "model,seed,output\na,0,1.5\na,1,3.5\nb,0,9.5\nb,1,\n"
    write_csv(CellArgs(out=tmp_path), "cell", COLUMNS, lambda: [("b", 0, 9.5)])
    assert path.read_text() == "model,seed,output\nb,0,9.5\n"
    path.write_text("model,seed\na,0\n")
    with pytest.raises(ValueError, match="columns"):
        write_csv(CellArgs(out=tmp_path, only="b"), "cell", COLUMNS, lambda: [("b", 0, 9.5)])


def test_hp18_a_cell_that_raises_leaves_the_old_file(tmp_path):
    path = tmp_path / "cell.csv"
    path.write_text(OLD)

    def rows():
        yield ("a", 0, 1.0)
        raise RuntimeError("part way")

    with pytest.raises(RuntimeError, match="part way"):
        write_csv(CellArgs(out=tmp_path), "cell", COLUMNS, rows)
    assert path.read_text() == OLD and [p.name for p in tmp_path.iterdir()] == ["cell.csv"]


def fake_log(model: str, created: str, status: str, scenarios: dict[str, list[float]], first: int = 0):
    samples = [
        SimpleNamespace(
            scores={"gain": SimpleNamespace(value={"run_score": score})},
            metadata={"scenario": scenario, "seed_index": first + n},
        )
        for scenario, scores in scenarios.items()
        for n, score in enumerate(scores)
    ]
    header = SimpleNamespace(model=model, created=created, metadata={"reasoning": "off"})
    return SimpleNamespace(status=status, eval=header, samples=samples)


def test_hp19_widest_reads_only_whole_and_newest_logs(tmp_path, monkeypatch, models_file):
    narrow = [0.5 + 0.01 * n for n in range(20)]
    wide = [float(n) for n in range(20)]
    logs = {
        "1-old": fake_log("mockllm/model", "2026-11-01T00:00:00", "success", {"one_shock": wide}),
        "2-new": fake_log("mockllm/model", "2026-11-02T00:00:00", "success", {"one_shock": narrow, "up_switch": [0.0, 9.0] * 2 + [5.0]}, 100),
        "3-error": fake_log("mockllm/other", "2026-11-03T00:00:00", "error", {"up_switch": wide}),
    }
    (tmp_path / "out" / "seeds").mkdir(parents=True)
    module = importlib.import_module("paranoid.harness.pilot.repeats")  # the package's own `repeats` is the cell
    monkeypatch.setattr(module, "list_eval_logs", lambda folder: [SimpleNamespace(name=n) for n in logs])
    monkeypatch.setattr(module, "read_eval_log", lambda name, header_only=False: logs[name])
    models = models_file(tmp_path, ("mockllm/model", "llm", "off"), ("mockllm/other", "llm", "off"))
    row, scenario, picks = widest(CellArgs(out=tmp_path / "out", models=models))
    assert row.id == "mockllm/model" and scenario == "one_shock"
    assert len(picks) == 10 and all(100 <= p < 120 for p in picks)
