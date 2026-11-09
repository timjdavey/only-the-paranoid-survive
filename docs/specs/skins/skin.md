# Skin

## Purpose

`Skin` holds one skin: the ten channel names and every piece of text the agent reads. `load_skin` reads one from a TOML file and lints it. `load_skins` gathers the example skin and every held-out skin into one mapping by name. What each field is for is in [skins](../../harness/skins.md#what-a-skin-file-holds), and where each lands in the prompt is in [prompts](../../harness/prompts.md#system-prompt).

## Interface

```python
@dataclass(frozen=True)
class Skin:
    name: str                               # short id. Equals the file stem, goes in log metadata
    channels: tuple[str, ...]               # ten names, in channel index order
    intro: str                              # who the agent is and what it runs
    rules: str                              # the budget of 100, the ten channels by name, whole numbers adding up to 100
    how_points_earn: str                    # what a point buys and what a reading means
    reading_note: str                       # a small spend gives a rough reading
    ask: str                                # the record is below, place this round's points with the tool
    tool_name: str                          # the tool's name as the model sees it
    tool_text: str                          # the tool's description
    bad_call: str                           # the retry message for bets the engine rejects. One message, no slots
    no_call: str                            # the retry message for a reply with no tool call
    question: str                           # Jev's choice question, see providers

class SkinError(ValueError): ...            # a skin file or a Skin that is not well formed

def load_skin(path: Path) -> Skin
def load_skins(path: Path | None = None) -> Mapping[str, Skin]
```

- **Every field is a `str`** except `channels`, which is a tuple of ten. There are no numbers on a skin, see [conventions](README.md#conventions).
- **The fields are the parts of the prompt**, one each, in the order the [system prompt](../../harness/prompts.md#system-prompt) uses them. Adding a part to the prompt means adding a field here, a key to every skin file, and a row to [skins](../../harness/skins.md#what-a-skin-file-holds).

## Behaviour

### Validation on construction

`__post_init__` normalises, then raises `SkinError` if any of these hold. Lint is separate, see [lint](lint.md), so a test can build a skin that fails lint.

- **Normalise first.** Every `str` field and every channel name has `\r\n` replaced by `\n`, then leading and trailing whitespace stripped. The stored value is the normalised one, so one file hashes the same on every OS.
- `name` does not match `^[a-z][a-z0-9_]*$`.
- Any `str` field is empty after stripping.
- `channels` does not have exactly ten entries. Ten is the [frame](../../glossary.md), and the engine default `channels` is ten, see [config](../engine/config.md#defaults). The harness never pairs a skin with a config of another size.
- Any channel name is empty, or contains `,`, `"`, `\n` or `\r`. These are the characters `Record.to_csv` rejects, see [record](../engine/game.md#record), so a bad name fails here and never mid-run.
- Two channel names are equal ignoring case.
- `tool_name` does not match `^[a-z][a-z0-9_]{0,63}$`. Every provider accepts a name of that shape.

### The TOML file

One file per skin, one table, no nesting.

- **Every field of `Skin` is a top-level key** of the same name. `channels` is an array of ten strings, every other key a string. Multi-line strings use TOML's `"""` form.
- **Every key is required.** A missing key, an unknown key, or a value of the wrong type raises `SkinError` naming the key. So a typo in a key name fails on load rather than silently dropping a part of the prompt.
- **`name` equals the file stem.** `example.toml` holds `name = "example"`. A mismatch raises `SkinError`.
- **Comments are free.** The example skin's first line is a comment holding the [canary](lint.md#canary). Held-out skins may carry it or not, as they are never published.
- **No templating.** A skin writes the ten names, the number 100 and its tool name into its own text. The renderer concatenates and never substitutes, see [render](render.md). The [lint](lint.md#frame-facts) checks the text and the `channels` list agree.

### `load_skin`

- **`load_skin(path)`** reads the file with `tomllib`, builds a `Skin`, calls `lint(skin)`, and returns it.
- **Errors in order.** A file that does not exist or is not valid TOML raises `SkinError` with the path. Then the key checks above. Then `Skin`'s own validation. Then `LintError` from the lint. Each names the file.

### `load_skins`

- **The example skin always loads**, from `example.toml` beside the code, as package data.
- **Then the held-out folder**, if there is one. `path` when given, else the folder `PARANOID_SKINS` names, else nothing. `PARANOID_SKINS` set to an empty string counts as unset. A `path` given explicitly wins over the variable.
- **A folder that does not exist or is not a directory** raises `SkinError`.
- **Every file in the folder whose name ends `.toml`** is loaded with `load_skin`, in sorted filename order. Other files are ignored, subfolders are not walked. The private repo keeps `skins/` a plain folder of TOML files, see [skins](../../harness/skins.md#where-skins-live).
- **Names are unique.** A held-out skin named `example`, or two files with one `name`, raises `SkinError`.
- **The result is a `types.MappingProxyType`**, keys in sorted order, so the harness cannot swap a skin under a name that is already in a log.
- **The harness picks by name.** The `skin` task arg defaults to `example`, see [running](../../harness/running.md#commands). A name not in the mapping is a harness error, not a skins one.

### The example skin

- **Lives at `src/paranoid/skins/example.toml`** and is the one skin in this repo, see [where skins live](../../harness/skins.md#where-skins-live).
- **Its wording is the wording in [prompts](../../harness/prompts.md)**, and only its wording is published. A held-out skin words the frame its own way, see [contamination](../../harness/contamination.md#why).
- **Its text never changes once a headline run has played it**, see [CONTRIBUTING](../../../CONTRIBUTING.md#what-never-changes-without-a-new-pilot). The test suite pins its `prompt_hash`, so a change is a reviewed change, see [tests](tests.md#skin).

## Invariants

- Every `str` field on a built `Skin` is non-empty, stripped, and free of `\r`.
- `len(skin.channels) == 10`, every name is CSV safe, and no two are equal ignoring case.
- `load_skins()` always contains `"example"`, and `load_skins()["example"].name == "example"`.
- Every skin `load_skins` returns has passed `lint`.
- A `Skin` is immutable. Two skins built from the same file are equal and hash alike.
- The skins layer imports nothing outside `paranoid.engine` and the standard library.

## Tests

See [tests](tests.md#skin).

## Open

- **Whether `reading_note` stays its own field.** It is separate so a pilot cell can drop it and see whether the agent still looks. If no such cell runs, fold it into `how_points_earn`.
- **Whether a skin should carry what a round stands for** as its own field, so the pilot can swap "week" for "minute" on one engine, see [future](../../design/future.md).
