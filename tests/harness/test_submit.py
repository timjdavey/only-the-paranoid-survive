"""HS7 to HS9, HS18 and HY2, see docs/specs/harness/tests.md#solver."""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from inspect_ai.event import ToolEvent
from inspect_ai.model import ChatMessageTool

from paranoid.engine import Record
from paranoid.skins import load_skins, render_record

EVEN = [10] * 10


@pytest.mark.parametrize("bets", [[10.0] * 10, ["10"] * 10, [True] * 10, [10.5] * 10], ids=["float", "str", "bool", "half"])
def test_hs7_refused_and_rejected_bets_read_the_skin(example, helpers, bets):
    bad = helpers.reply((example.tool_name, {example.bets_name: bets}))
    script = helpers.Script([bad], then=helpers.reply((example.tool_name, {example.bets_name: EVEN})))
    sample = helpers.run(script.model(), rounds=20).samples[0]
    store = helpers.store_of(sample)
    assert store.bad_calls == 1 and store.tries[0] == 2
    first = [m for m in script.calls[1][0] if isinstance(m, ChatMessageTool)][0]
    assert first.text == example.bad_call and first.error is None
    text = " ".join(m.text for m in sample.messages)
    assert "Bad tool call" not in text and "Error" not in text and "validation" not in text.lower()


def test_hs7_a_missing_tool_gets_no_call(example, helpers):
    script = helpers.Script([helpers.reply(("laser", {"x": 1}))], then=helpers.reply((example.tool_name, {example.bets_name: EVEN})))
    store = helpers.store_of(helpers.run(script.model(), rounds=20).samples[0])
    tool = [m for m in script.calls[1][0] if isinstance(m, ChatMessageTool)][0]
    assert tool.text == example.no_call and tool.error is None
    assert store.no_calls == 1 and store.bad_calls == 0


def test_hs8_the_second_submit_is_a_bad_call(example, helpers):
    call = (example.tool_name, {example.bets_name: EVEN})
    script = helpers.Script([helpers.reply(call, call)], then=helpers.reply(call))
    sample = helpers.run(script.model(), rounds=20).samples[0]
    store = helpers.store_of(sample)
    assert store.bad_calls == 1 and len(store.rows) == 20 and store.tries == [1] * 20
    round_one = [e for e in sample.events if isinstance(e, ToolEvent)][:2]
    assert round_one[1].result == example.bad_call


def test_hs9_the_tool_result_is_the_row_played(example, helpers):
    script = helpers.Script(then=helpers.reply((example.tool_name, {example.bets_name: EVEN})))
    sample = helpers.run(script.model(), rounds=20).samples[0]
    record = helpers.store_of(sample).record()
    results = [e.result for e in sample.events if isinstance(e, ToolEvent)]
    for n, result in enumerate(results, start=1):
        lines = render_record(example, Record(record.rows[:n])).splitlines(keepends=True)
        assert result == lines[0] + lines[-1]


def test_hs18_parameter_names_are_the_skin_s(tmp_path, monkeypatch, helpers, skin_file):
    skin_file(tmp_path / "renamed.toml", bets_name="amounts", notes_param="memo", compute_param="script")
    monkeypatch.setenv("PARANOID_SKINS", str(tmp_path))
    good, bad = ("send_fruit", {"amounts": EVEN}), ("send_fruit", {"bets": EVEN})
    script = helpers.Script([helpers.reply(bad)], then=helpers.reply(good))
    store = helpers.store_of(helpers.run(script.model(), skin="renamed", tools="notes", rounds=20).samples[0])
    assert store.bad_calls == 1 and len(store.rows) == 20
    offered = {tool.name: tool for tool in script.calls[0][1]}
    submit = offered["send_fruit"].parameters
    assert list(submit.properties) == ["amounts"] and submit.required == ["amounts"]
    assert submit.properties["amounts"].type == "array" and submit.properties["amounts"].items.type == "integer"
    note = offered["desk_note"].parameters
    assert list(note.properties) == ["memo"] and note.required == ["memo"] and note.properties["memo"].type == "string"
    renamed = load_skins()["renamed"]
    assert offered["desk_note"].description == renamed.notes_text != renamed.notes_param_text
    assert note.properties["memo"].description == renamed.notes_param_text


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
@given(st.lists(st.integers(0, 30), min_size=9, max_size=9).filter(lambda s: sum(s) <= 100))
def test_hy2_any_valid_split_plays(example, helpers, head):
    split = [*head, 100 - sum(head)]
    script = helpers.Script(then=helpers.reply((example.tool_name, {example.bets_name: split})))
    store = helpers.store_of(helpers.run(script.model(), rounds=20).samples[0])
    row = store.rows[0]
    assert row.bets == split
    assert [reading is None for reading in row.readings] == [bet == 0 for bet in split]
