# Two readers

Written by `shapes/src/make.py --readers`. Do not edit by hand. What it is for is in [the README](README.md#two-readers).

- **Seeds.** The first 100 public seeds. A run scores 0 at the Uniform baseline and 1 at the Discerning.
- **A shock's cost** is a reader's score on No change less its score on One shock.

| Reader | World | No change | One shock | Down switch | A shock's cost |
|---|---|---|---|---|---|
| hedge rule | today | 0.96 | 0.95 | 0.91 | 0.01 |
| hedge rule | new | 0.96 | 0.89 | 0.75 | 0.07 |
| Bayesian 0.005 | today | 0.98 | 0.97 | 0.94 | 0.01 |
| Bayesian 0.005 | new | 0.98 | 0.95 | 0.94 | 0.02 |
| Bayesian 0.01 | today | 0.97 | 0.96 | 0.94 | 0.01 |
| Bayesian 0.01 | new | 0.97 | 0.94 | 0.93 | 0.02 |
| Bayesian 0.025 | today | 0.95 | 0.94 | 0.91 | 0.01 |
| Bayesian 0.025 | new | 0.94 | 0.91 | 0.89 | 0.03 |
| Bayesian 0.05 | today | 0.92 | 0.91 | 0.88 | 0.02 |
| Bayesian 0.05 | new | 0.91 | 0.88 | 0.85 | 0.04 |
| Bayesian 0.1 | today | 0.88 | 0.85 | 0.82 | 0.02 |
| Bayesian 0.1 | new | 0.86 | 0.82 | 0.79 | 0.04 |

| World | Best hazard on One shock | Best hazard on Down switch | They differ |
|---|---|---|---|
| today | 0.005 | 0.005 | no |
| new | 0.005 | 0.005 | no |
