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
| A linear payout with no saturation | The engine pays each channel's level times its share of the 100 |
| A reading only where points were placed, and a rough one from few points | What the agent sees is the engine's rule, see [mechanics](../design/mechanics.md#what-the-agent-sees) |
| Readings that do not add up to the output | A reading is rough at any bet and the output is exact, see [readings](../specs/engine/game.md#readings) |
| An empty record on round 1 | Round 1 sends the CSV header alone |
| A tool that takes ten numbers and returns a CSV, beside a notes tool and a compute tool | The harness's interface, see [tools](../design/interface.md#tools) |

Where the story's real version would saturate, the skin still cannot say so. It can only avoid drawing attention to it.

The notes and compute tools are worded by the skin too. Say what each does and no more: a note comes back next round, the code sees the record as a file. Neither should suggest what to write down or what to work out.

## What the lint checks, and what only a reader can

The lint is a floor, not a proof. The rules are in the [lint spec](../specs/skins/lint.md) and the shape checks in [skin validation](../specs/skins/skin.md#validation-on-construction). In short:

- **Shape.** Every field a non-empty string, `channels` an array of ten, the stem, the three tool names and `bets_name` matching their patterns, no two tool names equal.
- **Channels.** Ten names, no two equal ignoring case, none holding `,`, `"` or a newline. They become CSV column headers.
- **Frame facts**, on the whole rendered prompt. It must hold `100`, every channel name as spelt, `whole number` or `integer`, and the tool name. Where each sits is up to you.
- **Banned word starts**, on every field the model reads and every channel name, see [words](../specs/skins/lint.md#words).
- **The canary GUID** is nowhere the model reads.

Until `paranoid.skins.lint` ships, mirror the spec in a throwaway script outside both repos.

Two rules the lint does not enforce and a reviewer must:

- **No number but 100 and ten** anywhere in the skin. Levels, onsets and history come from the engine, never the skin. Whether the lint should fail any other digit run is [not decided](../specs/skins/lint.md#not-decided).
- **Never say the world may move.** No "yields vary over time", no "a new season". The agent has to find that out.

## Choosing the story

This is where most rewrites come from. A story passes the lint and still fails if someone who does the job would say "that is not how it works".

- **Pitch the story in one line and run the story tests before writing a field.** A full file hides a false story behind clean wording. The tests are in the table below, each with an example of a story that fails it. The bullets under it say why each test is there.
- **A fix is a new draft.** After any change to the story, run every test again, as a fix for one test often breaks another. Then reread the verbs and the names in every field. A word that fit the old story may not fit the new one.

### The story tests

| Test | Ask | It fails when | An example that fails |
|---|---|---|---|
| One kind | Are the ten the same kind of thing? | Each kind pays back at its own speed | Ten kinds of advertising. A search advert pays back the same week and a billboard over months |
| Plainly matters | Would a reader ask why the channel makes a difference? | They would | Adverts for toothpaste shown to ten hobby groups. Chess players and knitters buy the same toothpaste |
| Belongs to the channel | Does the skin need a sentence on how a return is traced? | It does | A web shop advertising in ten magazines, with a discount code to say which magazine sent each buyer |
| Fixed, with the dynamics beneath | Would the operator edit or replace a channel? | A channel is something the operator makes | Ten designs of a checkout page. The owner would rewrite the worst one after a week |
| Nothing the trade expects | Does the trade know returns fade, tire or react to how much is sent? | It does | Ten new records to promote. Everyone in music knows a release fades after its first weeks |
| Unknown until sent | Could the firm learn the figure from its own office, or by testing what it holds? | It could | A plumbing firm sending fitters to ten districts. The calls come in to its own office, so it knows where the work is before anyone leaves |
| A small player | Does twice the units earn twice as much? | The firm shares out fixed demand | The one ice cream firm in a seaside town, with carts on ten pitches. A second cart on a pitch takes sales from the first |
| The whole run | Would all 100 on one channel hold up for the run? | The trade expects it to wear down or glut | A herd grazed over ten fields. All the cattle on one field eat it bare long before the run ends |
| Lead time | Can what is placed arrive and pay back within the period? | It takes weeks | Seed sown on ten plots each week. Nothing can be weighed until the harvest, months later |
| Wide enough | Can the figure swing two or three times over, and lose half in a bad spell? | It sits in a narrow band, or is a rate with a ceiling | Ten card payment providers, scored on the share of payments approved. A good one approves nearly all, and one that approved half would not exist |
| The unit | Does a reading in the tens, with one decimal, read true? Can it go below zero? | It is a count per person per day | Cars sold per seller per day. Nobody sells 61.2 cars in a day, and nobody sells fewer than none |
| The sums | Do an all in row and a split row match `how_points_earn`? | The story promises a total | The skin says units times the figure per unit. All 100 on a channel reading 61.2 would then make about 6,120, and the output shows 60.5 |
| The stakes | Would someone in the trade name this consequence? | It is the largest one the writer could think of | The only bakery in a city, where one poor day leaves people without bread |
| The empty record | Is the thing new, and not just the person? | A new person would inherit the files | A new manager at a firm that has worked the same ten sites for years. The last manager's figures are in the files |
| The aim | Does the skin say what the agent is for, with no target? | The model has to guess | A skin that gives the job and the stakes and never says to bring in as much as it can. A careful model spreads the 100 to be safe |

Keep the examples made up. One taken from a held-out skin, or from a draft of one, belongs in the private repo, see [what stays in the private repo](#what-stays-in-the-private-repo).

### What the ten things are

- **The engine must be natural in the story.** Points go out, each earns what its channel is paying, and the record shows a per-point figure only where points went. Test it with one question: would someone in this job believe the return per unit is unknown each period and only learnable by sending some there?
- **The ten channels are ten of one kind.** Ten different kinds of thing each bring their own mechanics: how fast they pay back and how the return is counted. The model then plays what it knows about each kind, not the record. Ten kinds of advertising fail, as one kind pays back the same week and another over months.
- **The channel must plainly matter to the return.** If a reader asks "why would that make a difference?", the story is false. Splitting adverts for a thing everyone buys across ten hobby groups fails this.
- **The return belongs to its channel, with no tracing story.** If the skin needs a sentence to say how a sale is traced back to its channel, someone who does the job will doubt the tracing. Prefer a return that arises at the channel. It need not be counted there to the last unit, as the channel's figure is an estimate, see [what is counted](#what-is-counted).
- **A channel is a fixed thing, and what moves is out of sight beneath it.** It stays what it is while what it yields moves for reasons nobody can see. That gives the agent something to work out. A thing the operator makes and would revise, such as a page design or an advert, fails, as an expert expects it to be edited or to wear out.
- **Moving every period must be plausible, and so must one person deciding it.** The agent redraws the whole split each round. If the people or things being placed cannot move that often, or nobody in the story has the authority to move them, the story is false.
- **Check the lead time.** The agent places its whole split each period and reads the result at the end of it. If the thing placed would really take weeks to arrive, the story is false. Ask what the agent could decide and see paid back inside one period.

### What is counted

- **Output is the average, not the total.** The engine pays each channel's level times its share of the 100, see [readings](../specs/engine/game.md#readings). All 100 on a channel at 61.2 pays 61.2. A story that says units times the figure per unit promises a total, and with 100 units that is a hundred times the last column.
- **Two wordings fit.** Call a channel's figure what the whole lot would make there, so each point brings in its part. Or call the last column the figure per unit across the whole.
- **The readings will not add up to the output.** A reading is rough even at 100 points, and the output is paid at the true level. All in on one channel can read 61.2 and pay 60.5. If the story counts both from one tally, the books look wrong. Make the channel's figure an estimate and the total the thing that is measured.
- **Pick a unit that can carry the engine's numbers.** Readings run to tens, with one decimal. Write a reading from the engine into the story's sentence and ask whether someone in the job would believe it. A count per person per day of that size is false in most trades.
- **The unit is one of many small things, each its own draw.** That is what makes a small bet a rough reading. Where one unit's return is the same however much is sent, as with money in a fund, a rough reading from a small bet is false.
- **The return per unit must swing as far as the engine's levels do.** In the default config the best channel pays two or three times the worst. A shock takes anything from a tenth to over a half off a channel, each by a different amount, see [config](../specs/engine/config.md). A story whose real figure sits in a narrow band cannot wear that. A payment system that approved half its payments would not exist.
- **Prefer a yield to a rate.** A level has no ceiling and is not clipped at zero. A pass rate or a percentage cannot go above 100, so the first level outside the band breaks the skin. A yield per unit has no ceiling.
- **The figure should be able to go below zero.** Levels and readings are not clipped. Money after costs can be negative. A count of things made cannot, and the engine will now and then show one.
- **One channel moves against the rest.** In a shock every channel falls but one, which rises. The story must stand one of the ten doing well in a bad period, without the skin saying so.

### Why it is unknown

- **The uncertainty needs a cause an expert accepts.** If the return per unit is a design constant, known the day the thing was built or commissioned, an expert sees nothing to learn and the story is false. Pick channels whose return really does vary period to period, for a reason the expert would name themselves.
- **A firm that takes its own orders already knows its demand.** If the work arrives through the firm's own office, the firm can see where it is before anyone is sent out. There is then nothing to learn by placing people, and the story is false. Pick a story where the figure only comes back from the place the units went.
- **The figure must only show in use.** If an expert could measure the thing before placing it, they would, and then there is nothing to learn by placing it.
- **Give a reason the record starts empty, and put it in the thing.** One clause, with nothing about levels or cycles. A new person inherits the old files, so starting the job this week is a weak reason. Prefer that the operation or its channels are new, as when a firm has not sold through these markets before. A new season opening still fails, as it hints that things move with the season. A game needs no reason, as a game starts at turn one.

### Why more is always better

- **Prefer a small player in a big market or resource.** The engine pays in a straight line, so twice the units must earn twice as much. That is true of a seller who takes a market's price, or a crew too small to use up what it works. It is false of a firm sharing out fixed local demand, where each extra unit plainly takes work from the last.
- **The run is the test, not the period.** The best play puts all 100 on one channel for most of the run. Ask whether someone in the job would expect that to hold up. If the trade knows returns fade, tire or react to how much is sent, the model brings that belief to the first period. It then moves on for that reason, and the score reads the move as an explore bet. An advert tires, a new release fades, and a lane that is inspected goes quiet.
- **What the agent places must last the run.** If it draws on something that runs down, an expert asks what happens when it is gone.
- **More is better must need no patch.** A line bolted on to explain why surplus still counts reads as a patch, and as a nudge. Pick a story where nobody would ask what happens to the extra.

### Stakes and the aim

- **Stakes live in `intro` only, as consequences.** A shortfall that costs someone something is fine. A target figure, a threshold, or anything the solver could read as a hint is not. Drop nudges such as "there is no such thing as making too much".
- **Size the stakes to what the trade would believe.** A stake can pass the lint and still fail if someone who does the job would call it melodrama. A sole supplier for a whole country, or one poor period that leaves a person without, reads as invented wherever the real thing is traded, stocked or backed up. Ask what really happens after a poor period, and say that.
- **A sole source is rarely true.** Few operations are the only source of anything. Ask who else supplies it before the stakes rest on the story's operation alone.
- **Prefer a cost to a catastrophe.** Ask what a shortfall really costs in the trade, as it is rarely ruin. A cost is believable, and it stays linear, as each unit short costs the same as the last.
- **A heavy stake must still be a believable one.** The set wants one skin with a heavy downside. Heavy means a real consequence a person in the job would name, not the largest one the writer can think of.
- **Say what the agent is for.** One clause in the story's words, such as bringing in as much as it can. With no aim a careful model spreads its bets for safety, and the score reads a spread as doubt. An aim is not a stake, as it names no target, no threshold and no loss.
- **Say it in every skin or in none.** If some skins give an aim and others leave it out, a gap between their scores may be the aim and not the story.

### Across the set

- **Spread the stories across the set.** Two tales from the same walk of life read as one skin. Aim for a mix: a plain operation, one with a heavy downside, one with a heavy upside, and one that says in plain words it is a game, as the contrast arm. The game skin is meant to be the one most likely to be called a test outright.
- **Pick the period word and keep it.** Day, month or turn. Every field uses the same one, and `question` asks about one period.
- **Spread the periods across the set.** The period word heads every record. Two skins with one period share a header, which the column words are there to stop. The word for a bet has the same squeeze where two skins split the same way.

## Naming things

- **Invent every proper noun and web search each one.** A real place that could not hold the operation makes the whole skin false to a model that knows it. A name with a loaded association is a judgement call: it can stay when nothing real carries it.
- **A name must not rank its channel.** Real brands, platforms, categories and age bands arrive with a size, an audience and a reputation, so the model has a favourite before the first reading. Invented names of one register do not.
- **A real place ranks too.** It arrives with its wealth, its housing and what is already sold there, so the model has a favourite before the first reading.
- **Drop a word that hints at a genre, a rank or a size.** A word for a guiding star says "leader", and a word from a sport says who is listening.
- **A name must not hint at plenty or at nothing.** A word that says rich, full, empty or spent gives the model a favourite.
- **Searching a common word always finds something.** The bar is no notable holder, and no exact match in the story's own trade. A coined name comes back clean, so coin the one name that matters most.
- **Place names should read as one place.** Ten names that could all be wards of one real city read as a city. Any-town names, or a mix of British and American registers, read as a list.
- **Channel names are headers.** Short, unique, comma-free, no quotes, none starting with a banned stem. Avoid one name being a substring of another. The lint finds `Rome` inside `Rome East` and passes, but the agent reading a header row does not, see [frame facts](../specs/skins/lint.md#frame-facts).
- **A name is a column in code.** The compute tool reads the record as a file, so a space, an apostrophe or a leading article makes a column the model has to quote.
- **A banned stem must start the word.** So `exchange` passes and `shift` fails, and a compound such as "night shift" fails on its second word. The ordinary words that fail by design are under [words](../specs/skins/lint.md#words). Pick another word rather than argue.
- **The column words are headers too.** `round_word`, `bet_word`, `level_word` and `output_word` head the record. Pick them in the story's words, never `round`, `bet`, `level` or `output`, which are the example skin's, see [render](../specs/skins/render.md#record).
- **The tool name is a verb and a noun in the story's words.** Never `submit`, which is the example skin's name for it and the harness's. It is linted like any field, so a verb from the banned list fails.

## Wording the frame your own way

The frame is a fingerprint. If a held-out skin shares a sentence shape with the example skin, a model that saw the example once can spot the benchmark under any story. The example skin's wording is in [prompts](prompts.md#system-prompt) and its [tool text](prompts.md#tool-text). Read it before writing a field, then put it away.

- **Avoid its nouns.** Budget, points, channels, split, round, record of play, submit. Each story has its own words for all of them.
- **A sentence with its shape and swapped nouns is still its sentence.** Change the shape, not just the nouns. Lead with what is wrong in the story's terms, fold the constraint into one clause, or say "none below zero" in the story's words rather than "none negative".
- **Vary the shape across the held-out set too.** If every `tool_text` is one sentence of the same shape with the nouns swapped, and every `how_points_earn` ends in the same two sentences, one rough and one firm, five skins are one skin to a model. The stakes sentence and the reason the record starts empty are shapes too. If two skins give either with the same construction, they are one skin to a model.
- **A template survives new words.** For each field, write down the job of each sentence in order: what earns, what is reported, what reports nothing, a small bet is rough, a large bet is firm. Two skins with the same jobs in the same order are one skin, whatever the words.
- **A stock answer on this page is a shape.** Where this page hands over a ready answer, at most one skin in the set should use it.
- **The facts may sit anywhere.** The lint checks the whole rendered prompt. If the story reads better with the ten names in `intro` and the tool in `rules`, do that.
- **Name the tool's parameter in the story's words.** `bets_name` is the one word the model reads beside its ten numbers, so it should not be `bets` in any held-out skin. A name the story would use for the list, in snake case, see [skin](../specs/skins/skin.md#validation-on-construction).
- **`question` is a which-channel question about one period**, with the channels as its options, see [Jev](providers.md#jev). It is linted like every other field.

## Reviewing a skin before you commit

Every skin so far has needed a second pass that only reading found.

Mechanical, with the lint or the throwaway script:

- The shape, channel and frame fact checks, and every banned stem on every field and channel name.
- No digit run anywhere except `100`.
- The canary is in line 1 and the GUID is nowhere in the rendered prompt.
- **Compare word runs.** List every run of three words a new skin shares with the example skin, and every run of four it shares with each other held-out skin. It finds a borrowed sentence that reading misses, and three finds a short borrowed phrase that four misses.

By reading:

- **Render the round 1 prompt and read it as someone who does the job.** Mark every sentence they would not say.
- **Read the stakes sentence as someone in the trade.** Would they say this is what follows one poor period? If the real answer is a cost or a delay, the skin should say that.
- **Write two rows of the record by hand.** One all in and one split, under the skin's own column words. Read every sentence of `how_points_earn` against them.
- **Read each field beside the example skin's wording**, then beside the same field in every other held-out skin. Any sentence that is a noun swap of another gets reshaped.
- **Compare skeletons in the fields reading skips.** `ask`, `no_call`, the order of the limits in `bad_call`, and the last sentence of `rules`.
- **Search each proper noun**: the firm, the place, the game, and every channel name that could be a real place.
- **Confirm the prompt states no level, no history, and nothing about the world moving.**
- **Confirm the intro says why the record is empty**, with a reason in the thing and no hint of a cycle.

## After it is written

- **Commit on a branch in the private repo, never anywhere public.** No skin, timeline, or log that played one leaves the machines that run it, see [who can see them](contamination.md#who-can-see-them).
- **Fix it before the first headline run.** A skin's text never changes once a headline run has played it, see [what never changes](../../CONTRIBUTING.md#what-never-changes-without-a-new-pilot). After that a fix is a new skin.
- **The recognition check is the real test.** It asks each model where the prompt comes from. A skin that gets more hits than the others is the one to rewrite.

## What stays in the private repo

This page holds the method. The private repo's own README holds what would undo it if published:

- Which codename wears which story.
- Lessons from rewrites that name a story, a place or a sentence.
- Anything that quotes a skin's text, including drafts that were dropped.

If a lesson can be told without naming a skin, it belongs on this page.
