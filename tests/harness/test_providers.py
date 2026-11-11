"""HR1, HR2, HR4 to HR6, HR8, HR9 and HY3, see docs/specs/harness/tests.md#providers."""

import asyncio
import sys

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from inspect_ai.model import ChatMessageAssistant, GenerateConfig, get_model

from paranoid.baselines import POLICIES, HedgeRule
from paranoid.engine import Record
from paranoid.harness import BaselineAPI, JevAPI, TimestralAPI
from paranoid.skins import render_record, render_system_prompt


def test_hr1_every_baseline_resolves():
    for name in POLICIES:
        assert isinstance(get_model(f"baseline/{name}").api, BaselineAPI)
    with pytest.raises(ValueError, match="hedge_rule"):
        get_model("baseline/nope")


def assistant_messages(sample):
    return [m for m in sample.messages if isinstance(m, ChatMessageAssistant)]


@pytest.mark.parametrize("model", ["baseline/complacent", "jev/fake", "timestral/top-pick"])
def test_hr2_one_call_and_no_text(model, example, helpers, FakeJev, Fake):
    args = {"jev/fake": {"client": FakeJev()}, "timestral/top-pick": {"forecaster": Fake()}}.get(model, {})
    sample = helpers.run(get_model(model, memoize=False, **args), rounds=20).samples[0]
    for event in [e for e in sample.events if type(e).__name__ == "ModelEvent"]:
        message = event.output.message
        assert message.content == "" and len(message.tool_calls) == 1
        call = message.tool_calls[0]
        assert call.function == example.tool_name and list(call.arguments) == [example.bets_name]
        assert len(call.arguments[example.bets_name]) == 10
        assert event.output.usage.input_tokens == 0 and event.output.usage.output_tokens == 0
    assert assistant_messages(sample)[-1].tool_calls[0].id == f"{model.split('/')[1]}-20"


def test_hr2_no_tools_raises():
    with pytest.raises(RuntimeError):
        asyncio.run(BaselineAPI("uniform").generate([], [], "any", GenerateConfig()))


def test_hr4_model_args_are_cast():
    assert BaselineAPI("hedge_rule", explore="1", window="4").policy == HedgeRule(explore=1, window=4)
    assert BaselineAPI("hedge_rule").policy == HedgeRule()
    with pytest.raises(ValueError, match="explore"):
        BaselineAPI("hedge_rule", nope="1")
    with pytest.raises(ValueError):
        BaselineAPI("uniform", explore="1")
    assert get_model("baseline/hedge_rule", explore="2").api.policy == HedgeRule(explore=2)


def test_hr5_hr6_jev(example, helpers, FakeJev):
    answers = {1: [0.5, 0.5] + [0.0] * 8, 2: [0.004, 0.996] + [0.0] * 8}
    client = FakeJev(answers)
    sample = helpers.run(get_model("jev/fake", client=client, memoize=False), rounds=20).samples[0]
    store = helpers.store_of(sample)
    assert list(store.rows[0].bets) == [50, 50] + [0] * 8 and list(store.rows[1].bets) == [0, 100] + [0] * 8
    state, question, options = client.asked[1]
    record = render_record(example, Record(store.record().rows[:1]))
    assert state == render_system_prompt(example) + "\n\n" + record
    assert question == example.question and options == example.channels
    metadata = assistant_messages(sample)[-1].metadata
    assert {"probabilities", "confidence", "raw", "rounded_out"} <= set(metadata)
    nine = FakeJev({1: [0.1] * 9})
    with pytest.raises(AssertionError):
        helpers.run(get_model("jev/fake", client=nine, memoize=False), rounds=20)


def test_hr8_timestral_without_the_extra(monkeypatch, Fake):
    for name in ("torch", "timestral"):
        monkeypatch.setitem(sys.modules, name, None)
    with pytest.raises(ImportError, match="uv sync --extra timestral"):
        TimestralAPI("top-pick")
    TimestralAPI("top-pick", forecaster=Fake())
    with pytest.raises(ValueError, match="odds-alone"):
        TimestralAPI("nope", forecaster=Fake())


def test_hr9_max_connections(FakeJev, Fake):
    assert BaselineAPI("uniform").max_connections() == 32
    assert JevAPI("fake", client=FakeJev()).max_connections() == 4
    assert TimestralAPI("odds", forecaster=Fake()).max_connections() == 1


@settings(max_examples=10, deadline=None)
@given(st.lists(st.floats(0.0, 1.0), min_size=10, max_size=10).filter(lambda p: sum(p) > 0))
def test_hy3_jev_bets_sum_to_the_budget(helpers, FakeJev, weights):
    probabilities = [w / sum(weights) for w in weights]
    client = FakeJev({1: probabilities})
    store = helpers.store_of(helpers.run(get_model("jev/fake", client=client, memoize=False), rounds=20).samples[0])
    assert len(store.rows[0].bets) == 10 and sum(store.rows[0].bets) == 100
