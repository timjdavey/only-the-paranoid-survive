"""AS3, AS4, AS8, AS9, AS11 and AS12's gap half: gaps, spread and sampling share. See docs/specs/analysis/tests.md#scores."""

import numpy as np
import pytest
from inspect_ai.log import read_eval_log

from paranoid.analysis import GAP_COLUMNS, load_runs, mean_over_epochs, paired_gap, public_gap, result_key
from paranoid.analysis import sampling_share, scenario_gap, scenario_scores, spread


def key(path):
    return result_key(read_eval_log(str(path)))


def table(*paths):
    return mean_over_epochs(load_runs(list(paths)))


def held_out_copy(**values):
    def change(log):
        for sample in log.samples:
            sample.metadata |= {"seed_set": "held-out"} | values
            sample.metadata.pop("seed", None)
            sample.scores["gain"].metadata = {}

    return change


def test_as3_paired_gap(logs, tmp_path, helpers):
    runs = table(logs.folder)
    complacent, discerning, uniform = key(logs.complacent), key(logs.discerning), key(logs.uniform)
    same = paired_gap(runs, complacent, complacent)
    assert list(same.columns) == list(GAP_COLUMNS) and len(same) == 9
    assert (same[["diff", "lo", "hi"]] == 0).all().all()
    one = paired_gap(runs, discerning, uniform)
    assert (one["diff"] == 1).all() and (one["lo"] == 1).all() and (one["hi"] == 1).all()
    held = helpers.edit(logs.complacent, tmp_path / "held.eval", held_out_copy())
    with pytest.raises(ValueError, match="seed set"):
        paired_gap(table(logs.complacent, held), complacent, key(held))

    def rehash(log):
        for sample in log.samples:
            sample.metadata["harness_version"] = "other"
            if sample.metadata["scenario"] == "down_switch":
                sample.metadata["engine_hash"] = "0" * 12

    rehashed = helpers.edit(logs.complacent, tmp_path / "rehashed.eval", rehash)
    with pytest.raises(ValueError, match="down_switch"):
        paired_gap(table(logs.complacent, rehashed), complacent, key(rehashed))


def test_as4_scenario_gap(logs):
    runs = table(logs.complacent)
    complacent = key(logs.complacent)
    (row,) = scenario_gap(runs, complacent, "no_change", "down_switch").itertuples()
    down = scenario_scores(runs).set_index("scenario").loc["down_switch", "score"]
    assert row.pair == "no_change − down_switch" and row.diff == pytest.approx(1 - down)
    assert row.lo <= row.diff <= row.hi and row.n_shared == 5
    assert list(scenario_gap(runs, complacent, "no_change", "down_switch", seeds=[0, 1]).columns) == list(GAP_COLUMNS)


def test_as8_sampling_share(epochs_log, tmp_path, helpers):
    runs = load_runs([epochs_log])
    shares = sampling_share(runs)
    assert (shares[shares["total_sd"] > 0]["share"] == 0).all() and (shares["total_sd"] > 0).any()
    assert shares[shares["total_sd"] == 0]["share"].isna().all()  # every run scored alike, so there is no share

    def wobble(log):
        for sample in log.samples:
            sample.scores["gain"].value["run_score"] = 0.4 if sample.epoch == 1 else 0.6

    wobbled = load_runs([helpers.edit(epochs_log, tmp_path / "wobbled.eval", wobble)])
    shares = sampling_share(wobbled)
    assert shares["share"].to_numpy() == pytest.approx(1.0) and (shares["seeds"] == 5).all() and (shares["epochs"] == 2).all()


def test_as9_spread(logs):
    runs = table(logs.mockllm)
    rows = spread(runs).set_index("scenario")
    scores = runs[runs["scenario"] == "down_switch"]["run_score"].to_numpy(dtype=float)
    assert rows.loc["down_switch", "sd"] == pytest.approx(np.std(scores, ddof=1))
    assert rows.loc["down_switch", "p10"] == pytest.approx(np.percentile(scores, 10)) and rows.loc["down_switch", "n"] == 5
    one = spread(runs[runs["seed_index"] == 0])
    assert one["sd"].isna().all() and one["p10"].isna().all()


def test_as11_public_gap(logs, tmp_path, helpers):
    held = helpers.edit(logs.complacent, tmp_path / "held.eval", held_out_copy())
    runs = table(logs.complacent, held)
    public, private = key(logs.complacent), key(held)
    gap = public_gap(runs, public)
    assert list(gap.columns) == list(GAP_COLUMNS) and list(gap["pair"])[-1] == "headline" and len(gap) == 9
    assert gap.equals(public_gap(runs, private))
    assert (gap["diff"] == 0).all() and (gap["lo"] <= 0).all() and (gap["hi"] >= 0).all()
    skinned = helpers.edit(logs.complacent, tmp_path / "skinned.eval", held_out_copy(skin="b"))
    with pytest.raises(ValueError, match="skin"):
        public_gap(table(logs.complacent, skinned), public)
    with pytest.raises(ValueError, match="held-out"):
        public_gap(table(logs.complacent), public)
