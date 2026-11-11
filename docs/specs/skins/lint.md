# Lint

## Purpose

The lint is the one gate every word the model reads passes through. `lint_text` finds [banned words](../../harness/prompts.md#banned-words) in any text. `lint` runs it over every field of a skin the model reads, checks the rendered prompt states the [frame](../../glossary.md), and checks nothing the model reads leaks the canary. A skin that fails does not load, see [lint](../../harness/skins.md#lint). The [recognition check](../../pilot/provider-checks.md#recognition) reuses `lint_text` on model replies.

## Interface

```python
BANNED_WORDS: tuple[str, ...]               # lowercase word starts, the table below
PREFIXES: tuple[str, ...] = ("un", "in", "de", "re", "non")   # removed once before a second match
WHOLE_NUMBER_PHRASES: tuple[str, ...] = ("whole number", "integer")
PERCENT_PHRASES: tuple[str, ...] = ("percent", "per cent", "%")

class LintError(SkinError):
    skin: str                               # the skin's name
    problems: tuple[str, ...]               # one entry per failure, the strings below, in the order found

def lint_text(text: str) -> tuple[str, ...]
def lint(skin: Skin) -> None

CANARY: str                                 # in paranoid.skins.canary
```

- **`LintError` is a `SkinError`**, so the harness catches one type on load. Tests tell them apart, see [tests](tests.md#skin).

## Behaviour

### Words

`lint_text` splits the text into words and reports each banned entry a word starts with.

- **A word is a maximal run of letters**, by `str.isalpha`, after lowercasing. Digits, punctuation and apostrophes end a word, so `can't` is `can` and `t`.
- **A word hits an entry when it starts with it**, as it is or after one entry of `PREFIXES` is removed from its front. So one entry catches a word's plural, its tenses and its negatives: `check` catches checks, checking, rechecked and unchecked, and `stabil` catches stability, destabilise and instability.
- **Substrings inside a word do not count.** `established` does not hit `stabl`, `exchange` does not hit `chang` and `research` does not hit `search`.
- **A word hits at most one entry.** The word as it is is tried first, then with a prefix removed, and the first entry that matches is reported. No entry in `BANNED_WORDS` is a prefix of another, and the test suite pins that.
- **The result is each entry hit, in text order, each once.** An empty tuple means the text is clean.

| Word in prompts | Entry | Also catches |
|---|---|---|
| check | `check` | checks, checking, checked, checkpoint, recheck, unchecked |
| change | `chang` | changes, changing, changed, unchanged |
| shift | `shift` | shifts, shifting, shifted |
| switch | `switch` | switches, switching, switched |
| shock | `shock` | shocks, shocked |
| drift | `drift` | drifts, drifting, drifted |
| trend | `trend` | trends, trending, detrend |
| anomaly | `anomal` | anomalies, anomalous |
| regime | `regime` | regimes, regimen |
| climate | `climat` | climates, climatic |
| detect | `detect` | detects, detection, detector, undetected |
| monitor | `monitor` | monitors, monitoring, unmonitored |
| watch | `watch` | watches, watching, unwatched |
| alert | `alert` | alerts, alerted |
| stable | `stabl`, `stabil` | stably, unstable, stability, instability, destabilise |
| volatile | `volatil` | volatility |
| benchmark | `benchmark` | benchmarks, benchmarking |
| canary | `canar` | canaries |
| paranoid | `paranoi` | paranoia |

- **The last three name the study itself.** The [canary](#canary) line says benchmark and canary, and the repo and package are called paranoid. A skin that says any of them has told the model where it is.
- **Adding a word** means a row in [prompts](../../harness/prompts.md#banned-words), a row here, and the entry in `BANNED_WORDS`, in that order.
- **No exceptions and no allow list.** A skin that needs a caught word picks another. The lint is strict so a held-out skin cannot slip one in, see [skins](../../harness/skins.md#lint).
- **Some ordinary words fail by design.** A medical `regimen`, a horse's `stable`, a `shock absorber`, `driftwood`, a `watchmaker` and the surname `Chang` all hit. That is the price of no allow list, so pick another word.

### Fields

`lint(skin)` first runs `lint_text` over every `str` field the model reads and every channel name. Each hit is a problem `"<field>: <entry>"`, with `channels[<i>]` as the field for a channel name. The three column words head every record the model reads, so they are linted too: a `bet_word` of `shift` fails.

- **The three tool names and the three parameter names are linted**, so a tool called `switch_bets` fails, and so does a parameter called `regime`.
- **`name` is not.** The model never reads it. It goes in log metadata only, see [skin](skin.md#load_skins).

### Numbers

In the same pass, `lint` fails any field that writes a number in digits, bar the budget. A skin names things and sets the scene. Levels, onsets and history come from the engine, see [skins](../../harness/skins.md#what-a-skin-file-holds).

- **A number is a maximal run of digits**, by `str.isdigit`. The run `100` passes, wherever it sits, as it is the budget the [frame facts](#frame-facts) ask for. Any other run fails: `10`, `1000`, `1987`, and the `5` in `100.5`.
- **The problem is `"<field>: number"`**, once a field however many runs it holds, after that field's word hits. It never repeats the digits, as they are the skin's text.
- **Every field the word lint reads is checked**, names included. So a tool called `send2` fails, and so does a channel called `Dock 4`.
- **Ten is written as a word.** The count of channels is the frame's, and the example skin says `ten markets`. `10 markets` fails.
- **Number words are a reader's job.** `twelve` and `a dozen` pass the lint, see [writing a skin](../../harness/writing-a-skin.md#what-the-lint-checks-and-what-only-a-reader-can).
- **No exceptions and no allow list**, as for words. A story that wants a year or a size picks other words.
- **`lint_text` does not check numbers.** It also reads a rendered record and a model's reply, which are full of them.

### Frame facts

Then it renders `render_system_prompt(skin)` and checks the facts in [what every skin must say](../../harness/prompts.md#what-every-skin-must-say). Each is a substring test on the rendered prompt.

| Fact | Passes when | Problem string |
|---|---|---|
| Percentages | any entry of `PERCENT_PHRASES` is in the prompt, ignoring case. `percent` covers `percentage` and `percentages` | `missing: percent` |
| The budget | `"100"` is in the prompt | `missing: 100` |
| Every channel | each name in `skin.channels` is in the prompt, case sensitive | `missing: channels[<i>]`, by index so a held-out name never reaches a log |
| Whole numbers | any entry of `WHOLE_NUMBER_PHRASES` is in the prompt, ignoring case. `whole number` covers `whole numbers`, `integer` covers `integers` | `missing: whole numbers` |
| The tool | `skin.tool_name` is in the prompt | `missing: tool name` |

- **The checks are on the whole prompt**, not on one field. A skin may put the names in `intro` and the tool in `rules` if its story reads better that way. The [frame](../../glossary.md) fixes the facts, not where they sit.
- **The other parts of the frame are the harness's.** That the record is below is true because the harness sends it, and that there is one tool is true because the harness offers one. The lint checks only what a skin's words can get wrong.
- **A name that is a substring of another passes trivially.** `Rome` is found inside `Rome East`. `"100"` is found inside `1000`. The lint is a floor, not a proof, so a reviewer still reads a new skin.

### Canary

Then it checks that nothing the model reads carries the canary GUID.

- **The GUID** is the part of `CANARY` after `canary GUID `. The line's first half fails the [word lint](#words) on its own, as `benchmark` and `canary` are banned, so this check needs only the GUID. The GUID holds `paranoid` and runs of digits, so a field with the GUID in it also fails the word lint with `paranoi` and the [number rule](#numbers).
- **Checked in** the rendered system prompt, and in `tool_text`, `bets_name`, `bets_text`, `bad_call`, `no_call`, `notes_name`, `notes_text`, `notes_param`, `compute_name`, `compute_text`, `compute_param`, `question` and the three column words. The problem string is `canary in prompt` for the first and `canary in <field>` for the others.
- **`CANARY`** is the line in [contamination](../../harness/contamination.md#canary), exactly, with no trailing newline. It lives in `paranoid.skins.canary` and is exported from `paranoid.skins`.
- **Every published file that holds prompt text carries it.** In this repo that is `example.toml` and `tests/skins/test_example.py`, each as its first comment line, and `docs/harness/prompts.md`. The test suite checks both, see [tests](tests.md#lint).
- **A model that can finish the line has seen our data.** The [recognition check](../../pilot/provider-checks.md#recognition) asks it to.

### Raising

- **`lint` collects every problem and raises once**, so a skin author sees the whole list. `LintError.problems` is the tuple in the order found: fields in `Skin` field order, each field's words then its number, then the frame facts in table order, then the canary.
- **`str(error)`** is `Skin <name> failed lint: <problems joined by "; ">`. It names fields and entries, never the skin's text, so the message is safe in a CI log, see [tests](tests.md#lint).
- **A clean skin returns `None`** and raises nothing.

## Invariants

- `lint_text("")` is `()`, and `lint_text` of any rendered record from a clean skin is `()`, as its words are the skin's own, already linted, and numbers are not words.
- Every entry in `BANNED_WORDS` and `PREFIXES` is lowercase letters only, and no entry in `BANNED_WORDS` is a prefix of another.
- `lint(skin)` passes for every skin `load_skins` returns.
- `lint` never edits the skin or renders anything but the system prompt.
- The canary GUID does not appear in any text the model reads from a skin that loads.

## Not decided

- **The whole-numbers phrases.** `whole number` and `integer` are a first pass. A held-out skin that words the fact another way adds its phrase to `WHOLE_NUMBER_PHRASES`, and the test suite pins the list. Decide skin by skin.
- **The percent phrases.** `percent`, `per cent` and `%` are a first pass, as every skin calls its split percentages, see [interface](../../design/interface.md#how-the-agent-plays). A held-out skin that says it another way adds its phrase to `PERCENT_PHRASES`, and the test suite pins the list. Decide skin by skin.
- **The prefixes.** `un`, `in`, `de`, `re`, `non` are a first pass too. A word that slips through adds its prefix, and the test suite pins the list. Decide skin by skin.
