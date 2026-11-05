# Only the paranoid survive

**A benchmark for how well an agent tells a change in the dynamics of a system from a run of ordinary bad luck.**

## Motivation

In the 1980s Intel's memory chip business was declining. The board thought it was simply a bad patch, so advised staying the course while innovating on the margin. Instead Andy Grove their CEO saw the industry had fundamentally shifted. He moved the company out of memory entirely and into processors to become one of the best performing companies of the century.

Keynes supposedly wrote "When the facts change, I change my mind. What do you do sir?" But that understates the hard bit, the difficulty is spotting the warning signals that they have changed. Grove wrote about this in his book *Only the Paranoid Survive* (Currency Doubleday, 1996).

There is a long line of famous companies which acted too slowly: Blockbuster, Kodak, Blackberry. However the reverse is also true with companies like Peloton and Hopin betting too hard on a new normal.

As agents take on longer jobs, the more likely the world will change under them. The more autonomous they become, the more they will need to tell a change in how the world works from a bad month, and update their strategies when it is the former. That is the skill we measure. Its everyday form is knowing when the notes you are working from have gone stale.


## Test design

- **A simple game wrapped in a narrative.** We wrap the core cybernetics style engine inside a variety of different story skins. This way we can control the environment and outputs, while also eliciting realistic responses. Such as ad-channels or factory lines.
- **Betting mechanics.** Each week the agent splits a budget across ten options and sees what each of its bets paid back (like splitting budget across paid marketing channels). The higher the bet the clearer the signal, but also potentially the higher the gains / losses.
- **Weather like periods.** The bets are not purely stochastic. Good and bad stretches last a while and then fade, where options rise and fall together to simulate real systems. But stable enough to feel like a typical static "game" which can be understood.
- **A quiet change.** Many rounds in, we change a key dynamic of the game. The change is like a boiling frog, where a previous plan will only fail slowly.
- **Baselined with no change.** Every game is replayed on the same initial setup but now with no fundamental change. So we can measure if any of the models are too jumpy.
- **Baselined against bots.** Every model is scored within the bounds of a perfect player, who knows the exact system and a dump player who acts with only a simple strategy.

The full design is in [docs/design](docs/design/README.md).
Also see the [glossary](docs/glossary.md) for full outline of terms.

## Contribution

We've specifically designed the study to focus on the following:

1. **A number which can be tracked across releases.** The full study's main score, discernment, measures the faintest change a model acts on, which is scored against a perfect bot. Once a model matches that bot, the parameters of the game are too easy, so the change becomes more subtle. Similar to the hearing aid analogy.
2. **Paranoia isn't enough.** Most tests only measure being blind to change. However, being too jumpy is also a failure mode. So we purposefully have a setup to measure the false alarms rate.
3. **The changes are masked.** In most studies which measure change the dynamic shift is abrupt telegraphing the change instantly and clearly. Meaning you're testing a models basic bayesian statistical capabilities, rather than judgement. Like the real world, it has to navigate a system without understanding the exact dynamics inside the black box. With unlikely streaks blurring real change.
4. **Different kinds of change, not just different sizes.** Under the hood the world is built from a few parts, and we change only one of them. The first version of the benchmark, the proof of concept, changes only how well one option pays. The full study also changes how options affect each other, how fast extra spend stops paying, and which option gets the credit for a result. A bot that watches each option on its own can't spot these - it needs to investigate holistically.

See [prior](docs/prior/README.md) for more details. 

## Reported

- **Performance**, the main score of the proof of concept. It measures how well the agent did against a perfect bot that is omniscient. This means it covers both noticing a change and appropriately acting on that change. It's the practical measure you want when trusting a model to complete economically valuable work.
- **Discernment**, the main score of the full study. Surgically measures the main aim of this benchmark, of identifying changes in dynamics.

Above are the headline figures we care about specifically for this task. But there are other skills compound into making these possible which we aim to measure independently. See [measure-headline.md](docs/design/measure-headline.md) for the headlines, and [measure-failure.md](docs/design/measure-failure.md) for where a model loses output.

## Results

To come.


## Motivation

This project isn't simply about getting the results. It is also a personal study in feeling my way toward what best practices exist when working with agents to build studies. This is why documents such as [TODO](TODO.md), [decisions.md](docs/design/decisions.md) and [requirements.md](docs/design/requirements.md) exist. They are a form of research harness - answering the question of what context, SKILLs, frameworks does an agent need to make good design decisions. Although ironically having structured documents like decisions.md is great for any human reviewing this study too.
