"""Skin and SkinError. See docs/specs/skins/skin.md.

No error message holds a skin's text, only field names and indexes, so a held-out skin that fails is safe to log.
"""

import re
import unicodedata
from dataclasses import dataclass, fields

NAME = re.compile(r"[a-z][a-z0-9_]*")
TOOL_NAME = re.compile(r"[a-z][a-z0-9_]{0,63}")
COLUMN_WORDS = ("round_word", "bet_word", "reading_word")
TOOL_NAMES = ("tool_name", "notes_name", "compute_name")
PARAM_NAMES = ("bets_name", "notes_param", "compute_param")  # one per tool, each a key in its JSON schema
CSV_BREAKERS = {",": "a comma", '"': "a double quote", "\n": "a newline"}
MIN_CHANNELS = 4  # the engine's floor, see docs/specs/engine/config.md#fields


class SkinError(ValueError):
    """A skin file or a Skin that is not well formed. LintError is one too."""


@dataclass(frozen=True)
class Skin:
    name: str
    channels: tuple[str, ...]
    intro: str
    rules: str
    how_points_earn: str
    ask: str
    tool_name: str
    tool_text: str
    bets_name: str
    bets_text: str
    bad_call: str
    no_call: str
    notes_name: str
    notes_text: str
    notes_param: str
    notes_param_text: str
    compute_name: str
    compute_text: str
    compute_param: str
    compute_param_text: str
    question: str
    round_word: str
    bet_word: str
    reading_word: str

    def __post_init__(self) -> None:
        for field in TEXT_FIELDS:
            object.__setattr__(self, field, normalise(getattr(self, field), field))
        if isinstance(self.channels, str):
            raise SkinError("channels must be a sequence of names, not one string")
        try:
            channels = tuple(self.channels)
        except TypeError:
            raise SkinError("channels must be a sequence of names") from None
        object.__setattr__(self, "channels", tuple(normalise(c, f"channels[{i}]") for i, c in enumerate(channels)))
        self._validate()

    def _validate(self) -> None:
        if not NAME.fullmatch(self.name):
            raise SkinError("name must be lowercase letters, digits and underscores, starting with a letter")
        for field in TEXT_FIELDS:
            if not getattr(self, field):
                raise SkinError(f"{field} is empty")
        if len(self.channels) < MIN_CHANNELS:
            raise SkinError(f"channels has {len(self.channels)} names, fewer than {MIN_CHANNELS}")
        words = {f"channels[{i}]": c for i, c in enumerate(self.channels)} | {f: getattr(self, f) for f in COLUMN_WORDS}
        for label, word in words.items():
            if not word:
                raise SkinError(f"{label} is empty")
            for char, what in CSV_BREAKERS.items():
                if char in word:
                    raise SkinError(f"{label} holds {what}, which would break the record's CSV")
        seen: dict[str, int] = {}
        for i, channel in enumerate(self.channels):
            key = channel.casefold()
            if key in seen:
                raise SkinError(f"channels[{seen[key]}] and channels[{i}] are equal ignoring case")
            seen[key] = i
        for field in (*TOOL_NAMES, *PARAM_NAMES):
            if not TOOL_NAME.fullmatch(getattr(self, field)):
                raise SkinError(f"{field} must be 1 to 64 lowercase letters, digits and underscores, from a letter")
        if len({getattr(self, field) for field in TOOL_NAMES}) < len(TOOL_NAMES):
            raise SkinError("tool_name, notes_name and compute_name must all differ")


def normalise(value: object, label: str) -> str:
    """`\\n` newlines, no trailing whitespace on any line, NFC, then stripped."""
    if not isinstance(value, str):
        raise SkinError(f"{label} must be a str, got {type(value).__name__}")
    lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return unicodedata.normalize("NFC", "\n".join(line.rstrip() for line in lines)).strip()


# Every str field, in field order. channels is the one field that is not a str.
TEXT_FIELDS = tuple(f.name for f in fields(Skin) if f.name != "channels")
