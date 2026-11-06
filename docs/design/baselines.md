# Baselines

A baseline is a fixed strategy run through the same engine, [scenarios](scenarios.md) and [score](scoring.md) as the models. The only ones so far are built on Timestral. They are near free to run, so we run every policy below.

## What Timestral gets and gives

- **In: each channel's level history**, as one series with ten variates forecast jointly. A round the channel was not funded goes in as NaN, which [Timestral](https://github.com/mistralai/timestral) supports.
- **Levels, never output.** Feed it output and a share of 0 reads as a real 0. It forecasts 0, the policy puts 0 on the channel, and it is locked out for good.
- **Out: 21 quantiles per channel** for next round's level.
- **It never sees the skin.** That makes it a floor for how much reading the situation helps.
- **A forecaster has no decide step.** Each baseline below is the forecast plus a policy we wrote. The policy is named, not hidden in "a fixed rule".

## Policies

One run per row. The split is whole numbers to 100, as on the [interface](interface.md) page.

| Baseline | Split rule | What it is a floor for |
|---|---|---|
| Argmax | 100 on the channel with the highest median | Forecast, never look. It switches only when the funded channel's forecast falls below what it remembers of another. The complacent floor |
| Probability of best | Each channel's share is the chance it has the highest level, read off the quantiles | Forecast, and look as much as its own doubt says. The look size is Timestral's, not ours |
| Constant look, 2 / 5 / 10 | That many points on every other channel, the rest on the highest median | Forecast plus a dumb look of a size we chose |
| Probability of best, split as covariate | As probability of best, with the shares passed in as a past covariate | Whether it can learn that a small share is a rough reading |

## Checks before we trust them

- **Gap test.** Ten readings, then thirty blanks. The quantiles should widen as the gap grows. If they do not, probability of best cannot look and is dropped.
- **Rounding.** A tiny probability rounds to 0, which is a blank, so a channel can still fall out of view. Watch how often it happens.
