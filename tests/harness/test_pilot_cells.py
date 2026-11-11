"""HP2, HM8, HP5 to HP10 and HP15: the cell list and the provider cells. See docs/specs/harness/tests.md#pilot.

Provider cells play `mockllm/model`, a fake Jev or a fake forecaster, so nothing calls out. Their evals
play the headline tools, so the `evals` fixture puts them on inspect's local sandbox.
"""

import csv
import re
from dataclasses import replace
from pathlib import Path

import inspect_ai
import pytest
from inspect_ai.log import list_eval_logs, read_eval_log

from paranoid.forecasters import TIMESTRAL_POLICIES
from paranoid.harness import CELLS, CellArgs, main, run_cell
from paranoid.skins import CANARY

SPEC = Path(__file__).parents[2] / "docs" / "specs" / "harness" / "pilot.md"
LLM = ("mockllm/model", "llm", "off")


def read(path: Path) -> list[dict]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def logs_in(folder: Path):
    return [read_eval_log(info.name) for info in list_eval_logs(str(folder))]


@pytest.fixture
def cell_args(tmp_path, monkeypatch, models_file):
    monkeypatch.setenv("PARANOID_PILOT_SEEDS", "5")

    def make(*rows) -> CellArgs:
        return CellArgs(out=tmp_path / "out", models=models_file(tmp_path, *rows))

    return make


def test_hp2_the_cells():
    names = re.findall(r"^#### `([a-z-]+)`", SPEC.read_text(), re.M)
    assert list(CELLS) == names and len(names) == 21
    with pytest.raises(ValueError, match="streaks.*warm-up"):
        run_cell("nope", CellArgs())


def test_hm8_the_pilot_command(tmp_path, capsys, monkeypatch):
    called = []
    monkeypatch.setattr("paranoid.harness.pilot.run_cell", lambda name, args: called.append((name, args)) or [])
    assert main(["pilot", "baseline-order", "--out", str(tmp_path), "--seeds", "5"]) == 0
    assert called == [("baseline-order", CellArgs(out=tmp_path, seeds=5))]
    monkeypatch.undo()
    assert main(["pilot", "nope"]) == 1
    out = capsys.readouterr().out
    assert all(name in out for name in CELLS)


def test_hp5_seeds_then_repeats(cell_args, evals, capsys):
    args = cell_args(LLM)
    with pytest.raises(ValueError, match="seeds"):
        run_cell("repeats", args)
    run_cell("seeds", args)
    (log,) = logs_in(args.out / "seeds")
    ids = [sample.id for sample in log.samples]
    assert sorted(i.split("/")[0] for i in ids) == ["one_shock"] * 20 + ["up_switch"] * 20
    assert log.eval.metadata == {"reasoning": "off", "kind": "llm"}
    run_cell("repeats", args)
    (again,) = logs_in(args.out / "repeats")
    picked = {sample.id for sample in again.samples}
    assert len(picked) == 10 and len({i.split("/")[0] for i in picked}) == 1
    assert sorted(sample.epoch for sample in again.samples) == sorted([1, 2, 3, 4] * 10)
    printed = capsys.readouterr().out
    assert "mockllm/model" in printed and ",".join(sorted((i.split("/")[1] for i in picked), key=int)) in printed


def test_hp6_recognition(cell_args, helpers, monkeypatch):
    replies = [helpers.say("It looks like a benchmark."), helpers.say("A sales desk."), helpers.say(CANARY.split(":", 1)[1])]
    script = helpers.Script(replies)
    monkeypatch.setattr("paranoid.harness.pilot.probes.model_for", lambda row: script.model())
    (path,) = run_cell("recognition", cell_args(LLM))
    rows = read(path)
    assert list(rows[0]) == ["model", "skin", "probe", "reply", "lint_hits", "canary_finished"]
    assert [(r["probe"], r["lint_hits"], r["canary_finished"]) for r in rows] == [
        ("round_1", "1", ""), ("round_20", "0", ""), ("canary", "0", "1"),
    ]  # fmt: skip
    guid = CANARY.split(":", 1)[1]
    assert not any(guid in m.text for call in script.calls for m in call[0])
    other = ("mockllm/other", "llm", "off")
    monkeypatch.setattr("paranoid.harness.pilot.probes.model_for", lambda row: helpers.Script(then=replies[1]).model())
    (path,) = run_cell("recognition", cell_args(LLM, other))
    assert [r["model"] for r in read(path)] == ["mockllm/model"] * 3 + ["mockllm/other"] * 3
    (path,) = run_cell("recognition", replace(cell_args(LLM, other), only="mockllm/other"))
    assert {r["model"] for r in read(path)} == {"mockllm/other"}


def test_hp7_jev(cell_args, monkeypatch, FakeJev, evals):
    answer = [0.004, 0.996] + [0.0] * 8
    monkeypatch.setattr("paranoid.harness.providers.jev.TypesafeClient", lambda model: FakeJev({3: answer}))
    args = cell_args(("jev/fake", "jev", "n/a"))
    paths = run_cell("jev", args)
    assert len(logs_in(args.out / "jev")) == 1 and paths[-1] == args.out / "jev.csv"
    rows = read(args.out / "jev.csv")
    assert len(rows) == 2 * 20 * 40
    assert all(r["rounded_out"] == ("1" if r["round"] == "3" else "0") for r in rows)


def test_hp8_timestral(cell_args, monkeypatch, Fake):
    monkeypatch.setattr("paranoid.harness.pilot.timestral_cell.extra_missing", lambda: False)
    monkeypatch.setattr("paranoid.harness.pilot.timestral_cell.shapes", lambda: [(1, Fake()), (0, Fake())])
    monkeypatch.setattr(
        "paranoid.harness.pilot.timestral_cell.policy_for",
        lambda model: replace(TIMESTRAL_POLICIES[model.split("/")[1]], forecaster=Fake()),
    )
    args = cell_args(("timestral/odds", "timestral", "n/a"))
    paths = run_cell("timestral", args)
    assert sorted(p.name for p in paths) == ["timestral-grid.csv", "timestral-rounding.csv", "timestral.csv"]
    rows = read(args.out / "timestral.csv")
    for joint in ("1", "0"):
        gaps = [r for r in rows if r["probe"] == "gap" and r["joint"] == joint]
        assert len(gaps) == 30 * 10
        for channel in map(str, range(10)):
            spreads = [float(r["spread"]) for r in gaps if r["channel"] == channel]
            assert spreads == sorted(spreads)
        assert [r["equal"] for r in rows if r["probe"] == "determinism" and r["joint"] == joint] == ["1"]
    grid = read(args.out / "timestral-grid.csv")
    assert len(grid) == 5 * 3 * 5 and len(read(args.out / "timestral-rounding.csv")) == len(grid) * 40
    assert not list(args.out.rglob("*.eval"))


def test_hp9_every_cell_dry_runs(tmp_path, capsys, evals):
    out = tmp_path / "out"
    for name in CELLS:
        run_cell(name, CellArgs(out=out, dry_run=True))
        assert capsys.readouterr().out.strip(), name
    assert not out.exists() and evals == []


def test_hp10_channel_order(cell_args, helpers, example, monkeypatch):
    requests: list[str] = []

    def answer(input, tools, tool_choice, config):
        request = input[-1].text
        requests.append(request)
        n = len(requests)
        bets = [0] * 10
        for name, bet in re.findall(r"(\w+) (\d+)", request.split(": ", 1)[1].split(".")[0]):
            bets[example.channels.index(name)] = int(bet)
        if n == 3:  # probe 2 of `one`: the 100 a place late
            bets = [100 if c == 3 else 0 for c in range(10)]
        if n == 14:  # a split summing to 90
            bets = [9] * 10
        if n == 26:  # no call
            return helpers.say("I would rather not.")
        return helpers.reply((example.tool_name, {example.bets_name: bets}))

    monkeypatch.setattr("paranoid.harness.pilot.probes.model_for", lambda row: helpers.Script.model_of(answer))
    (path,) = run_cell("channel-order", cell_args(LLM))
    rows = read(path)
    assert list(rows[0]) == ["model", "skin", "shape", "probe", "called", "valid", "matched", "slipped", "wanted", "sent"]
    assert len(rows) == 30 and sum(r["matched"] == "1" for r in rows) == 27
    assert [r["probe"] for r in rows if r["slipped"] == "1"] == ["2"] and rows[2]["shape"] == "one"
    assert (rows[13]["called"], rows[13]["valid"], rows[25]["called"]) == ("1", "0", "0")
    for row in (rows[13], rows[25]):
        assert row["matched"] == row["slipped"] == row["sent"] == ""
    for i, request in enumerate(requests[20:]):
        named = [example.channels.index(name) for name in re.findall(r"([A-Z]\w+) \d+", request)]
        assert named == [(i + 3 * j) % 10 for j in range(10)]
    assert not any(channel in path.read_text() for channel in example.channels)


def test_hp15_token_files(cell_args, helpers, example, monkeypatch, evals):
    valid = helpers.reply((example.tool_name, {example.bets_name: [10] * 10}))
    script = helpers.Script([helpers.say("Let me think.")], then=valid)
    monkeypatch.setattr("paranoid.harness.pilot.evals.PILOT_SEEDS", "0-2")  # the file's shape needs few seeds
    wrapped = inspect_ai.eval  # the evals fixture's, on the local sandbox
    monkeypatch.setattr(inspect_ai, "eval", lambda *a, **k: wrapped(*a, **(k | {"model": script.model()})))
    args = cell_args(LLM)
    paths = run_cell("seeds", args)
    assert paths[-1] == args.out / "seeds-tokens.csv"
    rows = read(args.out / "seeds-tokens.csv")
    assert list(rows[0]) == [
        "model", "rolling", "scenario", "seed_index", "round", "input_tokens", "cache_read_tokens", "cache_write_tokens",
    ]  # fmt: skip
    (log,) = logs_in(args.out / "seeds")
    assert len(rows) == sum(len(helpers.store_of(sample).tries) for sample in log.samples)
    assert {r["rolling"] for r in rows} == {"0"}
    (twice,) = [s for s in log.samples if helpers.store_of(s).tries[0] == 2]
    events = [e for e in twice.events if type(e).__name__ == "ModelEvent"]
    named = (twice.metadata["scenario"], str(twice.metadata["seed_index"]), "1")
    (first,) = [r for r in rows if (r["scenario"], r["seed_index"], r["round"]) == named]
    assert int(first["input_tokens"]) == events[0].output.usage.input_tokens + events[1].output.usage.input_tokens
    run_cell("rolling", args)
    assert {r["rolling"] for r in read(args.out / "rolling-tokens.csv")} == {"0", "1"}
