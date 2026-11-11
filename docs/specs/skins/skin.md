# Skin

## Purpose

`Skin` holds one skin: the channel names and every piece of text the agent reads, the record's column words included. `load_skin` reads one from a TOML file and lints it. `load_skins` gathers the example skin and every held-out skin into one mapping by name. What each field is for is in [skins](../../harness/skins.md#what-a-skin-file-holds), and where each lands in the prompt is in [prompts](../../harness/prompts.md#system-prompt).

## Interface

```python
@dataclass(frozen=True)
class Skin:
    name: str                               # short id, the file stem. Goes in log metadata, never to the model
    channels: tuple[str, ...]               # one name per channel, in channel index order. Ten in the example skin
    intro: str                              # who the agent is and what it runs
    rules: str                              # the channels by name, the split in whole percentages adding up to 100
    how_points_earn: str                    # what a percent of the budget buys, what a reading means, a small spend gives a rough reading
    ask: str                                # the record is below, place this round's points with the tool
    tool_name: str                          # the tool's name as the model sees it
    tool_text: str                          # the tool's description
    bets_name: str                          # the name of the tool's one parameter. "bets" in the example skin
    bets_text: str                          # the description of the tool's one parameter, one bet per channel
    bad_call: str                           # the retry message for bets the engine rejects. One message, no slots
    no_call: str                            # the retry message for a reply with no tool call
    notes_name: str                         # the notes tool's name as the model sees it
    notes_text: str                         # the notes tool's description
    compute_name: str                       # the compute tool's name as the model sees it
    compute_text: str                       # the compute tool's description
    question: str                           # Jev's choice question, see providers
    round_word: str                         # the record's first column header. "round" in the example skin
    bet_word: str                           # the suffix of each bet column. "bet" in the example skin
    reading_word: str                       # the suffix of each reading column. "reading" in the example skin

class SkinError(ValueError): ...            # a skin file or a Skin that is not well formed. LintError is one too

def load_skin(path: Path) -> Skin
def load_skins(path: Path | None = None) -> Mapping[str, Skin]
```

- **Every field is a `str`** except `channels`, which is a tuple of names. There are no numbers on a skin, see [conventions](README.md#conventions).
- **The fields are the parts of the prompt**, one each, in the order the [system prompt](../../harness/prompts.md#system-prompt) uses them, then the names and text of the three tools, then the three column words of the [record](render.md#record). Adding a part to the prompt means adding a field here, a key to every skin file, and a row to [skins](../../harness/skins.md#what-a-skin-file-holds).

## Behaviour

### Validation on construction

`__post_init__` normalises, then raises `SkinError` if any of these hold. Lint is separate, see [lint](lint.md), so a test can build a skin that fails lint.

- **Normalise first.** Every `str` field and every channel name has `\r\n` and `\r` replaced by `\n`, trailing whitespace removed from every line, Unicode normalised to NFC, then leading and trailing whitespace stripped. `channels` is stored as a `tuple` whatever sequence was passed. The stored values are the normalised ones, so one file hashes the same on every OS and in every editor, and two spellings of one accented name are one name.
- `name` does not match `^[a-z][a-z0-9_]*$`.
- Any `str` field is empty after stripping.
- `channels` has fewer than four entries, the engine's floor, see [config](../engine/config.md#fields). The example skin has ten, as the frozen study config does. Whether a skin's count matches its config is checked when the task is built, see [task settings](../harness/task.md#task-settings).
- Any channel name or column word is empty, or contains `,`, `"` or `\n`. Each is a word in the record's header, and any of those characters would add a column or a row to the CSV the agent reads, see [record](render.md#record). So a bad word fails here and never mid-run.
- Two channel names are equal ignoring case.
- `tool_name`, `notes_name` or `compute_name` does not match `^[a-z][a-z0-9_]{0,63}$`, or two of the three are equal. Every provider accepts a name of that shape, and needs the three to differ.
- `bets_name` does not match the same pattern. It is a key in the tool's JSON schema, so it has a tool name's shape. It may equal a tool name, as a parameter and a tool never share a namespace.

### The TOML file

One file per skin, one table, no nesting.

- **Every field of `Skin` but `name` is a top-level key** of the same name. `channels` is an array of strings, one per channel, every other key a string. Multi-line strings use TOML's `"""` form.
- **Every key is required.** A missing key, an unknown key, or a value of the wrong type raises `SkinError` naming the key. So a typo in a key name fails on load rather than silently dropping a part of the prompt.
- **`name` is the file stem.** `example.toml` is the skin `example`. There is no `name` key, so a file cannot disagree with its own name. A stem that fails the `name` pattern, such as `Rome.toml`, raises `SkinError`.
- **Comments are free.** The example skin's first line is a comment holding the [canary](lint.md#canary). Held-out skins carry it too, so a file that ever leaks is filtered, see [writing a skin](../../harness/writing-a-skin.md#before-you-start).
- **No templating.** A skin writes the channel names, the number 100 and its tool names into its own text. The renderer concatenates and never substitutes, see [render](render.md). The [lint](lint.md#frame-facts) checks the text and the `channels` list agree.

### `load_skin`

- **`load_skin(path)`** reads the file with `tomllib`, builds a `Skin` with the stem as `name`, calls `lint(skin)`, and returns it.
- **Errors in order.** A file that does not exist or is not valid TOML raises `SkinError` with the path. Then the key checks above. Then `Skin`'s own validation, the stem included. Then `LintError` from the lint. Each names the file.

### `load_skins`

- **The example skin always loads**, from `example.toml` beside the code, as package data.
- **Then the held-out folder**, if there is one. `path` when given, else the folder `PARANOID_SKINS` names, else nothing. `PARANOID_SKINS` set to an empty string counts as unset. A `path` given explicitly wins over the variable.
- **A folder that does not exist or is not a directory** raises `SkinError`.
- **Every file in the folder whose name ends `.toml`** is loaded with `load_skin`, in sorted filename order. Other files are ignored, subfolders are not walked. The private repo keeps `skins/` a plain folder of TOML files, see [skins](../../harness/skins.md#where-skins-live).
- **One bad file fails the call.** `load_skins` raises the `SkinError` or `LintError` the first bad file raises, naming it. It never skips a file, so a held-out skin that fails to lint is never quietly left out of a run.
- **Names are unique.** A held-out skin named `example` raises `SkinError`. Two files cannot share a stem, so that is the one way to clash.
- **Held-out names are opaque.** A skin's name is published in every results table, see [contamination](../../harness/contamination.md#public-and-held-out), so a held-out skin is a colour such as `amber`, never a word from its story, see [writing a skin](../../harness/writing-a-skin.md#before-you-start). The lint cannot check this, so a reviewer does.
- **The result is a `types.MappingProxyType`**, keys in sorted order, so the harness cannot swap a skin under a name that is already in a log.
- **The harness picks by name.** The `skin` task arg defaults to `example`, see [running](../../harness/running.md#commands). A name not in the mapping is a harness error, not a skins one.

### The example skin

- **Lives at `src/paranoid/skins/example.toml`** and is the one skin in this repo, see [where skins live](../../harness/skins.md#where-skins-live).
- **The file is coming.** Its story and words are being written and will be added to this repo as `example.toml`. Until then [prompts](../../harness/prompts.md#system-prompt) shows the shape with brackets where the story goes, and the tests that pin its bytes, KS2, KR2, KL11 and KL13, wait on it, see [tests](tests.md#waiting-on-the-example-skin).
- **Its wording is the wording in [prompts](../../harness/prompts.md)**, and only its wording is published. A held-out skin words the frame its own way, see [contamination](../../harness/contamination.md#why).
- **Its text never changes once a headline run has played it**, see [CONTRIBUTING](../../../CONTRIBUTING.md#what-never-changes-without-a-new-pilot). The test suite pins its `prompt_hash`, so a change is a reviewed change, see [tests](tests.md#skin).

## Invariants

- Every `str` field on a built `Skin` is non-empty, stripped, in NFC, free of `\r`, and has no trailing whitespace on any line.
- `len(skin.channels) >= 4`, `skin.channels` is a `tuple`, every name and column word is CSV safe, and no two names are equal ignoring case.
- `load_skins()` always contains `"example"`, and `load_skins()["example"].name == "example"`.
- Every skin `load_skins` returns has passed `lint`.
- A `Skin` is immutable. Two skins built from the same file are equal and hash alike.
- The skins layer imports nothing outside `paranoid.engine` and the standard library.

## Not decided

- **Whether a skin should carry what a round stands for** as its own field, so the pilot can swap "week" for "minute" on one engine, see [future](../../design/future.md). Decide when the pilot asks for a second unit.
- **Whether to pilot the reading note.** `how_points_earn` ends with the line that a small spend gives a rough reading. A pilot cell that drops it to see whether the agent still explores needs a second TOML file with the line cut, not a field of its own.
