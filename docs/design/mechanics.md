# Mechanics

## How the agent plays

- **Each round the agent splits a fixed budget across channels.** It returns shares that sum to 100, say A 70, B 20, C 10.
- **It returns a full split every round.** A split that does not sum to 100 gets a neutral error and a retry, so a bad call is never read as a decision. Rounds where the split matches the one before are counted afterwards as rounds it left the plan alone.
- **The split is its belief.** A small share on a new channel is a look. A large share is a switch. No cut-off decides which is which.
- **The budget is the same every round.** Output does not carry over, so an early lucky round cannot snowball. See [scoring](scoring.md).
- **The record shows each channel's level every round**, not just total output. The agent reads it, and a forecaster can forecast it.
- **Nothing tells the agent the world might change.** The prompt asks for a split, not for a view on change.

## Models that cannot write a split

Jev and Timestral are stateless and do not write text, so each gets a thin adapter that turns what it does produce into a split. The engine and the score are the same for all three.

| Model | How it plays |
|---|---|
| Classic LLM | Reads the record, returns a split |
| [Jev](https://docs.typesafe.ai/introduction) | Gets the record as state and one choice question, "which channel should the budget go on". Its probability map over channels is read as the split, normalised in our code |
| [Timestral](https://github.com/mistralai/timestral) | Gets each channel's level history as a series and forecasts next round's levels. A fixed rule in our code turns the forecast into a split |

- **The forecast to split rule is the one the oracle uses** when given the true levels. Timestral is then scored purely on how well it predicts. Any other rule would bake our own doubt into its split.
- **We score the output of the split, never the forecast.**
- **Timestral never sees the narrative skin.** That makes it a floor for how much reading the situation helps.

## Rejected

| Option | Why not |
|---|---|
| Pick one channel a round | One reading a round is too little evidence. Even an oracle mostly misses the switch by round 40. A look costs a whole round's output, and doubt only shows across several rounds |
| Pick one channel and a stake | The old coin flip game. Sizing a stake is a maths skill of its own that blurs with belief, and asking "how much do you move" every round hints that change is the question |
| Compounding bankroll | The right stake is a Kelly fraction, so the game tests bet sizing as much as spotting a change. Early luck multiplies through the run, so variance swamps model differences. Ruin scores zero and collapses the geometric mean |
| Cash as a safe channel | Models park in cash whenever unsure, so calm needs an extra cost to stay readable |
| Stop or continue, one irreversible switch | Clean detection delay, but binary, so no graded doubt |
| Ask for a probability the regime changed | The most direct measure, but it tells the agent change is the question |
| Forecast the levels, engine acts on them | Asking an LLM for a forecast nudges it that levels move. Kept only as the adapter for forecasters like Timestral, where there is no prompt to nudge |
| Rank the channels | Cheap for the model but coarse. A rank swap is as binary as a pick |
| Pivot with a conversion cost | The mechanic prices lateness and overreaction itself, but the fee leaks into every trait, and it is lumpy, so a timid agent and a confident one read the same until one moves |
| Controller with feedback | Prices both failures naturally, but the score becomes a cost rather than a fraction of the oracle, and the model has to reason about a system with memory. Kept as a second game to check the skill carries over |
