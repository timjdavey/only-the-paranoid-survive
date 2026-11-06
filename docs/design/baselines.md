# Baselines

## Fixed baselines

These are calculated scores based on fixed strategies.

| Baseline | Split rule | What it settles |
|---|---|---|
| Oracle | 100 on the channel with the highest mean level this round | The ceiling. Every score is a fraction of it, see [scoring](scoring.md). It chases a shock dip if another channel beats the trough, so nobody scores 1 on shock |
| Steady | 100 on the channel with the highest mean level in the current regime. Holds through a shock, moves at a switch | What patience earns against the ceiling. Not a denominator, as a model can beat it in a shock |
| Stale | The oracle's round 1 split, held to the end | The complacent floor. Matches the regime oracle on calm and shock, so the suite separates it only on switch and drift |
| Uniform | 10 on every channel, every round | What knowing nothing earns. It sees every channel at the roughest reading, so it is the fully paranoid floor too |

## Timestral

[Timestral](https://github.com/mistralai/timestral) is a forecaster, so each baseline here is its forecast plus a policy we wrote. The policy is named, not hidden in "a fixed rule".

- **In: each channel's level history**, as one series with ten variates forecast jointly. A round the channel was not funded goes in as NaN, which Timestral supports.
- **Levels, never output.** Feed it output and a share of 0 reads as a real 0. It forecasts 0, the policy puts 0 on the channel, and it is locked out for good.
- **Out: 21 quantiles per channel** for next round's level.
- **It never sees the skin.** That makes it a floor for how much reading the situation helps.

One run per row. The split is whole numbers to 100, as on the [interface](interface.md) page.

| Baseline | Split rule | What it is a floor for |
|---|---|---|
| Argmax | 100 on the channel with the highest median | Forecast, never look. It switches only when the funded channel's forecast falls below what it remembers of another |
| Probability of best | Each channel's share is the chance it has the highest level, read off the quantiles | Forecast, and look as much as its own doubt says. The look size is Timestral's, not ours |
| Constant look, 2 / 5 / 10 | That many points on every other channel, the rest on the highest median | Forecast plus a dumb look of a size we chose |
| Probability of best, split as covariate | As probability of best, with the shares passed in as a past covariate | Whether it can learn that a small share is a rough reading |

## Sanity ordering

- **On switch**, oracle above Timestral above stale above uniform.
- **On calm**, stale matches both oracles.
- **If the order breaks**, the noise knob in [mechanics](mechanics.md) or a baseline is wrong.

## Checks before we trust them

- **Gap test.** Ten readings, then thirty blanks. The quantiles should widen as the gap grows. If they do not, probability of best cannot look and is dropped.
- **Rounding.** A tiny probability rounds to 0, which is a blank, so a channel can still fall out of view. Watch how often it happens.

## Not yet

| Baseline | Why not yet |
|---|---|
| Bayesian | A belief that knows the engine's family, run through the same policies as Timestral. It is valid: it bets on past readings only, so there is no loop. Parked until Timestral has run, as the hazard prior is a dial we would have to pre register |
| Hedge | Incumbent plus a fixed spread that never acts pays for a look it never uses, so it sits below stale. With a switch rule it is the constant look row |
| Barbell | Incumbent plus one challenger. Needs a rule for the challenger, which waits on [what the other channels do in a switch](scenarios.md#open-questions) |
