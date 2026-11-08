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
