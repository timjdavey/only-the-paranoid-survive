# Only the paranoid survive

_A benchmark for how well an agent acts when presented with a shock to a system that returns to normal vs a shock that creates a new normal._

## Motivation

In the 1980s Intel's memory chip business was declining. The board thought it was simply a bad sales patch, so advised staying the course while innovating on the margin. Instead Andy Grove their CEO saw the industry had fundamentally shifted. He moved the company out of memory entirely and into processors to become one of the best performing companies of the century.

Keynes supposedly wrote "When the facts change, I change my mind. What do you do sir?" But that understates the hard part which is spotting that things have actually changed rather than it just being volatility. Grove wrote about this in his book *Only the Paranoid Survive*.

There is a long line of famous companies which acted too slowly to fundamental change: Blockbuster, Kodak, Blackberry. However the reverse is also true with companies like Peloton and Hopin betting too hard on a new normal, when it's surprising how resilient systems are and tend to regress to the mean. These stories are clear with hindsight, but is why we need to measure both scenarios.

As agents take on longer jobs and interact with long running complex systems, the more likely they will face these situations. The more autonomous they become the more they will need to be able to adapt appropriately.

People react to the signals in front of them and too little to the system that makes them. So they overreact when the world is stable and the signals are noisy, and underreact when the world is changing and the signals are precise. This is called [system neglect](docs/prior/people.md#massey-and-wu-2005-system-neglect). Whether agents share the bias, and which way they lean, is the question.


## Design

- The study is built around a simple cybernetics game engine.
- The agent plays by betting a fixed budget across channels each round. See [interface](docs/design/interface.md).
- The payout is linear, noise is the difficulty knob, and the agent only sees the channels it bets on. See [mechanics](docs/design/mechanics.md).
- That engine then has a set of _narrative skins_ around it. So that the model thinks it is a real situation and so is more likely to act accordingly. But also this helps with contamination, as we can publish the game engine but disguise the game skin.
- We [baseline](docs/design/baselines.md) a model's performance against various strategies. 
- A model has to respond appropriately in a variety of different [scenarios](docs/design/scenarios.md). The headline scores that one skill. Whether it predicts how an agent does on real work is a claim to test, see [themes](docs/prior/themes.md).
- We [score](docs/design/scoring.md) each scenario as the share of the gap between the Uniform and Discerning baselines a model earned, pooled over seeds. So 0 is knowing nothing and 1 is knowing the regime. The headline is the geometric mean across scenarios, so a model needs to do well in all of them to score highly.
- A [pilot](docs/pilot/checks.md) settles the knobs, such as how many seeds, before the full run.
- The full study plays a grid of noise levels on one signal to noise axis and reports the [noise threshold](docs/design/scoring.md#noise-threshold), the noisiest world a model still reads. Harder editions extend the grid rather than start a new chart.
- It has been designed so that we can test [Jev](https://docs.typesafe.ai/introduction) and [Timestral](https://github.com/mistralai/timestral) alongside classic LLMs.
- What the game gives up, and what checks each gap, is in [limits](docs/design/limits.md).

## Repo

- The code is four layers, engine, skins, harness and analysis, each importing only the one below. See [layout](docs/harness/layout.md).
- The harness is [inspect_ai](docs/harness/inspect.md). Setup and commands are in [running](docs/harness/running.md).
- The engine, the public seeds and this repo are public. The held-out skins and held-out seeds are private. See [contamination](docs/harness/contamination.md).

## Contribution

See [CONTRIBUTING](CONTRIBUTING.md).

## Results

To come.


