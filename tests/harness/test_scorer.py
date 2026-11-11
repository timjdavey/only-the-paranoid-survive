"""HO1 to HO3, HO7, HO11 and HO12: the scorer on whole evals. See docs/specs/harness/tests.md#scorer."""

import pytest
from inspect_ai.model import get_model
from inspect_ai.scorer import SampleScore

from paranoid.baselines import complacent, discerning, hedge_rule, perfect, scout_rule, uniform
from paranoid.engine import Record, make_timeline, play
from paranoid.harness import headline, load_seeds, pooled_score, retry_share, scenario_config, scenario_score
from paranoid.harness import tool_use_share, weakest_trait
from paranoid.skins import render_record

MARKS = {
    "uniform": uniform, "discerning": discerning, "complacent": complacent,
    "perfect": perfect, "hedge_rule": hedge_rule, "scout_rule": scout_rule,
}  # fmt: skip
KEYS = {
    "output", *MARKS, "gain", "gap", "run_score", "rounds", "warm_up_rounds", "retries", "retry_rounds", "gave_up",
    "bad_calls", "no_calls", "cut_offs", "notes_rounds", "compute_rounds", "unchanged_rounds", "explore_points",
    "sleeper_round",
}  # fmt: skip
EVEN = [10] * 10


def values(log) -> list[dict]:
    return [sample.scores["gain"].value for sample in log.samples]


def sample_scores(*logs) -> list[SampleScore]:
    return [
        SampleScore(score=s.scores["gain"], sample_id=s.id, sample_metadata=s.metadata) for log in logs for s in log.samples
    ]


def test_ho1_the_floor_and_the_yardstick(helpers):
    for value in values(helpers.run(get_model("baseline/uniform"), scenario="all", seeds="0-4")):
        assert value["gain"] == 0
    for value in values(helpers.run(get_model("baseline/discerning"), scenario="all", seeds="0-4")):
        assert value["gain"] == value["gap"]


def test_ho2_warm_up_rounds_score_nothing(helpers):
    sample = helpers.run(get_model("baseline/hedge_rule"), scenario="down_switch", warm_up="complacent:5").samples[0]
    value, store = sample.scores["gain"].value, helpers.store_of(sample)
    assert value["rounds"] == 35 and value["warm_up_rounds"] == 5
    assert value["output"] == sum(row.output for row in store.record().rows[5:])
    timeline = store.timeline()
    warm = Record(store.record().rows[:5])
    for name, policy in MARKS.items():
        assert value[name] == sum(row.output for row in play(policy, timeline, record=warm).rows[5:])


def kinds_by_position(positions) -> dict[str, int]:
    """A Down switch seed position of each switch kind, from the timeline."""
    found: dict[str, int] = {}
    for position in positions:
        timeline = make_timeline(scenario_config("down_switch"), load_seeds("public")[position])
        found.setdefault(timeline.events[0].numbers["kind"], position)
    return found


def test_ho3_every_key(helpers):
    kinds = kinds_by_position(range(20))
    seeds = f"{kinds['fall_and_rise']},{kinds['fall']}"
    log = helpers.run(get_model("baseline/uniform"), scenario="down_switch", seeds=seeds)
    for sample in log.samples:
        value = sample.scores["gain"].value
        assert set(value) == KEYS
        assert value["retries"] == 0 and value["gave_up"] == 0 and value["run_score"] == value["gain"] / value["gap"]
        assert value["explore_points"] == 90 and value["notes_rounds"] == value["compute_rounds"] == 0
        timeline = helpers.store_of(sample).timeline()
        if sample.metadata["seed_index"] == kinds["fall_and_rise"]:
            assert value["sleeper_round"] == timeline.events[0].onset
        else:
            assert value["sleeper_round"] is None


def test_ho7_a_run_that_gave_up(example, helpers):
    valid = helpers.reply((example.tool_name, {example.bets_name: EVEN}))
    bad = helpers.reply((example.tool_name, {example.bets_name: [11] * 10}))
    script = helpers.Script([valid, valid], then=bad)
    gave_up = helpers.run(script.model(), scenario="one_shock", seeds="0")
    value, store = values(gave_up)[0], helpers.store_of(gave_up.samples[0])
    assert value["gave_up"] == 1 and value["gain"] == 0 and value["run_score"] == 0 and value["rounds"] == 3
    assert value["output"] == sum(row.output for row in store.record().rows) and len(store.rows) == 2
    assert value["uniform"] == sum(row.output for row in play(uniform, store.timeline()).rows)
    scored = helpers.run(helpers.Script(then=valid).model(), scenario="one_shock", seeds="1-2")
    result = scenario_score()(sample_scores(gave_up, scored))
    assert result["one_shock_failed"] == 1 and result["one_shock_n"] == 3
    gains = [0.0] + [v["gain"] for v in values(scored)]
    gaps = [value["gap"]] + [v["gap"] for v in values(scored)]
    assert result["one_shock"] == pytest.approx(pooled_score(gains, gaps))


def test_ho11_answer_and_metadata(example, helpers):
    sample = helpers.run(get_model("baseline/complacent"), scenario="slow_drift", seeds="2").samples[0]
    score, store = sample.scores["gain"], helpers.store_of(sample)
    assert score.answer == render_record(example, store.record())
    assert score.metadata == {
        "scenario": "slow_drift", "seed_set": "public", "seed_index": 2,
        "engine_hash": sample.metadata["engine_hash"], "seed": load_seeds("public")[2],
    }  # fmt: skip


def test_ho12_metrics_need_no_seed_file(helpers, tmp_path, monkeypatch):
    log = helpers.run(get_model("baseline/hedge_rule"), scenario="one_shock,down_switch", seeds="0-3")
    logged = [(m.group, m.name, m.value) for m in log.results.scores[0].metrics.values()]
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PARANOID_SEEDS")
    with pytest.raises(FileNotFoundError):
        load_seeds("public")
    scores = sample_scores(log)
    metrics = {
        "scenario_score": scenario_score, "headline": headline, "weakest_trait": weakest_trait,
        "retry_share": retry_share, "tool_use_share": tool_use_share,
    }  # fmt: skip
    again = {group: metric()(scores) for group, metric in metrics.items()}
    assert len(logged) == sum(len(value) for value in again.values())
    for group, name, value in logged:
        name = name if name in again[group] else name[:-1]  # inspect adds a digit to a name two groups share
        assert again[group][name] == pytest.approx(value), (group, name)
