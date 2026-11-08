# Glossary

**The one word we use for each idea in the benchmark.**

Use these words in prose and in code. Add a word here before using it on any other page.

| Word | What it means |
|---|---|
| Game engine | The simple cybernetics game at the core of the study: the rules and numbers, with no story |
| Narrative skin | A story dressed over the game engine, so the model treats it as a real situation. It also lets us publish the engine while hiding which skin it wears |
| Model | The system we test: classic LLMs, plus Jev, Timestral etc |
| Agent | A model while it plays the game |
| Run | One playthrough of the game |
| Seed | The number that fixes a run's world: every channel's noise for every round, drawn up front |
| Channel | One of the things the agent can put budget on. Each pays out at its own level |
| Bet | The whole number of budget points the agent puts on one channel in a round. Its ten bets each round sum to 100 |
| Scenario | A pattern of change we put each model through. See [scenarios](design/scenarios.md) |
| Contamination | A model having seen the benchmark in training |
| Base level | A channel's mean when nothing is happening |
| Weather | The round-to-round wobble round a base level |
| Memory | How much of this round's weather carries into the next. At 0.8 a bad stretch is half gone after three rounds |
| Shared factor | One hidden series every channel loads on, so channels have good and bad weeks together |
| Loading | How much a channel moves with the shared factor. Uneven across channels |
| Hedge | The one channel with a negative loading. It rises when everything else falls |
| Look | A small bet on a channel the agent isn't backing, to read its level. A small bet gives a rough reading, see [mechanics](design/mechanics.md#what-the-agent-sees) |
| Leader | The channel that pays best when a run starts |
| Runner-up | The second best channel at the start. The obvious fallback |
| Field | The other channels, including the hedge |
| Sleeper | A field channel whose base level rises past the leader's in a switch |
| Event | A shock, switch or drift. The three moves a world can make |
| Tape | The true level of every channel in every round, as one seed produces it. Saved and replayed |
| Baseline | A fixed strategy run through the same game and score as the models. See [baselines](design/baselines.md) |
| Oracle | The baseline that knows each round's levels. Every score is a fraction of what it earns |
| Level | A channel's true payout, which its noisy output sits around. Never called a mean: that word is kept for averaging over runs |
| Error bar | How sure we are of a score. Spread over √seeds, so it shrinks with more seeds (epistemic uncertainty). See [scoring](design/scoring.md#error-bars) |
| Spread | How far one run lands from another. Does not shrink with more seeds (aleatoric uncertainty). See [scoring](design/scoring.md#spread) |
| Sampling spread | The part of spread from the model's own draws. Same seed, run again |
| World spread | The part of spread from the seed |
| Skin sensitivity | The gap in a model's score between skins. A finding, not an error. Not measured until more than one skin runs |
| Trait profile | A model's scores across scenarios. The signal the headline combines |

## Adding a word

1. **One word per idea.** Don't invent a second name for something already here.
2. **Prefer the word that says what the thing is**, not where it came from.
3. **Prose uses game engine words.** A skin's nouns appear only in examples that say which skin they're from.
