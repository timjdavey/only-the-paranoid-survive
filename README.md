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

This study specifically tests:

1. **Natural variation with memory.** In most tests the noise has no memory, so a bad streak is strong evidence by itself. Here a bad month is ordinary, and the matching run holds a dip that starts like the real change. An agent has to use judgement to tell a bad stretch from a changed world.
2. **Score discernment.** Most tests count only being too slow. However, being too jumpy is a failure state in itself. So we benchmark false alarms as well, on the same luck.
3. **Kinds of change, not sizes only.** The world is a small system of four blocks, and a change edits one. The proof of concept moves a level. The full study moves how units couple, how returns saturate and how yield is credited, which no per-unit tracker can find.
4. **A number to track across releases.** The full study's headline is the faintest change a model acts on, read against the best bot we can build. A model that matches the bot has saturated this edition, and a harder edition moves the bar while keeping the numbers on one axis. The proof of concept, at about $100 a model, is cheap enough to rerun on each release.

## Reported

The benchmark comes in two tiers. The proof of concept is built and run first. The full study is the funded version, with more runs per model.

- **Performance**, how well an agent performed against a perfect bot with complete information. This bundles both noticing the change and ability to update strategy to act on this new suspicion.
- **Discernment**, the full study headline. The smallest change the agent profits from. Smaller is better.
- **Insight.** Whether it worked out what changed, rather than just shuffling its bets.
- **Paranoia, caution and conviction.** Whether it doubts too readily, waits too long for evidence, or holds back once it switches. Each is read against our best bot, and zero is ideal.

How each is worked out is in [Measures](docs/design/measures.md).

## Results

To come.
