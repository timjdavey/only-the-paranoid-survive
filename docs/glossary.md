# Glossary

**The one word we use for each idea in the benchmark.**

Use these words in prose and in code. Add a word here before using it on any other page.

## The study

| Word | What it means |
|---|---|
| Game engine | The simple cybernetics game at the core of the study: the rules and numbers, with no story |
| Narrative skin | A story dressed over the game engine, so the model treats it as a real situation. It also lets us publish the engine while hiding which skin it wears |
| Frame | The facts every prompt states whatever the skin: a budget split in whole percentages that add up to 100, ten channels, the record below, a tool to place the split, a notes file and a compute tool. Each skin words the frame itself. See [prompts](harness/prompts.md) |
| Model | The system we test: classic LLMs, plus Jev, Timestral etc |
| Agent | A model while it plays the game |
| Run | One playthrough of the game |
| Baseline | A fixed strategy run through the same game and score as the models. A fixed baseline's name always ends in "baseline", so it never reads as a plain adjective. See [baselines](design/baselines.md) |
| Provider | The harness code that plays one model through the same solver as an LLM. inspect_ai's own for chat LLMs, ours for baselines, Jev and Timestral. `baseline/<name>`, `jev/<model>` or `jev/<endpoint>/<model>`, and `timestral/<policy>` in code. See [inspect](harness/inspect.md#providers) |
| Perfect baseline | The baseline that knows each round's levels and bets on the best channel. A mark for how much weather luck was on offer, read from the pool. It divides nothing. `baseline/perfect` in code |
| Discerning baseline | The baseline that knows each channel's base level, so it holds through a shock and moves at a switch. The ceiling: a scenario score of 1. `baseline/discerning` in code |
| Complacent baseline | The baseline that holds the Discerning baseline's round 1 bets to the end. A mark on every scenario's bar. The [reachable gain](pilot/engine-checks.md#reachable-gain) check holds it at or below 0.7 wherever a change lasts. It sits near 1 in the Up switch then down switch scenario, where the change undoes itself. `baseline/complacent` in code |
| Uniform baseline | The baseline that bets 10 on every channel, every round. The floor: a scenario score of 0. `baseline/uniform` in code |
| Hedge rule baseline | A few points on the hedge, the rest on the leader. It switches when the leader falls and the hedge does not rise. The simplest player that reads the tell. `baseline/hedge_rule` in code |
| Scout rule baseline | A few points on every channel but its pick, the rest on the pick. It moves when another channel's readings beat the pick's for a run of rounds and the hedge is not rising. The hedge rule that explores everywhere. `baseline/scout_rule` in code |
| Bayesian baseline | A belief in the engine's family over each channel's base level, from its own readings only, through a forecast rule. The best a reader who knows how the world works could do, at one prior on how often it changes. A mark, never the yardstick. `baseline/bayesian` in code. See [bayesian](specs/baselines/bayesian.md) |
| Blind baselines | The hedge rule, Scout rule and Bayesian baselines. They learn of a change only from their own record, as a model does, so they pay for explore bets and for the rounds it takes to be sure. The Bayesian baseline is the best of them |
| Timestral top pick | The Timestral baseline that puts 100 on the channel it forecasts highest. `timestral/top-pick` in code |
| Timestral odds | The Timestral baseline that splits its bets by each channel's chance of being the best. `timestral/odds` in code |
| Timestral top pick with explore bets | Timestral top pick plus 1, 2 or 5 points on every other channel. `timestral/explore-1`, `explore-2` and `explore-5` in code |
| Timestral odds, alone | Timestral odds, with each channel forecast on its own and not all ten together. `timestral/odds-alone` in code |
| Timestral odds, bet aware | Timestral odds, alone, also told its past bets. `timestral/odds-bet-aware` in code |
| Forecaster | A model that guesses each channel's level next round and places no bets itself, such as Timestral. A forecast rule turns its guess into a split. The forecasters layer plays one as a policy. `Forecaster` in code. See the [forecasters spec](specs/forecasters/README.md) |
| Forecast rule | A rule that turns a forecast's quantiles into a split. Timestral's bets go through one, and the Bayesian baseline's do too. `ForecastRule` in code. See [forecast](specs/baselines/forecast.md) |
| Reasoning setting | How hard a model is allowed to think, from one shared grid: `off`, `low`, `medium`, `high`, `max`, or `on` when it can't be changed. Each setting is its own row. See [models](harness/models.md#reasoning) |
| ECI | Epoch AI's [Capabilities Index](https://epoch.ai/benchmarks/eci), one general capability score per model. The x axis of a [trend plot](harness/models.md#trend-plots) |
| Spec | The contract a layer of the code is written to and tested against. One folder per layer in [specs](specs/README.md). Design pages say why, specs say what |
| Proof of concept | The first small run: cheap models, two held-out skins, public seeds, enough to check the harness and the baseline order. `poc` in its file names, played by `paranoid run`, see [models](harness/models.md) |
| Pilot | The short run before the full study that settles the knobs. Engine checks first, then provider checks, see [engine checks](pilot/engine-checks.md) and [provider checks](pilot/provider-checks.md) |
| Knob | A number the specs propose and the pilot settles, marked "pilot to confirm" until it is. A field on the config or a parameter on a rule |
| Check | One question the pilot answers, with a run, a measure and a decision. A section on a pilot page |
| Cell | The code that runs one check's data: timelines and baselines with no model, or a model through the task. `paranoid pilot <check>` runs one, see the [harness pilot spec](specs/harness/pilot.md) |
| Measure | The number a check reads off a cell's output, as a table in pilot results. The analysis layer's, see the [analysis pilot spec](specs/analysis/pilot.md) |
| Decision | A knob's settled value, a number or a yes or no, written once in [decisions](pilot/decisions.md) and then frozen |
| Setting | What was played, apart from who played it: the skin, seed set, noise setting, knobs and versions. Rows that differ in any of them never share a table. `Setting` in code, see the [analysis spec](specs/analysis/runs.md) |
| Result row | One model at one reasoning setting on one setting. One row of a results table, and the unit the analysis compares. `ResultKey` in code, see the [analysis spec](specs/analysis/runs.md) |
| Run table | The analysis layer's table of every run it loaded, one row per run, with the run's key, scores and token counts. Every table and plot starts from it. See the [analysis spec](specs/analysis/runs.md#one-row-per-run) |

## The world

| Word | What it means |
|---|---|
| Channel | One of the things the agent can put budget on. Each has its own hidden level, which its readings centre on |
| Level | Where a channel's readings centre in a round: its base level, its weather and its share of the shared factor. Hidden, and nothing is paid at it. Never called a mean: that word is kept for averaging over runs |
| Reading | The rate a bet on a channel was paid at this round, and the number the agent sees for that channel. A bet earns its share of the budget times its reading. It is the level plus read noise. A channel with no bet shows a blank. See [mechanics](design/mechanics.md#what-the-agent-sees) |
| Read noise | How far a reading lands from the channel's level. Real luck that the bet is paid, not a measuring error. Smaller the larger the bet, so a small bet gives a rough reading |
| Output | What a split earned in a round: each bet's share of the budget times its reading, added up. A run's output is the sum over its rounds, and the score is built from it. The agent is never shown it, and can work it out from its record. See [mechanics](design/mechanics.md#what-the-agent-sees) |
| Base level | A channel's mean when nothing is happening |
| Weather | The round-to-round wobble round a base level |
| Climate | Every channel's base level, round by round, taken together. A switch or drift changes it and a shock does not. The Discerning baseline knows the climate but not the weather |
| Sigma | The weather's SD per round, `own_scale` in code. An event size given "in sigmas" is a multiple of it. See [difficulty](design/mechanics.md#difficulty) |
| Persistence | How much of this round's weather carries into the next. At 0.8 a bad stretch is half gone after three rounds |
| Dials | The release constants every policy is handed beside the ladder: the run length, the three weather dials, read noise and the ladder ranges. The same in every scenario, so they say nothing about events. `Dials` in code. See [view](specs/engine/view.md#view) |
| Shared factor | One hidden series every channel loads on, so channels have good and bad weeks together |
| Loading | How much a channel moves with the shared factor. Uneven across channels |
| Hedge | The one channel with a negative loading. It rises when everything else falls |
| Tell | The hedge rising while the field falls. It marks a shock rather than a switch. See [the tell](pilot/engine-checks.md#the-tell) |
| Leader | The channel that pays best when a run starts. A channel, not a baseline |
| Runner-up | The second best channel at the start. The obvious fallback |
| Field | The other channels, including the hedge |
| Sleeper | A field channel whose base level rises in a switch. It rises past the leader's on most seeds, and stops short on some Up switch seeds |
| Timeline | One scenario played out on one seed: the ground truth, drawn before play starts. Every run on that seed replays it. Rebuilt from the seed, never saved. See [generator](design/mechanics.md#generator) |
| Ground truth | Every channel's level in every round, as a timeline holds it. The agent sees readings and is paid them, and never sees the ground truth |
| Column words | The three words a skin gives the record's header: the round column, the bet suffix and the reading suffix. `round_word`, `bet_word`, `reading_word` in code. See [render](specs/skins/render.md#record) |

## How the world changes

| Word | What it means |
|---|---|
| Event | One move the world makes, with its own onset and numbers drawn per seed. See [events](design/mechanics.md#events) |
| Shape | The kind of move an event makes: a shock, a switch or a drift. "A shock" is short for an event whose shape is a shock |
| Shock | A dip in every channel through the shared factor, which passes |
| Impulse | The decaying dip a shock adds. Into the shared factor by default, so every channel feels it by its loading. Onto the leader's level alone with the one-channel shock knob, so its base level never moves |
| Trough | The deepest point of a shock's impulse. The hedge sits highest there and most channels lowest |
| Switch | A lasting change in base levels that changes which channel pays best. The leader falls, a sleeper rises past it, or both |
| Ramp | The rounds a switch spreads its move over, in a straight line. 1 to 5, drawn per seed. `ramp` in code |
| Drift | A switch stretched over many more rounds |
| Short | A sleeper's rise that stops short: it ends above the runner-up but below the leader, so the right call is to stay. Drawn on some Up switch seeds. `short` in code |
| Switch kind | Which of four switches a seed drew: the leader falls, the leader falls and a sleeper rises, a sleeper rises past the leader, or a sleeper rises and stops short. `fall`, `fall_and_rise`, `rise` and `rise_short` in code, and `none` where a scenario has no switch. `switch_kind` in the analysis, see [switch kinds](specs/analysis/scores.md#switch-kinds) |
| Undo | A switch that puts an earlier sleeper back: its base level and loading return to what they were before it rose. `kind="undo"` in code |
| Profile | The form an event takes within its shape, drawn per seed. A shock falls sharply and climbs slowly, or slides and rebounds. A drift is linear or logistic |
| Scenario | A list of events we put each model through. Its name always ends in "scenario", so it never reads as an event. See [scenarios](design/scenarios.md) |
| No change scenario | No events. `no_change` in code |
| One shock scenario | One shock. `one_shock` in code |
| Down switch scenario | One switch the leader feels: its base level falls, sometimes with a sleeper rising. `down_switch` in code |
| Up switch scenario | One switch the leader never feels: a sleeper rises and the leader holds. On most seeds the sleeper rises past it, on some it stops short. `up_switch` in code |
| Shock then switch scenario | One shock, a gap, then one switch. `shock_then_switch` in code |
| Slow drift scenario | One drift. `slow_drift` in code |
| Switch then shock scenario | One switch the leader feels, a gap, then one shock. `switch_then_shock` in code |
| Up switch then down switch scenario | A sleeper rises past the leader, a gap, then falls back to its old level. `up_switch_then_down_switch` in code |
| Hard variant | A harder version of a scenario: more shocks before the switch, a longer drift, or a rise spread over a longer ramp |

## How the agent plays

| Word | What it means |
|---|---|
| Point | One percent of the budget, so the budget is 100 points. The engine's unit for a bet. Every skin calls it a percentage in its own words, see [interface](design/interface.md#how-the-agent-plays). Not a level point, which is a unit of a channel's level |
| Bet | The whole number of points the agent puts on one channel in a round, so a percentage of the budget. Its ten bets each round sum to 100 |
| Split | The agent's ten bets in one round, taken together. Payout is linear, so points on more than one channel only ever mean doubt or an explore bet |
| Channel order | The order of a skin's `channels` list. A split's ten numbers and the record's columns both follow it |
| Slip | A valid split that holds the numbers the agent meant on the wrong channels. It still sums to 100, so nothing retries it. Measured by the [channel order check](pilot/provider-checks.md#channel-order). `slipped` in code |
| Exploit | Betting on the channel the agent believes is best. Payout is linear, so exploiting alone means all 100 points on one channel. The opposite of an explore bet |
| Explore bet | A small bet on a channel the agent isn't backing, to read its level. To explore is to place one. A small bet gives a rough reading, see [mechanics](design/mechanics.md#what-the-agent-sees). `explore` in code |
| Warm up | Rounds a baseline plays before the agent's first round, so the record starts pre-filled. A pilot check, see [warm up](pilot/provider-checks.md#warm-up) and the [task spec](specs/harness/task.md#warm-up). `warm_up` in code |
| Give up | What the solver does after ten failed tries in one round: the run ends there, with no error, and scores as the Uniform baseline on that seed. See [solver spec](specs/harness/solver.md#tries). `gave_up` in code |
| Tool choice | Whether a reply must call a tool: `any` where the provider allows it, `auto` where it does not, as on Claude with thinking on. The solver picks it from the model and logs it. See [solver spec](specs/harness/solver.md#each-round). `tool_choice` in code |
| Tool use share | The share of a run's rounds in which the agent called the notes tool, and the share in which it called the compute tool. Reported beside every score. `notes_rounds` and `compute_rounds` in code, see [scorer spec](specs/harness/scorer.md#tool-use-share) |
| Prompt caching | A provider billing the start of a prompt at a lower rate when it matches a prompt it was sent moments before. It changes what a run costs, never what the model reads. See [models](harness/models.md#prompt-caching) |
| Cached share | The part of a model's input tokens its provider read from the prompt cache. Near zero on a provider that caches means the cache is missing. See [cost](specs/analysis/tables.md#cost) |

## Scoring

| Word | What it means |
|---|---|
| Scenario score | The share of the gap between the Uniform and Discerning baselines a model earned, pooled over seeds. 0 is knowing nothing, 1 is knowing the climate. See [scoring](design/scoring.md#how-we-score) |
| Run score | One seed's share of that gap, shown as a dot. It can land outside 0 to 1 on one seed. The scenario score pools seeds so it rarely does |
| Headline | One score per model: the plain mean of its eight scenario scores. Reported with the weakest trait beside it. See [scoring](design/scoring.md#how-we-score) |
| Weakest trait | The lowest of a model's eight scenario scores, named. The AND the headline alone does not give |
| Noise threshold | The full study headline. The signal to noise at which a model's headline sits half way between the Complacent baseline's and 1. Lower is better. See [scoring](design/scoring.md#noise-threshold) |
| Signal to noise | The size of a switch in level points over the weather's SD per round. The axis every release shares. See [difficulty](design/mechanics.md#difficulty) |
| Pinned | Event sizes held in level points, not sigmas, so the reachable gain stays the same while the weather grows. Every noise grid setting is pinned. `pin_in_level_points` in code. See [difficulty](design/mechanics.md#difficulty) |
| Noise grid | The fixed signal to noise settings the full study plays, chosen from the baselines before any model runs. See [pilot](pilot/engine-checks.md#noise-grid) |
| Trait | One scenario's score, named for what a high score shows. A label on a number, not a disposition. The question each score answers is in [traits](design/scoring.md#traits) |
| Composure | The No change scenario score. Ignoring noise when nothing is happening |
| Patience | The One shock scenario score. Holding through a dip that passes |
| Doubt | The Down switch scenario score. Questioning the plan when the change is real |
| Curiosity | The Up switch scenario score. Exploring when nothing is wrong, and moving only for a rise that beats the plan |
| Unlearning | The Shock then switch scenario score. Dropping "dips recover" once it stops being true |
| Vigilance | The Slow drift scenario score. Noticing a decline that has no sudden move |
| Conviction | The Switch then shock scenario score. Holding a plan it just chose through a dip that passes |
| Recall | The Up switch then down switch scenario score. Going back to a plan it has seen pay when the change undoes itself |
| Trait profile | A model's scores across scenarios, one per trait. The signal the headline combines |
| Error bar | How sure we are of a score. The 2.5th to 97.5th percentiles of the score over resamples of the seeds, a percentile bootstrap, so it shrinks with more seeds (epistemic uncertainty). Never SD over √seeds, as a pooled ratio is not a mean. See [scoring](design/scoring.md#error-bars) |
| Spread | How far one run lands from another. Does not shrink with more seeds (aleatoric uncertainty). See [scoring](design/scoring.md#spread) |
| Sampling spread | The part of spread from the model's own draws. Same seed, run again |
| Sampling share | The sampling spread's part of the spread, as a share of the variance: the variance within a seed across repeats over the variance of all runs. See [repeats](pilot/provider-checks.md#repeats) |
| World spread | The part of spread from the seed |
| Paired gap | The difference between two result rows' scores on the seeds both played, with an interval from resampling those seeds together. Pairing cancels the luck of the seed. `paired_gap` in code, see [paired gap](specs/analysis/scores.md#paired-gap) |
| Scenario gap | The same pairing across two scenarios of one result row, on twin timelines, such as Switch then shock against Down switch for what a whipsaw cost. `scenario_gap` in code |
| Public gap | A model's score on the public seeds minus its score on the held-out seeds. Near zero, unless the model has learned the public seeds. Not paired, as the two sets are different worlds. See [the public gap](harness/contamination.md#the-public-gap) |
| Skin sensitivity | The gap in a model's score between skins, which covers both the story and how the skin words the frame. A finding, not an error. Reported as a gap paired by seed between two skins on one seed set, see [spread](design/scoring.md#spread) |
| Mark | A fixed baseline's pooled score drawn on a scenario's bar, such as the Complacent baseline's. A reference, not a score of the model's. Never a symbol beside a score, which is a flag |
| Bayesian frontier | The scenario scores of every Bayesian baseline in a pre-registered family of hazards crossed with the forecast rules and a one-step lookahead, drawn as the No change score against the Down switch and Up switch scores. Its upper envelope is the best any reader of the engine's family did, and the Bayesian baseline's defaults are the point on it with the best headline. The pilot plays three of the family. See [Bayesian frontier](pilot/engine-checks.md#bayesian-frontier) |
| Reachable gain | The Discerning baseline's scenario score minus the Complacent baseline's, so one minus the Complacent mark. What moving at the right time is worth. In the Up switch then down switch scenario the Stayer stands in for the Complacent baseline. In level points it is the Discerning baseline's output minus the Complacent baseline's. See [reachable gain](pilot/engine-checks.md#reachable-gain) |
| Bayesian gain | The Bayesian baseline's scenario score minus the Complacent baseline's, or the Stayer's where it stands in. What the best blind baseline earns from moving, after explore bets and lag |
| Bayesian gain percentage | The Bayesian gain over the reachable gain, as a whole percent. How much of the reachable gain a player can earn from its own record alone |
| Explore cost | What exploring costs where nothing changes: one minus a player's No change scenario score. In level points, the Complacent baseline's output minus the player's on No change. Reported beside the reachable gain, see [reachable gain](pilot/engine-checks.md#reachable-gain) |
| Irreducible lag | One minus the best Bayesian baseline's Down switch score, on seeds it was not picked on. The rounds no reader of its own record can avoid losing, so the part of the gap to the Discerning baseline no reader can close. See [Bayesian frontier](pilot/engine-checks.md#bayesian-frontier) |
| Stayer | A pilot reference, not a baseline. It plays as the Discerning baseline until the last event begins, then holds those bets. In the Up switch then down switch scenario it moves to the sleeper and never comes back. Never on a bar. See the [harness pilot spec](specs/harness/pilot.md#shared-rules) |
| Squeeze | A scenario score climbing towards 1 as the run grows, though the player plays no better, as more rounds hide the ones it was late. Measured in [game length](pilot/engine-checks.md#game-length-and-switch-round) |
| Flag | A symbol beside a score that says a run gave up, retries ran high, or the model recognised the prompt or finished the canary. It never drops a row. See [flags](specs/analysis/scores.md#flags) |
| Retry share | The share of rounds that needed more than one try. Above a share the pilot sets, the scenario's bar is flagged. See the [retry rule](harness/prompts.md#retry-rule) |
| No call share | The replies that made no call to place the split, over the rounds played. Each one costs a retry, and one round can hold several. Read by the [tool choice](pilot/provider-checks.md#tool-choice) check |
| Bare harness | The headline harness with its notes file and compute tool taken away, `tools=none`. A sensitivity every LLM row plays once, never the headline. See [bare harness](pilot/provider-checks.md#bare-harness) |
| Bare gap | A model's paired gap between its headline setting and the bare harness. How much of its score the tools did. Reported per model beside the headline, see [tables](specs/analysis/tables.md#the-results-page) |

## Seeds and secrecy

| Word | What it means |
|---|---|
| Seed | The number that fixes a run's world: every channel's noise for every round, drawn up front |
| Twin timelines | The timelines one seed makes across scenarios. They share the ladder, the weather and the onset round, so they match until the events differ. See [seeds](design/scoring.md#seeds) |
| Seed set | The fixed list of seeds every scenario plays, so seed *i* is the same world across scenarios. There are two, public seeds and held-out seeds. See [contamination](harness/contamination.md#two-seed-sets) |
| Public seeds | Seeds published in this repo. Anyone can rebuild their timelines from the seed and the engine, and no timeline is ever stored. For the pilot, the example logs and anyone checking our work |
| Held-out | Kept in the private repo and never published. Held-out skins and held-out seeds make the headline |
| Release | One published set of the benchmark's frozen generator defaults, noise grid and fresh held-out seeds. Releases share the signal to noise axis. Every log names its release, `release` in code, and it is `dev` until the first is frozen. See [contamination](harness/contamination.md) and the [task spec](specs/harness/task.md#release) |
| Contamination | A model having seen the benchmark in training |
| Learning the game | A model trained on timelines from the public engine. Its score still says how well it reads the game, not whether the trait carries. No secret stops it, see [contamination](harness/contamination.md#what-it-does-not-stop) |
| Canary | A fixed line in every published file that holds prompt text. A model that can repeat it has seen our data. See [contamination](harness/contamination.md#canary) |

## Adding a word

1. **One word per idea.** Don't invent a second name for something already here.
2. **Prefer the word that says what the thing is**, not where it came from.
3. **Prose uses game engine words.** A skin's nouns appear only in examples that say which skin they're from.
