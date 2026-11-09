# Adapters

Jev and Timestral do not write text, so each gets a provider that turns what it does produce into a `submit` call. The solver, engine and score are the same as for an LLM, see [interface](../design/interface.md#models-that-cannot-place-bets).

## Jev

[Jev](https://docs.typesafe.ai/introduction) takes a state and typed questions and returns probabilities, not text.

- **Provider** `jev/jev-latest`. SDK `typesafe-sdk`, key `TYPESAFE_API_KEY`. Each call is self-contained, which matches the fresh call each round.
- **State** is the rendered system prompt and record, the same text an LLM sees.
- **One choice question**, in the skin's words: which channel should the budget go on this round. Ten criteria, one per channel, named and described by the skin.
- **Bets** are the probability map times 100, rounded by largest remainder so they sum to 100. The raw probabilities and Jev's confidence go in the log.
- **What it tests.** Jev's own doubt sets the look size, so it is a floor for a split as belief with no reasoning at all.

## Timestral

[Timestral](https://github.com/mistralai/timestral) forecasts series. The provider feeds it the record and a named policy turns the forecast into bets, see [baselines](../design/baselines.md#timestral).

| Setting | Choice | Why |
|---|---|---|
| Model | `mistralai/Timestral-209M` | The largest. Weights are under a gigabyte, fine on a laptop |
| Device | CPU | Documented and tested upstream. Apple MPS is not, so we do not rely on it |
| Install | Optional extra, `uv sync --extra timestral`, from git | Keeps torch out of the default install |
| Input | One series, ten variates, levels only. A round with no bet is NaN | Levels never output, see baselines |
| Output | 21 quantiles per channel for next round | Policies read the middle guess and the spread |
| Covariates | Past bets as `past_covariates` for Timestral odds, bet aware | Supported by the API |
| Cache | Forecasts cached on disk by a hash of the input arrays | Deterministic, so reruns cost nothing |

- **Provider names** are `timestral/top-pick`, `timestral/odds`, `timestral/look-1`, `timestral/look-2`, `timestral/look-5` and `timestral/odds-bet-aware`. One run per policy.
- **The policies are engine functions.** Quantiles in, bets out, with no Timestral import, so they are tested on made up quantiles and reused by the Bayesian baseline later.
- **Checks** before trusting it are in the [pilot](../pilot/provider-checks.md#timestral-checks).
