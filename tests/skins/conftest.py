"""Fixtures for the skins suite, see docs/specs/skins/tests.md.

Every skin here is built by hand or written to tmp_path, so no bad skin is checked in.
"""

import json
from pathlib import Path

import pytest

from paranoid.baselines import uniform
from paranoid.engine import SCENARIOS, Record, make_timeline, play
from paranoid.skins import Skin, load_skins

# A clean four channel skin that passes the lint. The example skin is pinned in test_example.py only.
CLEAN = {
    "channels": ("Ashford", "Brill", "Corran", "Dunmore"),
    "intro": "You run a bakery that sends bread to four shops: Ashford, Brill, Corran and Dunmore.",
    "rules": "Each day you split the bread across the four shops, as percentages. "
    "Each percentage is a whole number and the four add up to 100.",
    "how_points_earn": "Each shop pays a price per loaf on what you sent it.",
    "ask": "Your record is below. Send today's bread with the send_bread tool.",
    "tool_name": "send_bread",
    "tool_text": "Send today's bread to the shops.",
    "bets_name": "split",
    "bets_text": "The percentage of today's bread for each shop.",
    "bad_call": "That split can't be sent.",
    "no_call": "Send the bread with the send_bread tool.",
    "notes_name": "note",
    "notes_text": "Leave yourself a note.",
    "notes_param": "words",
    "notes_param_text": "What the note says.",
    "compute_name": "calculate",
    "compute_text": "Run Python.",
    "compute_param": "code",
    "compute_param_text": "The Python to run.",
    "question": "Which shop should get today's bread?",
    "round_word": "day",
    "bet_word": "sent",
    "reading_word": "price",
}
DROP = object()  # an override that leaves the key out of a written file


def make_skin(**overrides) -> Skin:
    """The clean skin, named `bakery`, with any field replaced."""
    return Skin(**({"name": "bakery"} | CLEAN | overrides))


def toml_value(value) -> str:
    """A TOML literal. A JSON string is a valid TOML basic string."""
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(toml_value(v) for v in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def write_skin(folder: Path, stem: str, **overrides) -> Path:
    """The clean skin as `<stem>.toml` in folder. An override of DROP leaves its key out."""
    keys = CLEAN | overrides
    path = folder / f"{stem}.toml"
    path.write_text("".join(f"{k} = {toml_value(v)}\n" for k, v in keys.items() if v is not DROP), encoding="utf-8")
    return path


# The suite runs with --import-mode=importlib, so tests take each helper as a fixture.


@pytest.fixture(scope="session", name="make_skin")
def make_skin_fixture():
    return make_skin


@pytest.fixture(scope="session", name="write_skin")
def write_skin_fixture():
    return write_skin


@pytest.fixture(scope="session", name="drop")
def drop_fixture():
    return DROP


@pytest.fixture(scope="session", name="clean")
def clean_fixture():
    return CLEAN


@pytest.fixture(scope="session")
def example(tmp_path_factory) -> Skin:
    """The example skin, loaded beside an empty held-out folder so PARANOID_SKINS is never read."""
    return load_skins(tmp_path_factory.mktemp("empty"))["example"]


@pytest.fixture(scope="session")
def played() -> Record:
    """Three rounds of uniform on a public seed, ten channels."""
    return play(uniform, make_timeline(SCENARIOS["no_change"], 0), max_rounds=3)


@pytest.fixture
def no_held_out(monkeypatch):
    """PARANOID_SKINS unset, so load_skins() reads the example skin only."""
    monkeypatch.delenv("PARANOID_SKINS", raising=False)
