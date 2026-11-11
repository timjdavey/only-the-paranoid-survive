"""HM5 to HM7, HM10 to HM16 and HK8's eval half: the paranoid command. See docs/specs/harness/tests.md#command."""

import shutil
import sys

from inspect_ai.log import list_eval_logs, read_eval_log

from paranoid.harness import load_models, main

UNIFORM = ("baseline/uniform", "baseline", "n/a")
LLM = ("mockllm/model", "llm", "off")


def logs_in(folder):
    return [read_eval_log(info.name) for info in list_eval_logs(str(folder))]


def test_hm5_a_dry_run(capsys, evals):
    assert main(["run", "--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    rows = load_models("configs/models/poc.toml")
    assert len(lines) == sum(len(row.reasoning) for row in rows)
    ids = [line.split()[1].rstrip(":") if line.startswith("skipping") else line.split()[0] for line in lines]
    kind = {row.id: row.kind for row in rows}
    kinds = [kind[i] for i in ids]
    assert kinds == sorted(kinds, key=lambda k: k == "llm") and kinds[-1] == "llm" and evals == []


def test_hm6_hm13_hk8_one_eval(tmp_path, models_file, evals):
    path = models_file(tmp_path, UNIFORM)
    assert main(["run", "--models", str(path), "--limit", "2", "--log-dir", str(tmp_path / "logs")]) == 0
    assert len(evals) == 1 and evals[0]["retry_on_error"] == 1 and evals[0]["max_connections"] == 32
    (log,) = logs_in(tmp_path / "logs")
    assert len(log.samples) == 2 and {"engine_hash", "prompt_hash", "release"} <= set(log.samples[0].metadata)
    assert log.eval.metadata["reasoning"] == "n/a" and log.eval.metadata["kind"] == "baseline"


def test_hm7_subcommands(capsys, monkeypatch):
    called = []

    class FakeEntryPoint:
        name = "fake"

        def load(self):
            return lambda argv: called.append(argv) or 0

    monkeypatch.setattr("paranoid.harness.cli.entry_points", lambda group: [FakeEntryPoint()])
    assert main(["nope"]) == 1
    assert "run, pilot, fake" in capsys.readouterr().out
    assert main(["fake", "x", "--y"]) == 0 and called == [["x", "--y"]]


def test_hm10_only(tmp_path, capsys, models_file):
    path = models_file(tmp_path, LLM, UNIFORM)
    assert main(["run", "--models", str(path), "--only", "baseline/uniform", "--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and lines[0].startswith("baseline/uniform ")


def test_hm11_a_missing_extra_skips_the_row(tmp_path, capsys, monkeypatch, models_file, evals):
    for name in ("torch", "timestral"):
        monkeypatch.setitem(sys.modules, name, None)
    path = models_file(tmp_path, ("timestral/top-pick", "timestral", "n/a"), UNIFORM)
    assert main(["run", "--models", str(path), "--limit", "1", "--log-dir", str(tmp_path / "logs")]) == 0
    out = capsys.readouterr().out
    assert out.count("timestral/top-pick") == 1 and "uv sync --extra timestral" in out
    assert [call["model"] for call in evals] == ["baseline/uniform"]


def test_hm12_a_failed_eval_carries_on(tmp_path, models_file, evals):
    path = models_file(tmp_path, ("nosuch/model", "llm", "off"), UNIFORM)
    assert main(["run", "--models", str(path), "--limit", "1", "--log-dir", str(tmp_path / "logs")]) == 1
    assert [call["model"] for call in evals] == ["baseline/uniform", "nosuch/model"]
    assert len(logs_in(tmp_path / "logs")) >= 1


def test_hm14_skins(tmp_path, capsys, monkeypatch, models_file, evals):
    skins = tmp_path / "skins"
    skins.mkdir()
    for name in ("a", "b"):
        shutil.copy("src/paranoid/skins/example.toml", skins / f"{name}.toml")
    monkeypatch.setenv("PARANOID_SKINS", str(skins))
    path = models_file(tmp_path, UNIFORM, LLM)
    assert main(["run", "--models", str(path), "--skins", "a,b", "--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [(line.split()[0], line.split()[2]) for line in lines] == [
        ("baseline/uniform", "skin=a"), ("mockllm/model", "skin=a"), ("mockllm/model", "skin=b"),
    ]  # fmt: skip
    one = models_file(tmp_path, UNIFORM)
    assert main(["run", "--models", str(one), "--skins", "a,b", "--limit", "1", "--log-dir", str(tmp_path / "logs")]) == 0
    (log,) = logs_in(tmp_path / "logs")
    assert {sample.metadata["skin"] for sample in log.samples} == {"a"}


def test_hm15_unknown_skins(capsys, evals):
    for skins in ("nope", "example,example"):
        assert main(["run", "--skins", skins]) == 1
        out = capsys.readouterr().out
        assert "example" in out and "PARANOID_SKINS" in out
    assert evals == []


def test_hm16_own_scale(tmp_path, capsys, models_file, configs, evals):
    folder = configs(grid='release = "dev"\nown_scale = [3.0, 6.0]\n')
    path = models_file(folder, UNIFORM)
    assert main(["run", "--models", str(path), "--own-scale", "grid", "--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert ["own_scale=3.0" in lines[0], "own_scale=6.0" in lines[1], len(lines)] == [True, True, 2]
    assert main(["run", "--models", str(path), "--own-scale", "6", "--dry-run"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 1
    for bad in ("0", "lots", "-1", "nan"):
        assert main(["run", "--models", str(path), "--own-scale", bad]) == 1
    assert evals == []
