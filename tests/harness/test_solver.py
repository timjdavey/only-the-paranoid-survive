"""HS2 to HS6, HS10, HS16 and HS17, see docs/specs/harness/tests.md#solver."""

from inspect_ai.model import ChatMessageSystem, ChatMessageTool, ChatMessageUser, GenerateConfig

from paranoid.engine import Record
from paranoid.harness import BLOCK_CACHE_APIS, record_blocks, tool_choice_for
from paranoid.skins import render_record, render_system_prompt

EVEN = [10] * 10


def submit_call(skin, bets=EVEN):
    return (skin.tool_name, {skin.bets_name: bets})


def test_hs2_each_round_starts_fresh(example, helpers):
    script = helpers.Script(then=helpers.reply(submit_call(example)))
    sample = helpers.run(script.model()).samples[0]
    store = helpers.store_of(sample)
    second = script.calls[1][0]
    assert [type(m) for m in second] == [ChatMessageSystem, ChatMessageUser]
    assert second[0].text == render_system_prompt(example)
    assert second[1].text == render_record(example, Record(store.record().rows[:1]))
    assert len(store.rows) == 40 and store.tries == [1] * 40 and len(script.calls) == 40


def test_hs3_a_bad_call_then_a_valid_one(example, helpers):
    valid = helpers.reply(submit_call(example))
    script = helpers.Script([helpers.reply(submit_call(example, [10] * 9))], then=valid)
    store = helpers.store_of(helpers.run(script.model()).samples[0])
    assert store.bad_calls == 1 and store.tries == [2] + [1] * 39 and len(store.rows) == 40
    retry = script.calls[1][0]
    tool_messages = [m for m in retry if isinstance(m, ChatMessageTool)]
    assert [m.text for m in tool_messages] == [example.bad_call] and tool_messages[0].error is None


def test_hs4_text_then_a_valid_call(example, helpers):
    script = helpers.Script([helpers.say("thinking")], then=helpers.reply(submit_call(example)))
    store = helpers.store_of(helpers.run(script.model()).samples[0])
    assert store.no_calls == 1 and store.bad_calls == 0 and store.tries[0] == 2
    assert script.calls[1][0][-1].role == "user" and script.calls[1][0][-1].text == example.no_call


def test_hs5_a_cut_off_reply(example, helpers):
    script = helpers.Script([helpers.say("long", "max_tokens")], then=helpers.reply(submit_call(example)))
    store = helpers.store_of(helpers.run(script.model()).samples[0])
    assert store.cut_offs == 1 and store.no_calls == 1


def test_hs6_ten_bad_calls_give_up(example, helpers):
    script = helpers.Script(then=helpers.reply(submit_call(example, [11] * 10)))
    sample = helpers.run(script.model()).samples[0]
    store = helpers.store_of(sample)
    assert store.gave_up and store.tries == [10] and store.bad_calls == 10
    assert store.rows == [] and not store.awaiting_submit and len(script.calls) == 10
    assert sample.scores["gain"].value["gave_up"] == 1


def test_hs10_tool_choice(example, helpers):
    valid = helpers.reply(submit_call(example))
    for choice in ("any", "auto"):
        script = helpers.Script(then=valid)
        sample = helpers.run(script.model(), tool_choice=choice).samples[0]
        assert {c[2] for c in script.calls} == {choice} and sample.metadata["tool_choice"] == choice
    script = helpers.Script(then=valid)
    sample = helpers.run(script.model()).samples[0]
    assert helpers.store_of(sample).tool_choice == "any" == sample.metadata["tool_choice"] == script.calls[0][2]
    offered = script.calls[0][1][0]
    assert offered.name == example.tool_name and offered.description == example.tool_text
    assert offered.parameters.properties[example.bets_name].description == example.bets_text


def test_hs16_tool_choice_for():
    assert tool_choice_for("anthropic", GenerateConfig(reasoning_effort="low")) == "auto"
    assert tool_choice_for("anthropic", GenerateConfig(reasoning_tokens=1024)) == "auto"
    assert tool_choice_for("anthropic", GenerateConfig()) == "any"
    assert tool_choice_for("anthropic", GenerateConfig(reasoning_effort="none")) == "any"
    assert tool_choice_for("openai", GenerateConfig(reasoning_effort="high")) == "any"


def test_hs17_record_blocks(example, played, helpers, monkeypatch):
    text = render_record(example, played)
    pieces = record_blocks(text)
    assert len(pieces) == 4 and "".join(pieces) == text and pieces[0] == text.splitlines(keepends=True)[0]
    assert BLOCK_CACHE_APIS == ()
    script = helpers.Script(then=helpers.reply(submit_call(example)))
    helpers.run(script.model())
    assert len(script.calls[2][0][1].content) == 1
    monkeypatch.setattr("paranoid.harness.solver.BLOCK_CACHE_APIS", ("mockllm",))
    script = helpers.Script(then=helpers.reply(submit_call(example)))
    helpers.run(script.model())
    assert len(script.calls[2][0][1].content) == 3
    note = (example.notes_name, {example.notes_param: "abc"})
    script = helpers.Script([helpers.reply(note, submit_call(example))], then=helpers.reply(submit_call(example)))
    helpers.run(script.model(), tools="notes")
    blocks = script.calls[2][0][1].content
    assert len(blocks) == 4 and blocks[-1].text == "abc"
