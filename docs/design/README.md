# Design

| Page | What's in it |
|---|---|
| [mechanics.md](mechanics.md) | The logic behind the game design |
| [alternatives.md](alternatives.md) | A small collection of the different options of games we weighed up |
| [measures.md](measures.md) | What measurements we take and why |
| [decisions.md](decisions.md) | The  |
| [architecture.md](architecture.md) | How the code is split into layers, and how that keeps it hard to game |
| [future.md](future.md) | Extensions beyond the full study |
| [glossary.md](../glossary.md) | The one word we use for each idea, and the older names it replaces |

The studies it builds on are in [prior](../prior/README.md). What to do next is in [TODO.md](../../TODO.md).

## The question

How good is an agent at telling a change in the dynamics of a system from ordinary bad luck, and so at knowing when its own notes have gone stale?

That one question breaks into six traits, each read from the log of a run. Three are abilities, where more is better. Three are dispositions, where the score is a gap from the reference bot and zero is ideal. How each is measured is in [measures.md](measures.md#the-traits).

- **Performance.** Takes the gain on offer
- **Discernment.** Profits from small changes
- **Insight.** Rewrites what it believed, and acts on it
- **Paranoia.** Doubts notes that are working
- **Caution.** Waits for evidence
- **Conviction.** Acts on the switch

## Design principles

What we care about in the design of a benchmark.

- Open and reproducible
- Cheap and repeatable
- Hard to saturate
- Tied to real work
- Connected with the wider ecosystem themes
- Honesty with error bars
- Directly measures this skill, not a proxy
- Hard to game
- Ideally a single communicable headline number
- Evidence over story

## Two tiers

The benchmark is built in two tiers over the same game. The proof of concept has to show one thing, that the measure separates models with usable error bars, so it leads with one continuous number. The full study adds the runs that a threshold needs. See [Why two tiers](decisions.md#why-two-tiers).

| | Proof of concept | Full study |
|---|---|---|
| Headline | Performance, the share of the gain on offer the model took | Discernment, the smallest drop the model acts on |
| Runs per seed | A briefing, a no-change run and two change sizes | A briefing, a no-change run and five change sizes |
| Kind of change | The level change | Level, then coupling, gain and observation |
| Seeds | 20 | About 30 |
| Runs a model | 60 and 20 briefings, about $100 at the target | About 180 at one reasoning setting |
| Reasoning | One setting | A sweep |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | Four skins and two history styles in the pilot, to decide pooling | A real task with a stale handoff note as well |

## Requirements

What the benchmark must do, grouped by the part of a run each one constrains. The groups follow a run from briefing to score.

### What the agent is given

- **Rules simple enough for every model to learn.** The test is noticing change, not working out rules. A model that never learns the rules can't be scored on noticing they moved. Underneath, the game is a changepoint problem on ten streams.
- **A world with somewhere to hide and a rule to rethink.** Ten units, five kinds by two sides, with the change in one. The record funds both sides alike, and the change makes side matter. See [Why ten units](decisions.md#why-ten-units-in-five-kinds-by-two-sides).
- **Names that match how the game behaves.** Every unit yields in the week it is bought, in every skin, so no noun imports a belief about lag or trend the generator doesn't have. See [Why names must match the generator](decisions.md#why-names-must-match-the-generator).
- **A record with a long, good run, and notes the agent wrote itself.** Trust needs a past, and the record gives every model the same one. The notes are the agent's own, written before the world can change, so what it doubts later is its own belief. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes).
- **A record written by a bot.** The record demonstrates how much to experiment, so its author is the reference bot, damped, and its style is sized once in the pilot. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor).
- **No hint of change in the prompt or the skin.** Naming change, probe, commit, experiment, explore or exploit hands over the schedule. Deciding to look again unprompted is the thing being measured. The one hint is in the data: the record shows changes the previous operator caught.

### How the notes go stale

- **Weather with memory, so a bad month is ordinary.** A streak of bad luck must be a real explanation, or spotting the change is trivial. Each unit has stretches that fade, every unit shares some luck, and the odd unit dips and recovers. See [Why weather has memory](decisions.md#why-weather-has-memory).
- **A stale split that keeps winning, just less than the best one.** That is the Grove case. Every round on the stale split forgoes a little output, so slow and very slow models end at different scores. See [Why the standing split still pays](decisions.md#why-the-standing-split-still-pays).
- **Changes at sizes from loud to faint.** The proof of concept plays one loud and one faint. The full study plays five, because discernment is read off a curve across them.
- **A change that is an edit to the world's dynamics.** The generator has four blocks and a change edits one. The proof of concept edits the level. Later rungs edit coupling, gain and observation, which no per-unit tracker can find. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event).
- **A change driven from outside.** Nothing the agent does moves the levels, so the no-change run stays clean and the reference bot stays a yardstick. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive).
- **A false alarm that starts like the real thing.** The no-change run holds a dip on the same unit, starting on the same round at the same slope, that then recovers. See [Why the yoked dip](decisions.md#why-the-yoked-dip).
- **A start and shape that vary by seed.** A change that always starts at round 5 can be learnt rather than noticed.

### What the agent can do

- **Looking costs something.** A share under a told threshold buys nothing, so the standing split sees four units and the rest are dark until the agent pays. Above it, a bigger share buys a sharper reading. Then looking is a decision, and the unit that rises is never heard for free. See [Why attention is scarce](decisions.md#why-attention-is-scarce).
- **A response sized on a scale, not a switch.** The share shows how sure the model is, not only whether it moved.
- **Every move taken as a logged action.** What the agent suspects is read from what it does, not from what it says.
- **A way to check the numbers.** A sandboxed code tool, so a model that would notice the change fails only on judgement, not on arithmetic. See [Why a code tool](decisions.md#why-a-code-tool).

### How it is scored

- **A matching run on each seed where nothing changes.** Without it, paranoia always wins. It is where jumpiness shows, and the yoked dip is where it shows sharpest.
- **Each trait read in the run where it is cleanest.** Paranoia in the no-change run, caution and conviction in the change runs. These are the parts of [the question](#the-question), and one number would hide which one failed. See [Why each trait lives in one kind of run](decisions.md#why-each-trait-lives-in-one-kind-of-run).
- **Every score read against the reference bot and the no-update bot.** Each measure becomes a gap against what was knowable, bounded above and below. See [Why two bots bound the game](decisions.md#why-two-bots-bound-the-game).
- **A backup that needs no oracle.** Both headlines lean on the reference bot and our generator's true levels, which could set a fake target. So the catch rate, which reads only the agent's own shares and its no-change run, is reported beside them.
- **Every amplitude on the grid worth catching.** If the reference bot doesn't gain from switching at an amplitude, the rational play is to stay and the amplitude says nothing. See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter).

### What the suite must do

- **At most $100 a model for the proof of concept.** Cheap enough to run every new model on release. The current estimate is above this, see [What it costs](measures.md#what-it-costs).
- **Error bars that split two frontier models at that budget.** A score whose error bars overlap for every pair can't be plotted over time.
- **A condition the best models still find hard.** Otherwise every model scores near the top within a few releases and the line goes flat. The proof of concept's headline tops out at 1, which is accepted until the full study.
- **Skins whose effect is known.** Four skins over one interface, with the spread across them reported beside the spread across models. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface).
- **Everything published except a private set.** Anyone can rerun a model, and the private set catches a model that learnt the public one. See [Why publish all but a private set](decisions.md#why-publish-all-but-a-private-set).

## Limitations of this design

| Limitation | Why we accepted it | How to overcome, and at which tier |
|---|---|---|
| **A headline that tops out at 1.** Performance can't be plotted over releases once models match the reference bot | No model will be near it before the full study exists, and one continuous number is what a proof of concept needs. See [Why two tiers](decisions.md#why-two-tiers) | Full study: discernment |
| **One kind of change in the proof of concept.** A per-unit tracker can find a level change, so insight is weaker than it will be | The level change is the one with a known bot and one paragraph to explain. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event) | Full study: coupling, gain and observation |
| **No human baseline.** A score says how models compare with each other, not with people | Comparing models over time needs no human anchor, and recruiting people costs time a proof of concept doesn't have | Beyond the full study: human baseline |
| **One reasoning setting per model.** Scores are a lower bound for models that do better with more thinking | Budget. Each model runs at its standard high setting, so the comparison is fair even if it isn't complete | Full study: reasoning sweep |
| **One generator.** A model could be good at this game and nothing else | Four skins widen the surface without the cost of a second game. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface) | Full study: one real agentic task with a stale handoff note. Beyond: a second game. See [future work](future.md#whether-it-holds-outside-our-game) |
| **Four skins, none free of priors.** A plant says stable and a market says drifting | The abstract skin is the anchor, the fictional skin the headline, and the spread is a result | Beyond: the time unit and shown inputs as factors |
| **Test awareness can be measured, not removed** | The no-change run prices any experimenting it causes, and the scan reports it. See [Why the game is hard to game](decisions.md#why-the-game-is-hard-to-game) | Full study: every transcript read |
| **A small sample.** Twenty seeds on a few models | We are aiming to only show the measure works, so model comparisons are early reads | Full study: every model on release, more seeds and amplitudes |
| **The change never reacts to the agent.** Real plans often wear out because they are leaned on, and real units pay out late | A reflexive change muddies the no-change run, the reference bot and the error bars. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive) | Beyond: reflexive change, lagged units |
| **A past the agent read, not lived**, per Schubert | The record gives every model the same grounding and cuts cost to one briefing and the live horizon. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes) | Beyond: full live run |
| **The record demonstrates a style** | Its author is the reference bot, so the style is the right amount, and the pilot sizes the cue. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor) | Beyond: a history style sweep |
| **A switch is never sticky** | A wrong split forgoes output every round it stands, and the 40 round limit prices time. See [Why no lock-in](decisions.md#why-no-lock-in) | Beyond: cost ratio |
| **Our generator could set a fake target** | The catch rate backup reads only the agent's own shares, and every skin runs in the pilot | Full study: real-task check. Beyond: realism ladder, second game |
