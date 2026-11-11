"""AS1, AS2, AS10, AS12 and AS13: scenario scores, headlines and flags. See docs/specs/analysis/tests.md#scores."""

import pandas as pd
import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import headlines, load_recognition, load_runs, mean_over_epochs, scenario_scores
from paranoid.engine import SCENARIOS

TOLERANCE = 1e-9


def table(*paths):
    return mean_over_epochs(load_runs(list(paths)))


def metrics(path) -> dict[tuple[str, str], float]:
    log = read_eval_log(str(path), header_only=True)
    return {(m.group, m.name): m.value for score in log.results.scores for m in score.metrics.values()}


def test_as1_scores_equal_the_log(logs):
    runs = table(logs.mockllm)
    logged = metrics(logs.mockllm)
    for row in scenario_scores(runs).itertuples():
        for column, suffix in (("score", ""), ("lo", "_lo"), ("hi", "_hi"), ("n", "_n"), ("failed", "_failed")):
            assert getattr(row, column) == pytest.approx(logged[("scenario_score", f"{row.scenario}{suffix}")], abs=TOLERANCE)
    (head,) = headlines(runs).itertuples()
    for column in ("headline", "lo", "hi"):
        assert getattr(head, column) == pytest.approx(logged[("headline", column)], abs=TOLERANCE)
    assert logged[("weakest_trait", head.weakest_trait)] == pytest.approx(head.weakest_score, abs=TOLERANCE)


def test_as2_the_floor_the_yardstick_and_a_mark(logs):
    scores = scenario_scores(table(logs.folder)).set_index(["model", "scenario"])
    for scenario in SCENARIOS:
        assert scores.loc[("baseline/uniform", scenario), "score"] == 0
        assert scores.loc[("baseline/discerning", scenario), "score"] == 1
        complacent = scores.loc[("baseline/complacent", scenario)]
        assert complacent["complacent"] == pytest.approx(complacent["score"], abs=TOLERANCE)


def recognition(tmp_path, rows) -> pd.DataFrame:
    path = tmp_path / "recognition.csv"
    frame = pd.DataFrame(rows, columns=["model", "skin", "probe", "reply", "lint_hits", "canary_finished"])
    frame.to_csv(path, index=False)
    return load_recognition(path)


def probes(model, hits, canary=None):
    rows = [(model, "example", probe, "a reply", hits.pop(0) if hits else 0, None) for probe in ("round_1", "round_20") * 3]
    return rows + [(model, "example", "canary", "a reply", 0, canary) for _ in range(3)]


def test_as10_flags(logs, tmp_path, helpers):
    first = read_eval_log(str(logs.mockllm)).samples[0]
    gave_up = helpers.edit(
        logs.mockllm,
        tmp_path / "a" / "gave-up.eval",
        lambda log: helpers.set_score(log, lambda s: s.id == first.id, gave_up=1, gain=0.0, run_score=0.0),
    )
    scores = scenario_scores(table(gave_up))
    assert "†" in scores.set_index("scenario").loc[first.metadata["scenario"], "flags"]
    assert set(scores["flags"]) == {"", "†"} and headlines(table(gave_up))["flags"].iloc[0] == "†"
    retried = helpers.edit(logs.mockllm, tmp_path / "b" / "retried.eval", lambda log: helpers.set_score(log, retry_rounds=4))
    assert (scenario_scores(table(retried))["flags"] == "‡").all()
    runs = table(logs.mockllm)
    recognised = recognition(tmp_path, probes("mockllm/model", [1, 1]))
    assert (scenario_scores(runs, recognition=recognised)["flags"] == "§").all()
    assert headlines(runs, recognition=recognised)["flags"].iloc[0] == "§"
    finished = recognition(tmp_path, probes("mockllm/model", [], canary=1))
    assert (scenario_scores(runs, recognition=finished)["flags"] == "¶").all()
    other = recognition(tmp_path, probes("someone/else", [1, 1, 1, 1, 1, 1], canary=1))
    assert (scenario_scores(runs, recognition=other)["flags"] == "").all()


def test_as12_recognition_keeps_no_reply(tmp_path):
    rows = [("m", "example", "round_1", "THE PLANTED REPLY", 1, None)]
    loaded = recognition(tmp_path, rows)
    assert list(loaded.columns) == ["model", "skin", "probe", "lint_hits", "canary_finished"]
    assert "THE PLANTED REPLY" not in loaded.to_csv()


def test_as13_tool_shares(logs):
    runs = table(logs.mockllm)
    two = runs[(runs["scenario"] == "no_change") & (runs["seed_index"] < 2)].copy()
    two["rounds"] = pd.array([40, 40], dtype="Int64")
    two["notes_rounds"] = pd.array([4, 0], dtype="Int64")
    two["compute_rounds"] = pd.array([0, 0], dtype="Int64")
    (row,) = scenario_scores(two).itertuples()
    assert row.notes_share == 0.05 and row.compute_share == 0
