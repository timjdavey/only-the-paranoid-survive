"""AI3, AI5, AI6, AI9, AI17 to AI22 and AI25: the provider sections, on edited logs under `<logs>/<cell>/`.

See docs/specs/analysis/tests.md#pilot.
"""

from pathlib import Path

import pandas as pd
import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import load_runs, paired_gap, result_key, write_cost, write_pilot

COLUMNS = {
    "recognition": ["model", "skin", "probe", "reply", "lint_hits", "canary_finished"],
    "channel-order": ["model", "skin", "shape", "probe", "called", "valid", "matched", "slipped", "wanted", "sent"],
    "rolling-tokens": [
        "model",
        "rolling",
        "scenario",
        "seed_index",
        "round",
        "input_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
    ],
}


def table(out: Path, section: str, name: str) -> pd.DataFrame:
    return pd.read_csv(out / "results" / f"{section}-{name}.csv")


def keep(*scenarios, seeds=range(5)):
    def change(log):
        log.samples = [s for s in log.samples if s.metadata["scenario"] in scenarios and s.metadata["seed_index"] in seeds]

    return change


def test_ai3_recognition(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    logs.mkdir()
    rows = [
        ("m", "example", probe, "A PLANTED REPLY", hits, finished)
        for probe, hits, finished in (("round_1", 1, None), ("round_20", 0, None), ("canary", 0, 1))
    ]
    pd.DataFrame(rows, columns=COLUMNS["recognition"]).to_csv(logs / "recognition.csv", index=False)
    write_pilot(logs, out)
    (row,) = table(out, "recognition", "hits").itertuples()
    assert (row.probes, row.hits, row.hit_share, row.canary_finished) == (2, 1, 0.5, 1)
    assert not any("PLANTED" in p.read_text() for p in out.rglob("*") if p.is_file())


def test_ai5_up_against_down(logs, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    sleepers = {0: 9, 1: 13, 2: 0, 3: 0}

    def played(log):
        keep("up_switch", "down_switch")(log)
        log.samples = [s for s in log.samples if s.metadata["scenario"] == "down_switch" or s.metadata["seed_index"] in sleepers]
        for sample in log.samples:
            if sample.metadata["scenario"] == "up_switch":
                sample.scores["gain"].value["sleeper_round"] = sleepers[sample.metadata["seed_index"]]

    helpers.edit(logs.complacent, folder / "up-against-down" / "a.eval", played)
    helpers.edit(logs.complacent, folder / "seeds" / "a.eval", keep("one_shock", "up_switch"))
    write_pilot(folder, out)
    sleeper = table(out, "up-against-down", "sleeper").set_index("scenario")
    assert sleeper.loc["up_switch", "reached_share"] == 0.5 and sleeper.loc["up_switch", "median_round"] == 11
    assert "one_shock − down_switch" in table(out, "up-against-down", "gaps")["pair"].tolist()
    assert "_Inertia needs --main._" in (out / "results.md").read_text()


def test_ai6_channel_order(tmp_path):
    logs, out = tmp_path / "logs", tmp_path / "out"
    logs.mkdir()
    rows = []
    for probe in range(12):
        valid = probe < 10
        slipped = probe in (0, 1)
        matched = valid and not slipped and probe != 2
        sent = "0 100 0 0 0 0 0 0 0 0" if slipped else "100 0 0 0 0 0 0 0 0 0"
        rows.append(
            (
                "m",
                "example",
                "one",
                probe,
                1,
                int(valid),
                int(matched) if valid else None,
                int(slipped) if valid else None,
                "100 0 0 0 0 0 0 0 0 0",
                sent if valid else None,
            )
        )
    pd.DataFrame(rows, columns=COLUMNS["channel-order"]).to_csv(logs / "channel-order.csv", index=False)
    write_pilot(logs, out)
    shares = table(out, "channel-order", "shares")
    pooled = shares[shares["shape"] == "all"].iloc[0]
    assert pooled["valid_share"] == pytest.approx(10 / 12) and pooled["slip_share"] == pytest.approx(0.2)
    assert pooled["own_numbers_share"] == pytest.approx(0.1)
    assert table(out, "channel-order", "slips").to_dict("records") == [{"model": "m", "place": 0, "slips": 2}]


def test_ai9_seeds_and_repeats(logs, epochs_log, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    spread = {0: 0.5 - 0.2 * 2**0.5, 1: 0.5 + 0.2 * 2**0.5, 2: 0.5, 3: 0.5, 4: 0.5}  # an SD of 0.2 on Down switch

    def widen(log):
        for sample in log.samples:
            if sample.metadata["scenario"] == "down_switch":
                sample.scores["gain"].value["run_score"] = spread[sample.metadata["seed_index"]]

    helpers.edit(logs.complacent, folder / "seeds" / "a.eval", widen)
    helpers.edit(epochs_log, folder / "repeats" / "a.eval")
    write_pilot(folder, out)
    needed = table(out, "seeds-and-repeats", "seeds-needed").set_index("target")
    assert needed.loc[0.05, "scenario"] == "down_switch" and needed.loc[0.05, "seeds_needed"] == 24
    assert len(table(out, "seeds-and-repeats", "sampling-share"))


def knob_logs(source, folder, helpers, cell, field, values):
    paths = {}
    for value in values:
        name = str(value).replace(",", "-")
        paths[value] = helpers.edit(
            source, folder / cell / f"{name}.eval", lambda log, v=value: helpers.set_metadata(log, **{field: v})
        )
    return paths


def test_ai17_bare_harness(logs, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    paths = knob_logs(logs.mockllm, folder, helpers, "bare", "tools", ["notes,compute", "notes", "compute", "none"])
    write_pilot(folder, out)
    gaps = table(out, "bare-harness", "gaps").set_index("tools")
    assert len(gaps) == 3
    runs = load_runs([folder / "bare"])
    base = result_key(read_eval_log(str(paths["notes,compute"])))
    for tools in ("notes", "compute", "none"):
        gap = paired_gap(runs, result_key(read_eval_log(str(paths[tools]))), base).set_index("pair").loc["headline"]
        assert gaps.loc[tools, "diff"] == pytest.approx(gap["diff"]) and gaps.loc[tools, "lo"] == pytest.approx(gap["lo"])


def test_ai18_tool_choice(logs, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    knob_logs(logs.mockllm, folder, helpers, "tool-choice", "tool_choice", ["any"])
    helpers.edit(
        logs.mockllm,
        folder / "tool-choice" / "auto.eval",
        lambda log: (helpers.set_metadata(log, tool_choice="auto"), helpers.set_score(log, no_calls=4, rounds=40)),
    )
    write_pilot(folder, out)
    scores = table(out, "tool-choice", "scores")
    assert (scores[scores["tool_choice"] == "auto"]["no_call_share"] == 0.1).all()
    (gap,) = table(out, "tool-choice", "gaps").itertuples()
    assert gap.tool_choice == "auto" and gap.against == "any"


def test_ai19_rolling(logs, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    knob_logs(logs.mockllm, folder, helpers, "rolling", "rolling", [False, True])
    rows = [
        ("mockllm/model", rolling, "no_change", 0, r, 100 * r if rolling else 100, 0, 0)
        for rolling in (0, 1)
        for r in range(1, 5)
    ]
    pd.DataFrame(rows, columns=COLUMNS["rolling-tokens"]).to_csv(folder / "rolling-tokens.csv", index=False)
    write_pilot(folder, out)
    tokens = table(out, "rolling-conversation", "tokens").set_index("rolling")
    assert tokens.loc[0, "input_per_round"] == 100 and tokens.loc[1, "input_per_round"] == 250
    (gap,) = table(out, "rolling-conversation", "gaps").itertuples()
    assert gap.clears_zero in (True, False)


def test_ai20_warm_up(logs, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    kept = {0: 1, 1: 1, 2: 0, 3: 0, 4: None}
    helpers.edit(logs.mockllm, folder / "warm-up" / "cold.eval")

    def warm(log):
        for sample in log.samples:
            sample.metadata["warm_up"] = "complacent:5"
            sample.scores["gain"].value["warm_up_kept"] = kept[sample.metadata["seed_index"]]

    helpers.edit(logs.mockllm, folder / "warm-up" / "warm.eval", warm)
    write_pilot(folder, out)
    scores = table(out, "warm-up", "scores")
    assert (scores[scores["warm_up"] == "complacent:5"]["warm_up_kept"] == 0.5).all()
    assert scores[scores["warm_up"].isna()]["warm_up_kept"].isna().all()
    assert len(table(out, "warm-up", "gaps")) == 1


def test_ai21_cost_per_run(logs, epochs_log, tmp_path, helpers):
    folder, out = tmp_path / "logs", tmp_path / "out"
    helpers.edit(logs.mockllm, folder / "seeds" / "a.eval")
    helpers.edit(epochs_log, folder / "repeats" / "a.eval")
    write_pilot(folder, out)
    cost = table(out, "cost-per-run", "cost")
    assert cost["cell"].tolist() == ["seeds", "repeats"] and "retry_share" in cost
    for cell in ("seeds", "repeats"):
        expected = write_cost(load_runs([folder / cell]))
        assert cost[cost["cell"] == cell]["runs"].tolist() == expected["runs"].tolist()


def test_ai22_odd_columns_and_inertia(logs, tmp_path, helpers):
    odd = tmp_path / "odd"
    odd.mkdir()
    pd.DataFrame(columns=["setting", "seed", "perfect", "discerning", "uniform", "extra"]).to_csv(odd / "luck.csv", index=False)
    with pytest.raises(ValueError, match="luck.csv.*extra"):
        write_pilot(odd, tmp_path / "odd-out")
    folder, out = tmp_path / "logs", tmp_path / "out"
    helpers.edit(logs.complacent, folder / "up-against-down" / "a.eval", keep("up_switch", "down_switch"))
    main = tmp_path / "main"
    helpers.edit(logs.complacent, main / "a.eval")
    helpers.edit(logs.mockllm, main / "b.eval")
    write_pilot(folder, out, main=main)
    (row,) = table(out, "up-against-down", "inertia").itertuples()
    assert {row.a, row.b} == {"baseline/complacent", "mockllm/model (off)"}


def test_ai25_up_against_down_keeps_models_apart(logs, tmp_path, helpers):
    both = tmp_path / "both"
    for name in ("complacent", "discerning"):
        helpers.edit(getattr(logs, name), both / "up-against-down" / f"{name}.eval", keep("up_switch", "down_switch"))
        helpers.edit(getattr(logs, name), tmp_path / name / "up-against-down" / "a.eval", keep("up_switch", "down_switch"))
    write_pilot(both, tmp_path / "out")
    for name in ("complacent", "discerning"):
        write_pilot(tmp_path / name, tmp_path / f"{name}-out")
        for kind in ("kinds", "sleeper"):
            together = table(tmp_path / "out", "up-against-down", kind)
            mine = together[together["model"] == f"baseline/{name}"].reset_index(drop=True)
            alone = table(tmp_path / f"{name}-out", "up-against-down", kind)
            assert len(mine) and (alone["model"] == f"baseline/{name}").all(), kind
            pd.testing.assert_frame_equal(mine, alone, check_dtype=False)
