# Providers for Jev and Timestral

Jev and Timestral are the two models that cannot call `submit` themselves. This page says how the harness plays them. Why they are in the study is on the [interface](../design/interface.md#models-that-cannot-place-bets) page. What every provider shares, the baselines included, is on the [inspect](inspect.md#providers) page.

- **Each gets a provider** that turns what the model does produce into a `submit` call. The solver, engine and score are the same as for an LLM.
- **The two tables below have the same rows**, so you can read them side by side.

## Jev

[Jev](https://docs.typesafe.ai/introduction) takes a state and a question with fixed options, and returns a probability for each option rather than text.

| | Jev |
|---|---|
| Provider | `jev/jev-latest`, `kind = "jev"` in [models](models.md#columns) |
| Install | `typesafe-sdk`, in the default `uv sync`. Key `TYPESAFE_API_KEY`, see [keys](models.md#keys) |
| Input | The rendered system prompt and record as its state, the same text an LLM sees, see [prompts](prompts.md). Then one question in the skin's words, from the skin's `question` field: which channel should the budget go on this round. Ten options, one per channel, named by the skin's `channels`. The question stands in for the line that tells an LLM to call `submit` |
| Output | A probability for each of the ten channels |
| Bets | Each probability times 100, rounded to whole numbers that sum to 100. Leftover points go to the channels that lost most in rounding, which is largest remainder rounding |
| Blanks | A probability under 0.005 rounds to a bet of 0, which shows a blank in the record, so a channel can fall out of Jev's view. The pilot watches how often, see [Jev checks](../pilot/provider-checks.md#jev-checks) |
| Log | The raw probabilities, and the confidence Jev reports with them, beside the bets |
| Memory | None. Each call is self-contained, which matches the fresh call each round |
| What it tests | Jev spreads its bets as far as it doubts, with no text reasoning. So it marks what doubt alone earns, before any reading of the story |
| Checks | [Jev checks](../pilot/provider-checks.md#jev-checks) |

## Timestral

[Timestral](https://github.com/mistralai/timestral) forecasts series. It never sees the story, so it marks how much reading the skin helps, see [baselines](../design/baselines.md#timestral).

- **The model lives in the forecasters layer**, not here. That layer plays Timestral as a policy, so `play` runs it with no harness, see the [forecasters spec](../specs/forecasters/README.md). The provider only plays that policy through the solver, as it plays a baseline.

| | Timestral |
|---|---|
| Provider | One per policy, `timestral/<policy>`, `kind = "timestral"`. The [glossary](../glossary.md#the-study) maps each id to its baseline |
| Install | Optional extra, `uv sync --extra timestral`, from the Timestral git repo at one pinned commit. Keeps torch out of the default install. No key, it runs locally |
| Model | `mistralai/Timestral-209M`, the largest of the Timestral sizes. Weights are under a gigabyte, fine on a laptop |
| Device | CPU. Documented and tested upstream. Apple MPS is not, so we do not rely on it |
| Input | One series with a variate per channel: each channel's reading in each round, taken from the record. The same readings every player sees. A round with no bet is a blank and never a 0, as Timestral would read a 0 as a channel that pays nothing, see [baselines](../design/baselines.md#timestral). For Timestral odds, bet aware, each channel is a series of its own with its past bets as `past_covariates`, so it can learn that a small bet gives a rough reading. Timestral cannot tie a row of bets to one variate of a joint series, see [two shapes](../specs/forecasters/timestral.md#two-shapes) |
| Output | 21 quantiles per channel for next round: a middle guess and a spread. The levels are 0.01, 0.05, then 0.10 to 0.90 in steps of 0.05, then 0.95 and 0.99, as the model card says, so the median is the eleventh |
| Bets | A named [forecast rule](../specs/baselines/forecast.md), one row of the [Timestral table](../design/baselines.md#timestral). The rules are baselines layer functions, quantiles in and bets out, with no Timestral import. So they are tested on hand-written quantiles with no model, and the [Bayesian baseline](../design/baselines.md#the-bayesian-frontier) reuses them |
| Blanks | A round with no bet on a channel is a blank, passed as NaN, which Timestral handles. A channel never read is left out and gets no forecast. Timestral odds can round a tiny chance to 0, so a channel goes blank the same way Jev's can. The pilot watches how often |
| Log | The 21 quantiles per channel and the cache key, beside the bets |
| Memory | None beyond the record. Forecasts are cached on disk by a hash of the input arrays, so a rerun costs nothing and replays the same bets |
| What it tests | How far forecasting gets you with no story. Each policy asks a different question, see [baselines](../design/baselines.md#timestral) |
| Checks | [Timestral checks](../pilot/provider-checks.md#timestral-checks): gap test, rounding, determinism and where it lands on the grid. What was checked on the real model before the code is in [checked](../specs/forecasters/timestral.md#checked) |
