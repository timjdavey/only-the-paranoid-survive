# Requirements

**What the benchmark must do, whatever game it uses.** A requirement says what the game must do, not how, in words a cold reader can follow, and links to the decision that meets it. The full rules are at [the end](#what-counts-as-a-requirement). How this game meets each one is in [decisions.md](decisions.md).

## Design principles

- **No measure is better than an inaccurate one.**
- **Only the skill is tested.** Not a proxy for it, and not the ability to learn rules, do sums or work an interface.
- **Evidence over story.** Scores come from what the agent did, and design choices from what studies found.
- **Honest error bars.** A difference without a bar is not a finding.
- **Hard to game.** A model can't raise its score without the skill.
- **Hard to saturate.** A harder edition exists before models reach the ceiling.
- **Tied to real work.** The game looks like a job an agent is given.
- **Open and reproducible.** Anyone can rerun it and get the same number.
- **Cheap enough to run on every release.**
- **Says something to the wider field.** The result can sit beside other measures of agents.

## What the benchmark must do

Each line ends with its status. *Met* means a decision meets it. *Open* means it is not met yet. *Unmeasured* means only a run can tell.

### The world

- **The dynamics are legible.** A model can learn how the world works from what it is shown, and every model tested can. The test is noticing the rules moved, not working them out. *Unmeasured.*
- **A change in one part barely moves the whole.** The world has enough parts that a change in one is faint in the totals, so an agent watching the whole misses it. *Met.*
- **Bad luck comes in stretches.** Ordinary variation lasts a while, is partly shared across parts, and sometimes dips and recovers, so a bad month is a real explanation. See [Why weather has memory](decisions.md#why-weather-has-memory). *Met.*
- **A past where the plan worked.** Long enough that trusting it is reasonable, the same for every model, and the agent forms its belief about it before the world can change. What it doubts later must be its own belief, not someone else's words. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes). *Met.*
- **The past sets an example.** The agent will copy how much the previous operator experimented, so that amount must be right, and its pull measured. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor). *Met.*
- **The story adds no dynamics.** The nouns and framing must not imply behaviour, such as lag or trend, that the world doesn't have. See [Why names must match the generator](decisions.md#why-names-must-match-the-generator). *Met.*
- **The only hint of change is in the past.** Nothing in the prompt, the tools or the story says the world may move. The past shows changes the previous operator caught, which says change happens, not when or where. Deciding to look again unprompted is the thing being measured. See [How we avoid it simply being solved](decisions.md#how-we-avoid-it-simply-being-solved). *Met.*

### The change

- **A rule the agent can state, and the change breaks it.** The world has a structure the agent will write down as a rule. The change makes that rule wrong, so the right response is to rethink, not retune. See [Why ten units](decisions.md#why-ten-units-in-five-kinds-by-two-sides). *Met.*
- **The old plan keeps paying, just less than the best one.** Nothing fails outright, so no alarm goes off, and every round of delay costs a little. See [Why the standing split still pays](decisions.md#why-the-standing-split-still-pays). *Met.*
- **The signal is dialled from loud to faint.** Discernment is read off a curve across the dial, so it says where a model stops profiting, not whether. See [Discernment](measure-headline.md#discernment-the-full-study-headline). *Met.*
- **The change is to the dynamics, not to one number.** It edits how the world works, and some kinds can't be found by watching each part on its own. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event). *Open.* The proof of concept plays one kind.
- **The change comes from outside.** Nothing the agent does moves the world, so every model plays the same world, the paired run where nothing changes stays clean and the ceiling stays computable. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive). *Met.*
- **When and how the change arrives varies.** A change that always comes at the same time can be learnt rather than noticed. *Met.*

### The agent

- **Seeing costs something.** Watching a part takes budget off the plan, and a bigger spend sees more clearly. Deciding to look is the decision. See [Why attention is scarce](decisions.md#why-attention-is-scarce). *Met.*
- **The response is a dial, not a switch.** How sure the agent is shows in how far it moves. See [Why a budget split](decisions.md#why-a-budget-split). *Met.*
- **What the agent does is the record.** Suspicion is read from actions, never from a question about whether anything has changed. See [Why tools](decisions.md#why-tools). *Met.*
- **Arithmetic is not the test.** The agent can check its numbers reliably, so a failure is one of judgement. See [Why a code tool](decisions.md#why-a-code-tool). *Met.*
- **One go, no replay.** The task is a job, not a puzzle to retry. A wrong move costs every round it stands and can be undone the next. See [Why a single long run](decisions.md#why-a-single-long-run-rather-than-multiple-tries) and [Why no lock-in](decisions.md#why-no-lock-in). *Met.*

### The score

- **Every change is paired with the same world where nothing changes.** Same luck, same past, same briefing, and a false alarm that looks like the change. Without it, doubting everything would always pay. See [Why the yoked dip](decisions.md#why-the-yoked-dip). *Met.*
- **Too jumpy and too slow are told apart.** Each is reported on its own, so a model that doubts everything and one that doubts nothing can't score the same. See [Why each trait lives in one kind of run](decisions.md#why-each-trait-lives-in-one-kind-of-run). *Met.*
- **Every score sits between a floor and a ceiling.** The floor is a player that never changes the plan. The ceiling is the best player we can build. A score says how much of what was knowable the model found. See [Why two bots bound the game](decisions.md#why-two-bots-bound-the-game). *Met.*
- **One headline number a reader can understand without knowing the game.** See [Why performance is the proof of concept headline](decisions.md#why-performance-is-the-proof-of-concept-headline). *Met.*
- **One reading uses none of our own machinery.** No bot and no true values from our simulation, so a flaw in either shows as a disagreement. See [Catch rate](measure-headline.md#catch-rate-a-backup). *Met.*
- **Every size tested is worth acting on.** If the best player doesn't gain from acting on a size, the rational play is to stay, and that size tells us nothing. See [Why performance is the arbiter](decisions.md#why-performance-is-the-arbiter). *Open.* The margin is set with the bots.
- **Every rule the score uses is told to the agent.** No hidden cut-off decides what counts as a look or a switch. The look threshold is the case in point. See [Why attention is scarce](decisions.md#why-attention-is-scarce). *Met.*
- **No fixed strategy scores well.** Always switching, never switching, switching at a set time and playing at random all score well below the ceiling. See [Why the bots set the difficulty](decisions.md#why-the-bots-set-the-difficulty). *Open.* Checked with the bots.
- **The score is checked against general ability.** A stronger model must not score higher for free, and we must be able to tell. See [Why older models and a general ability check](decisions.md#why-older-models-and-a-general-ability-check). *Met.*

### The suite

- **Cheap enough to run every new model on release.** The budget and the current estimate are in [runs-and-cost.md](../spec/runs-and-cost.md#cost-per-model). *Open.* The estimate is above the budget.
- **Error bars that split two frontier models at that budget.** A score whose bars overlap for every pair can't be plotted over time. *Unmeasured.*
- **It can get harder on the same scale.** When models reach the ceiling, a harder edition exists and its scores sit on the same axis. See [Why discernment is the full study headline](decisions.md#why-discernment-is-the-full-study-headline). *Open.*
- **The story must not move the score much, and we measure how much it does.** The same game in more than one dress, with the spread reported. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface). *Unmeasured.*
- **Frozen and published, all but a private set.** The same worlds, past and bots for every model, so a score today compares with one next year. Everything is released except a set held back to catch a model that learnt the public one. See [Why publish all but a private set](decisions.md#why-publish-all-but-a-private-set). *Met.*
- **Older models score on the same scale, and the headline sits beside other measures of agents.** So a line over releases exists from day one, and the result can be read against the wider field. See [Why older models and a general ability check](decisions.md#why-older-models-and-a-general-ability-check). *Met.*

## What counts as a requirement

Before adding a line to this page, check it against these.

- **It says what the game must do, not how.** A different game could meet it another way.
- **It is strategic, not specific.** It may name the parts any such game has: a world, a past, a plan, a change, a score. It may not name a number, a mechanism or a component. "The dynamics are legible" is a requirement. "Ten units" is a decision.
- **A cold reader can understand it.** If it only makes sense once you know the game, it belongs in [decisions.md](decisions.md).
- **It is not a value.** Values go under [design principles](#design-principles). "Only the skill is tested" is a principle. "Arithmetic is not the test" is the requirement it leads to.
- **It is not a status.** Progress goes in [TODO.md](../../TODO.md). The tag at the end of each line is the one exception.
- **It links to the decision that meets it**, where one exists.
