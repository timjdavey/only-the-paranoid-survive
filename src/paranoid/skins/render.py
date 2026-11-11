"""The system prompt, the record as CSV, and prompt_hash. See docs/specs/skins/render.md.

The renderer joins a skin's own words and never writes one of its own.
"""

import hashlib
import json

from paranoid.engine import Record

from .skin import Skin, header_words

# Goes up by one when the layout of either text changes, see docs/specs/skins/render.md#prompt-hash.
RENDER_VERSION = 1

PROMPT_PARTS = ("intro", "rules", "how_points_earn", "ask")
# Every field the model reads apart from the system prompt and channels, see docs/specs/skins/render.md#prompt-hash.
HASHED_FIELDS = (
    "tool_name",
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


def render_system_prompt(skin: Skin) -> str:
    """The four prompt parts joined by one blank line."""
    return "\n\n".join(getattr(skin, part) for part in PROMPT_PARTS)


def render_record(skin: Skin, record: Record) -> str:
    """The header, then one row per round played. Every line ends with a newline."""
    channels = len(skin.channels)
    lines = [",".join(header_words(skin))]
    for row in record.rows:
        if len(row.bets) != channels or len(row.readings) != channels:
            raise ValueError(
                f"round {row.round} has {len(row.bets)} bets and {len(row.readings)} readings, "
                f"but the skin has {channels} channels"
            )
        cells = [str(row.round), *(str(bet) for bet in row.bets), *(reading_cell(r) for r in row.readings)]
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def reading_cell(reading: float | None) -> str:
    """One decimal, an empty field for None, and never -0.0."""
    if reading is None:
        return ""
    text = f"{reading:.1f}"
    return "0.0" if text == "-0.0" else text


def prompt_hash(skin: Skin) -> str:
    """The first 12 hex characters of the SHA-256 of every word the model reads, and RENDER_VERSION."""
    covered = {field: getattr(skin, field) for field in HASHED_FIELDS}
    covered |= {"render_version": RENDER_VERSION, "system": render_system_prompt(skin), "channels": list(skin.channels)}
    canonical = json.dumps(covered, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
