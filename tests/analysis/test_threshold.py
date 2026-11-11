"""AS5 to AS7, AS14 and AY2: switch kinds and the noise threshold. See docs/specs/analysis/tests.md#scores."""

import math
from dataclasses import replace

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from inspect_ai.log import read_eval_log

from paranoid.analysis import load_runs, mean_over_epochs, noise_threshold, result_key, signal_points, switch_kinds
from paranoid.engine import SCENARIOS, make_timeline
from paranoid.harness import load_seeds, scenario_config

SCALES = (1.0, 2.0, 4.0, 8.0, 16.0)  # signal to noise 8 down to 0.5, as signal_points is 8


def h(snr: float, complacent: float = 0.55, k: float = 2.0, x0: float = math.log(2)) -> float:
    return complacent + (1 - complacent) / (1 + math.exp(-k * (math.log(snr) - x0)))


def expected_kind(scenario: str, seed: int) -> str:
    timeline = make_timeline(SCENARIOS[scenario], seed)
    switch = next((e for e in timeline.events if e.shape == "switch"), None)
    if switch is None:
        return "none"
    return "rise_short" if switch.numbers.get("short") == 1 else switch.numbers["kind"]


def test_as5_switch_kinds(logs, held_out, tmp_path, helpers, monkeypatch):
    capped = helpers.run(
        "baseline/complacent",
        tmp_path / "capped",
        metadata={"reasoning": "n/a", "kind": "baseline"},
        scenario="down_switch",
        seeds="0-1",
        inertia=10,
    )
    assert len(switch_kinds(mean_over_epochs(load_runs([capped])))) == 2
    kinds = switch_kinds(mean_over_epochs(load_runs([logs.complacent])))
    assert "kind" not in kinds and len(kinds) == 40
    public = load_seeds("public")
    for row in kinds.itertuples():
        assert row.switch_kind == expected_kind(row.scenario, public[row.seed_index])
    assert set(kinds[kinds["scenario"] == "no_change"]["switch_kind"]) == {"none"}
    held_runs = mean_over_epochs(load_runs([held_out]))
    before = sorted(tmp_path.rglob("*"))
    held = switch_kinds(held_runs)
    assert len(held) == 9 and held["switch_kind"].notna().all() and sorted(tmp_path.rglob("*")) == before


def curve_logs(source, folder, helpers, headlines, complacent=0.55, sway=0.0, scales=SCALES):
    for scale, headline in zip(scales, headlines):
        helpers.edit(source, folder / f"{scale}.eval", helpers.on_curve(headline, complacent, scale, sway))
    runs = mean_over_epochs(load_runs([folder]))
    return runs, result_key(read_eval_log(str(folder / f"{scales[0]}.eval")))


def test_as6_the_noise_threshold(logs, tmp_path, helpers):
    runs, key = curve_logs(logs.complacent, tmp_path / "curve", helpers, [h(8 / s) for s in SCALES])
    found = noise_threshold(runs, key)
    assert found.status == "crossed" and found.settings == 5 and found.key == key
    assert found.snr == pytest.approx(2, rel=0.02) and found.k == pytest.approx(2, rel=0.1)
    assert found.snr_80 == pytest.approx(2 * math.exp(math.log(4) / 2), rel=0.05)
    assert found.complacent == pytest.approx(0.55) and found.complacent_drift == pytest.approx(0, abs=1e-12)
    for headlines, status in (([0.9] * 5, "off the noisy end"), ([0.6] * 5, "off the quiet end")):
        runs, key = curve_logs(logs.complacent, tmp_path / status, helpers, headlines)
        found = noise_threshold(runs, key)
        assert found.status == status and found.snr is None and found.k is None
    runs, key = curve_logs(logs.complacent, tmp_path / "two", helpers, [0.9, 0.6], scales=SCALES[:2])
    with pytest.raises(ValueError, match="2 noise settings"):
        noise_threshold(runs, key)
    runs, key = curve_logs(logs.complacent, tmp_path / "twice", helpers, [0.9, 0.8, 0.6], scales=SCALES[:3])
    helpers.edit(
        tmp_path / "twice" / "1.0.eval",
        tmp_path / "twice" / "again.eval",
        lambda log: helpers.set_metadata(log, harness_version="other"),
    )
    with pytest.raises(ValueError, match="own_scale"):
        noise_threshold(mean_over_epochs(load_runs([tmp_path / "twice"])), key)


def test_as7_signal_points():
    spec = next(e for e in scenario_config("down_switch").events if type(e).__name__ == "SwitchSpec")
    assert signal_points(scenario_config("down_switch")) == sum(spec.size_points) / 2
    with pytest.raises(ValueError):
        signal_points(scenario_config("no_change"))


def test_as14_draws_off_the_grid(logs, tmp_path, helpers):
    scales = SCALES[1:]
    near = [0.80, 0.78, 0.77, 0.70]  # the half way mark is 0.775
    runs, key = curve_logs(logs.complacent, tmp_path / "near", helpers, near, sway=0.3, scales=scales)
    found = noise_threshold(runs, key)
    assert found.status == "crossed" and found.uncrossed_draws > 0
    assert found.lo <= found.snr <= found.hi


@pytest.fixture(scope="module")
def base(logs) -> pd.DataFrame:
    return mean_over_epochs(load_runs([logs.complacent]))


def curve_table(base: pd.DataFrame, complacent: float, k: float, x0: float) -> pd.DataFrame:
    """The run table on_curve's logs would load to, built in memory for speed."""
    tables = []
    sway = base["seed_index"].map(lambda i: (1, -1, 1, -1, 0)[i % 5]) * 0.02 * base["gap"].mean()
    for scale in SCALES:
        table = base.copy()
        headline = h(8 / scale, complacent, k, x0)
        table["own_scale"] = scale
        table["gain"] = headline * table["gap"] + sway
        table["complacent"] = table["uniform"] + complacent * table["gap"]
        tables.append(table)
    return pd.concat(tables, ignore_index=True)


@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    complacent=st.floats(0.4, 0.7),
    k=st.floats(0.5, 4.0),
    snr=st.floats(0.75, 6.0),
)
def test_ay2_a_curve_always_crosses(logs, base, complacent, k, snr):
    runs = curve_table(base, complacent, k, math.log(snr))
    plain = result_key(read_eval_log(str(logs.complacent), header_only=False))
    key = replace(plain, setting=replace(plain.setting, own_scale=SCALES[0]))
    found = noise_threshold(runs, key)
    assert found.status == "crossed"
    assert found.lo <= found.snr * (1 + 1e-9) and found.snr <= found.hi * (1 + 1e-9)
