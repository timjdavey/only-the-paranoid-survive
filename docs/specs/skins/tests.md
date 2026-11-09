# Tests

Every test the skins suite runs, in `tests/skins/`. They need no model, no network and no inspect, see [layout](../../harness/layout.md#four-layers). Records come from `paranoid.engine`, so a test may call `play` and `make_tape` on public seeds. Where a test needs a skin that fails, it builds a `Skin` by hand or writes a TOML file to `tmp_path`, so no bad skin is checked in.

## Skin

| Id | Test | Page |
|---|---|---|
| S1 | `load_skins()` with `PARANOID_SKINS` unset returns a mapping with the one key `example`, whose `name` is `example`, and assigning to it raises `TypeError` | [skin](skin.md#load_skins) |
| S2 | `prompt_hash(load_skins()["example"])` equals a pinned string. Changing the pinned string is a reviewed change | [skin](skin.md#the-example-skin) |
| S3 | A `Skin` with each bad value raises `SkinError`, one case per clause: a `name` with a capital, an empty `intro`, nine channels, eleven channels, a name with a comma, two names equal ignoring case, a `tool_name` with a space and a `tool_name` of 65 characters | [skin](skin.md#validation-on-construction) |
| S4 | A field given as `"  text\r\n"` is stored as `"text"`, and two skins differing only in such whitespace are equal with equal hashes | [skin](skin.md#validation-on-construction) |
| S5 | A TOML file missing a key, with an unknown key, with `channels` as a string, or with `intro` as an integer raises `SkinError` whose message names the key and the file | [skin](skin.md#the-toml-file) |
| S6 | A file `other.toml` with `name = "example"` raises `SkinError` for the stem mismatch | [skin](skin.md#the-toml-file) |
| S7 | A file that is not valid TOML, and a path that does not exist, raise `SkinError` with the path in the message | [skin](skin.md#load_skin) |
| S8 | A folder with two clean skins and a `notes.txt`: `load_skins(folder)` returns three skins, `example` included, keys sorted, and ignores the text file. A subfolder holding a skin is not walked | [skin](skin.md#load_skins) |
| S9 | A folder holding `example.toml` raises `SkinError` for the duplicate name, as do two files with one `name` | [skin](skin.md#load_skins) |
| S10 | With `PARANOID_SKINS` set to a folder, `load_skins()` reads it. Set to `""`, it reads nothing. With both the variable and `path` given, `path` wins | [skin](skin.md#load_skins) |
| S11 | `load_skins(path)` on a missing folder, or on a file, raises `SkinError` | [skin](skin.md#load_skins) |
| S12 | A skin file with a banned word in `rules` raises `LintError`, not `SkinError`, and the file does not appear in `load_skins(folder)` | [skin](skin.md#load_skin) |
| S13 | The skins package imports nothing outside `paranoid.engine` and the standard library, checked by walking `sys.modules` after import | [skin](skin.md#invariants) |

## Render

| Id | Test | Page |
|---|---|---|
| R1 | `render_system_prompt` of a hand-built skin equals a pinned string: four parts joined by `"\n\n"`, `how_points_earn` and `reading_note` joined by one space, no leading or trailing whitespace | [render](render.md#system-prompt) |
| R2 | `render_system_prompt(example)` equals a pinned string. The example skin's wording never changes once played | [render](render.md#system-prompt) |
| R3 | `render_system_prompt` called twice gives equal strings, and a subprocess gives the same | [render](render.md#system-prompt) |
| R4 | `render_record(skin, Record())` is one line holding each channel name as `<name>_bet` and `<name>_level`, in index order, and ends with `\n` | [render](render.md#record) |
| R5 | `render_record` on `play(uniform, make_tape(SCENARIOS["no_change"], 0), max_rounds=3)` has four lines and equals `record.to_csv(skin.channels)` | [render](render.md#record) |
| R6 | `render_record` on a record from a hand-built four-channel tape raises `ValueError` | [render](render.md#record) |
| R7 | `prompt_hash` is 12 lowercase hex characters. Replacing each covered field with a different value changes it, replacing `name` does not | [render](render.md#prompt-hash) |
| R8 | `prompt_hash` of a skin with a non-ASCII channel name equals a pinned string, so the JSON canonical form is fixed | [render](render.md#prompt-hash) |

## Lint

| Id | Test | Page |
|---|---|---|
| L1 | `lint_text` on each word in the table's "also catches" column returns its entry. `established`, `exchange`, `cheque` and `swatch` return `()` | [lint](lint.md#words) |
| L2 | `lint_text("Check the CHECKS, then check again")` returns `("check",)`, one entry once, and `lint_text("")` returns `()` | [lint](lint.md#words) |
| L3 | `lint_text` on a text with three different banned words returns them in text order | [lint](lint.md#words) |
| L4 | Every entry in `BANNED_WORDS` is lowercase letters only, and the tuple equals the pinned list from the table | [lint](lint.md#words) |
| L5 | A skin with a banned word in each field in turn, channel names and `tool_name` included, raises `LintError` whose `problems` holds `"<field>: <entry>"`, with `channels[3]` for the fourth name | [lint](lint.md#fields) |
| L6 | A skin whose text omits `100`, omits one channel name, says neither `whole number` nor `integer`, or omits the tool name raises `LintError` with the matching `missing:` problem, one case each | [lint](lint.md#frame-facts) |
| L7 | A skin that puts the ten names in `intro` and the tool name in `rules` passes, as the facts are checked on the whole prompt | [lint](lint.md#frame-facts) |
| L8 | `Whole Numbers` and `integers` both satisfy the whole-numbers fact | [lint](lint.md#frame-facts) |
| L9 | A skin whose `ask` contains the canary GUID raises `LintError` with `canary in prompt` | [lint](lint.md#frame-facts) |
| L10 | A skin with two banned words and a missing fact raises once, with three problems in field order then fact order, and `str(error)` starts `Skin <name> failed lint: ` | [lint](lint.md#raising) |
| L11 | `lint(example)` returns `None`, and `lint_text` of every text field of the example skin is `()` | [lint](lint.md#invariants) |
| L12 | For every skin in `load_skins()`, `lint_text(render_record(skin, record))` is `()` on a played record, and `CANARY` is not in `render_system_prompt(skin)`. With `PARANOID_SKINS` set this covers the held-out skins on the machine that has them | [lint](lint.md#invariants) |
| L13 | `CANARY` equals the line in [contamination](../../harness/contamination.md#canary), with no trailing newline. The first line of `example.toml` is a comment containing it, and `docs/harness/prompts.md` contains it | [lint](lint.md#canary) |

## Property tests

With `hypothesis`, kept fast with a small example count.

| Id | Test |
|---|---|
| H1 | For any text of letters, spaces and punctuation, every entry `lint_text` returns is in `BANNED_WORDS`, and some word in the lowercased text starts with it |
| H2 | For any text with no banned entry at the start of any word, `lint_text` returns `()` |
| H3 | For any valid record from `play(uniform, tape)` on a public seed, `render_record(example, record).count("\n") == len(record) + 1` |

## Open

- Whether to run L12 in CI against a private checkout, or on the maintainers' machines only. Held-out skins never reach CI today, see [who can see them](../../harness/contamination.md#who-can-see-them).
