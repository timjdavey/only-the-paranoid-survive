"""KR1 and KR3 to KR10, see docs/specs/skins/tests.md#render. KR2 is in test_example.py."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from paranoid.baselines import uniform
from paranoid.engine import SCENARIOS, Record, Row, ScenarioConfig, make_timeline, play
from paranoid.skins import prompt_hash, render_record, render_system_prompt

FOUR_CHANNEL_HEADER = (
    "day,Ashford_sent,Brill_sent,Corran_sent,Dunmore_sent,Ashford_price,Brill_price,Corran_price,Dunmore_price\n"
)


def test_kr1_the_prompt_is_four_fields_joined_by_a_blank_line(make_skin):
    skin = make_skin(intro="  Intro.\r\n", rules="Rules.", how_points_earn="How.\nIt pays.", ask="Ask. ")
    assert render_system_prompt(skin) == "Intro.\n\nRules.\n\nHow.\nIt pays.\n\nAsk."


def test_kr3_the_prompt_is_the_same_every_call_and_in_a_subprocess(make_skin):
    skin = make_skin()
    assert render_system_prompt(skin) == render_system_prompt(skin)
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); from conftest import make_skin; "
        "from paranoid.skins import render_system_prompt; "
        "sys.stdout.write(render_system_prompt(make_skin()))"
    )
    command = [sys.executable, "-c", code, str(Path(__file__).parent)]
    out = subprocess.run(command, capture_output=True, check=True).stdout
    assert out.decode("utf-8") == render_system_prompt(skin)


def test_kr4_an_empty_record_is_the_header(make_skin):
    assert render_record(make_skin(), Record()) == FOUR_CHANNEL_HEADER


def test_kr4_the_example_header(example):
    header = render_record(example, Record())
    columns = header.rstrip("\n").split(",")
    assert header.count("\n") == 1 and header.endswith("\n")
    assert columns == [
        "week",
        *(f"{name}_sent" for name in example.channels),
        *(f"{name}_price" for name in example.channels),
    ]


def test_kr5_a_played_record(example, played):
    lines = render_record(example, played).splitlines()
    assert len(lines) == 4
    for line in lines[1:]:
        cells = line.split(",")
        assert len(cells) == 1 + 2 * len(example.channels)
        assert all(re.fullmatch(r"\d+", cell) for cell in cells[: 1 + len(example.channels)])
        assert all(re.fullmatch(r"-?\d+\.\d", cell) for cell in cells[1 + len(example.channels) :])


def test_kr6_a_record_that_does_not_fit_the_skin(example):
    four = make_timeline(ScenarioConfig(name="four", channels=4), 0)
    record = play(uniform, four, max_rounds=1)
    with pytest.raises(ValueError, match="channels"):
        render_record(example, record)


def test_kr7_the_hash_is_twelve_lowercase_hex(make_skin):
    assert re.fullmatch(r"[0-9a-f]{12}", prompt_hash(make_skin()))


COVERED = {
    "channels": ("Ashford", "Brill", "Corran", "Elmstead"),
    "intro": "Another intro.",
    "rules": "Other rules.",
    "how_points_earn": "Another way.",
    "ask": "Another ask.",
    "tool_name": "send_loaves",
    "tool_text": "Other text.",
    "bets_name": "shares",
    "bets_text": "Other text.",
    "bad_call": "Other text.",
    "no_call": "Other text.",
    "notes_name": "memo",
    "notes_text": "Other text.",
    "notes_param": "memo_text",
    "compute_name": "python",
    "compute_text": "Other text.",
    "compute_param": "script",
    "question": "Other question?",
    "round_word": "morning",
    "bet_word": "baked",
    "reading_word": "takings",
}


@pytest.mark.parametrize("field", COVERED)
def test_kr7_every_covered_field_moves_the_hash(field, make_skin):
    assert prompt_hash(make_skin(**{field: COVERED[field]})) != prompt_hash(make_skin())


def test_kr7_the_name_does_not_move_the_hash(make_skin):
    assert prompt_hash(make_skin(name="teal")) == prompt_hash(make_skin())


def test_kr7_a_render_version_bump_moves_the_hash(make_skin, monkeypatch):
    before = prompt_hash(make_skin())
    monkeypatch.setattr("paranoid.skins.render.RENDER_VERSION", 2)
    assert prompt_hash(make_skin()) != before


def test_kr8_a_non_ascii_name_hashes_to_a_pinned_value(make_skin):
    """Worked out from the spec by hand. With ensure_ascii on, the same skin would hash to 1f222cbb1ca7."""
    skin = make_skin(channels=("Ashford", "Brill", "Corran", "Zürich"))
    assert prompt_hash(skin) == "6380dbdb2b6f"


TWO_ROUNDS = Record(
    [
        Row(round=1, bets=(100, 0, 0, 0), readings=(61.2, None, None, None)),
        Row(round=2, bets=(40, 30, 20, 10), readings=(58.04, 71.0, -0.04, 99.95)),
    ]
)


def test_kr9_a_two_round_record_byte_for_byte(make_skin):
    assert render_record(make_skin(), TWO_ROUNDS) == (
        FOUR_CHANNEL_HEADER + "1,100,0,0,0,61.2,,,\n" + "2,40,30,20,10,58.0,71.0,0.0,100.0\n"
    )


def test_kr10_cells(make_skin):
    record = Record(
        [
            Row(round=1, bets=(25, 25, 25, 25), readings=(-0.0, 1.0, 2.5, 3.0)),
            Row(round=2, bets=(100, 0, 0, 0), readings=(5.0, None, None, None)),
            Row(round=3, bets=(97, 1, 1, 1), readings=(-1.5, 0.0, 0.0, 0.0)),
        ]
    )
    lines = render_record(make_skin(), record).splitlines()
    assert len(lines) == 4
    assert lines[1] == "1,25,25,25,25,0.0,1.0,2.5,3.0"
    assert lines[2] == "2,100,0,0,0,5.0,,,"
    assert lines[3] == "3,97,1,1,1,-1.5,0.0,0.0,0.0"
