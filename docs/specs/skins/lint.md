# Lint

## Purpose

The lint is the one gate every word the model reads passes through. `lint_text` finds [banned words](../../harness/prompts.md#banned-words) in any text. `lint` runs it over every field of a skin, then checks the rendered prompt states the [frame](../../glossary.md) and does not leak the canary. A skin that fails does not load, see [lint](../../harness/skins.md#lint). The [recognition check](../../pilot/provider-checks.md#recognition) reuses `lint_text` on model replies.

## Interface

```python
BANNED_WORDS: tuple[str, ...]               # lowercase word starts, the table below
WHOLE_NUMBER_PHRASES: tuple[str, ...] = ("whole number", "integer")

class LintError(ValueError):
    skin: str                               # the skin's name
    problems: tuple[str, ...]               # one entry per failure, the strings below, in the order found

def lint_text(text: str) -> tuple[str, ...]
def lint(skin: Skin) -> None

CANARY: str                                 # in paranoid.skins.canary
```

## Behaviour

### Words

`lint_text` splits the text into words and reports each banned entry a word starts with.

- **A word is a maximal run of letters**, by `str.isalpha`, after lowercasing. Digits, punctuation and apostrophes end a word, so `can't` is `can` and `t`.
- **A word hits an entry when it starts with it.** So one entry catches a word's plural and its tenses. `BANNED_WORDS` holds word starts, not whole words, and the words in [prompts](../../harness/prompts.md#banned-words) map to them as below.
- **The result is each entry hit, in text order, each once.** An empty tuple means the text is clean.
- **Substrings inside a word do not count.** `established` does not hit `stabl` and `exchange` does not hit `chang`. The entries for `unchanged` and `unstable` are listed on their own for that reason.

| Word in prompts | Entries | Also catches |
|---|---|---|
| check | `check` | checks, checking, checked, checkpoint |
| change | `chang`, `unchang` | changes, changing, changed, unchanged |
| shift | `shift` | shifts, shifting, shifted |
| switch | `switch` | switches, switching, switched |
| shock | `shock` | shocks, shocked |
| drift | `drift` | drifts, drifting, drifted |
| trend | `trend` | trends, trending, trendy |
| anomaly | `anomal` | anomalies, anomalous |
| regime | `regime` | regimes |
| climate | `climat` | climates, climatic |
| detect | `detect` | detects, detection, detector |
| monitor | `monitor` | monitors, monitoring, monitored |
| watch | `watch` | watches, watching, watched |
| alert | `alert` | alerts, alerted |
| stable | `stabl`, `stabil`, `unstabl`, `instabil` | stably, stability, unstable, instability |
| volatile | `volatil` | volatility |

- **Adding a word** means a row in [prompts](../../harness/prompts.md#banned-words), an entry here, and the entry in `BANNED_WORDS`, in that order.
- **No exceptions and no allow list.** A skin that needs a caught word picks another. The lint is strict so a held-out skin cannot slip one in, see [skins](../../harness/skins.md#lint).

### Fields

`lint(skin)` first runs `lint_text` over every `str` field and every channel name. Each hit is a problem `"<field>: <entry>"`, with `channels[<i>]` as the field for a channel name. `name` and `tool_name` are linted too, so a tool called `switch_bets` fails.

### Frame facts

Then it renders `render_system_prompt(skin)` and checks the facts in [what every skin must say](../../harness/prompts.md#what-every-skin-must-say). Each is a substring test on the rendered prompt.

| Fact | Passes when | Problem string |
|---|---|---|
| The budget | `"100"` is in the prompt | `missing: 100` |
| Every channel | each name in `skin.channels` is in the prompt, case sensitive | `missing: channel <name>` |
| Whole numbers | any entry of `WHOLE_NUMBER_PHRASES` is in the prompt, ignoring case. `whole number` covers `whole numbers`, `integer` covers `integers` | `missing: whole numbers` |
| The tool | `skin.tool_name` is in the prompt | `missing: tool name` |
| No canary | the GUID from `CANARY`, the part after `canary GUID `, is not in the prompt | `canary in prompt` |

- **The checks are on the whole prompt**, not on one field. A skin may put the names in `intro` and the tool in `rules` if its story reads better that way. The [frame](../../glossary.md) fixes the facts, not where they sit.
- **A name that is a substring of another passes trivially.** `Rome` is found inside `Rome East`. The lint is a floor, not a proof, so a reviewer still reads a new skin.

### Raising

- **`lint` collects every problem and raises once**, so a skin author sees the whole list. `LintError.problems` is the tuple in the order found: fields in `Skin` field order, then the frame facts in table order.
- **`str(error)`** is `Skin <name> failed lint: <problems joined by "; ">`.
- **A clean skin returns `None`** and raises nothing.

### Canary

- **`CANARY`** is the line in [contamination](../../harness/contamination.md#canary), exactly, with no trailing newline. It lives in `paranoid.skins.canary` and is exported from `paranoid.skins`.
- **Every published file that holds prompt text carries it.** In this repo that is `example.toml`, as its first comment line, and `docs/harness/prompts.md`. The test suite checks both, see [tests](tests.md#lint).
- **The prompt never carries it**, so the model never sees it. The frame facts check above enforces that for every skin that loads.
- **A model that can finish the line has seen our data.** The [recognition check](../../pilot/provider-checks.md#recognition) asks it to.

## Invariants

- `lint_text("")` is `()`, and `lint_text` of any rendered record from a clean skin is `()`, as numbers are not words.
- Every entry in `BANNED_WORDS` is lowercase letters only.
- `lint(skin)` passes for every skin `load_skins` returns.
- `lint` never edits the skin or renders anything but the system prompt.
- `CANARY` does not appear in `render_system_prompt(skin)` for any skin that loads.

## Tests

See [tests](tests.md#lint).

## Open

- **Whether to ban numbers.** A skin should hold no number but 100 and ten, see [skins](../../harness/skins.md#what-a-skin-file-holds). A lint that fails any other digit run would enforce it, but blocks a story with a year or a size in it. Decide after the first held-out skin is written.
- **The whole-numbers phrases.** `whole number` and `integer` are a first pass. A held-out skin that words the fact another way adds its phrase to `WHOLE_NUMBER_PHRASES`, and the test suite pins the list.
- **Pilot-only tool text.** The notes and compute tools in [notepad and compute](../../pilot/provider-checks.md#notepad-and-compute) have descriptions of their own. Whether they are skin fields or harness text run through `lint_text` is a harness spec question.
- **Whether the recognition check needs more words** than the prompt lint, such as "benchmark" or "evaluation". If so they are a second list in the harness, not an addition here.
