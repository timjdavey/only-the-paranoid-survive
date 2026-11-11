"""HR3, HR7, HR10, HS1, HS14 and HK9: whole evals through the providers. See docs/specs/harness/tests.md."""

import tempfile
from dataclasses import dataclass, replace

import inspect_ai
import pytest
from inspect_ai.model import ChatMessageAssistant, get_model

from paranoid.baselines import POLICIES, complacent, uniform
from paranoid.engine import SCENARIOS, Game, make_timeline, play
from paranoid.forecasters import TIMESTRAL_POLICIES
from paranoid.harness import load_seeds, paranoid


def rows_of(store):
    return store.record().rows


@pytest.mark.parametrize("name", list(POLICIES))
def test_hr3_a_baseline_plays_as_play_does(name, helpers):
    log = helpers.run(get_model(f"baseline/{name}"), scenario="down_switch", seeds="0-4")
    seeds = load_seeds("public")
    for sample in log.samples:
        timeline = make_timeline(SCENARIOS["down_switch"], seeds[sample.metadata["seed_index"]])
        assert rows_of(helpers.store_of(sample)) == play(POLICIES[name](), timeline).rows


@pytest.mark.parametrize("name", list(TIMESTRAL_POLICIES))
def test_hr7_a_timestral_policy_plays_as_play_does(name, helpers, Fake):
    model = get_model(f"timestral/{name}", forecaster=Fake(), memoize=False)
    log = helpers.run(model, scenario="down_switch", seeds="0-2")
    seeds = load_seeds("public")
    policy = replace(TIMESTRAL_POLICIES[name], forecaster=Fake())
    for sample in log.samples:
        timeline = make_timeline(SCENARIOS["down_switch"], seeds[sample.metadata["seed_index"]])
        assert rows_of(helpers.store_of(sample)) == play(policy, timeline).rows
        replies = [e.output.message for e in sample.events if type(e).__name__ == "ModelEvent"]
        for n, message in enumerate(replies):
            assert {"quantiles", "cache_key", "rounded_out"} <= set(message.metadata)
            assert (message.metadata["quantiles"] is None) == (n == 0) == (message.metadata["cache_key"] is None)
    with pytest.raises(ValueError, match="odds-bet-aware"):
        get_model("timestral/nope", forecaster=Fake(), memoize=False)


def test_hs1_a_baseline_run(helpers):
    sample = helpers.run(get_model("baseline/uniform"), scenario="one_shock").samples[0]
    store = helpers.store_of(sample)
    assert len(store.rows) == store.config().rounds and store.tries == [1] * len(store.rows)
    assert rows_of(store) == play(uniform, store.timeline()).rows


def test_hs14_the_log_replays(helpers):
    sample = helpers.run(get_model("baseline/hedge_rule"), scenario="down_switch", seeds="3").samples[0]
    store = helpers.store_of(sample)
    game = Game(store.timeline())
    for stored in rows_of(store):
        replayed = game.play(stored.bets)
        assert replayed.readings == stored.readings and replayed.output == stored.output


def test_hk9_warm_up(helpers):
    sample = helpers.run(get_model("baseline/uniform"), scenario="down_switch", warm_up="complacent:5").samples[0]
    store = helpers.store_of(sample)
    assert store.warm_up_rounds == 5 and len(store.tries) == 35
    assert rows_of(store)[:5] == play(complacent, store.timeline(), max_rounds=5).rows
    first = helpers.sent(sample)[0]
    assert len(first[1].text.splitlines()) == 6
    assert isinstance(sample.messages[-2], ChatMessageAssistant)
    for bad in ("complacent:0", "complacent:40", "nope:5", "complacent"):
        with pytest.raises(ValueError):
            paranoid(seeds="0", warm_up=bad)


@dataclass(frozen=True)
class OverBudget:
    """A buggy baseline: 110 points a round."""

    peeks: bool = False

    def __call__(self, view):
        return [11] * 10


def test_hr10_a_baseline_that_bets_badly_errors_the_sample(monkeypatch, helpers):
    monkeypatch.setattr("paranoid.harness.providers.baseline.POLICIES", {**POLICIES, "over_budget": OverBudget})
    task = paranoid(scenario="no_change", seeds="0", tools="none")
    model = get_model("baseline/over_budget", memoize=False)
    (log,) = inspect_ai.eval(task, model=model, display="none", log_dir=tempfile.mkdtemp(), log_realtime=False)
    sample = log.samples[0]
    assert sample.error is not None and "over_budget" in sample.error.message and "round 1" in sample.error.message
    store = helpers.store_of(sample)
    assert not store.gave_up and store.bad_calls == 0 and store.rows == []
