# Tests

Every test the skins suite runs, in `tests/skins/`. Ids start `K` for skins, then the page's letter, see [test ids](../README.md#rules). They need no model, no network and no inspect, see [layout](../../harness/layout.md#five-layers). Records come from `paranoid.engine`, with `uniform` from `paranoid.baselines`, so a test may call `play(uniform, make_timeline(...))` on public seeds. Where a test needs a skin that fails, it builds a `Skin` by hand or writes a TOML file to `tmp_path`, so no bad skin is checked in.

- **A test over held-out skins never prints their text.** With `PARANOID_SKINS` set, pytest would show both sides of a failed assertion in a CI log. Those tests fail with `pytest.fail` and the skin's name only, see [who can see them](../../harness/contamination.md#who-can-see-them).

## Skin

| Id | Test | Page |
|---|---|---|
| KS1 | `load_skins()` with `PARANOID_SKINS` unset returns a mapping with the one key `example`, whose `name` is `example`, and assigning to it raises `TypeError` | [skin](skin.md#load_skins) |
| KS2 | `prompt_hash(load_skins()["example"])` equals a pinned string. Changing the pinned string is a reviewed change | [skin](skin.md#the-example-skin) |
| KS3 | A `Skin` with each bad value raises `SkinError`, one case per clause: a `name` with a capital, an empty `intro`, three channels, a name with a comma, a `bet_word` with a comma, an empty `reading_word`, two names equal ignoring case, a `tool_name` with a space, a `tool_name` of 65 characters, a `bets_name` with a capital and a `notes_name` equal to `tool_name`. A `bets_name` equal to `tool_name` builds | [skin](skin.md#validation-on-construction) |
| KS4 | A field given as `"  text  \r\nmore \r"` is stored as `"text\nmore"`, `channels` given as a list is stored as a tuple, and a name spelled in NFD equals the same name in NFC. Two skins differing only in such whitespace or form are equal with equal hashes | [skin](skin.md#validation-on-construction) |
| KS5 | A TOML file missing a key, with an unknown key, with a `name` key, with `channels` as a string, or with `intro` as an integer raises `SkinError` whose message names the key and the file | [skin](skin.md#the-toml-file) |
| KS6 | `load_skin` on `rome.toml` gives a skin named `rome`. `Rome.toml` and `1x.toml` raise `SkinError` for the stem | [skin](skin.md#the-toml-file) |
| KS7 | A file that is not valid TOML, and a path that does not exist, raise `SkinError` with the path in the message | [skin](skin.md#load_skin) |
| KS8 | A folder with two clean skins and a `notes.txt`: `load_skins(folder)` returns three skins, `example` included, keys sorted, and ignores the text file. A subfolder holding a skin is not walked | [skin](skin.md#load_skins) |
| KS9 | A folder holding `example.toml` raises `SkinError` for the duplicate name | [skin](skin.md#load_skins) |
| KS10 | With `PARANOID_SKINS` set to a folder, `load_skins()` reads it. Set to `""`, it reads nothing. With both the variable and `path` given, `path` wins | [skin](skin.md#load_skins) |
| KS11 | `load_skins(path)` on a missing folder, or on a file, raises `SkinError` | [skin](skin.md#load_skins) |
| KS12 | A folder with one clean skin and one with a banned word in `rules`: `load_skins(folder)` raises `LintError`, which is a `SkinError`, naming the bad file. `load_skin` on the bad file raises `LintError` and not a plain `SkinError` | [skin](skin.md#load_skins) |
| KS13 | In a subprocess that imports `paranoid.skins` and nothing else, `sys.modules` holds no top-level package outside `paranoid`, numpy and the standard library | [skin](skin.md#invariants) |

## Render

| Id | Test | Page |
|---|---|---|
| KR1 | `render_system_prompt` of a hand-built skin equals a pinned string: four fields joined by `"\n\n"`, no leading or trailing whitespace | [render](render.md#system-prompt) |
| KR2 | `render_system_prompt(example)` equals a pinned string. The example skin's wording never changes once played | [render](render.md#system-prompt) |
| KR3 | `render_system_prompt` called twice gives equal strings, and a subprocess gives the same | [render](render.md#system-prompt) |
| KR4 | `render_record(skin, Record())` is one line holding each channel name as `<name>_<bet_word>` then `<name>_<reading_word>`, in index order, after `round_word`, with no column after the last reading, and ends with `\n` | [render](render.md#record) |
| KR5 | `render_record` on `play(uniform, make_timeline(SCENARIOS["no_change"], 0), max_rounds=3)` has four lines. Each row's bets are ints, its readings have exactly one decimal, and it has `1 + 2 × channels` fields, so no output | [render](render.md#record) |
| KR6 | `render_record` with the example skin on a record from a hand-built four-channel timeline raises `ValueError` from the skins layer | [render](render.md#record) |
| KR7 | `prompt_hash` is 12 lowercase hex characters. Replacing each covered field with a different value changes it, the three column words and the four notes and compute fields included, replacing `name` does not, and patching `RENDER_VERSION` to 2 changes it | [render](render.md#prompt-hash) |
| KR8 | `prompt_hash` of a skin with a non-ASCII channel name equals a pinned string, so the JSON canonical form is fixed | [render](render.md#prompt-hash) |
| KR9 | `render_record` on a fixed two-round record with a hand-built four-channel skin equals a pinned string, byte for byte, with one trailing newline per row and the header | [render](render.md#record) |
| KR10 | A reading of `-0.0` renders as `0.0`, a `None` reading renders as an empty field, a bet renders with no decimal, and a three-row record renders four lines | [render](render.md#record) |

## Lint

| Id | Test | Page |
|---|---|---|
| KL1 | `lint_text` on each word in the table's "also catches" column returns its entry, `undetected`, `unchecked`, `destabilised` and `detrended` included. `established`, `exchange`, `research`, `cheque` and `swatch` return `()` | [lint](lint.md#words) |
| KL2 | `lint_text("Check the CHECKS, then recheck again")` returns `("check",)`, one entry once, and `lint_text("")` returns `()` | [lint](lint.md#words) |
| KL3 | `lint_text` on a text with three different banned words returns them in text order | [lint](lint.md#words) |
| KL4 | Every entry in `BANNED_WORDS` and `PREFIXES` is lowercase letters only, no entry in `BANNED_WORDS` is a prefix of another, and the four tuples `BANNED_WORDS`, `PREFIXES`, `WHOLE_NUMBER_PHRASES` and `PERCENT_PHRASES` equal pinned lists | [lint](lint.md#words) |
| KL5 | A skin with a banned word in each field the model reads in turn, channel names, the three tool names, `bets_name`, `notes_text`, `compute_text` and the three column words included, raises `LintError` whose `problems` holds `"<field>: <entry>"`, with `channels[3]` for the fourth name. A banned word in `name` alone passes | [lint](lint.md#fields) |
| KL6 | A skin whose text says none of `percent`, `per cent` and `%`, omits `100`, omits one channel name, says neither `whole number` nor `integer`, or omits the tool name raises `LintError` with the matching `missing:` problem, one case each | [lint](lint.md#frame-facts) |
| KL7 | A skin that puts the ten names in `intro` and the tool name in `rules` passes, as the facts are checked on the whole prompt | [lint](lint.md#frame-facts) |
| KL8 | `Whole Numbers` and `integers` both satisfy the whole-numbers fact. `Percentages`, `per cent` and `%` each satisfy the percent fact | [lint](lint.md#frame-facts) |
| KL9 | A skin whose `ask` contains the canary GUID raises `LintError` with `canary in prompt`. One whose `tool_text` contains it raises with `canary in tool_text`, one whose `compute_text` contains it with `canary in compute_text`, and one whose `reading_word` is the GUID raises with `canary in reading_word` | [lint](lint.md#canary) |
| KL10 | A skin with two banned words, a missing fact and the GUID in `question` raises once, with four problems in field order, then fact, then canary, and `str(error)` starts `Skin <name> failed lint: ` and holds none of the skin's text | [lint](lint.md#raising) |
| KL11 | `lint(example)` returns `None`, and `lint_text` of every text field of the example skin is `()` | [lint](lint.md#invariants) |
| KL12 | For every skin in `load_skins()`, `lint_text(render_record(skin, record))` is `()` on a played record, and the canary GUID is in none of the texts the model reads. With `PARANOID_SKINS` set this covers the held-out skins on the machine that has them, and fails with the skin's name only | [lint](lint.md#invariants) |
| KL13 | `CANARY` equals the line in [contamination](../../harness/contamination.md#canary), with no trailing newline. The first line of `example.toml` is a comment containing it, and `docs/harness/prompts.md` contains it | [lint](lint.md#canary) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| KH1 | For any text of letters, spaces and punctuation, every entry `lint_text` returns is in `BANNED_WORDS`, and some word in the lowercased text starts with it, as is or after one prefix is removed |
| KH2 | For any text with no banned entry at the start of any word, as is or after one prefix is removed, `lint_text` returns `()` |
| KH3 | For any valid record from `play(uniform, timeline)` on a public seed, `render_record(example, record).count("\n") == len(record) + 1` |

## Not decided

- Whether to run KL12 in CI against a private checkout, or on the maintainers' machines only. Held-out skins never reach CI today, see [who can see them](../../harness/contamination.md#who-can-see-them).

## Waiting on the example skin

- KS2, KR2, KL11 and KL13 pin or lint the bytes of `example.toml`, which is [coming](skin.md#the-example-skin). They are written when the file lands, and its `prompt_hash` is pinned then. Every other test here builds its own skin by hand and can be written now.
