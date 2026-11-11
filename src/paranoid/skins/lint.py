"""The lint every word the model reads passes through. See docs/specs/skins/lint.md.

Problems name fields, indexes and entries, never the skin's text, so a failure is safe in a CI log.
"""

import itertools
import unicodedata
from dataclasses import fields

from .canary import CANARY
from .render import render_system_prompt
from .skin import Skin, SkinError

# Word starts, in the order of the table in docs/harness/prompts.md#banned-words.
BANNED_WORDS: tuple[str, ...] = (
    "check",
    "chang",
    "shift",
    "switch",
    "shock",
    "drift",
    "trend",
    "anomal",
    "regime",
    "climat",
    "detect",
    "monitor",
    "watch",
    "alert",
    "stabl",
    "stabil",
    "volatil",
    "benchmark",
    "canar",
    "paranoi",
)
PREFIXES: tuple[str, ...] = ("un", "in", "de", "re", "non")
WHOLE_NUMBER_PHRASES: tuple[str, ...] = ("whole number", "integer")
PERCENT_PHRASES: tuple[str, ...] = ("percent", "per cent", "%")
BUDGET = "100"  # the one number a skin may write in digits, see docs/specs/skins/lint.md#numbers

GUID = CANARY.split("canary GUID ", 1)[1]
# The fields checked for the GUID on their own, beside the rendered prompt, see docs/specs/skins/lint.md#canary.
CANARY_FIELDS = (
    "tool_text",
    "bets_name",
    "bets_text",
    "bad_call",
    "no_call",
    "notes_name",
    "notes_text",
    "notes_param",
    "notes_param_text",
    "compute_name",
    "compute_text",
    "compute_param",
    "compute_param_text",
    "question",
    "round_word",
    "bet_word",
    "reading_word",
)


class LintError(SkinError):
    """A skin that fails the lint. `problems` holds every failure, in the order found."""

    def __init__(self, skin: str, problems: tuple[str, ...]) -> None:
        self.skin = skin
        self.problems = tuple(problems)
        super().__init__(f"Skin {skin} failed lint: {'; '.join(self.problems)}")


def lint_text(text: str) -> tuple[str, ...]:
    """Each banned entry some word starts with, as is or after one prefix, in text order, each once."""
    hits: dict[str, None] = {}
    for is_word, letters in itertools.groupby(fold(text), str.isalpha):
        if is_word:
            entry = banned_entry("".join(letters))
            if entry is not None:
                hits[entry] = None
    return tuple(hits)


def fold(text: str) -> str:
    """NFKC then casefold, so fullwidth letters and ligatures are plain lowercase, see docs/specs/skins/lint.md#words."""
    return unicodedata.normalize("NFKC", text).casefold()


def banned_entry(word: str) -> str | None:
    """The first entry the word starts with as is, else after one prefix is removed, else None."""
    candidates = [word, *(word[len(prefix) :] for prefix in PREFIXES if word.startswith(prefix))]
    for candidate in candidates:
        for entry in BANNED_WORDS:
            if candidate.startswith(entry):
                return entry
    return None


def lint(skin: Skin) -> None:
    """Raise one LintError listing every problem: fields, then frame facts, then the canary."""
    problems = [*field_problems(skin), *frame_problems(skin), *canary_problems(skin)]
    if problems:
        raise LintError(skin.name, tuple(problems))


def field_problems(skin: Skin) -> list[str]:
    """`<field>: <entry>` for every banned word, then `<field>: number`, for every field the model reads, in order."""
    texts: list[tuple[str, str]] = []
    for field in fields(Skin):
        if field.name == "channels":
            texts += [(f"channels[{i}]", name) for i, name in enumerate(skin.channels)]
        elif field.name != "name":  # the model never reads the name
            texts.append((field.name, getattr(skin, field.name)))
    problems = []
    for label, text in texts:
        problems += [f"{label}: {entry}" for entry in lint_text(text)]
        if has_number(text):
            problems.append(f"{label}: number")
    return problems


def has_number(text: str) -> bool:
    """Whether the text holds a run of digits other than the budget."""
    runs = ("".join(digits) for is_digit, digits in itertools.groupby(text, str.isdigit) if is_digit)
    return any(run != BUDGET for run in runs)


def frame_problems(skin: Skin) -> list[str]:
    """The frame facts the rendered prompt must state, see docs/specs/skins/lint.md#frame-facts."""
    prompt = render_system_prompt(skin)
    lowered = prompt.lower()
    problems = []
    if not any(phrase in lowered for phrase in PERCENT_PHRASES):
        problems.append("missing: percent")
    if BUDGET not in prompt:
        problems.append("missing: 100")
    problems += [f"missing: channels[{i}]" for i, name in enumerate(skin.channels) if name not in prompt]
    if not any(phrase in lowered for phrase in WHOLE_NUMBER_PHRASES):
        problems.append("missing: whole numbers")
    if skin.tool_name not in prompt:
        problems.append("missing: tool name")
    return problems


def canary_problems(skin: Skin) -> list[str]:
    """The canary GUID in the rendered prompt, then in each other field the model reads."""
    problems = ["canary in prompt"] if GUID in render_system_prompt(skin) else []
    return problems + [f"canary in {field}" for field in CANARY_FIELDS if GUID in getattr(skin, field)]
