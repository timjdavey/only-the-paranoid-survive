"""HO4 to HO6, HO8 to HO10, HO13 and HY1, see docs/specs/harness/tests.md#scorer.

Every SampleScore here is built by hand, so the metrics are tested with no eval.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from inspect_ai.scorer import SampleScore, Score

from paranoid.engine import SCENARIOS
from paranoid.harness import TRAITS, bootstrap, headline, pooled_score, retry_share, scenario_score
from paranoid.harness import tool_use_share, weakest_trait


def scored(scenario: str, index: int, gain: float, gap: float = 100.0, **value) -> SampleScore:
    full = {"gain": gain, "gap": gap, "gave_up": 0, "rounds": 40, "retry_rounds": 0, "cut_offs": 0}
    full |= {"notes_rounds": 0, "compute_rounds": 0} | value
    return SampleScore(score=Score(value=full), sample_metadata={"scenario": scenario, "seed_index": index})


def test_ho4_pooled_not_mean():
    assert pooled_score([880, 220], [1100, 550]) == pytest.approx(2 / 3)
    assert pooled_score([880, 220], [1100, 550]) != pytest.approx(0.6)
    for gains, gaps in (([], []), ([1.0], [0.0]), ([1.0, -1.0], [1.0, -1.0])):
        with pytest.raises(ValueError):
            pooled_score(gains, gaps)


def test_ho5_bootstrap():
    assert bootstrap([30.0], [60.0]) == (0.5, 0.5)
    rng = np.random.default_rng(1)
    gaps = rng.uniform(50, 150, 100)
    gains = gaps * rng.normal(0.7, 0.1, 100)
    assert bootstrap(gains, gaps) == bootstrap(gains, gaps)
    lo, hi = bootstrap(gains, gaps)
    assert lo < 0.7 < hi


def test_ho6_scenario_score():
    scores = [scored("one_shock", i, g) for i, g in enumerate([50, 70, 90])]
    scores += [scored("down_switch", i, g, 200) for i, g in enumerate([20, 40])]
    result = scenario_score()(scores)
    assert result["one_shock"] == pytest.approx(210 / 300) and result["down_switch"] == pytest.approx(60 / 400)
    for name, n in (("one_shock", 3), ("down_switch", 2)):
        assert result[f"{name}_lo"] <= result[name] <= result[f"{name}_hi"]
        assert result[f"{name}_n"] == n and result[f"{name}_failed"] == 0


def test_ho8_headline():
    scores = [scored(name, i, 40 + 10 * s + i) for s, name in enumerate(SCENARIOS) for i in range(5)]
    result = headline()(scores)
    per = scenario_score()(scores)
    assert result["headline"] == pytest.approx(np.mean([per[name] for name in SCENARIOS]))
    assert result["scenarios"] == 8 and result["lo"] <= result["headline"] <= result["hi"]
    assert headline()([s for s in scores if s.sample_metadata["scenario"] in list(SCENARIOS)[:3]])["scenarios"] == 3


def test_ho9_weakest_trait():
    assert len(TRAITS) == 8 and list(TRAITS) == list(SCENARIOS)
    assert TRAITS["down_switch"] == "doubt" and TRAITS["up_switch_then_down_switch"] == "recall"
    scores = [scored("one_shock", 0, 50), scored("down_switch", 0, 30), scored("up_switch", 0, 30)]
    assert weakest_trait()(scores) == {"doubt": pytest.approx(0.3)}


def test_ho10_retry_share():
    four = scored("one_shock", 0, 1, rounds=4, retry_rounds=2, cut_offs=1)
    assert retry_share()([four])["all"] == 0.5
    gave_up = scored("down_switch", 0, 0, rounds=3, retry_rounds=1, gave_up=1)
    result = retry_share()([gave_up])
    assert result["down_switch"] == pytest.approx(1 / 3) and result["cut_off_share"] == 0
    assert retry_share()([four, gave_up])["cut_off_share"] == pytest.approx(1 / 7)


def test_ho13_tool_use_share():
    scores = [scored("one_shock", 0, 1, notes_rounds=4), scored("one_shock", 1, 1)]
    assert tool_use_share()(scores) == {"notes": 0.05, "compute": 0}


@settings(max_examples=50, deadline=None)
@given(st.lists(st.tuples(st.floats(0, 1e4), st.floats(1e-3, 1e4)), min_size=1, max_size=20))
def test_hy1_pooled_lies_between_run_scores(pairs):
    gains, gaps = zip(*pairs)
    runs = [g / p for g, p in pairs]
    tolerance = 1e-9 * max(1.0, max(runs))
    assert min(runs) - tolerance <= pooled_score(gains, gaps) <= max(runs) + tolerance
