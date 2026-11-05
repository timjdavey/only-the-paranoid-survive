# Requirements

**What the benchmark must do, whatever game it uses.** How this game meets each one is in [decisions.md](decisions.md). What counts as a requirement is at [the end](#what-counts-as-a-requirement).

## Design principles

- **No measure is better than an inaccurate one.**
- **Only the skill is tested.** Not a proxy for it, and not the ability to learn rules, do sums or work an interface.
- **Evidence over story.** Scores come from what the agent did, and design choices from what studies found.
- **Honest error bars.**
- **Hard to game.**
- **Hard to saturate.**
- **Tied to real work.** The game looks like a job an agent is given.
- **Open and reproducible.**
- **Cheap enough to run on every release.**
- **One headline number a reader can understand without knowing the game.**
- **Says something to the wider field.** The result can sit beside other measures of agents.

## What the benchmark must do

### The world

- **The dynamics are legible.** A model can learn how the world works from what it is shown, and every model tested can. The test is noticing the rules moved, not working them out.
- **A change in one part barely moves the whole.** The world has enough parts that a change in one is faint in the totals, so an agent watching the whole misses it.
- **A rule the agent can state, and the change breaks it.** The world has a structure the agent will write down as a rule. The change makes that rule wrong, so the right response is to rethink, not retune. See [Why ten units](decisions.md#why-ten-units-in-five-kinds-by-two-sides).
- **A past where the plan worked.** Long enough that trusting it is reasonable, the same for every model, and the agent forms its belief about it before the world can change. What it doubts later must be its own belief, not someone else's words. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes).
- **The past sets an example.** The agent will copy how much the previous operator experimented, so that amount must be right, and its pull measured. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor).
- **The story adds no dynamics.** The nouns and framing must not imply behaviour, such as lag or trend, that the world doesn't have. See [Why names must match the generator](decisions.md#why-names-must-match-the-generator).
- **No hint of change.** Nothing in the prompt, the tools or the story says the world may move. Deciding to look again unprompted is the thing being measured. The one hint is in the data: the past shows changes the previous operator caught. See [How we avoid it simply being solved](decisions.md#how-we-avoid-it-simply-being-solved).

### The change

- **Bad luck comes in stretches.** Ordinary variation lasts a while, is partly shared across parts, and sometimes dips and recovers, so a bad month is a real explanation. See [Why weather has memory](decisions.md#why-weather-has-memory).
- **The old plan keeps paying, just less than the best one.** Nothing fails outright, so no alarm goes off, and every round of delay costs a little. See [Why the standing split still pays](decisions.md#why-the-standing-split-still-pays).
- **Changes at sizes from loud to faint.** Discernment is read off a curve across them. The proof of concept plays two, the full study five.
- **The change is to the dynamics, not to one number.** It edits how the world works, and some kinds can't be found by watching each part on its own. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event).
- **The change comes from outside.** Nothing the agent does moves the world, so every model plays the same world, the no-change run stays clean and the ceiling stays computable. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive).
- **A false alarm that begins exactly like the change.** The no-change run holds a stretch that starts on the same part, at the same time, on the same luck, and then recovers. See [Why the yoked dip](decisions.md#why-the-yoked-dip).
- **When and how the change arrives varies.** A change that always comes at the same time can be learnt rather than noticed.

### The agent

- **Seeing costs something.** Watching a part takes budget off the plan, and a bigger spend sees more clearly. The part that improves is one the plan doesn't fund, so it is never seen for free. Deciding to look is the decision. See [Why attention is scarce](decisions.md#why-attention-is-scarce).
- **The response is a dial, not a switch.** How sure the agent is shows in how far it moves. See [Why a budget split](decisions.md#why-a-budget-split).
- **What the agent does is the record.** Suspicion is read from actions, never from a question about whether anything has changed. See [Why tools](decisions.md#why-tools).
- **Arithmetic is not the test.** The agent can check its numbers reliably, so a failure is one of judgement. See [Why a code tool](decisions.md#why-a-code-tool).

### The score

- **Every change is paired with the same world where nothing changes.** Same luck, same past, same notes. Without it, doubting everything would always pay. See [Why the yoked dip](decisions.md#why-the-yoked-dip).
- **Too jumpy and too slow are told apart.** Each is reported on its own, so a model that doubts everything and one that doubts nothing can't score the same. See [Why each trait lives in one kind of run](decisions.md#why-each-trait-lives-in-one-kind-of-run).
- **Every score sits between a floor and a ceiling.** The floor is a player that never changes the plan. The ceiling is the best player we can build. A score says how much of what was knowable the model found. See [Why two bots bound the game](decisions.md#why-two-bots-bound-the-game).
- **One reading uses none of our own machinery.** No bot and no true values from our simulation, so a flaw in either shows as a disagreement. See [Catch rate](measures.md#catch-rate-a-backup).
- **Every change size worth catching.** If the best player doesn't gain from acting on a size, the rational play is to stay, and that size tells us nothing. See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter).
- **Every rule the score uses is told to the agent.** No hidden cut-off decides what counts as a look or a switch. See [Why attention is scarce](decisions.md#why-attention-is-scarce).
- **No fixed strategy scores well.** Always switching, never switching, switching at a set time and playing at random all score well below the ceiling. See [Why the bots set the difficulty](decisions.md#why-the-bots-set-the-difficulty).

### The suite

- **At most $100 a model for the proof of concept.** Cheap enough to run every new model on release. The current estimate is above this, see [What it costs](measures.md#what-it-costs).
- **Error bars that split two frontier models at that budget.** A score whose bars overlap for every pair can't be plotted over time.
- **It can get harder on the same scale.** When models reach the ceiling, a harder edition exists and its scores sit on the same axis. See [Why discernment is the full study headline](decisions.md#why-discernment-is-the-full-study-headline).
- **The story must not move the score much, and we measure how much it does.** The same game in more than one dress, with the spread reported. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface).
- **Frozen and published, all but a private set.** The same worlds, past and bots for every model, so a score today compares with one next year. Everything is released except a set held back to catch a model that learnt the public one. See [Why publish all but a private set](decisions.md#why-publish-all-but-a-private-set).

## What counts as a requirement

Before adding a line to this page, check it against these.

- **It says what the game must do, not how.** A different game could meet it another way.
- **It is strategic, not specific.** It may name the parts any such game has: a world, a past, a plan, a change, a score. It may not name a number, a mechanism or a component. "The dynamics are legible" is a requirement. "Ten units" is a decision.
- **A cold reader can understand it.** If it only makes sense once you know the game, it belongs in [decisions.md](decisions.md).
- **It is not a value.** Values go under [design principles](#design-principles). "Only the skill is tested" is a principle. "Arithmetic is not the test" is the requirement it leads to.
- **It links to the decision that meets it**, where one exists.
