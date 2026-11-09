# Baselines

## Fixed baselines

These are calculated scores based on fixed strategies.

| Baseline | Betting rule | What it settles |
|---|---|---|
| Discerning baseline | 100 on the channel with the highest base level. Holds through a shock, moves the round a switch lands | The ceiling. A scenario score of 1, see [scoring](scoring.md). Its one edge over an ideal reader is zero lag, which is the thing we price |
| Uniform baseline | 10 on every channel, every round | The floor. A scenario score of 0. What knowing nothing earns. It sees every channel at the roughest reading, so it is the fully paranoid floor too |
| Complacent baseline | The Discerning baseline's round 1 bets, held to the end | A mark on every bar. Near 0.55 where there is a switch, so it says whether a model acted at all. Equals the Discerning baseline where nothing changes |
| Perfect baseline | 100 on the channel with the highest level this round | A mark for how much weather luck was on offer. It divides nothing: it chases weather no reader can see, so nobody could reach it |
| Hedge rule baseline | A few points on the hedge, the rest on the leader. When the leader falls and the hedge does not rise, it moves to the best channel it can see | The simplest player that reads the tell. A mark on every bar, and a reference curve on the [noise grid](../pilot/engine-checks.md#noise-grid) |

- **Players may read their own record. The yardstick may not.** The Discerning baseline reads the tape, so the score is the same whatever the agent chose to look at. A Bayesian or CUSUM player that reads its own record is a fine mark, see [not yet](#not-yet), but never a denominator, as a lazy agent would get a lenient yardstick.

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
| Timestral odds | Splits the 100 by each channel's chance of being the best. The less sure it is, the more it spreads, and so the more it looks | Whether a forecaster's own doubt makes it look the right amount. Dropped if it fails the [gap test](../pilot/provider-checks.md#timestral-checks) |
| Timestral top pick with looks, 1 / 2 / 5 | 1, 2 or 5 points on each of the other nine channels, the rest on its top pick, which gets 91, 82 or 55 | Whether a look size we choose by hand does better than Timestral's own doubt |
| Timestral odds, bet aware | As Timestral odds, but its past bets go in alongside the levels | Whether it learns that a small bet gives a rough reading |

## Checks

- **Timestral** must pass a gap test and a rounding watch before we trust it, see [pilot](../pilot/provider-checks.md#timestral-checks).
- **The baselines must land in the expected order** in the One switch and No change scenarios, see [pilot](../pilot/engine-checks.md#baseline-order).

## Not yet

| Baseline | Why not yet |
|---|---|
| Bayesian | A belief that knows the engine's family, run through the same policies as Timestral. It is valid as a player: it bets on past readings only, so there is no loop. Never the yardstick, as what it could know depends on what it looked at. Parked until Timestral has run, as the hazard prior is a dial we would have to pre register |
| CUSUM | The textbook change detector: sum how much each reading favours a change, move when the sum crosses a line. Swept from hasty to patient it draws the trade between delay and false alarms. Add it once the hedge rule has run |
| Fixed split | Incumbent plus a fixed split that never acts pays for a look it never uses, so it sits below the Complacent baseline. With a switch rule it is the hedge rule or the Timestral top pick with looks row |
| Barbell | Leader plus the round 1 runner-up. A cheap win when only the leader falls, a decoy when a [sleeper](mechanics.md#events) rises. Add it once the pilot shows how often a sleeper rises |
