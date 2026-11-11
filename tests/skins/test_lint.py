"""KL1 to KL10, KL12 and KL14, see docs/specs/skins/tests.md#lint. KL11 and KL13 are in test_example.py."""

import dataclasses

import pytest

from paranoid.baselines import uniform
from paranoid.engine import SCENARIOS, make_timeline, play
from paranoid.skins import (
    BANNED_WORDS,
    CANARY,
    PERCENT_PHRASES,
    PREFIXES,
    WHOLE_NUMBER_PHRASES,
    LintError,
    Skin,
    lint,
    lint_text,
    load_skins,
    render_record,
    render_system_prompt,
)

GUID = CANARY.split("canary GUID ", 1)[1]

# The "also catches" column of docs/specs/skins/lint.md#words, and the extra words KL1 names.
ALSO_CATCHES = {
    "check": ["checks", "checking", "checked", "checkpoint", "recheck", "unchecked"],
    "chang": ["changes", "changing", "changed", "unchanged"],
    "shift": ["shifts", "shifting", "shifted"],
    "switch": ["switches", "switching", "switched"],
    "shock": ["shocks", "shocked"],
    "drift": ["drifts", "drifting", "drifted"],
    "trend": ["trends", "trending", "detrend", "detrended"],
    "anomal": ["anomalies", "anomalous"],
    "regime": ["regimes", "regimen"],
    "climat": ["climates", "climatic"],
    "detect": ["detects", "detection", "detector", "undetected"],
    "monitor": ["monitors", "monitoring", "unmonitored"],
    "watch": ["watches", "watching", "unwatched"],
    "alert": ["alerts", "alerted"],
    "stabl": ["stably", "unstable"],
    "stabil": ["stability", "instability", "destabilise", "destabilised"],
    "volatil": ["volatility"],
    "benchmark": ["benchmarks", "benchmarking"],
    "canar": ["canaries"],
    "paranoi": ["paranoia"],
}


@pytest.mark.parametrize("entry, word", [(e, w) for e, words in ALSO_CATCHES.items() for w in words])
def test_kl1_each_word_hits_its_entry(entry, word):
    assert lint_text(word) == (entry,)
    assert lint_text(word.capitalize()) == (entry,)


@pytest.mark.parametrize("word", ["established", "exchange", "research", "cheque", "swatch"])
def test_kl1_a_substring_inside_a_word_does_not_count(word):
    assert lint_text(word) == ()


def test_kl2_one_entry_once():
    assert lint_text("Check the CHECKS, then recheck again") == ("check",)
    assert lint_text("") == ()


def test_kl2_apostrophes_and_digits_end_a_word():
    assert lint_text("can't 3drift") == ("drift",)


def test_kl3_entries_come_in_text_order():
    assert lint_text("A trend, then a shock; the drift.") == ("trend", "shock", "drift")


def test_kl4_the_lists_are_pinned():
    assert BANNED_WORDS == tuple(ALSO_CATCHES)
    assert PREFIXES == ("un", "in", "de", "re", "non")
    assert WHOLE_NUMBER_PHRASES == ("whole number", "integer")
    assert PERCENT_PHRASES == ("percent", "per cent", "%")


def test_kl4_entries_are_lowercase_letters_and_none_starts_another():
    for entry in BANNED_WORDS + PREFIXES:
        assert entry.isascii() and entry.isalpha() and entry.islower()
    for a in BANNED_WORDS:
        assert not any(b != a and b.startswith(a) for b in BANNED_WORDS)


def problems_of(skin: Skin) -> tuple[str, ...]:
    with pytest.raises(LintError) as caught:
        lint(skin)
    return caught.value.problems


def drifted(field: str, clean: dict) -> dict:
    """The clean value of field with a banned word added, still a valid Skin."""
    if field == "channels":
        return {"channels": (*clean["channels"][:3], "Driftwood")}
    if field in ("tool_name", "bets_name", "notes_name", "notes_param", "compute_name", "compute_param"):
        return {field: "drift_" + clean[field]}
    if field in ("round_word", "bet_word", "reading_word"):
        return {field: "drifted"}
    return {field: clean[field] + " Drift."}


@pytest.mark.parametrize("field", [f.name for f in dataclasses.fields(Skin) if f.name != "name"])
def test_kl5_a_banned_word_in_each_field(field, make_skin, clean):
    label = "channels[3]" if field == "channels" else field
    assert f"{label}: drift" in problems_of(make_skin(**drifted(field, clean)))


def test_kl5_a_banned_word_in_the_name_alone_passes(make_skin):
    assert lint(make_skin(name="drift_bakery")) is None


MISSING = {
    "missing: percent": {"rules": "Each day you split the bread across the shops. Each share is a whole number "
                         "and the four add up to 100."},
    "missing: 100": {"rules": "Each day you split the bread across the shops, as percentages. Each percentage "
                     "is a whole number and the four add up to a hundred."},
    "missing: channels[3]": {"intro": "You run a bakery that sends bread to shops in Ashford, Brill and Corran."},
    "missing: whole numbers": {"rules": "Each day you split the bread across the shops, as percentages. The four "
                               "add up to 100."},
    "missing: tool name": {"ask": "Your record is below. Send today's bread with the tool."},
}


@pytest.mark.parametrize("problem", MISSING)
def test_kl6_each_missing_fact(problem, make_skin):
    assert problems_of(make_skin(**MISSING[problem])) == (problem,)


TEN = ("Ashford", "Brill", "Corran", "Dunmore", "Elmstead", "Fenwick", "Garth", "Holme", "Ivybridge", "Jarrow")


def test_kl7_the_facts_are_checked_on_the_whole_prompt(make_skin):
    skin = make_skin(
        channels=TEN,
        intro="You run a bakery with ten shops: " + ", ".join(TEN) + ".",
        rules="Use the send_bread tool to split the bread as percentages, whole numbers adding up to 100.",
        ask="Your record is below.",
    )
    assert lint(skin) is None


@pytest.mark.parametrize(
    "rules",
    [
        "Split it in Whole Numbers adding up to 100 percent.",
        "Split it in integers adding up to 100 percent.",
        "Split it in Percentages, each a whole number, adding up to 100.",
        "Split it per cent, each a whole number, adding up to 100.",
        "Split it in %, each a whole number, adding up to 100.",
    ],
)
def test_kl8_phrases_that_state_a_fact(rules, make_skin):
    assert lint(make_skin(rules=rules)) is None


@pytest.mark.parametrize(
    "field, value, problem",
    [
        ("ask", "Use the send_bread tool. " + GUID, "canary in prompt"),
        ("tool_text", "Send it. " + GUID, "canary in tool_text"),
        ("compute_text", "Run Python. " + GUID, "canary in compute_text"),
        ("notes_param_text", "The note. " + GUID, "canary in notes_param_text"),
        ("reading_word", GUID, "canary in reading_word"),
    ],
)
def test_kl9_the_guid_anywhere_the_model_reads(field, value, problem, make_skin):
    assert problem in problems_of(make_skin(**{field: value}))


def test_kl10_every_problem_in_one_error(make_skin, clean):
    skin = make_skin(
        intro=clean["intro"] + " Prices drift.",
        tool_text="Send the bread, then check.",
        rules="Each day you split the bread as percentages, each a whole number.",
        question="Which shop? " + GUID,
    )
    with pytest.raises(LintError) as caught:
        lint(skin)
    # The GUID holds the word paranoid and runs of digits, so the question hits the word lint and the number rule too.
    assert caught.value.problems == (
        "intro: drift",
        "tool_text: check",
        "question: paranoi",
        "question: number",
        "missing: 100",
        "canary in question",
    )
    message = str(caught.value)
    assert message.startswith("Skin bakery failed lint: ")
    texts = [getattr(skin, f.name) for f in dataclasses.fields(Skin) if f.name not in ("name", "channels")]
    assert not any(text in message for text in [*texts, *skin.channels, GUID])


def test_kl12_no_skin_on_this_machine_leaks():
    """Covers held-out skins when PARANOID_SKINS is set. A failure names the skin, never its text."""
    for skin in load_skins().values():
        config = dataclasses.replace(SCENARIOS["no_change"], channels=len(skin.channels))
        record = play(uniform, make_timeline(config, 0), max_rounds=3)
        texts = [render_system_prompt(skin), render_record(skin, record), *skin.channels]
        texts += [getattr(skin, f.name) for f in dataclasses.fields(Skin) if f.name not in ("name", "channels")]
        if lint_text(render_record(skin, record)) != () or any(GUID in text for text in texts):
            pytest.fail(skin.name, pytrace=False)


NUMBERS = {
    "intro": "You run a bakery that has sent bread to four shops since 1987: Ashford, Brill, Corran and Dunmore.",
    "how_points_earn": "Each shop pays a price per loaf on what you sent it, about 2 a loaf.",
    "rules": "Each day you split the bread across the four shops, as percentages. "
    "Each percentage is a whole number and the four add up to 100, never 1000.",
    "notes_name": "note2",
    "notes_param": "words_1",
    "channels": ("Ashford", "Brill", "Corran", "Dunmore 4"),
    "round_word": "day7",
}


@pytest.mark.parametrize("field", NUMBERS)
def test_kl14_a_number_in_each_field(field, make_skin):
    label = "channels[3]" if field == "channels" else field
    assert f"{label}: number" in problems_of(make_skin(**{field: NUMBERS[field]}))


def test_kl14_a_number_is_the_only_problem(make_skin):
    assert problems_of(make_skin(how_points_earn=NUMBERS["how_points_earn"])) == ("how_points_earn: number",)


def test_kl14_one_problem_a_field_after_its_words(make_skin, clean):
    skin = make_skin(tool_text="Send 3 loaves, then check the other 12.")
    assert problems_of(skin) == ("tool_text: check", "tool_text: number")


@pytest.mark.parametrize("text", ["They add up to 100.", "100% of the bread", "Send all 100, or ten each."])
def test_kl14_the_budget_and_number_words_pass(text, make_skin, clean):
    assert lint(make_skin(tool_text=clean["tool_text"] + " " + text)) is None


def test_kl14_a_number_in_the_name_alone_passes(make_skin):
    assert lint(make_skin(name="bakery2")) is None


def test_kl14_lint_text_ignores_numbers():
    assert lint_text("In 1987 we sent 12 loaves.") == ()
