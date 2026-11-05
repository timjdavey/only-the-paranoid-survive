# Requirements

## Design principles

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

## What the benchmark must do

Grouped by the part of a run each one shapes, in the order a run happens, from the briefing to the score.

### What the agent is given

- **Rules simple enough for every model to learn.** The test is noticing change, not working out rules. A model that never learns the rules can't be scored on noticing they moved. At heart the game asks when one of ten streams of results changed.
- **A world with somewhere to hide and a rule to rethink.** Ten units, five kinds by two sides, with the change in one. The record funds both sides alike, and the change makes side matter. See [Why ten units](decisions.md#why-ten-units-in-five-kinds-by-two-sides).
- **Names that match how the game behaves.** Every unit yields in the week it is bought, in every skin, so no noun imports a belief about lag or trend the generator doesn't have. See [Why names must match the generator](decisions.md#why-names-must-match-the-generator).
- **A record with a long, good run, and notes the agent wrote itself.** Trust needs a past, and the record gives every model the same one. The notes are the agent's own, written before the world can change, so what it doubts later is its own belief. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes).
- **A record written by a bot.** The record shows the agent how much to experiment, so that should be the right amount. Its author is the reference bot, toned down to read as a steady operator, and the pilot tries a steady and a jittery version once to see how much the style matters. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor).
- **No hint of change in the prompt or the skin.** Any of the words change, probe, commit, experiment, explore or exploit would give the game away. Deciding to look again unprompted is the thing being measured. The one hint is in the data: the record shows changes the previous operator caught.

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

- **A matching run on each seed where nothing changes.** Without it, doubting everything would always pay. It is where jumpiness shows, most sharply at the dip built to start like the change.
- **Each trait read in the run where it is cleanest.** Paranoia in the no-change run, caution and conviction in the change runs. These are the parts of [the question](measures.md#the-question), and one number would hide which one failed. See [Why each trait lives in one kind of run](decisions.md#why-each-trait-lives-in-one-kind-of-run).
- **Every score read against the reference bot and the no-update bot**, which keeps the standing split to the end. Each measure becomes a gap against what was knowable, bounded above and below. See [Why two bots bound the game](decisions.md#why-two-bots-bound-the-game).
- **A backup that needs no oracle.** Both headline scores lean on the reference bot and our generator's true levels, which could set a fake target. So we also report the catch rate: how often the agent switches in a change run without a false alarm in its no-change run. It reads only the agent's own shares.
- **Every change size worth catching.** Each change is played at a few sizes, called amplitudes. If the reference bot doesn't gain from switching at one of them, the rational play is to stay, and that size tells us nothing. See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter).

### What the suite must do

- **At most $100 a model for the proof of concept.** Cheap enough to run every new model on release. The current estimate is above this, see [What it costs](measures.md#what-it-costs).
- **Error bars that split two frontier models at that budget.** A score whose error bars overlap for every pair can't be plotted over time.
- **A condition the best models still find hard.** Otherwise every model scores near the top within a few releases and the line goes flat. The proof of concept's headline tops out at 1, which is accepted until the full study.
- **Skins whose effect is known.** Four skins over one interface, with the spread across them reported beside the spread across models. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface).
- **Everything published except a private set.** Anyone can rerun a model, and the private set catches a model that learnt the public one. See [Why publish all but a private set](decisions.md#why-publish-all-but-a-private-set).
