# Baselines

## Fixed baselines

These are calculated scores based on fixed strategies.

| Baseline | Betting rule | What it settles |
|---|---|---|
| Perfect baseline | 100 on the channel with the highest level this round | The ceiling. Every score is a fraction of it, see [scoring](scoring.md). It chases a shock dip if another channel beats the trough, so nobody scores 1 in the One shock scenario |
| Discerning baseline | 100 on the channel with the highest base level. Holds through a shock, moves at a switch | What patience earns against the ceiling. Not a denominator, as a model can beat it in a shock |
| Complacent baseline | The Perfect baseline's round 1 bets, held to the end | The floor for never updating. Matches the Discerning baseline in the No change and One shock scenarios, so the suite separates it only in scenarios with a switch or drift |
| Uniform baseline | 10 on every channel, every round | What knowing nothing earns. It sees every channel at the roughest reading, so it is the fully paranoid floor too |

## Timestral

[Timestral](https://github.com/mistralai/timestral) is a forecaster. It guesses each channel's level next round, and a policy we wrote turns that guess into bets. It only learns about a channel by betting on it.

- **What it sees:** each channel's past levels, but only for the rounds it bet on that channel. Every other round is a gap, which Timestral handles.
- **Why levels and not output:** a bet of 0 pays 0. Timestral would read that as a channel that pays nothing, put 0 on it and never return.
- **What it gives back:** a range of guesses, low to high, for each channel's level next round. That is 21 quantiles per channel.
- **What it never sees:** the skin. So it shows how much reading the story helps.

The policy that turns the forecast into bets is ours. One run per row. The bets are whole numbers to 100, as on the [interface](interface.md) page.

| Baseline | How it bets | What it tells us |
|---|---|---|
| Timestral top pick | 100 on the channel it forecasts highest. The other channels go dark, so it only moves when its own channel's forecast falls below its last memory of another | How far forecasting gets you with no looking |
| Timestral odds | Splits the 100 by each channel's chance of being the best. The less sure it is, the more it spreads, and so the more it looks | Whether a forecaster's own doubt makes it look the right amount. Dropped if it fails the [gap test](../pilot/checks.md#timestral-checks) |
| Timestral top pick with looks, 1 / 2 / 5 | 1, 2 or 5 points on each of the other nine channels, the rest on its top pick, which gets 91, 82 or 55 | Whether a look size we choose by hand does better than Timestral's own doubt |
| Timestral odds, bet aware | As Timestral odds, but its past bets go in alongside the levels | Whether it learns that a small bet gives a rough reading |

## Checks

- **Timestral** must pass a gap test and a rounding watch before we trust it, see [pilot](../pilot/checks.md#timestral-checks).
- **The baselines must land in the expected order** in the One switch and No change scenarios, see [pilot](../pilot/checks.md#baseline-order).

## Not yet

| Baseline | Why not yet |
|---|---|
| Bayesian | A belief that knows the engine's family, run through the same policies as Timestral. It is valid: it bets on past readings only, so there is no loop. Parked until Timestral has run, as the hazard prior is a dial we would have to pre register |
| Fixed split | Incumbent plus a fixed split that never acts pays for a look it never uses, so it sits below the Complacent baseline. With a switch rule it is the Timestral top pick with looks row |
| Barbell | Leader plus the round 1 runner-up. A cheap win when only the leader falls, a decoy when a [sleeper](mechanics.md#events) rises. Add it once the pilot shows how often a sleeper rises |
