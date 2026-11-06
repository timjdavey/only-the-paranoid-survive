# Interface

## How the agent plays

- **Each round the agent bets a fixed budget across ten channels.** It places ten whole number bets that sum to 100, say 55 on one channel, 15 and 10 on two more, 5 on four others and 0 on the rest. Whole numbers to 100 is how budgets are talked about in every skin, the sum check is exact, and models fumble decimals more than they fumble percentages.
- **It places all ten bets every round.** Bets that do not sum to 100 get a neutral error and a retry, so a bad call is never read as a decision. Rounds where the bets match the round before are counted afterwards as rounds it left the plan alone.
- **Its bets are its belief.** A small bet on a new channel is a look. A large bet is a switch. No cut-off decides which is which.
- **The budget is the same every round.** Output does not carry over, so an early lucky round cannot snowball. See [scoring](scoring.md).
- **The agent sees the level of every channel it bet on**, not just total output, in the record described under [tools](#tools). A bet of 0 shows nothing. See [mechanics](mechanics.md).
- **Nothing tells the agent the world might change.** The prompt asks for bets, not for a view on change.

## Tools

- **Each round is a fresh call.** The agent gets the rules, the skin and the record, then calls one tool. Nothing carries over between rounds and nothing is compacted, so a run is the same whichever round you replay it from.
- **The record is in the prompt, not behind a tool.** It is a CSV of the agent's own play so far: the round, its bets, the level of each channel it bet on and the output. Round 1 has an empty record.
- **This is the same shape Jev and Timestral get.** History in, bets out. See [below](#models-that-cannot-place-bets).
- **Tool descriptions never say check, change or anomaly.** A lint on the prompt and tool text keeps them out.
- **No scratchpad or calculator in the headline.** Whether they change play is a [pilot check](pilot.md#notepad-and-compute).

| Tool | Takes | Returns |
|---|---|---|
| `submit(bets)` | Ten whole numbers that sum to 100 | The level of each channel it bet on this round and the output. A neutral error and a retry if the sum is off |

## Models that cannot place bets

Jev and Timestral are stateless and do not write text, so each gets a thin adapter that turns what it does produce into bets. The engine and the score are the same for all three.

| Model | How it plays |
|---|---|
| Classic LLM | Reads the record, returns its bets |
| [Jev](https://docs.typesafe.ai/introduction) | Gets the record as state and one choice question, "which channel should the budget go on". Its probability map over the ten channels is read as its bets, normalised in our code |
| [Timestral](https://github.com/mistralai/timestral) | Gets each channel's level history as a series and forecasts next round's levels. A named policy turns the forecast into bets, one run per policy. See [baselines](baselines.md) |

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
| Three channels | Where to go is a coin flip, there is no room for a decoy, and calm saturates so it stops separating models |
| A `read_record` tool | Lets a model never look, and then lazy and confident read the same. A default row count is a hidden choice about how far back it can see, which is the thing drift tests |
| A rolling conversation | The agent's own reasoning piles up, and that is the one place a model will not question a claim ([Self-Correction Illusion](../prior/past-in-the-prompt.md#the-self-correction-illusion-2026-the-same-claim-under-a-different-role)). Cost grows with the square of the game length |
