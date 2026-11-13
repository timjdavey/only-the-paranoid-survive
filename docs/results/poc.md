# Results: poc

Written by `paranoid analyse` from the logs, and never edited by hand.

- One table per setting, and a skin is its name only.
- Scores run from the Uniform baseline at 0 to the Discerning baseline at 1, and the headline is their plain mean.
- `Tools` is how often each tool was used, as a share of rounds played.

Written by paranoid analyse from 14 logs at harness version 0.1.0+71027a4, 0.1.0+ced6610 on 2026-11-13, see poc.csv.

## amber, public

Prompt hash 294df13cd447, generator version 1, release dev, harness version 0.1.0+71027a4, 0.1.0+ced6610.

| Model | No change | One shock | Down switch | Up switch | Shock then switch | Slow drift | Switch then shock | Up switch then down switch | Headline | Weakest trait | Tools |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jev/jev-latest | 0.84 [0.79, 0.87] | 0.81 [0.76, 0.86] | 0.52 [0.40, 0.64] | 0.69 [0.64, 0.75] | 0.63 [0.58, 0.68] | 0.68 [0.63, 0.73] | 0.56 [0.46, 0.65] | 0.65 [0.60, 0.70] | 0.67 [0.65, 0.70] | Doubt 0.52 [0.40, 0.64] |  |
| jev/decisionmodels/s1-pro-5 | 0.88 [0.83, 0.92] | 0.87 [0.83, 0.91] | 0.63 [0.52, 0.71] | 0.70 [0.63, 0.77] | 0.73 [0.69, 0.77] | 0.69 [0.62, 0.76] | 0.64 [0.56, 0.71] | 0.71 [0.67, 0.76] | 0.73 [0.71, 0.75] | Doubt 0.63 [0.52, 0.71] |  |
| jev/decisionmodels/s1-pro-3 | 0.88 [0.84, 0.92] | 0.84 [0.74, 0.90] | 0.77 [0.69, 0.82] | 0.75 [0.66, 0.82] | 0.80 [0.76, 0.84] | 0.76 [0.70, 0.81] | 0.75 [0.68, 0.80] | 0.76 [0.71, 0.80] | 0.79 [0.77, 0.81] | Curiosity 0.75 [0.66, 0.82] |  |
| jev/decisionmodels/s1-fast-2 | 0.52 [0.45, 0.58] | 0.53 [0.46, 0.58] | 0.48 [0.41, 0.55] | 0.56 [0.49, 0.63] | 0.50 [0.44, 0.56] | 0.47 [0.42, 0.52] | 0.47 [0.40, 0.54] | 0.44 [0.39, 0.48] | 0.50 [0.48, 0.52] | Recall 0.44 [0.39, 0.48] |  |
| jev/decisionmodels/reax-1-20261021 | 0.86 [0.85, 0.87] | 0.85 [0.83, 0.87] | 0.75 [0.72, 0.77] | 0.82 [0.78, 0.85] | 0.77 [0.75, 0.79] | 0.71 [0.68, 0.75] | 0.74 [0.71, 0.76] | 0.66 [0.61, 0.70] | 0.77 [0.76, 0.78] | Recall 0.66 [0.61, 0.70] |  |
| timestral/top-pick | 0.97 [0.97, 0.98] | 0.97 [0.96, 0.97] | 0.63 [0.52, 0.76] | 0.69 [0.62, 0.77] | 0.75 [0.66, 0.84] | 0.92 [0.91, 0.94] | 0.66 [0.54, 0.78] | 0.83 [0.81, 0.85] | 0.80 [0.78, 0.83] | Doubt 0.63 [0.52, 0.76] |  |
| timestral/odds | 0.93 [0.92, 0.93] | 0.88 [0.87, 0.90] | 0.66 [0.54, 0.79] | 0.71 [0.63, 0.79] | 0.79 [0.72, 0.84] | 0.87 [0.86, 0.89] | 0.67 [0.55, 0.79] | 0.81 [0.78, 0.84] | 0.79 [0.76, 0.82] | Doubt 0.66 [0.54, 0.79] |  |
| timestral/explore-1 | 0.87 [0.86, 0.87] | 0.87 [0.86, 0.87] | 0.83 [0.81, 0.84] | 0.86 [0.85, 0.87] | 0.83 [0.82, 0.84] | 0.83 [0.82, 0.85] | 0.83 [0.81, 0.84] | 0.83 [0.82, 0.84] | 0.84 [0.84, 0.85] | Conviction 0.83 [0.81, 0.84] |  |
| timestral/explore-2 | 0.78 [0.77, 0.78] | 0.78 [0.77, 0.78] | 0.76 [0.75, 0.76] | 0.77 [0.76, 0.78] | 0.75 [0.74, 0.76] | 0.76 [0.75, 0.77] | 0.76 [0.75, 0.77] | 0.75 [0.74, 0.76] | 0.76 [0.76, 0.76] | Recall 0.75 [0.74, 0.76] |  |
| timestral/explore-5 | 0.49 [0.49, 0.49] | 0.49 [0.48, 0.49] | 0.48 [0.47, 0.48] | 0.49 [0.48, 0.49] | 0.47 [0.47, 0.48] | 0.48 [0.47, 0.49] | 0.48 [0.47, 0.48] | 0.47 [0.47, 0.48] | 0.48 [0.48, 0.48] | Recall 0.47 [0.47, 0.48] |  |
| timestral/odds-alone | 0.93 [0.92, 0.94] | 0.89 [0.87, 0.90] | 0.67 [0.55, 0.80] | 0.69 [0.61, 0.77] | 0.77 [0.71, 0.84] | 0.88 [0.86, 0.90] | 0.66 [0.54, 0.78] | 0.81 [0.78, 0.83] | 0.79 [0.76, 0.81] | Conviction 0.66 [0.54, 0.78] |  |
| timestral/odds-bet-aware | 0.93 [0.92, 0.94] | 0.89 [0.87, 0.90] | 0.67 [0.55, 0.79] | 0.68 [0.61, 0.77] | 0.77 [0.71, 0.83] | 0.88 [0.86, 0.90] | 0.66 [0.53, 0.78] | 0.81 [0.78, 0.83] | 0.78 [0.76, 0.81] | Conviction 0.66 [0.53, 0.78] |  |
| anthropic/claude-haiku-5-5 (off) | 0.75 [0.61, 0.89] †‡ | 0.76 [0.62, 0.86] †‡ | 0.31 [0.19, 0.43] †‡ | 0.54 [0.46, 0.64] ‡ | 0.45 [0.34, 0.56] †‡ | 0.45 [0.35, 0.55] †‡ | 0.32 [0.21, 0.43] †‡ | 0.64 [0.57, 0.72] ‡ | 0.53 [0.49, 0.57] †‡ | Doubt 0.31 [0.19, 0.43] | notes 0.06, compute 0.26 |

† 15 runs gave up and scored as the Uniform baseline. ‡ Retry share over 0.1.

### Marks

| Scenario | Complacent | Hedge rule | Scout rule | Perfect |
|---|---|---|---|---|
| No change | 1.00 | 0.98 | 0.90 | 1.00 |
| One shock | 1.00 | 0.96 | 0.90 | 1.00 |
| Down switch | 0.39 | 0.92 | 0.84 | 1.01 |
| Up switch | 0.71 | 0.70 | 0.87 | 1.01 |
| Shock then switch | 0.62 | 0.88 | 0.85 | 1.01 |
| Slow drift | 0.70 | 0.91 | 0.85 | 1.03 |
| Switch then shock | 0.39 | 0.92 | 0.84 | 1.02 |
| Up switch then down switch | 0.86 | 0.79 | 0.75 | 1.00 |

### Spread

| Model | Scenario | SD | 10th percentile | Seeds |
|---|---|---|---|---|
| jev/jev-latest | No change | 0.08 | 0.76 | 16 |
| jev/jev-latest | One shock | 0.11 | 0.75 | 16 |
| jev/jev-latest | Down switch | 0.23 | 0.24 | 16 |
| jev/jev-latest | Up switch | 0.13 | 0.54 | 16 |
| jev/jev-latest | Shock then switch | 0.10 | 0.51 | 16 |
| jev/jev-latest | Slow drift | 0.10 | 0.54 | 16 |
| jev/jev-latest | Switch then shock | 0.20 | 0.27 | 16 |
| jev/jev-latest | Up switch then down switch | 0.10 | 0.53 | 16 |
| jev/decisionmodels/s1-pro-5 | No change | 0.09 | 0.74 | 16 |
| jev/decisionmodels/s1-pro-5 | One shock | 0.09 | 0.73 | 16 |
| jev/decisionmodels/s1-pro-5 | Down switch | 0.18 | 0.41 | 16 |
| jev/decisionmodels/s1-pro-5 | Up switch | 0.16 | 0.56 | 16 |
| jev/decisionmodels/s1-pro-5 | Shock then switch | 0.09 | 0.59 | 16 |
| jev/decisionmodels/s1-pro-5 | Slow drift | 0.14 | 0.52 | 16 |
| jev/decisionmodels/s1-pro-5 | Switch then shock | 0.16 | 0.46 | 16 |
| jev/decisionmodels/s1-pro-5 | Up switch then down switch | 0.10 | 0.59 | 16 |
| jev/decisionmodels/s1-pro-3 | No change | 0.08 | 0.76 | 16 |
| jev/decisionmodels/s1-pro-3 | One shock | 0.16 | 0.72 | 16 |
| jev/decisionmodels/s1-pro-3 | Down switch | 0.16 | 0.65 | 16 |
| jev/decisionmodels/s1-pro-3 | Up switch | 0.16 | 0.58 | 16 |
| jev/decisionmodels/s1-pro-3 | Shock then switch | 0.09 | 0.70 | 16 |
| jev/decisionmodels/s1-pro-3 | Slow drift | 0.12 | 0.65 | 16 |
| jev/decisionmodels/s1-pro-3 | Switch then shock | 0.16 | 0.54 | 16 |
| jev/decisionmodels/s1-pro-3 | Up switch then down switch | 0.09 | 0.74 | 16 |
| jev/decisionmodels/s1-fast-2 | No change | 0.14 | 0.43 | 16 |
| jev/decisionmodels/s1-fast-2 | One shock | 0.13 | 0.44 | 16 |
| jev/decisionmodels/s1-fast-2 | Down switch | 0.14 | 0.28 | 16 |
| jev/decisionmodels/s1-fast-2 | Up switch | 0.14 | 0.36 | 16 |
| jev/decisionmodels/s1-fast-2 | Shock then switch | 0.13 | 0.38 | 16 |
| jev/decisionmodels/s1-fast-2 | Slow drift | 0.12 | 0.35 | 16 |
| jev/decisionmodels/s1-fast-2 | Switch then shock | 0.13 | 0.30 | 16 |
| jev/decisionmodels/s1-fast-2 | Up switch then down switch | 0.09 | 0.36 | 16 |
| jev/decisionmodels/reax-1-20261021 | No change | 0.03 | 0.83 | 16 |
| jev/decisionmodels/reax-1-20261021 | One shock | 0.04 | 0.82 | 16 |
| jev/decisionmodels/reax-1-20261021 | Down switch | 0.07 | 0.63 | 16 |
| jev/decisionmodels/reax-1-20261021 | Up switch | 0.07 | 0.75 | 16 |
| jev/decisionmodels/reax-1-20261021 | Shock then switch | 0.05 | 0.72 | 16 |
| jev/decisionmodels/reax-1-20261021 | Slow drift | 0.09 | 0.61 | 16 |
| jev/decisionmodels/reax-1-20261021 | Switch then shock | 0.06 | 0.66 | 16 |
| jev/decisionmodels/reax-1-20261021 | Up switch then down switch | 0.10 | 0.50 | 16 |
| timestral/top-pick | No change | 0.00 | 0.97 | 16 |
| timestral/top-pick | One shock | 0.01 | 0.95 | 16 |
| timestral/top-pick | Down switch | 0.27 | 0.39 | 16 |
| timestral/top-pick | Up switch | 0.18 | 0.57 | 16 |
| timestral/top-pick | Shock then switch | 0.17 | 0.55 | 16 |
| timestral/top-pick | Slow drift | 0.04 | 0.88 | 16 |
| timestral/top-pick | Switch then shock | 0.25 | 0.39 | 16 |
| timestral/top-pick | Up switch then down switch | 0.04 | 0.78 | 16 |
| timestral/odds | No change | 0.01 | 0.91 | 16 |
| timestral/odds | One shock | 0.03 | 0.84 | 16 |
| timestral/odds | Down switch | 0.24 | 0.36 | 16 |
| timestral/odds | Up switch | 0.19 | 0.53 | 16 |
| timestral/odds | Shock then switch | 0.11 | 0.59 | 16 |
| timestral/odds | Slow drift | 0.03 | 0.83 | 16 |
| timestral/odds | Switch then shock | 0.22 | 0.35 | 16 |
| timestral/odds | Up switch then down switch | 0.06 | 0.74 | 16 |
| timestral/explore-1 | No change | 0.01 | 0.85 | 16 |
| timestral/explore-1 | One shock | 0.01 | 0.85 | 16 |
| timestral/explore-1 | Down switch | 0.04 | 0.78 | 16 |
| timestral/explore-1 | Up switch | 0.02 | 0.84 | 16 |
| timestral/explore-1 | Shock then switch | 0.02 | 0.81 | 16 |
| timestral/explore-1 | Slow drift | 0.03 | 0.81 | 16 |
| timestral/explore-1 | Switch then shock | 0.03 | 0.78 | 16 |
| timestral/explore-1 | Up switch then down switch | 0.03 | 0.80 | 16 |
| timestral/explore-2 | No change | 0.01 | 0.77 | 16 |
| timestral/explore-2 | One shock | 0.01 | 0.77 | 16 |
| timestral/explore-2 | Down switch | 0.02 | 0.73 | 16 |
| timestral/explore-2 | Up switch | 0.02 | 0.76 | 16 |
| timestral/explore-2 | Shock then switch | 0.02 | 0.72 | 16 |
| timestral/explore-2 | Slow drift | 0.02 | 0.74 | 16 |
| timestral/explore-2 | Switch then shock | 0.02 | 0.73 | 16 |
| timestral/explore-2 | Up switch then down switch | 0.02 | 0.72 | 16 |
| timestral/explore-5 | No change | 0.00 | 0.48 | 16 |
| timestral/explore-5 | One shock | 0.00 | 0.48 | 16 |
| timestral/explore-5 | Down switch | 0.01 | 0.47 | 16 |
| timestral/explore-5 | Up switch | 0.01 | 0.48 | 16 |
| timestral/explore-5 | Shock then switch | 0.01 | 0.46 | 16 |
| timestral/explore-5 | Slow drift | 0.01 | 0.47 | 16 |
| timestral/explore-5 | Switch then shock | 0.01 | 0.47 | 16 |
| timestral/explore-5 | Up switch then down switch | 0.01 | 0.46 | 16 |
| timestral/odds-alone | No change | 0.02 | 0.92 | 16 |
| timestral/odds-alone | One shock | 0.03 | 0.85 | 16 |
| timestral/odds-alone | Down switch | 0.24 | 0.37 | 16 |
| timestral/odds-alone | Up switch | 0.18 | 0.53 | 16 |
| timestral/odds-alone | Shock then switch | 0.12 | 0.57 | 16 |
| timestral/odds-alone | Slow drift | 0.04 | 0.82 | 16 |
| timestral/odds-alone | Switch then shock | 0.24 | 0.36 | 16 |
| timestral/odds-alone | Up switch then down switch | 0.06 | 0.74 | 16 |
| timestral/odds-bet-aware | No change | 0.02 | 0.91 | 16 |
| timestral/odds-bet-aware | One shock | 0.04 | 0.84 | 16 |
| timestral/odds-bet-aware | Down switch | 0.25 | 0.36 | 16 |
| timestral/odds-bet-aware | Up switch | 0.18 | 0.54 | 16 |
| timestral/odds-bet-aware | Shock then switch | 0.12 | 0.57 | 16 |
| timestral/odds-bet-aware | Slow drift | 0.04 | 0.83 | 16 |
| timestral/odds-bet-aware | Switch then shock | 0.24 | 0.36 | 16 |
| timestral/odds-bet-aware | Up switch then down switch | 0.05 | 0.74 | 16 |
| anthropic/claude-haiku-5-5 (off) | No change | 0.32 | 0.27 | 16 |
| anthropic/claude-haiku-5-5 (off) | One shock | 0.25 | 0.54 | 16 |
| anthropic/claude-haiku-5-5 (off) | Down switch | 0.27 | 0.00 | 16 |
| anthropic/claude-haiku-5-5 (off) | Up switch | 0.21 | 0.37 | 16 |
| anthropic/claude-haiku-5-5 (off) | Shock then switch | 0.23 | 0.16 | 16 |
| anthropic/claude-haiku-5-5 (off) | Slow drift | 0.24 | 0.00 | 16 |
| anthropic/claude-haiku-5-5 (off) | Switch then shock | 0.25 | 0.00 | 16 |
| anthropic/claude-haiku-5-5 (off) | Up switch then down switch | 0.15 | 0.43 | 16 |

## amber, public, tool_choice auto

Prompt hash 294df13cd447, generator version 1, release dev, harness version 0.1.0+71027a4.

| Model | No change | One shock | Down switch | Up switch | Shock then switch | Slow drift | Switch then shock | Up switch then down switch | Headline | Weakest trait | Tools |
|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-sonnet-5-5 (low) | 0.90 [0.88, 0.92] § | 0.86 [0.83, 0.89] § | 0.59 [0.50, 0.71] § | 0.63 [0.57, 0.72] § | 0.77 [0.71, 0.81] § | 0.83 [0.80, 0.85] § | 0.65 [0.59, 0.72] § | 0.78 [0.75, 0.81] § | 0.75 [0.73, 0.77] § | Doubt 0.59 [0.50, 0.71] | notes 0.10, compute 0.00 |

§ Recognised the prompt on over a quarter of probes.

### Marks

| Scenario | Complacent | Hedge rule | Scout rule | Perfect |
|---|---|---|---|---|
| No change | 1.00 | 0.98 | 0.90 | 1.00 |
| One shock | 1.00 | 0.96 | 0.90 | 1.00 |
| Down switch | 0.39 | 0.92 | 0.84 | 1.01 |
| Up switch | 0.71 | 0.70 | 0.87 | 1.01 |
| Shock then switch | 0.62 | 0.88 | 0.85 | 1.01 |
| Slow drift | 0.70 | 0.91 | 0.85 | 1.03 |
| Switch then shock | 0.39 | 0.92 | 0.84 | 1.02 |
| Up switch then down switch | 0.86 | 0.79 | 0.75 | 1.00 |

### Spread

| Model | Scenario | SD | 10th percentile | Seeds |
|---|---|---|---|---|
| anthropic/claude-sonnet-5-5 (low) | No change | 0.04 | 0.87 | 16 |
| anthropic/claude-sonnet-5-5 (low) | One shock | 0.06 | 0.81 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Down switch | 0.23 | 0.35 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Up switch | 0.17 | 0.50 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Shock then switch | 0.10 | 0.65 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Slow drift | 0.05 | 0.77 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Switch then shock | 0.13 | 0.52 | 16 |
| anthropic/claude-sonnet-5-5 (low) | Up switch then down switch | 0.06 | 0.70 | 16 |
