# Mechanics

How the game engine pays out, how noisy it is, and what the agent gets to see. How the agent sends its split is on the [interface](interface.md) page.

## Payout

- **Linear.** Output is the sum over channels of share times level. Point 70 on a channel pays the same as point 1.
- **So the oracle goes all in** on the channel with the highest level. A spread only ever means doubt or a look. See [scoring](scoring.md).

## Noise

- **Each channel's level wanders round its mean every round.** One sigma for every channel, set per scenario.
- **Noise is the difficulty knob.** With low noise one reading settles whether a dip is a shock or a switch. With high noise it takes many rounds. Raise it to keep the test from saturating.

## What the agent sees

- **Only the channels it funded.** A share of 0 shows a blank in the record, not a 0.
- **A small share gives a rough reading, a large share a clean one.** Read noise shrinks as spend rises, the way customers from a small spend are a small count. The skin explains it, so there is no rule to tell the agent.
- **Why.** A look costs something, so paranoia has a price. You know a market by being in it.

## Rejected

| Option | Why not |
|---|---|
| Concave payout | The oracle spreads too, so a spread stops reading as belief. The agent has to be told the curve and do the maths, and a model bad at the maths looks like a model full of doubt |
| A sigma per channel | With a fixed budget that does not compound and a linear payout, sigma never changes which channel is best. It adds risk maths the score never rewards |
| Every channel visible | A look is free, so a calm agent and a paranoid one only differ by jumpiness. A forecaster then wins by reading series, which is a different study |
