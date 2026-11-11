"""KH1 to KH3, see docs/specs/skins/tests.md#property-tests."""

import re

from hypothesis import given, settings
from hypothesis import strategies as st

from paranoid.baselines import uniform
from paranoid.engine import SCENARIOS, make_timeline, play
from paranoid.skins import BANNED_WORDS, PREFIXES, lint_text, render_record

FAST = settings(max_examples=40, deadline=None)

# Words near the banned entries, so a draw hits some, plus random letters.
NEAR = [p + e + s for e in BANNED_WORDS for p in ("", *PREFIXES, "s", "x") for s in ("", "s", "ed", "ing")]
words = st.one_of(st.sampled_from(NEAR), st.text(st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEZ"), min_size=1))
texts = st.lists(st.tuples(words, st.sampled_from([" ", ", ", ". ", "'", "-", "; ", "!"]))).map(
    lambda pairs: "".join(word + gap for word, gap in pairs)
)


def hits(word: str, entry: str) -> bool:
    """The spec's rule, written apart from the code: the word starts with the entry, or with a prefix and then it."""
    return any(word.startswith(start + entry) for start in ("", *PREFIXES))


@FAST
@given(text=texts)
def test_kh1_every_entry_found_is_banned_and_starts_a_word(text):
    found = re.findall(r"[a-z]+", text.lower())
    for entry in lint_text(text):
        assert entry in BANNED_WORDS
        assert any(hits(word, entry) for word in found)


@FAST
@given(text=texts.filter(lambda t: not any(hits(w, e) for w in re.findall(r"[a-z]+", t.lower()) for e in BANNED_WORDS)))
def test_kh2_a_text_with_no_banned_start_is_clean(text):
    assert lint_text(text) == ()


@FAST
@given(
    seed=st.integers(min_value=0, max_value=2**64 - 1),
    name=st.sampled_from(list(SCENARIOS)),
    rounds=st.integers(0, 40),
)
def test_kh3_one_line_per_round_and_the_header(seed, name, rounds, example):
    record = play(uniform, make_timeline(SCENARIOS[name], seed), max_rounds=rounds)
    assert render_record(example, record).count("\n") == len(record) + 1
