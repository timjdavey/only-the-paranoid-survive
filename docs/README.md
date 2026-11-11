# Docs

Every page in this folder, and what it holds.

- **New here?** Read the [README](../README.md) for the question the study asks, then the [glossary](glossary.md) for the one word we use for each idea.
- **Changing something?** Read [CONTRIBUTING](../CONTRIBUTING.md) first.
- **Folders are in reading order.** Design is why, harness is how it is built, specs is exactly what each layer must do.

## Design

Why the game is the way it is. The decisions and the reasons.

| Page | What's in it |
|---|---|
| [Interface](design/interface.md) | How the agent plays: ten bets a round, the tools it gets, and the models that cannot place bets |
| [Mechanics](design/mechanics.md) | How the engine pays out, where each channel's level comes from and what the agent sees |
| [Scenarios](design/scenarios.md) | The scenarios we play, the events each is built from and the ones we skip |
| [Baselines](design/baselines.md) | What each baseline is for |
| [Scoring](design/scoring.md) | The scenario score, the headline, error bars and the noise threshold |
| [Limits](design/limits.md) | What the game gives up, why we accept it and what checks each gap |
| [Future work](design/future.md) | Studies we'd like to run beyond the headline |

## Harness

How it is built. Layers, tools and commands.

| Page | What's in it |
|---|---|
| [Layout](harness/layout.md) | The six layers of the code and the rule for what imports what |
| [Inspect](harness/inspect.md) | How the design maps onto inspect_ai |
| [Running](harness/running.md) | Setup, commands, logs and the cost guard |
| [Models](harness/models.md) | Which models run and with what settings |
| [Providers](harness/providers.md) | How the harness plays Jev and Timestral |
| [Prompts](harness/prompts.md) | What the agent sees each round. Frozen once the pilot has run |
| [Skins](harness/skins.md) | What a skin file holds and where it lives |
| [Writing a skin](harness/writing-a-skin.md) | How to write a good skin |
| [Contamination](harness/contamination.md) | What is published, what is held back and why |

## Specs

The contract each layer of the code is written to, and tested against.

- **Start at the [specs README](specs/README.md).** It holds the rules for a spec page and links each layer's folder: engine, baselines, skins, harness and analysis.
- **Each layer's README lists its pages.** So they are not listed again here.

## Pilot

The short run before the full study that settles the knobs.

| Page | What's in it |
|---|---|
| [Engine checks](pilot/engine-checks.md) | The first half of the pilot: checks that need timelines and baselines but no model |
| [Provider checks](pilot/provider-checks.md) | The second half of the pilot: checks that need a model |
| [Decisions](pilot/decisions.md) | One row per check and per knob, filled once and then frozen |
| [Results](pilot/results.md) | The pilot's tables and plots. Written by `paranoid analyse`, never by hand |

## Results

| Page | What's in it |
|---|---|
| [Proof of concept](results/poc.md) | The first run of the full harness. Written by `paranoid analyse`, never by hand |

## Prior work

What others have found on telling a shock from a switch, in LLMs, in people and in animals.

- **Start at the [prior work README](prior/README.md).** It lists the pages, sums up the literature and says how our game differs.
