# Only the paranoid survive

**A benchmark for how well an agent tells a change in the dynamics of a system from a run of ordinary bad luck.**

## Motivation

In the 1980s Intel's memory chip business was declining. The board thought it was simply a bad patch, so advised staying the course while innovating on the margin. Instead Andy Grove their CEO saw the industry had fundamentally shifted. He moved the company out of memory entirely and into processors to become one of the best performing companies of the century.

Keynes supposedly wrote "When the facts change, I change my mind. What do you do sir?" But that understates the hard bit, the difficulty is spotting the warning signals that they have changed. Grove wrote about this in his book *Only the Paranoid Survive* (Currency Doubleday, 1996).

There is a long line of famous companies which acted too slowly: Blockbuster, Kodak, Blackberry. However the reverse is also true with companies like Peloton and Hopin betting too hard on a new normal.

As agents take on longer jobs, the more likely the world will change under them. The more autonomous they become, the more they will need to tell a change in how the world works from a bad month, and update their strategies when it is the former. That is the skill we measure. Its everyday form is knowing when the notes you are working from have gone stale.

## The game

- **A simple betting game.** Each week the agent splits a budget across ten options and sees what each of its bets paid back. It learns nothing about options it didn't bet on.
- **Weather.** Good and bad stretches last a while and then fade, options rise and fall together, and now and then one dips and recovers. A bad month is ordinary.
- **A quiet change.** A few weeks in, one of its favourite options slowly gets worse and one it ignores gets better. Its old split still wins, just less than it could.
- **The same game with no change.** Every game is replayed on the same luck with nothing changed, only a dip that starts the same way and then recovers. So acting too early counts against the agent, not only acting too late.
- **One game, many stories.** The options can be ad channels or factory lines, with the same numbers underneath.

The full design is in [docs/design](docs/design/README.md), and the words are in the [glossary](docs/glossary.md).

## Contribution

This study tests four things most benchmarks leave out.

1. **Bad luck comes in streaks.** In most tests each result is drawn fresh, so a bad streak is strong evidence that something changed. Here a bad month is ordinary, and the same game with no change holds a dip that starts just like the real change. The agent has to judge whether it is looking at a bad stretch or a changed world.
2. **Acting too early counts, not only acting too late.** Most tests only count being too slow. Being too jumpy is a failure too, so we count false alarms as well, on the same luck.
3. **Different kinds of change, not just different sizes.** Under the hood the world is built from four parts, and a change edits one of them. The first version of the benchmark, the proof of concept, changes only how well one option pays. The full study also changes how options affect each other, how fast extra spend stops paying, and which option gets the credit for a result. A bot that watches each option on its own can't spot these.
4. **A number to track across releases.** The full study's main score, discernment, is the faintest change a model acts on, measured against the best bot we can build. Once a model matches that bot, this edition of the game is too easy for it, so we make a harder one. Every edition reports on the same scale, so the line over releases stays unbroken. The proof of concept costs about $100 a model, cheap enough to rerun on each release.

## Reported

The benchmark comes in two tiers. The proof of concept is built and run first. The full study is the funded version, with more runs per model.

- **Performance**, the main score of the proof of concept. It measures how well the agent did against a perfect bot with complete information, so it covers both noticing the change and changing strategy to act on it.
- **Discernment**, the main score of the full study. It is the smallest change the agent profits from, so smaller is better.
- **Insight.** Whether it worked out what changed, rather than just shuffling its bets.
- **Paranoia, caution and conviction.** Whether it doubts too readily, waits too long for evidence, or holds back once it switches. Each is measured as a gap from our best bot, so zero is ideal.

How each is worked out is in [Measures](docs/design/measures.md).

## Results

To come.
