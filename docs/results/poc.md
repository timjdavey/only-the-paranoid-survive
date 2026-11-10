# Proof of concept results

The first run of the full harness on the [proof of concept model list](../harness/models.md#two-lists), two held-out skins on the public seeds, written by `uv run paranoid analyse`. Do not edit by hand.

- **One table per skin.** Skins are never pooled, and a skin is its name only. The gap between the two, paired by seed, is the skin sensitivity table below, see [scoring](../design/scoring.md#spread).
- **Timestral rows are in the first table only.** They never read the skin, so they play one, see [models](../harness/models.md#two-lists).
- **Played with the notes and compute tools**, see [interface](../design/interface.md#tools). `Tools` is how often each was used, and the bare gap per model is in the sensitivity table below, see [tables](../specs/analysis/tables.md#the-results-page).
- **Scores run from the Uniform baseline at 0 to the Discerning baseline at 1** per scenario, and the headline is the plain mean, with the weakest trait beside it, see [scoring](../design/scoring.md#how-we-score).

## First skin, public

| Model | No change | One shock | Down switch | Up switch | Shock then switch | Slow drift | Switch then shock | Up switch then down switch | Headline | Weakest trait | Tools |
|---|---|---|---|---|---|---|---|---|---|---|---|
| _Not run yet_ | | | | | | | | | | | |

## Second skin, public

| Model | No change | One shock | Down switch | Up switch | Shock then switch | Slow drift | Switch then shock | Up switch then down switch | Headline | Weakest trait | Tools |
|---|---|---|---|---|---|---|---|---|---|---|---|
| _Not run yet_ | | | | | | | | | | | |

## Skin sensitivity

The first skin's score minus the second's, paired by seed, with its interval.

| Model | Skins | No change | One shock | Down switch | Up switch | Shock then switch | Slow drift | Switch then shock | Up switch then down switch | Headline |
|---|---|---|---|---|---|---|---|---|---|---|
| _Not run yet_ | | | | | | | | | | |
