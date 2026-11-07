# Only the paranoid survive

_A benchmark for how well an agent acts when presented with a shock to a system the returns to normal vs a shock that creates a new normal._

## Motivation

In the 1980s Intel's memory chip business was declining. The board thought it was simply a bad sales patch, so advised staying the course while innovating on the margin. Instead Andy Grove their CEO saw the industry had fundamentally shifted. He moved the company out of memory entirely and into processors to become one of the best performing companies of the century.

Keynes supposedly wrote "When the facts change, I change my mind. What do you do sir?" But that understates the hard part which is spotting that things have actually changed rather than it just being volatility. Grove wrote about this in his book *Only the Paranoid Survive*.

There is a long line of famous companies which acted too slowly to fundamental change: Blockbuster, Kodak, Blackberry. However the reverse is also true with companies like Peloton and Hopin betting too hard on a new normal, when it's surprising how resilient systems are and tend to regress to the mean.

As agents take on longer jobs, the more likely they will face these situations. The more autonomous they become the more they will need to be be able to adapt correctly.


## Design

- The study is build around a simple cybernetics game engine.
- The agent plays by betting a fixed budget across channels each round. See [interface](docs/design/interface.md).
- The payout is linear, noise is the difficulty knob, and the agent only sees the channels it bets on. See [mechanics](docs/design/mechanics.md).
- That engine then has a set of _narrative skins_ around it. So that the model thinks it is a real situation and so is more likely to act accordingly. But also this helps with contamination, as we can publish the game engine but disguise the game skin.
- We [baseline](docs/design/baselines.md) a models performance against various strategies. 
- In order for models to be economically trustworthy they need to respond appropriately in a variety of different [scenarios](docs/design/scenarios.md).
- We [score](docs/design/scoring.md) each scenario as the mean over seeds of a model's output as a fraction of an oracle's, and take the geometric mean across scenarios as the headline. So it needs to perform well across all scenarios to score highly.
- A [pilot](docs/pilot/README.md) settles the knobs, such as how many seeds, before the full run.
- This study avoids becoming saturated by extending the game. Increasing the number of shocks before a switch; or more subtle drift into a switch.
- It has been designed so that we can test [Jev](https://docs.typesafe.ai/introduction) and [Timestral](https://github.com/mistralai/timestral) alongside classic LLMs.

## Contribution

To complete

## Results

To come.


