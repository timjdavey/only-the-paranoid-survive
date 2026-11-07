# Mechanics

## Noise

- Each channel's output is noisy around its mean every turn. With a set sigma pure channel per regime.
- Noise can be seen as a difficulty knob. With low noise one reading settles whether a dip is a shock or a switch. With high noise it takes many rounds. Its level is set in the [pilot](../pilot/checks.md#noise).

## Information

- We want this setup to feel as real as possible. You only get information on channel performance for your company or campaign by actually trying it. So agents only see information for channels they bet on. Betting zero gives you NaN (for Timestral).
- A small bet gives a worse reading. This is for realism, but also to give a reward for exploration. This can be done through small count errors. e.g. Small bets, lead to lower volume int returns so coarse grained returns or via noise. How rough, and by which route, is set in the [pilot](../pilot/checks.md#reading-roughness).

## Payout

We go with a simple linear payout (rather than concave). This keeps the game simpler arithmetic wise. And means a rational strategy is to go all in on a specific channel, if you have perfect information (which of course agents do not).
