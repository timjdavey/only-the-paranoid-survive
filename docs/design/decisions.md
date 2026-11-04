# Design decisions

**Every choice behind the game, what else it could have been, and why we picked this one.**

Each decision starts with the question it answers and the options we weighed. The chosen option is in bold and ticked. The bullets under it say why, and a **Cost** bullet names what we gave up. The values behind the choices are the [design principles](README.md#design-principles). The benchmark has two tiers, a proof of concept and a full study, and a decision that differs between them says so. See [Why two tiers](#why-two-tiers).

## At a glance

| Decision | Chosen | Main alternative |
|---|---|---|
| [How the agent responds](#why-a-budget-split) | A budget split across ten units, with volume scaling with spend | Pick one unit and a stake |
| [What ordinary variation looks like](#why-weather-has-memory) | Weather with memory, a shared factor and dips | Coin flips at a fixed rate |
| [What makes the world](#why-the-generator-is-a-state-space-system) | A four block state-space system | Ten independent arms |
| [What a change is](#why-a-change-is-a-typed-event) | An edit to one block, the level in the proof of concept | A mean shift only |
| [What a small share buys](#why-attention-is-scarce) | Nothing under a told threshold, then a reading that sharpens with spend | A noisy reading at any share |
| [How the world is laid out](#why-ten-units-in-five-kinds-by-two-sides) | Ten units, five kinds by two sides, the change in one | Weekly conditions the agent is handed, or dashboard signals |
| [What a skin may call things](#why-names-must-match-the-generator) | Nouns that carry no lag, trend or memory the generator lacks | Brand, SEO, referrals |
| [What makes it more than a bandit](#why-this-is-more-than-a-drifting-bandit) | Weather with a yoked false alarm, typed changes, a no-change twin, silence about change | A drifting bandit |
| [How luck is shared](#why-shared-luck-is-a-stream-of-numbers) | A stream of numbers per unit per round, and per weather term | Noise added to each reading |
| [How the agent plays](#why-tools) | Tool calls, one round per call | Ask it whether anything has changed |
| [Whether it can run code](#why-a-code-tool) | A sandboxed `compute` tool | No code |
| [How many tries](#why-a-single-long-run-rather-than-multiple-tries) | One run per seed | Several playthroughs, the rules changing in one |
| [How bad the stale split gets](#why-the-standing-split-still-pays) | Never below a 0.55 level | A unit worse than the rest |
| [What causes the change](#why-the-change-is-not-reflexive) | Something outside the agent | The agent leaning on its notes |
| [What the no-change run holds](#why-the-yoked-dip) | A dip that starts like the change, on the same seed | Quiet rounds only |
| [Whether a switch sticks](#why-no-lock-in) | Free to undo | A switching cost |
| [Where the agent's beliefs come from](#why-the-agent-writes-its-own-notes) | It reads the record and writes its own notes at a briefing | A plan written by a previous agent |
| [Who wrote the record](#why-the-record-comes-from-a-bot-and-its-style-is-a-factor) | The damped reference bot, with its style a pilot factor | A model's own live run |
| [What the game looks like](#why-four-skins-over-one-interface) | Four skins over one interface, the fictional one the headline | One public story skin |
| [How much is built first](#why-two-tiers) | A proof of concept, then a full study | One funded edition |
| [What is measured](#why-traits-in-two-kinds) | Six traits in two kinds | One detection score |
| [Where each trait lives](#why-each-trait-lives-in-one-kind-of-run) | One kind of run each | Both runs |
| [How doubt is read](#why-split-doubting-from-switching) | Paranoia, caution and conviction as three traits | One detection time |
| [How caution is read](#why-caution-is-a-cusum-line) | The CUSUM line, fed the weather model | Switch minus first doubt |
| [How insight is read](#why-insight-reads-the-notes) | The shares on the changed side, and the rewritten notes | The shares alone |
| [What scores are measured against](#why-two-bots-bound-the-game) | A reference bot and a retune bot | Other models |
| [How complacency is made](#complacency-as-a-parameter-not-a-history) | Rounds of record before the change | Real long tasks |
| [How a round is scored](#why-each-round-is-scored-on-expected-output) | Expected output at the true levels | Real output |
| [How lags are reported](#why-first-doubt-and-the-switch-are-read-as-curves) | Diagnostic curves by round | Mean round |
| [Curiosity](#why-curiosity-is-a-diagnostic-not-a-trait) | A diagnostic, not a trait | Score it from experiments |
| [The proof of concept headline](#why-edge-captured-is-the-proof-of-concept-headline) | Edge captured, pooled by output | A threshold from two amplitudes |
| [The full study headline](#why-discernment-is-the-full-study-headline) | The amplitude where edge captured crosses a set level | The amplitude caught half the time |
| [What the arbiter is](#why-edge-captured-is-the-arbiter) | Edge captured | Discernment alone |
| [Efficiency](#why-efficiency-is-in-game-spend) | Output given up to experiments | Token cost |
| [Stopping a trivial solve](#how-we-avoid-it-simply-being-solved) | Weather, a split that still works, no hint in the prompt | Tell it change may come |
| [Stopping gaming](#why-the-game-is-hard-to-game) | A no-change run, private seeds, fixed bots, scans | Trust the public seeds |
| [Runs per seed](#why-one-no-change-run-and-a-grid-per-seed) | One no-change run and a grid of amplitudes | Cross every dial |
| [Who sets difficulty](#why-the-bots-set-the-difficulty) | The bots | Today's models |
| [Sample](#why-more-seeds-not-repeats) | Seeds, each run once | One seed, run many times |
| [Comparators](#why-older-models-and-a-general-ability-check) | An older model and general ability scores | Today's models alone |
| [Release](#why-publish-all-but-a-private-set) | Everything but a private set | Everything |

## The game

### Why a budget split

**Question.** How does the agent respond, so that its confidence shows?

| Option | Problem |
|---|---|
| Pick one unit, with no share | A binary answer can only be early or late, so doubt never shows |
| Pick one unit and a stake | The old coin flip game. One flip a round carries too little evidence, and it needs a sizing rule, a cap against ruin and cut-offs the agent never knew about. See [alternatives.md](alternatives.md#why-the-coin-flip-game-was-dropped) |
| A flat split, the same every round | Nothing to read |
| **Shares of a fixed budget across ten units, with saturation and a threshold** ✓ | |

- **The response is graded.** Each extra pound on a unit buys a little less, so the best split moves smoothly with belief rather than jumping from one unit to another. A slipping split can be met with an experiment, a retune or a rethink.
- **Testing and committing are the same dial.** A small share above the threshold is a look, and a large one is a switch, so no cut-off decides which is which.
- **It looks like real work.** Splitting spend across units is what an operator does every week, in every skin.
- **Cost.** The shares must sum to one, which a model may fumble. The tool rejects a bad split with a neutral error.

### Why weather has memory

**Question.** What does ordinary variation look like, so that a bad stretch is a real explanation?

| Option | Problem |
|---|---|
| Coin flips at a fixed level | No runs. Three bad weeks in a row are strong evidence of change, so the agent is right to move and nothing is ever ambiguous |
| A seasonal wave | Learnable from 200 rounds of record, so a good agent subtracts it and it becomes a clue, not weather |
| Noise with memory on each unit alone | A bad week for everyone would read as ten units changing at once |
| **A per-unit term with memory, a shared factor and rare dips that recover** ✓ | |

- **A bad month is ordinary.** With memory 0.8 a shock is half gone after three rounds, so a bad week tends to be followed by another and then fades. A ramp looks like one until about round ten.
- **A shared factor makes a bad week for everyone ordinary**, and a bad week for one unit while the others are fine the thing to notice.
- **Dips are the false alarm with teeth.** A fall that starts like a change and then recovers. The record holds several the previous operator sat through, so the agent can learn what one looks like.
- **A change is told apart by two things only.** It persists, and a unit on the same side rises. That is the judgement the README promises.
- **Cost.** The reference bot needs a two-state belief, dip or shift, instead of a plain hazard, and the CUSUM bot must be fed the weather model or it fires on every dip. Memory, spread and dip size are three more dials to tune in [next step 1](../../TODO.md#next-steps).

### Why the generator is a state-space system

**Question.** What makes the world, so that a change can be a change in how it behaves?

| Option | Problem |
|---|---|
| Ten independent arms with a mean each | The only change possible is a mean shift, so a tracker that updates ten means wins and nothing has to be rethought |
| An open simulator, as rich as we like | No principled bot can model it, so the yardstick stops being the best we can build and edge captured loses its meaning |
| **A linear Gaussian state per unit, a coupling matrix, an observation step and a regime switch** ✓ | |

| Block | Holds | A change here |
|---|---|---|
| Inputs | The shared factor, and anything a later skin shows | Nothing yet |
| State | A level per unit and its weather | A level ramps |
| Coupling | How units pull on each other | Two units start to compete, or to feed each other |
| Observation | Saturation, the threshold, the count | Returns flatten, or yield is credited to the wrong unit |

- **A change is an edit to one block.** That is what "a change in dynamics" means in code, and it gives the kinds of change below.
- **The family has a filter.** A Kalman-style filter with a changepoint belief over the parameters tracks it, so the reference bot stays principled however rich the coupling gets.
- **It stays one file.** Four blocks and a config.
- **Cost.** The filter is more work than a Beta belief per unit, and richer families than this one are off the table.

### Why a change is a typed event

**Question.** Which kinds of change does the suite run?

| Option | Problem |
|---|---|
| The level change only, for good | Insight stays hollow: a per-unit tracker finds every change, so there is no rule to rethink |
| Every kind from the start | Four generators, four bots and four tunings before anything is known |
| **The level change in the proof of concept, with coupling, gain and observation as full-study rungs** ✓ | |

| Kind of change | What the agent sees | What a per-unit tracker does |
|---|---|---|
| Level | One unit's yield drifts down and, if it looks, another's is up | Catches it. This is today's game |
| Coupling | Two units wobble together | Sees two means move, never sees why |
| Gain | Volume falls at the same level | Reads a volume problem as a level problem |
| Observation | Yield moves between units while output barely does | Chases a number that isn't real |

- **The ladder makes insight real.** On the later rungs the retune bot and a per-unit tracker both fail, and only an agent that asks what kind of change this is wins.
- **The generator is built for all four now**, so a kind of change is config, not a rewrite.
- **Cost.** The proof of concept tests one kind, and that is a [limitation](README.md#limitations-of-this-design) it says out loud.

### Why attention is scarce

**Question.** What does a small share buy?

| Option | Problem |
|---|---|
| A full reading of every unit each round | Watching is free, so nothing is ever tested |
| A reading that sharpens with spend alone | The old answer. A 5% sliver on the unit that rises buys 27 impressions a round at N = 400, and hears an 11 point rise within ten rounds, so the standing split catches every change without a decision |
| A hidden cut-off below which nothing is reported | A rule the agent never knew about, which was why it was rejected before |
| **A told threshold below which a unit buys nothing, then a reading that sharpens with spend** ✓ | |

- **The agent can't watch everything.** The standing split funds four units. Seeing any other unit costs a share above the threshold, taken off the best units. Attention is a budget.
- **The rise is silent until it looks.** C0 sits under the share saturation would give it, so the standing split reads nothing from it. A look answers the question at once, and the skill is choosing to look.
- **It is a rule, not a cut-off.** The threshold is in the `allocate` tool's description. The scoring has no hidden line.
- **Precision still scales with spend.** Above the threshold, 3% buys 6 of volume and 25% buys 43, so a cheap look is a slow one.
- **Cost.** A model that never looks beyond the standing split cannot find the rise, which is the point. Budget put under the threshold is lost, which a model may fumble once.

### Why ten units in five kinds by two sides

**Question.** How is the world laid out, so that the change has somewhere to hide and there is a rule to rethink?

| Option | Problem |
|---|---|
| Three kinds and two weekly conditions, one a promotion week | The old answer. The change sat in half the rounds, behind the one clue the notes treated oddly, so there was nowhere for it to hide |
| Kinds plus weekly conditions the agent is handed, such as "this week's visitors are on mobile" | A real week is a blend, not one kind of visitor. A condition the agent is handed and can't set reads like a clue, and a frontier model will test it on the first round because that is good practice, not discernment |
| Kinds plus dashboard signals | Nobody could say what the right response to a signal is, so it was either a label for the change or a number to ignore |
| Many units with no structure | The change can only be one unit rising, so retuning catches it and there is nothing to rethink |
| **Ten units, five kinds by two sides, with the change in one** ✓ | |

- **A unit is the only thing funded.** Side is a tag on a unit, not a condition the week arrives in. The report has ten rows, every week.
- **The record asserts structure, and the change breaks it.** The previous operator funded both sides evenly, and the agent's own notes will say side doesn't matter. The change makes side matter on one kind.
- **The change can hide.** It hits one unit of ten. A player watching totals sees A slip a little overall.
- **The rule stays one line**: "on side 0, C now leads".
- **Cost.** Ten units is more to read than three, and the reference bot holds ten beliefs rather than three. The pilot checks whether the older model can hold ten in its head at all.

### Why names must match the generator

**Question.** What may a skin call the units?

| Option | Problem |
|---|---|
| Any realistic nouns | Brand, SEO or referrals import a belief about lag or stock that the generator doesn't have, so a careful model plays a game that isn't there |
| Nouns with a known trend | The market skin's AI placements story is one a 2026 model already believes, so it may switch on priors and get credit it didn't earn |
| **Nouns that carry no lag, trend or memory the generator lacks, checked by the skin lint** ✓ | |

- **Every unit yields in the week it is bought**, in every skin, so no noun imports a delay.
- **Direction priors are named, not hidden.** The market skin keeps its leak on purpose as one end of the skin test. See [Why four skins over one interface](#why-four-skins-over-one-interface).
- **Cost.** The nouns are a little duller than real accounts.

### Why this is more than a drifting bandit

**Question.** Underneath, this is a changepoint problem on ten streams. What makes it a test of telling change from weather rather than another bandit paper?

Prior drifting-bandit work, [Zhang](../prior/worlds-that-change.md#zhang-et-al-2025-llms-in-a-drifting-bandit), [Mellor and Shapiro](../prior/further-work.md#quickest-detection-and-drifting-bandits) and [BanditBench](../prior/worlds-that-change.md#banditbench-nie-et-al-2025-in-context-exploration), has memoryless noise, unstructured arms and a change that is only a mean moving. Four things here are different, and each is a decision on this page:

| Difference | Why it matters | Decision |
|---|---|---|
| **Weather with memory, and a yoked false alarm** | A bad stretch is a real explanation, and the no-change run holds one that starts exactly like the change | [Why weather has memory](#why-weather-has-memory), [Why the yoked dip](#why-the-yoked-dip) |
| **Typed changes** | A change is an edit to a block, and on the later rungs a per-unit tracker can't find it | [Why a change is a typed event](#why-a-change-is-a-typed-event) |
| **A no-change twin inside the headline** | A false alarm costs as much as a miss, on the same luck | [Why each trait lives in one kind of run](#why-each-trait-lives-in-one-kind-of-run) |
| **Silence about change** | No prompt, skin or tool says the world can move. The record shows that it has | [How we avoid it simply being solved](#how-we-avoid-it-simply-being-solved) |

- **It is barely a bandit.** The agent can fund many units at once, so the exploration dilemma is weaker than in a bandit. The threshold is what keeps looking costly.
- **Being a changepoint problem underneath is an asset.** Known theory, a reference bot we can build, and one paragraph to explain.
- **Cost.** A reader who skims will file it as a bandit. The README and the [prior-work page](../prior/README.md#at-a-glance) lead with the four differences for that reason.

### Why shared luck is a stream of numbers

**Question.** How do runs on the same seed share their luck?

| Option | Problem |
|---|---|
| Separate dice for each run | A change run can't be compared with its no-change run round by round, so far more runs are needed |
| One noise term per unit and round, added to the observed rate | A 3% look would see the same noise as a full share, so precision would no longer scale with spend |
| **A stream of numbers per unit per round, with yield counted on the first n, and a stream per weather term** ✓ | |

- **A bigger buy sees more of the same luck.** Every run on a seed draws from the same stream, so two splits differ only in how far down it they read. See [Shared luck](mechanics.md#shared-luck).
- **The weather is shared too.** Each weather term is drawn in advance, so the yoked dip and the ramp sit on the same bad and good weeks.
- **Precision still scales with spend.** A look reads a few numbers and a full share reads dozens.

### Why tools

**Question.** How does the agent play, and how do we see what it suspects?

| Option | Problem |
|---|---|
| Ask each round whether anything has changed | It says what sounds right, and the question hints at change |
| Show the whole log and ask for a split | No timing, so no lag to measure |
| Let it write moves in prose, and parse them | Scoring needs a judge |
| **Five [tools](mechanics.md#tools), one round per call** ✓ | |

- **What it does is the record.** Experimenting is an action, so suspicion is seen rather than asked.
- **The switch is visible.** It is the largest share on a side moving to a new unit, and a rewrite of the notes confirms it.
- **No judge.** The no-change run and the bots are read from the same log.

### Why a code tool

**Question.** May the agent run code?

| Option | Problem |
|---|---|
| No code | A model that must add up hundreds of rows in its head may fail on arithmetic, not judgement, and the score mixes the two |
| A shell or an open sandbox | It could read the generator, the seeds or the logs |
| **`compute(code)`: Python in a sandbox that sees only what the agent pastes in** ✓ | |

- **Deciding to check is the skill.** Choosing to write a changepoint check on the yield is what we want to see. Adding up counts in context is not.
- **It sees nothing new.** No files, no network, no engine. The only data in it is what the agent already saw and chose to paste.
- **The confound is measured.** Every scored run has the tool, and the pilot runs one model without it, so we see how far the tool moves the score.
- **Cost.** A fifth tool may hint that something is worth computing, so its description is neutral and passes the banned word lint. A model that writes a good test scores well even if it would miss the change by eye, which is the trade we take.

### Why a single long run rather than multiple tries

**Question.** Does the agent get one go at each world, or several?

| Option | Problem |
|---|---|
| Several playthroughs, the rules changing in one, as in EBR-bench | Real work has no replay. The early tries give a stable past, but the record does that more cheaply |
| **One run per seed, briefing to the end** ✓ | |

- **Closer to Grove**, and to complex real environments, where there is no replay.
- **Cost.** Learning across tries isn't tested. Multiple tries are an extension.

### Why the standing split still pays

**Question.** How bad does the stale split get?

| Option | Problem |
|---|---|
| The standing unit falls to 0.45 or below, as bad as the rest | The split stops being worth trusting, so the test is no longer Grove's |
| **The standing unit never falls below 0.55** ✓ | |

- **It is Grove's case.** The split keeps working, just worse than the best one.
- **Slow and very slow stay apart.** Every round on the stale split forgoes a little output, so the score falls steadily with delay rather than hitting a floor.
- **The fall is the amplitude.** A0 falls by it and C0 ends the same distance above A's old level, so the prize scales with the amplitude and the rise is never what the standing split hears. See [Why attention is scarce](#why-attention-is-scarce).

Three bots run on every seed before any model does, and the generator is tuned until they separate:

| Bot | Role | Warning sign |
|---|---|---|
| No-update bot | The floor: the standing split to the end | Wins almost nothing less than the reference bot, so the change is too small |
| [Retune bot](#why-two-bots-bound-the-game) | The retune bound | |
| Reference bot | The yardstick | Beaten by a fixed bot, so the scoring rewards a trick |

If a lucky no-update bot wins more real output than an unlucky reference bot on more than a few seeds, the change is too faint or the horizon too short.

### Why the change is not reflexive

**Question.** Does the change come from outside, or from the agent leaning on its notes?

| Option | Problem |
|---|---|
| Reflexive: the standing unit worsens the more the agent spends on it, and recovers when rested | Spoils four things the design leans on, below |
| A loop the agent drives, such as spend that builds a stock which lifts other units, or any lagged unit | The same four problems, and a game about pacing spend |
| **From outside: nothing the agent does moves the levels** ✓ | |

- **Why a reflexive change tempts.** It is more realistic. SEO, the Phillips curve and a copied trading edge all wore out because people leaned on them, and Grove's memory business drew rivals because it paid.
- **Why it waits.** It would cost only $30 to $45 more a model, as one more run per seed. The real cost falls on the measure.

| What fails | How |
|---|---|
| **The no-change run stops being clean** | A timid agent wears the split out less, so it scores for spreading its budget rather than for noticing |
| **The yardstick stops being the best we can build** | Each round's spend moves future levels, so the reference bot would need to plan ahead |
| **Every agent plays a different world** | Levels follow each agent's path, so skill mixes with the world it made |
| **It tests a second skill** | Pacing how hard you lean on a split is real, but it isn't noticing that it has gone stale |

- **The coupling block is the place for it.** A lagged unit or a reflexive level is an edit to coupling, run once on a few models after the proof of concept is frozen. See [Future work](future.md#how-the-agent-can-act).

### Why the yoked dip

**Question.** What does the no-change run hold?

| Option | Problem |
|---|---|
| Quiet rounds only | Paranoia is a rate over 40 rounds with nothing in them to doubt, so a calm model and a blind one look the same |
| A dip anywhere, on any unit | Not comparable with the change run round by round |
| **A dip on the same unit, starting on the same round and at the same slope as the ramp, that then recovers** ✓ | |

- **The two runs match until the dip turns.** Same unit, same weather, same dice. An agent that switches at the same round in both runs is a false alarmer. One that switches only in the change run, after the dip would have turned, is discerning.
- **Paranoia gets a moment, not only a rate.** Whether and how far it moved during the dip is read beside the three rates.
- **A look settles it.** C0 is still at 0.55 in the no-change run, so an agent that looks before it switches is rewarded in both runs.
- **Cost.** The dip's length is one more dial, and a model that has read these docs knows the first dip is bait. Private seeds vary the dip's length and unit.

### Why no lock-in

**Question.** Once the agent switches to a new rule, can it go back?

| Option | Problem |
|---|---|
| A sticky switch, with a fee to switch back | Only needed once the price of switching must move apart from the share, which is the cost ratio extension |
| **Free to undo the next round** ✓ | |

- **A wrong split prices itself.** A wrong allocation forgoes output every round it stands.
- **The round limit prices time.** In life the limit is time, which a model has no feel for, so 40 rounds stand in. Every experiment spends some of a round's output.
- **Timidity doesn't pay.** Holding back from the best unit forgoes output every round.
- **Cost.** A rewrite of the notes can be undone the next round, so the switch is read from the shares and the rewrite only confirms it.

## The record and the briefing

### Why the agent writes its own notes

**Question.** Where do the agent's beliefs about the world come from?

| Option | Problem |
|---|---|
| A plan written by a model, handed over as a previous agent's | The old answer. A plan has a voice and an author, and [Kumaran](../prior/past-in-the-prompt.md#kumaran-et-al-2025-whose-first-answer-it-was) and [Schubert](../prior/past-in-the-prompt.md#schubert-et-al-2024-asymmetric-belief-updating) find both move how much a model trusts it. Rotating three plans spreads that variance rather than removing it |
| A plan rendered from a template | Still someone else's words, and a template's confidence is a bias we injected |
| No past at all | Nothing to doubt, and 200 rounds of calls to build one |
| **The record alone, and a briefing where the agent writes its own notes before round 1** ✓ | |

- **The baseline is the agent's own.** It read the record and wrote what it believes. When the world moves, insight reads whether it rewrites what it itself believed.
- **It is formed before the world can change.** The briefing happens before round 1 and the change starts at round 3 or later.
- **Both runs share it.** The briefing is one call per seed, and the change run and the no-change run get the same notes, so the two differ only in the world.
- **Same past, lower cost.** Every model starts from the same 200 rounds, and the cost is one call rather than 200.
- **Cost.** One more call a seed. A model that writes poor notes starts behind, which is scored, and which the briefing quality diagnostic reports. A read past is still a weaker pull than a lived one, which the full live run extension tests.

### Why the record comes from a bot, and its style is a factor

**Question.** Who played the 200 rounds the agent reads?

| Option | Problem |
|---|---|
| A model's own live run, frozen | The old answer. Each model explores in its own style, and the record then demonstrates that style to every reader |
| 200 rounds with no change and no experiments | The reference bot's hazard prior came from us, and the agent never saw how often change happens here |
| **The reference bot, damped, with one or two resolved changes and several dips, and its style a pilot factor** ✓ | |

- **The record is a demonstration.** [BanditBench](../prior/worlds-that-change.md#banditbench-nie-et-al-2025-in-context-exploration) put five example runs in the prompt and it moved behaviour. 200 rounds with two caught changes is the same thing, including what catching looks like.
- **A bot's style is the right amount by definition.** The record's experimentation is the yardstick's own, damped to read as a steady operator who moved a few times.
- **The hazard is anchored in data.** The agent and the bot can both count the resolved changes.
- **The cue is sized once.** The pilot runs a steady record and a jittery one on the same seeds. The spread is reported beside the skin spread, then one style is frozen.
- **Cost.** It bends "no hint of change in the prompt". The prompt is still silent, but the data says change happens here. The no-change run has the same record, so it charges for any doubt this causes.

### Why four skins over one interface

**Question.** What does the game look like to the agent?

| Option | Problem |
|---|---|
| The abstract game only | A score tied to one look, and nothing to say about whether a story changes play |
| One public story skin, the marketing one | Its story, that AI placements rise on mobile, is a trend a 2026 model already believes. It may switch on priors and score for discernment it never did |
| Skins picked for realism | No real domain is flat on how stable it expects the world to be. A plant says stable, so drift reads as a sensor fault. A market says drifting, so any wobble reads as change |
| **Four skins over one interface: abstract, fictional, plant and market** ✓ | |

| Skin | Direction prior | Stationarity prior | Role |
|---|---|---|---|
| Abstract, A to E | None | None | The anchor. Every other skin is read against it |
| Fictional, a real job with invented names | None | Weak | The headline skin. Story without baggage |
| Plant, five lines on two sites | Weak | Stable | One end of the stationarity test |
| Market, the old public skin | Strong | Drifting | The other end, with its direction leak named |

- **The skin is a naming layer.** The generator exposes units, one lever, two counts per unit and an output. A skin supplies nouns and a story and nothing else, and the skin lint checks it: same tables, same numbers.
- **The spread is a result.** The pilot runs every skin on two models. If the spread across skins beats the spread across models, the headline reads from the fictional skin and the others are sensitivity checks.
- **The record can dominate the prior** if it is informative. Two resolved changes in 200 rounds say the hazard out loud, whatever the nouns suggest.
- **What a skin may not vary.** The time unit is a week in every skin, and no proof of concept skin shows the generator's inputs. Both are [open questions](../../TODO.md#open-questions) for later.
- **Private skins** dress private seeds, so a model that learnt the public look is caught. None tells a story of disruption, and none is described here.
- **Cost.** Four skins is four files to lint and four pilot cells. The fictional skin is still to be written.

## Measuring

### Why two tiers

**Question.** How much is built and run before anything is known?

| Option | Problem |
|---|---|
| One funded edition, with the full grid and the threshold headline | Several hundred dollars a model before we know the measure separates models at all, and a curve fitted over five amplitudes on ten seeds is too noisy to read |
| A proof of concept with no path to the full study | A headline that can't be plotted over releases |
| **A proof of concept that leads with edge captured, then a full study that leads with discernment** ✓ | |

| | Proof of concept | Full study |
|---|---|---|
| Headline | Edge captured, pooled, gain and loss split | Discernment: the threshold from a fitted curve |
| Grid per seed | One no-change run and two amplitudes | One no-change run and five amplitudes |
| Kind of change | Level | Level, then coupling, gain and observation |
| Seeds | 20 | About 30, with extra runs where a model starts to miss |
| Runs a model | 60 and 20 briefings, about $100 at the target | About 180 at one reasoning setting |
| Reasoning | One setting | A sweep |
| Models | Two in the pilot, then each on release | Every model on release, older ones back-filled |
| Realism | The skin and history spreads, deciding pooling | The real-task check as well |

- **The proof of concept has to show one thing**: that the measure separates models with usable error bars. One continuous number does that. A threshold does not, until the grid exists.
- **Nothing is thrown away.** The two amplitudes are points on the full study's curve, in the same unit against the same bot.
- **The game is the same at both tiers.** Only the number of runs, the kinds of change and the headline change.
- **Cost.** The proof of concept's headline tops out at 1 and can't be plotted over releases for long. That is accepted because no model will be near 1 before the full study exists.

### Why traits, in two kinds

**Question.** What does the benchmark measure?

| Option | Problem |
|---|---|
| One detection score | Switching too early and too late blur into one number, so a jumpy model and a complacent one can tie |
| A list of the game's mechanics: experiment, switch and the gap between them | Each rests on a cut-off the agent never knew about, and none maps onto a trait a reader cares about |
| **Six traits, split into abilities and dispositions** ✓ | |

- **Abilities are things more of is better.** Edge captured, discernment and insight. Each is a plain score, and a model may pass the reference bot on any of them.
- **Dispositions have a right amount.** Paranoia, caution and conviction. Each is a signed gap from the reference bot on the same seed, so zero is ideal and the sign says which way the model leans. Grove and Kodak needed to move, and Shopify and Hopin moved on a change that reversed.
- **A reader can name the failure.** "Cautious but calm" says more than "switch lag 8".
- **Cost.** Every disposition and both headlines lean on the reference bot, so a flaw in that bot moves them all. Insight and the catch rate backup stand without it.

### Why each trait lives in one kind of run

**Question.** Is a trait read across both the no-change run and the change runs, or in one of them?

| Option | Problem |
|---|---|
| Read every trait across both runs | A score mixes a false alarm in the no-change run with a slow catch in a change run, and the reader can't tell which happened |
| First doubt and the switch as two moments, caution the gap between them | Both moments rest on cut-offs the agent never knew about, and a run that never doubted has no moment at all |
| **Paranoia from the no-change run, caution and conviction from the change runs** ✓ | |

- **Rates beat moments.** In the no-change run every doubt is misplaced, so paranoia is a rate over all 40 rounds rather than the round a cut-off was crossed. Every run counts, including the ones that never doubted.
- **The yoked dip adds a moment where paranoia is sharpest.** The first rounds of the dip are the change, as far as the agent can tell. What it does there is read beside the rates.
- **Spend beats cheap actions.** Experimenting and hedging are read in share of the budget, which costs the output the agent is trying to win. Reading the record costs nothing, so it is the weakest of the three paranoia readings.
- **First doubt is demoted.** It stays as a diagnostic curve, the share of runs with an experiment by each round, because it still shows when models start to experiment.
- **Cost.** Paranoia rests on the no-change runs alone, 20 a model in the proof of concept, so its error bar is wider than the traits read from the change runs.

### Why split doubting from switching

**Question.** Is noticing one moment, or two?

| Option | Problem |
|---|---|
| One detection time | Switching too early and too late blur together, the two bad rows of the [profile](measures.md#a-profile-not-a-ranking) |
| Ask when it noticed | Self-report |
| First doubt and the switch as two lags, caution the gap | The old answer. Both lags rest on cut-offs the agent never knew about, and a run that never experimented has no gap |
| **Three traits: paranoia for doubt, caution for the switch, conviction for what follows** ✓ | |

- **Never experimenting is always wrong.** A cheap experiment pays whenever doubt is above nearly zero, so no loss function is needed. That is why paranoia is read in the no-change run, where every experiment is a misplaced one.
- **Switching has a price.** Its bar is set by the cost of being wrong, which is where Shopify and Kodak differ. That bar is caution.
- **The ideal is computable.** A long record raises the bar for switching through the prior, not a new threshold, so each trait is a gap from the reference bot.
- **The judgement is a dial.** Grove and Kodak needed to move, and Shopify and Hopin moved on a COVID change that reversed. How much to value stability lives only in the ratio of the price of switching to the price of experimenting.
- **First doubt is now a diagnostic curve.** See [Why each trait lives in one kind of run](#why-each-trait-lives-in-one-kind-of-run).

### Why caution is a CUSUM line

**Question.** How is caution, the evidence an agent needs before it switches, put into a number?

| Option | Problem |
|---|---|
| Switch round minus first doubt round | First doubt rests on a share cut-off, and a run with no experiment has no gap |
| Rounds from the start of the change to the switch | Easy to read, but three rounds of bad weather and three rounds of clear evidence count as the same wait |
| Experiments, the off-split rounds played before the switch | Says how the agent spent its wait, not how much evidence it demanded |
| Price, the output given up before the switch | The same, in output |
| **The CUSUM line, with rounds as the plain reading beside it** ✓ | |

- **It is in units of evidence.** The CUSUM bot adds up how much each result favours a change and fires when the sum crosses a line. The height of the line that would fire on the agent's switch round, fed the same rounds, is how much evidence the agent demanded. Two agents who waited the same rounds on different weather get different lines.
- **It is fed the weather model.** A CUSUM on raw yield fires on every dip. Ours sums evidence for a shift over a dip, given the memory and spread in `params.yaml`, so a dip adds little.
- **It needs almost no model beyond that.** The CUSUM bot takes a reference amplitude and the weather settings. The reference bot's odds of change at the switch, the evidence backup, depend on the hazard prior we chose, so the line is the main reading and the odds the backup.
- **Rounds stay beside it**, because anyone can read them, and the experiment count and price stay as diagnostics.
- **Cost.** A run with no switch has no line, so caution is read only on switches. Discernment and edge captured carry the misses.

### Why insight reads the notes

**Question.** How do we tell a rethink from a retune?

| Option | Problem |
|---|---|
| The shares alone | An agent that moves A0's share to B0 scores on edge captured without ever finding C0, and the shares can't say whether it knew why |
| A judge reading the notes | Scoring needs a model |
| **The largest share on the changed side, and a simple check that the rewritten notes state the new rule** ✓ | |

- **It reads what the agent believed.** The notes are the agent's own, so a rewrite is the agent changing its mind, not editing someone else's.
- **The retune bot is the bound.** It pools sides, so it can only move A and B together. Output between it and the reference bot is what rethinking was worth.
- **The check is a string match**, not a judge: does the note say that on side 0 C leads, in the skin's nouns.
- **Cost.** A model that acts without writing is read as retuning. The say/do gap under conviction catches the reverse.

### Why two bots bound the game

**Question.** What is each score measured against?

| Option | Problem |
|---|---|
| Other models | No fixed scale, and no way to say what was knowable |
| The no-update bot only | Beating the floor doesn't say how much was possible |
| A bot that splits on its best guess of the levels | The old ceiling bot. It never values a look for its own sake, so it may never fund C0 enough to be sure, and fall towards the retune bot |
| **A reference bot and a retune bot on every seed** ✓ | |

| Bot | What it is | What it settles |
|---|---|---|
| Reference bot | A filter on the generator's family: a belief per unit over its level, a belief over whether it is in a dip or has shifted, and a belief over how long ago a change began (Adams and MacKay). Each round it samples from the belief and takes the best split under saturation and the threshold for that sample | The yardstick for edge captured, discernment and every disposition |
| Retune bot | The same code with sides pooled, so each kind is one belief | Whether the agent retuned or rethought |

- **It values information because sampling does.** A unit the bot is unsure of sometimes samples high, so it gets budget above the threshold. This is how [Mellor and Shapiro](../prior/further-work.md#quickest-detection-and-drifting-bandits) handle a world that switches, and what [Denrell and March](../prior/further-work.md#the-new-ceo) say a fair yardstick needs.
- **It wrote the record.** Damped, so the record's experiments are the yardstick's own, at the right rate by definition.
- **It is the best bot we can build, not the best possible.** A model may beat it, and then edge captured passes 1. That is a finding, not a bug.
- **Should complacency rise at all?** A long past lowers the hazard but sharpens the bot's view of the old levels. Which wins is computed, not assumed.
- **Retune or rethink.** The retune bot can't split a kind by side, so it moves both sides together or neither, and never finds the new rule.
- **The hazard's prior is pre-registered.** It is a Beta prior centred on how often changes happen across the suite, no-change runs included, set before any model runs. The bot updates it over the record, where it can count the resolved changes, and tracks run length over the live rounds, as [Wilson et al.](../prior/people.md#wilson-nassar-and-gold-2010-learning-the-hazard-rate) do.
- **Cost.** Both headlines and every disposition lean on this bot and on our generator's true levels, so a flaw in either moves them all. The catch rate needs neither, and is reported beside them so a disagreement shows. Realism is the [realism ladder](future.md#whether-it-holds-outside-our-game).

### Complacency as a parameter, not a history

**Question.** How do we create the pull of past success?

| Option | Problem |
|---|---|
| Real long tasks with a late change | Costly, and every run has a different past |
| A longer prompt | Mixes complacency with context length |
| **Rounds of record before the change** ✓ | |

- **The measure is a gap.** The reference bot slows a little too, so the agent's curve is read against the bot's, with the no-change run.
- **Swept once.** Both tiers fix the record at 200. See [Why one no-change run and a grid per seed](#why-one-no-change-run-and-a-grid-per-seed).

| Delay in the change run | False alarms in the no-change run | Reading |
|---|---|---|
| Rises | Falls | Bayesian. Check the gap against the reference bot |
| Rises | Flat | Complacent |
| Flat | Flat | Not reading the past at all |

### Why each round is scored on expected output

**Question.** How is one round's play scored?

| Option | Problem |
|---|---|
| Real output | Partly dice and partly weather, so more runs are needed for the same error bar |
| Expected output with the weather in | A lucky stretch of weather rewards a split that didn't earn it |
| Rounds where the standing unit was right | Ignores the shares, so confidence doesn't count |
| **Expected output at the true levels, the sum over funded units of level × N × share^alpha** ✓ | |

- **The dice and the weather drop out.** The score depends only on the split and the true levels, so far fewer runs give the same error bar. [Next step 2](../../TODO.md#next-steps) measures how many fewer.
- **No bot needed.** It needs only the true levels, which we set.
- **It adds up** across rounds, and is what the reference bot tries to maximise.
- The agent still plays real dice and real weather, and the real output is reported alongside.

### Why first doubt and the switch are read as curves

**Question.** How are first doubt and the switch reported by round?

| Option | Problem |
|---|---|
| Mean round of first doubt or the switch | A run that never experiments has no round, so the mean drops it or invents one |
| **Share of runs that have experimented or switched, by round** ✓ | |

- **Every run is kept**, and the spread shows.
- **They are diagnostics now.** The traits carry the score. The curves show when models start to experiment and when they move. See [Why each trait lives in one kind of run](#why-each-trait-lives-in-one-kind-of-run).
- **The share thresholds are fixed before the pilot.**

### Why curiosity is a diagnostic, not a trait

**Question.** Should how hard the agent experiments be scored as one of its traits?

| Option | Problem |
|---|---|
| Score it from experiments | A share on an unfavoured unit looks the same whether it is a test or the spread saturation calls for, so curiosity blurs with sizing |
| Count any share above the rational spread as an experiment | A convention the agent doesn't know about, so it scores an intent the agent may never have had |
| Add a `trial(unit)` tool that reveals one reading for a fee | A new tool may hint that something is worth testing |
| **Report it as a diagnostic, beside calibration, steadiness, anchoring and candour** ✓ | |

- **The other traits stand without it.** Paranoia says when the agent starts to doubt, caution how much it needs to see before it switches, and conviction how fully it acts. Curiosity sits between doubt and switch, and both ends read cleanly from the log.
- **The data is still kept.** The share on units the standing split leaves out, which ones it tried, and the output given up to experiments are all reported.
- **Cost.** We can't say whether a model failed because it never tested its doubts or because it tested them badly. The trial tool is the extension that would split the two.

## The headline

### Why edge captured is the proof of concept headline

**Question.** What one number does the proof of concept report?

| Option | Problem |
|---|---|
| A threshold fitted over two amplitudes | Two points don't make a curve. The crossing would move with the fit's shape more than with the model |
| The catch rate at one amplitude | A yes or no per run throws away when the switch came and how full it was, and it saturates once models catch that amplitude |
| The ratio at each amplitude, averaged | At the faint amplitude the reference bot gains little, so the ratio there swings on a small denominator and the average inherits the swing |
| **Edge captured pooled by output: one ratio from totals summed over every run** ✓ | |

- **It is continuous and luck-free.** Each run scores on expected output, so the dice and the weather drop out and 20 seeds give a standard error near 0.05. That is what splits two models, which is the one thing a proof of concept has to show.
- **It reads without explanation.** "Took 62% of the gain on offer, where 0 is never changing the split and 1 is the best bot we can build."
- **Every run counts by what it won.** An early switch beats a late one, a timid switch earns less than a full one, and a false alarm counts through the output it cost. No switch cut-off and no voiding rule.
- **The loud amplitude counts more, and should.** Each amplitude weighs by what was on offer, which is what the agent was trying to win. The no-change loss is counted once.
- **It is a point on the full study's curve.** The same ratio, taken amplitude by amplitude, is what discernment fits. See [Why two tiers](#why-two-tiers).
- **Cost.** It tops out at 1, so it can't be plotted over releases for long, and it leans on the reference bot and the true levels. The catch rate, d′ and the CUSUM dot stay as [backups](measures.md#catch-rate-a-backup) that don't lean on the bot.

### Why discernment is the full study headline

**Question.** What one number goes on the plot over releases?

| Option | Problem |
|---|---|
| Edge captured, pooled over every run | Tops out at 1, and one number mixes the amplitudes, so it can't say how faint a change a model handles |
| Lag in rounds | Mixes how loud the change was with how fast it was caught |
| Catch rate at one amplitude | Saturates once models catch that amplitude |
| The smallest amplitude caught half the time | The old answer. A yes or no catch rises with skill and with a low bar for raising the alarm. It needs a switch cut-off and a voiding rule, and a catch in round 10 counts the same as one in round 39 |
| A staircase, sizing each run from the last | Runs in series, not in parallel |
| **The amplitude where edge captured crosses a set level, on a fixed grid** ✓ | |

How it works:

1. **Every change run is a ramp**, with an amplitude of 3, 5, 8, 12 or 15 points of level.
2. **At each amplitude, pool the seeds.** The model's gain over the no-update bot in the change runs, minus its loss in the no-change runs, divided by the same for the reference bot.
3. **Fit a curve** of that ratio against amplitude and read off where it crosses the level. Whether amplitude enters as points or their log is fixed before the pilot.
4. **Each model is plotted** against its release date, and differences between models are paired seed by seed.

- **It reads like a hearing test.** 15 points is a loud beep and 3 is a whisper. METR's time horizon uses the same shape.
- **The beep is the fall.** The amplitude is how far the standing unit slips, which is the only thing the standing split hears. The rise is silent until the agent looks, so the test is of how faint a slip makes it look. See [Why attention is scarce](#why-attention-is-scarce).
- **The level is read at 50% and at 80%.** 50% is the curve's centre: it is the location the fit estimates directly, so it has the tightest bar, and it is the level most models reach somewhere on the grid. METR tracks 50% for those reasons and reports 80% beside it. 80% is what a reader means by "acts on", so it is the quoted number, with its wider bar. The wording never says "half": discernment is the smallest drop in level the model acts on.
- **Every run counts.** A run adds what it won, so an early catch beats a late one, and a run that never switches still scores what its experiments earned.
- **No cut-off and no voiding rule.** Paranoia shows as the no-change loss, taken off at every amplitude, so a model that always switches gains nothing.
- **The small denominator is bounded.** At 3 points the reference bot gains little, so a ratio there swings. The arbiter's rule, that an amplitude must be [worth catching](#why-edge-captured-is-the-arbiter) by a margin set in `params.yaml`, keeps such an amplitude off the grid.
- **It can saturate, and we say so.** The reference bot scores 1 at every amplitude, so its own threshold sits below the grid, and a model that matches it reads "below the grid". The remedy is a harder edition, with a lower N, a longer memory or a fainter grid. Each threshold is also published as the evidence a round carries at that amplitude, so every edition sits on one axis.
- **Cost.** It needs the five-amplitude grid and about 30 seeds, which is why it waits for the full study. It leans on the reference bot and the true levels, where the old catch rate needed neither. The catch rate, d′ and the CUSUM dot stay as [backups](measures.md#catch-rate-a-backup).

### Why edge captured is the arbiter

**Question.** When a trait or an amplitude is in doubt, what settles it?

| Option | Problem |
|---|---|
| Discernment alone | It reads amplitude by amplitude, so it can't drop an amplitude or a trait that isn't worth anything, and the proof of concept doesn't have it |
| Nothing settles it | Every trait stays on the page whether or not it costs output |
| **Edge captured is the arbiter at both tiers** ✓ | |

Two rules follow:

1. **An amplitude the reference bot doesn't profit from is moved.** Its gain over the no-update bot, pooled over seeds, must beat a margin set in `params.yaml`. This also keeps discernment's denominator from getting too small. The devil you know: if updating doesn't pay even for the reference bot, the rational play is to stay, and a model that stays has shown nothing.
2. **A trait that doesn't predict edge captured is a diagnostic.** Across the disposition bots, and then across models, a trait that fails to track edge captured isn't costing anything the game can see.

- **It keeps the page honest.** Every trait has to earn its place in output.
- **Cost.** The margin is a judgement, and so is how strong "predicts" has to be. Both are fixed in [next steps](../../TODO.md#next-steps) 1 and 2, before any model runs.

### Why efficiency is in-game spend

**Question.** How is the cost of experimenting measured?

| Option | Problem |
|---|---|
| Token cost | Pricing, not reasoning |
| Experiment count | Ignores what each experiment cost |
| **Output given up on rounds that move share off the standing split** ✓ | |

- **Output is the only currency inside the game.**
- **Dollar cost is still reported** in its own column, beside the score but not part of it.

## Robustness and the suite

### How we avoid it simply being solved

**Question.** What stops a model spotting the change without judgement?

| Shortcut | What blocks it |
|---|---|
| Treat one bad round as proof | Weather has memory, so a bad month is ordinary |
| Treat a bad month as proof | The no-change run holds a dip that starts exactly like the change |
| Wait for an alarm | The standing split keeps working after the change |
| Refit the record | The record was written before the change, so only new spend on the units that changed can reveal it |
| Experiment all the time | Experiments cost output, and the no-change run punishes them |
| Watch the rising unit for free | It sits under the threshold at the standing split, so watching it costs a share |
| Take the hint | The prompt never mentions change, and no skin tells a story of disruption. The record's resolved changes say change happens, not when or where |
| Watch the totals | The change sits in one unit of ten, and the standing split barely loses on the week as a whole |

### Why the game is hard to game

**Question.** Can a model raise its score without the skill?

There are three ways to fake it, and each defence below closes one:

1. **Spot the test** and experiment because of that.
2. **Learn the public seeds.**
3. **Find a fixed strategy** the scoring rewards.

| Defence | What it catches |
|---|---|
| **No-change run**, whose loss is counted in the headline | Always switching or always experimenting |
| **Change start drawn per seed**, from round 3 to 10 | Learning that the change comes at round 5 |
| **Private seeds that differ in structure**, such as start round, ramp length, dip length and which unit changes | A model that learnt the shape of the public seeds |
| **[Four public skins and private ones](#why-four-skins-over-one-interface)** | Recognising the game across releases |
| **A record frozen after the pilot**, the same for every model | A model that learnt one record's quirks |
| **A canary string in every published file** | Training on the benchmark by accident |
| **Fixed bots**: switch at a fixed round, split at random, always split evenly, always look at a set share | A scoring rule that rewards a fixed strategy |
| **A test-awareness scan**, flagging "this is a test" or "the rules may have changed" before any loss | Experimenting because it guessed the test. Reported per model, with whether it predicts experiments in the no-change run |
| **A sandbox that sees only what the agent already saw** | Reading the generator, seeds or logs through code |
| **A public threshold** | A model that trickles under it loses the budget and reads nothing |
| **Transcript review** | Invalid splits, oversized record reads, or steering text left in the notes |

- **Cost.** Test awareness can be measured, not removed. A model that hides it passes the scan, so the no-change run stays the main defence.

### Why one no-change run and a grid per seed

**Question.** Which runs does each seed get?

| Option | Problem |
|---|---|
| Cross kind of change, record, speed and amplitude | Several hundred dollars a model |
| **One no-change run and a grid of amplitudes, all on the same shared luck** ✓ | |

| | Proof of concept | Full study |
|---|---|---|
| Grid | 12 points, and 5 or 8 | 3, 5, 8, 12 and 15 |
| Runs per seed | 3, and one briefing | 6, and one briefing |
| Seeds | 20 | About 30 |

- **The proof of concept needs one loud and one faint amplitude**, enough to show that edge captured separates models and that the faint change costs them. The 3 point amplitude is left out because it has the smallest denominator and is the likeliest to fail the worth-catching rule.
- **It keeps cost down.** Each run added to a seed costs $60 to $90 a model across 20 seeds, at the thinking we now expect. Spending the proof of concept's runs on 20 seeds rather than five amplitudes doubles the no-change runs, which is where paranoia's error bar comes from.
- **Ramp only**, since work drifts more often than it changes overnight. Amplitude varies instead of speed.
- **The level change stays.** Other kinds of change, the history style and the record sweep shouldn't differ between releases, so they run once.
- **The no-change run is the one not to cut.**

### Why the bots set the difficulty

**Question.** What is the difficulty tuned against?

| Option | Problem |
|---|---|
| Today's models, in the pilot | Pitched at today's models, so it saturates with the next release |
| **The bots** ✓ | |

- **The targets.** The reference bot profits from the 3 point change about half as well as it could and from larger ones reliably. The no-update bot catches none, and every [fixed bot](#why-the-game-is-hard-to-game) scores well below the reference bot.
- **The ramp is ambiguous for about ten rounds.** Memory, spread and dip size are tuned until the reference bot's odds that a change has begun stay under 3 to 1 for about ten rounds of the ramp, and the dip-only bot and the reference bot part at about the same round.
- **Disposition bots check the traits.** Jumpy and cautious are the reference bot with its switching bar moved down or up, hedging is the reference bot with the standing units' share halved, the dip-only bot reads every fall as weather, and the retune bot pools sides. Each trait must recover its bot's dial, and a trait that can't split jumpy from cautious across the seeds is demoted to a diagnostic.
- **It is free.** The bots make no API calls.
- **It is hard by construction.** Matching the reference bot means valuing information as well as the best bot we can build.

### Why more seeds, not repeats

**Question.** How is the sample spent?

| Option | Problem |
|---|---|
| One seed run many times | Covers one kind of luck. Repeats only help a fixed item |
| **Seeds, each run once at every amplitude on its grid** ✓ | |

- **A generated seed is a new item and a new sample.** The error bar is about the same, at the same price.
- **Cost is set by total runs.** [Next step](../../TODO.md#next-steps) 2 checks that 20 seeds is enough for the proof of concept.

### Why older models and a general ability check

**Question.** What is each model's score compared with?

| Option | Problem |
|---|---|
| Today's models alone | No points from the past, so no line over time |
| The headline alone | If it just tracks general ability, it adds nothing, and we couldn't tell |
| **An older model in the pilot, and general scores beside each model's headline** ✓ | |

- **Older models are cheap.**
- **The outliers are the finding**: models well above or below the trend.
- **METR's time horizon is the best comparator.** It tests whether this skill is part of why models fail long tasks. See [How this connects to other work](../prior/README.md#how-this-connects-to-other-work).

### Why publish all but a private set

**Question.** What is released?

| Option | Problem |
|---|---|
| Everything | Nothing catches a model that learnt the public set |
| Nothing | No one can rerun a model or check the numbers |
| **Everything but the private seeds and skins, with scores on both** ✓ | |

- **What is released.** The generator, the bots, the public seeds and skins, the frozen records, full transcripts and model settings, each file with a canary string.
- **The gap is the warning sign.** A large gap between the public and private sets flags a model that learnt the public one.
