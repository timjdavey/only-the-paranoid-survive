# Writing a skin

A skin is the story dressed over the game engine, see [glossary](../glossary.md). The engine is public, so the skin is the one thing a model could memorise, and the held-out skins are what the headline plays. [Skins](skins.md) says what a skin file holds and the [lint](../specs/skins/lint.md) says what fails on load. This page is the judgement calls neither can make: picking a story someone who does the job would believe, naming things, wording the frame so it reads nothing like the example skin, and reviewing the result before it is committed.

Read these first, in this order:

- [skins](skins.md), the fields and where each lands in the prompt.
- [prompts](prompts.md), the example skin's wording, the frame facts and the banned words.
- [contamination](contamination.md), why held-out skins are private and what never leaves the private repo.
- The [skin](../specs/skins/skin.md) and [lint](../specs/skins/lint.md) specs, what the loader checks.

## Before you start

- **Pick a colour for the codename.** Results tables publish skin names, so the name must say nothing about the story. A colour is a word, it is opaque, and ten of them tell no story together.
- **The file is `skins/<colour>.toml`** in the private repo, and the stem is the name. There is no `name` key, see [the TOML file](../specs/skins/skin.md#the-toml-file).
- **Line 1 is the canary**, as a TOML comment, copied from `example.toml`. The model never sees a comment, and if a skin ever leaks the line gets it filtered, see [canary](contamination.md#canary).
- **One table, no nesting, every key required.** The keys are the fields in [what a skin file holds](skins.md#what-a-skin-file-holds). A missing or unknown key fails on load rather than silently dropping a part of the prompt.

## What you cannot change

Every skin has these tells and no wording removes them. They are the [frame](../glossary.md), and the [recognition check](../pilot/provider-checks.md#recognition) exists to price them. Do not spend effort hiding them.

| Tell | Why it stays |
|---|---|
| Exactly 100 points over exactly ten named channels, in whole numbers | The engine's budget and channel count |
| A linear payout with no saturation | The engine pays points times level |
| A reading only where points were placed, and a rough one from few points | What the agent sees is the engine's rule, see [mechanics](../design/mechanics.md#what-the-agent-sees) |
| An empty record on round 1 | Round 1 sends the CSV header alone |
| One forced tool that takes ten numbers and returns a CSV | The harness's one interface |

Where the story's real version would saturate, the skin still cannot say so. It can only avoid drawing attention to it.

## What the lint checks, and what only a reader can

The lint is a floor, not a proof. The rules are in the [lint spec](../specs/skins/lint.md) and the shape checks in [skin validation](../specs/skins/skin.md#validation-on-construction). In short:

- **Shape.** Every field a non-empty string, `channels` an array of ten, the stem and `tool_name` matching their patterns.
- **Channels.** Ten names, no two equal ignoring case, none holding `,`, `"` or a newline. They become CSV column headers.
- **Frame facts**, on the whole rendered prompt. It must hold `100`, every channel name as spelt, `whole number` or `integer`, and the tool name. Where each sits is up to you.
- **Banned word starts**, on every field the model reads and every channel name, see [words](../specs/skins/lint.md#words).
- **The canary GUID** is nowhere the model reads.

Until `paranoid.skins.lint` ships, mirror the spec in a throwaway script outside both repos.

Two rules the lint does not enforce and a reviewer must:

- **No number but 100 and ten** anywhere in the skin. Levels, onsets and history come from the engine, never the skin. Whether the lint should fail any other digit run is [open](../specs/skins/lint.md#open).
- **Never say the world may move.** No "yields vary over time", no "a new season". The agent has to find that out.

## Choosing the story

This is where most rewrites come from. A story passes the lint and still fails if someone who does the job would say "that is not how it works".

- **The engine must be natural in the story.** Points go out, each earns what its channel is paying, and the record shows a per-point figure only where points went. Test it with one question: would someone in this job believe the return per unit is unknown each period and only learnable by sending some there?
- **The uncertainty needs a cause an expert accepts.** If the return per unit is a design constant, known the day the thing was built or commissioned, an expert sees nothing to learn and the story is false. Pick channels whose return really does vary period to period, for a reason the expert would name themselves.
- **Moving every period must be plausible, and so must one person deciding it.** The agent redraws the whole split each round. If the people or things being placed cannot move that often, or nobody in the story has the authority to move them, the story is false.
- **Spread the stories across the set.** Two tales from the same walk of life read as one skin. Aim for a mix: a plain operation, one with a heavy downside, one with a heavy upside, and one that says in plain words it is a game, as the contrast arm. The game skin is meant to be the one most likely to be called a test outright.
- **Stakes live in `intro` only, as consequences.** A shortfall that costs someone something is fine. A target figure, a threshold, or anything the solver could read as a hint is not. Drop nudges such as "there is no such thing as making too much".
- **Give a reason the record starts empty.** One clause, with nothing about levels or cycles. Starting the job this week works. A new season opening does not, as it hints that things move with the season. A game needs no reason, as a game starts at turn one.
- **Pick the period word and keep it.** Day, month or turn. Every field uses the same one, and `question` asks about one period.

## Naming things

- **Invent every proper noun and web search each one.** A real place that could not hold the operation makes the whole skin false to a model that knows it. A name with a loaded association is a judgement call: it can stay when nothing real carries it.
- **Place names should read as one place.** Ten names that could all be wards of one real city read as a city. Any-town names, or a mix of British and American registers, read as a list.
- **Channel names are headers.** Short, unique, comma-free, no quotes, none starting with a banned stem. Avoid one name being a substring of another. The lint finds `Rome` inside `Rome East` and passes, but the agent reading a header row does not, see [frame facts](../specs/skins/lint.md#frame-facts).
- **A banned stem must start the word.** So `exchange` passes and `shift` fails, and a compound such as "night shift" fails on its second word. The ordinary words that fail by design are under [words](../specs/skins/lint.md#words). Pick another word rather than argue.
- **The column words are headers too.** `round_word`, `bet_word`, `level_word` and `output_word` head the record. Pick them in the story's words, never `round`, `bet`, `level` or `output`, which are the example skin's, see [render](../specs/skins/render.md#record).
- **The tool name is a verb and a noun in the story's words.** Never `submit`, which is the example skin's name for it and the harness's. It is linted like any field, so a verb from the banned list fails.

## Wording the frame your own way

The frame is a fingerprint. If a held-out skin shares a sentence shape with the example skin, a model that saw the example once can spot the benchmark under any story. The example skin's wording is in [prompts](prompts.md#system-prompt) and its [tool text](prompts.md#tool-text). Read it before writing a field, then put it away.

- **Avoid its nouns.** Budget, points, channels, split, round, record of play, submit. Each story has its own words for all of them.
- **A sentence with its shape and swapped nouns is still its sentence.** Change the shape, not just the nouns. Lead with what is wrong in the story's terms, fold the constraint into one clause, or say "none below zero" in the story's words rather than "none negative".
- **Vary the shape across the held-out set too.** If every `tool_text` is one sentence of the same shape with the nouns swapped, and every `how_points_earn` ends in the same two sentences, one rough and one firm, five skins are one skin to a model.
- **The facts may sit anywhere.** The lint checks the whole rendered prompt. If the story reads better with the ten names in `intro` and the tool in `rules`, do that.
- **`question` is a which-channel question about one period**, with the channels as its options, see [Jev](providers.md#jev). It is linted like every other field.

## Reviewing a skin before you commit

Every skin so far has needed a second pass that only reading found.

Mechanical, with the lint or the throwaway script:

- The shape, channel and frame fact checks, and every banned stem on every field and channel name.
- No digit run anywhere except `100`.
- The canary is in line 1 and the GUID is nowhere in the rendered prompt.

By reading:

- **Render the round 1 prompt and read it as someone who does the job.** Mark every sentence they would not say.
- **Read each field beside the example skin's wording**, then beside the same field in every other held-out skin. Any sentence that is a noun swap of another gets reshaped.
- **Search each proper noun**: the firm, the place, the game, and every channel name that could be a real place.
- **Confirm the prompt states no level, no history, and nothing about the world moving.**
- **Confirm the intro says why the record is empty**, without hinting at a cycle.

## After it is written

- **Commit on a branch in the private repo, never anywhere public.** No skin, tape, or log that played one leaves the machines that run it, see [who can see them](contamination.md#who-can-see-them).
- **Fix it before the first headline run.** A skin's text never changes once a headline run has played it, see [what never changes](../../CONTRIBUTING.md#what-never-changes-without-a-new-pilot). After that a fix is a new skin.
- **The recognition check is the real test.** It asks each model where the prompt comes from. A skin that gets more hits than the others is the one to rewrite.

## What stays in the private repo

This page holds the method. The private repo's own README holds what would undo it if published:

- Which codename wears which story.
- Lessons from rewrites that name a story, a place or a sentence.
- Anything that quotes a skin's text, including drafts that were dropped.

If a lesson can be told without naming a skin, it belongs on this page.
