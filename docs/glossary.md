# Glossary

**The one word we use for each idea in the benchmark.**

Use these words in prose and in code. Add a word here before using it on any other page.

## The study

| Word | What it means |
|---|---|
| Game engine | The simple cybernetics game at the core of the study: the rules and numbers, with no story |
| Narrative skin | A story dressed over the game engine, so the model treats it as a real situation. It also lets us publish the engine while hiding which skin it wears |
| Frame | The facts every prompt states whatever the skin: a budget of 100 points, ten channels, whole numbers, the record below and one tool to place points. Each skin words the frame itself. See [prompts](harness/prompts.md) |
| Model | The system we test: classic LLMs, plus Jev, Timestral etc |
| Agent | A model while it plays the game |
| Run | One playthrough of the game |
| Baseline | A fixed strategy run through the same game and score as the models. A fixed baseline's name always ends in "baseline", so it never reads as a plain adjective. See [baselines](design/baselines.md) |
| Provider | The harness code that plays one model through the same solver as an LLM. inspect_ai's own for chat LLMs, ours for baselines, Jev and Timestral. `baseline/<name>`, `jev/<model>` and `timestral/<policy>` in code. See [inspect](harness/inspect.md#providers) |
| Perfect baseline | The baseline that knows each round's levels and bets on the best channel. A mark for how much weather luck was on offer. It divides nothing. `baseline/perfect` in code |
| Discerning baseline | The baseline that knows each channel's base level, so it holds through a shock and moves at a switch. The ceiling: a scenario score of 1. `baseline/discerning` in code |
| Complacent baseline | The baseline that holds the Discerning baseline's round 1 bets to the end. A mark on every scenario's bar, near 0.55 where there is a switch. `baseline/complacent` in code |
| Uniform baseline | The baseline that bets 10 on every channel, every round. The floor: a scenario score of 0. `baseline/uniform` in code |
| Hedge rule baseline | A few points on the hedge, the rest on the leader. It switches when the leader falls and the hedge does not rise. The simplest player that reads the tell. `baseline/hedge_rule` in code |
| Scout rule baseline | A few points on every channel but its pick, the rest on the pick. It moves when another channel's readings beat the pick's for a run of rounds and the hedge is not rising. The hedge rule that looks everywhere. `baseline/scout_rule` in code |
| Timestral top pick | The Timestral baseline that puts 100 on the channel it forecasts highest. `timestral/top-pick` in code |
| Timestral odds | The Timestral baseline that splits its bets by each channel's chance of being the best. `timestral/odds` in code |
| Timestral top pick with looks | Timestral top pick plus 1, 2 or 5 points on every other channel. `timestral/look-1`, `look-2` and `look-5` in code |
| Timestral odds, bet aware | Timestral odds, also told its past bets. `timestral/odds-bet-aware` in code |
| Reasoning setting | How hard a model is allowed to think, from one shared grid: `off`, `low`, `medium`, `high`, `max`, or `on` when it can't be changed. Each setting is its own row. See [models](harness/models.md#reasoning) |
| ECI | Epoch AI's [Capabilities Index](https://epoch.ai/benchmarks/eci), one general capability score per model. The x axis of a [trend plot](harness/models.md#trend-plots) |
| Spec | The contract a layer of the code is written to and tested against. One folder per layer in [specs](specs/README.md). Design pages say why, specs say what |

## The world

| Word | What it means |
|---|---|
| Channel | One of the things the agent can put budget on. Each pays out at its own level |
| Level | A channel's true payout, which its noisy reading sits around. Never called a mean: that word is kept for averaging over runs |
| Reading | The noisy number the agent sees for a channel it bet on. It sits round the level, and is rougher the smaller the bet. A channel with no bet shows a blank. See [mechanics](design/mechanics.md#what-the-agent-sees) |
| Base level | A channel's mean when nothing is happening |
| Weather | The round-to-round wobble round a base level |
| Climate | Every channel's base level, round by round, taken together. A switch or drift changes it and a shock does not. The Discerning baseline knows the climate but not the weather |
| Persistence | How much of this round's weather carries into the next. At 0.8 a bad stretch is half gone after three rounds |
| Shared factor | One hidden series every channel loads on, so channels have good and bad weeks together |
| Loading | How much a channel moves with the shared factor. Uneven across channels |
| Hedge | The one channel with a negative loading. It rises when everything else falls |
| Tell | The hedge rising while the field falls. It marks a shock rather than a switch. See [the tell](pilot/engine-checks.md#the-tell) |
| Leader | The channel that pays best when a run starts |
| Runner-up | The second best channel at the start. The obvious fallback |
| Field | The other channels, including the hedge |
| Sleeper | A field channel whose base level rises past the leader's in a switch |
| Tape | The true level of every channel in every round, as one seed produces it. Saved and replayed |

## How the world changes

| Word | What it means |
|---|---|
| Event | One move the world makes, with its own onset and numbers drawn per seed. See [events](design/mechanics.md#events) |
| Shape | The kind of move an event makes: a shock, a switch or a drift. "A shock" is short for an event whose shape is a shock |
| Shock | A dip in every channel through the shared factor, which passes |
| Impulse | The decaying dip a shock adds. Into the shared factor by default, so every channel feels it by its loading. Onto the leader's level alone with the one-channel shock knob, so its base level never moves |
| Switch | A lasting change in base levels that changes which channel pays best. The leader falls, a sleeper rises past it, or both |
| Drift | A switch stretched over many more rounds |
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
| Hard variant | A harder version of a scenario: more shocks before the switch, or a longer drift |

## How the agent plays

| Word | What it means |
|---|---|
| Bet | The whole number of budget points the agent puts on one channel in a round. Its ten bets each round sum to 100 |
| Split | The agent's ten bets in one round, taken together. Payout is linear, so points on more than one channel only ever mean doubt or a look |
| Look | A small bet on a channel the agent isn't backing, to read its level. A small bet gives a rough reading, see [mechanics](design/mechanics.md#what-the-agent-sees) |

## Scoring

| Word | What it means |
|---|---|
| Scenario score | The share of the gap between the Uniform and Discerning baselines a model earned, pooled over seeds. 0 is knowing nothing, 1 is knowing the climate. See [scoring](design/scoring.md#how-we-score) |
| Run score | One seed's share of that gap, shown as a dot. It can land outside 0 to 1 on one seed. The scenario score pools seeds so it rarely does |
| Headline | One score per model: the plain mean of its eight scenario scores. Reported with the weakest trait beside it. See [scoring](design/scoring.md#how-we-score) |
| Weakest trait | The lowest of a model's eight scenario scores, named. The AND the headline alone does not give |
| Noise threshold | The full study headline. The signal to noise at which a model's headline sits half way between the Complacent baseline's and 1. Lower is better. See [scoring](design/scoring.md#noise-threshold) |
| Signal to noise | The size of a switch in level points over the weather's SD per round. The axis every release shares. See [difficulty](design/mechanics.md#difficulty) |
| Noise grid | The fixed signal to noise settings the full study plays, chosen from the baselines before any model runs. See [pilot](pilot/engine-checks.md#noise-grid) |
| Trait | What one scenario tests, named as the virtue a high score shows. See [traits](design/scoring.md#traits) |
| Composure | The No change scenario's trait. Ignoring noise when nothing is happening |
| Patience | The One shock scenario's trait. Holding through a dip that passes |
| Doubt | The Down switch scenario's trait. Questioning the plan when the change is real |
| Curiosity | The Up switch scenario's trait. Looking when nothing is wrong, and moving only for a rise that beats the plan |
| Unlearning | The Shock then switch scenario's trait. Dropping "dips recover" once it stops being true |
| Vigilance | The Slow drift scenario's trait. Noticing a decline that has no sudden move |
| Conviction | The Switch then shock scenario's trait. Holding a plan it just chose through a dip that passes |
| Recall | The Up switch then down switch scenario's trait. Going back to a plan it has seen pay when the change undoes itself, rather than treating the change as permanent |
| Trait profile | A model's scores across scenarios, one per trait. The signal the headline combines |
| Error bar | How sure we are of a score. Spread over √seeds, so it shrinks with more seeds (epistemic uncertainty). See [scoring](design/scoring.md#error-bars) |
| Spread | How far one run lands from another. Does not shrink with more seeds (aleatoric uncertainty). See [scoring](design/scoring.md#spread) |
| Sampling spread | The part of spread from the model's own draws. Same seed, run again |
| World spread | The part of spread from the seed |
| Skin sensitivity | The gap in a model's score between skins, which covers both the story and how the skin words the frame. A finding, not an error. Not measured until more than one skin runs |

## Seeds and secrecy

| Word | What it means |
|---|---|
| Seed | The number that fixes a run's world: every channel's noise for every round, drawn up front |
| Twin tapes | The tapes one seed makes across scenarios. They share the ladder, the weather and the onset round, so they match until the events differ. See [seeds](design/scoring.md#seeds) |
| Seed set | The fixed list of seeds a scenario plays. Each scenario has two, public seeds and held-out seeds. See [contamination](harness/contamination.md#two-seed-sets) |
| Public seeds | Seeds published in this repo with their tapes. For the pilot, the example logs and anyone checking our work |
| Held-out | Kept in the private repo and never published. Held-out skins and held-out seeds make the headline |
| Release | One published set of the benchmark's frozen generator defaults, noise grid and fresh held-out seeds. Releases share the signal to noise axis. See [contamination](harness/contamination.md) |
| Contamination | A model having seen the benchmark in training |
| Canary | A fixed line in every published file that holds prompt text. A model that can repeat it has seen our data. See [contamination](harness/contamination.md#canary) |

## Adding a word

1. **One word per idea.** Don't invent a second name for something already here.
2. **Prefer the word that says what the thing is**, not where it came from.
3. **Prose uses game engine words.** A skin's nouns appear only in examples that say which skin they're from.
