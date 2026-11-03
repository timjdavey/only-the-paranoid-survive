# Only the paranoid survive

**A benchmark for assessing how good an agent is at discerning a change in system dynamics from just a run of unusual events.**

## Motivation

In the 1980s Intel's memory chip business was declining. The board thought it was simply a bad patch, so advised staying the course while innovating on the margin. Instead Andy Grove their CEO saw the industry had fundamentally shifted. He moved the company out of memory entirely and into processors to become one of the best performing companies of the century.

Keynes supposedly wrote "When the facts change, I change my mind. What do you do sir?" But that understates the hard bit, the difficulty is spotting the warning signals that they have changed. Grove wrote about this in his book *Only the Paranoid Survive*.

There is a long line of famous companies which acted too slowly: Blockbuster, Kodak, Blackberry. However the reverse is also true with companies like Peloton and Hopin betting too hard on a new normal.

As agents take on longer jobs, the more likely the world will change. The more autonomous they become, the more they will need to learn on the fly to update their strategies. Here we aim to measure how agents handle discerning if a plan it was given has gone stale.

## Contribution

This study specifically tests:

1. **Dynamics which change slowly.** Most tests swap the rules abruptly. Meaning a single bad result makes the dynamics obvious. Here we boil the frog, so that an agent has to use judgement to tell a bad streak from a changed dynamic.
2. **Score discernment.** Most tests count only being too slow. However, being too jumpy is a failure state in itself. So we benchmark false alarms as well.
3. **A number to track across releases.** The threshold has no ceiling, so it won't saturate within a few model releases. At about $100 a model, it is cheap enough to rerun on each one.

## Reported

To come.

## Results

To come.
