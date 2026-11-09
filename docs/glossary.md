# Glossary

**The one word we use for each idea in the benchmark.**

Use these words in prose and in code. Add a word here before using it on any other page.

## The study

| Word | What it means |
|---|---|
| Game engine | The simple cybernetics game at the core of the study: the rules and numbers, with no story |
| Narrative skin | A story dressed over the game engine, so the model treats it as a real situation. It also lets us publish the engine while hiding which skin it wears |
| Model | The system we test: classic LLMs, plus Jev, Timestral etc |
| Agent | A model while it plays the game |
| Run | One playthrough of the game |
| Baseline | A fixed strategy run through the same game and score as the models. A fixed baseline's name always ends in "baseline", so it never reads as a plain adjective. See [baselines](design/baselines.md) |
| Perfect baseline | The baseline that knows each round's levels and bets on the best channel. Every score is a fraction of what it earns. `baseline/perfect` in code |
| Discerning baseline | The baseline that knows each channel's base level, so it holds through a shock and moves at a switch. `baseline/discerning` in code |
| Stale baseline | The baseline that holds its round 1 bets to the end. `baseline/stale` in code |
| Uniform baseline | The baseline that bets 10 on every channel, every round. `baseline/uniform` in code |
| Reasoning setting | How hard a model is allowed to think, from one shared grid: `off`, `low`, `medium`, `high`, `max`, or `on` when it can't be changed. Each setting is its own row. See [models](harness/models.md#reasoning) |
| ECI | Epoch AI's [Capabilities Index](https://epoch.ai/benchmarks/eci), one general capability score per model. The x axis of a [trend plot](harness/models.md#trend-plots) |

## The world

| Word | What it means |
|---|---|
| Channel | One of the things the agent can put budget on. Each pays out at its own level |
| Level | A channel's true payout, which its noisy output sits around. Never called a mean: that word is kept for averaging over runs |
| Base level | A channel's mean when nothing is happening |
| Weather | The round-to-round wobble round a base level |
| Persistence | How much of this round's weather carries into the next. At 0.8 a bad stretch is half gone after three rounds |
| Shared factor | One hidden series every channel loads on, so channels have good and bad weeks together |
| Loading | How much a channel moves with the shared factor. Uneven across channels |
| Hedge | The one channel with a negative loading. It rises when everything else falls |
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
| Switch | A lasting fall in the leader's base level, sometimes with a sleeper rising |
| Drift | A switch stretched over many more rounds |
| Profile | The form an event takes within its shape, drawn per seed. A shock falls sharply and climbs slowly, or slides and rebounds. A drift is linear or logistic |
| Scenario | A list of events we put each model through. Its name always ends in "scenario", so it never reads as an event. See [scenarios](design/scenarios.md) |
| No change scenario | No events. `no_change` in code |
| One shock scenario | One shock. `one_shock` in code |
| One switch scenario | One switch. `one_switch` in code |
| Shock then switch scenario | One shock, a gap, then one switch. `shock_then_switch` in code |
| Slow drift scenario | One drift. `slow_drift` in code |
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
| Headline | One score per model: the geometric mean of its scenario scores. See [scoring](design/scoring.md#how-we-score) |
| Trait | What one scenario tests, named as the virtue a high score shows. See [traits](design/scoring.md#traits) |
| Composure | The No change scenario's trait. Ignoring noise when nothing is happening |
| Patience | The One shock scenario's trait. Holding through a dip that passes |
| Doubt | The One switch scenario's trait. Questioning the plan when the change is real |
| Unlearning | The Shock then switch scenario's trait. Dropping "dips recover" once it stops being true |
| Vigilance | The Slow drift scenario's trait. Noticing a decline that has no sudden move |
| Trait profile | A model's scores across scenarios, one per trait. The signal the headline combines |
| Error bar | How sure we are of a score. Spread over √seeds, so it shrinks with more seeds (epistemic uncertainty). See [scoring](design/scoring.md#error-bars) |
| Spread | How far one run lands from another. Does not shrink with more seeds (aleatoric uncertainty). See [scoring](design/scoring.md#spread) |
| Sampling spread | The part of spread from the model's own draws. Same seed, run again |
| World spread | The part of spread from the seed |
| Skin sensitivity | The gap in a model's score between skins. A finding, not an error. Not measured until more than one skin runs |

## Seeds and secrecy

| Word | What it means |
|---|---|
| Seed | The number that fixes a run's world: every channel's noise for every round, drawn up front |
| Seed set | The fixed list of seeds a scenario plays. Each scenario has two, public seeds and held-out seeds. See [contamination](harness/contamination.md#two-seed-sets) |
| Public seeds | Seeds published in this repo with their tapes. For the pilot, the example logs and anyone checking our work |
| Held-out | Kept in the private repo and never published. Held-out skins and held-out seeds make the headline |
| Edition | One release of the benchmark, with fresh held-out seeds. See [contamination](harness/contamination.md) |
| Contamination | A model having seen the benchmark in training |

## Adding a word

1. **One word per idea.** Don't invent a second name for something already here.
2. **Prefer the word that says what the thing is**, not where it came from.
3. **Prose uses game engine words.** A skin's nouns appear only in examples that say which skin they're from.
