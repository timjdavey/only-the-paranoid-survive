# Interface

## How the agent plays

- **Each round the agent splits a fixed budget across ten channels.** It returns whole number shares that sum to 100, say 55 on one channel, 15 and 10 on two more, 5 on four others and 0 on the rest. Whole numbers to 100 is how budgets are talked about in every skin, the sum check is exact, and models fumble decimals more than they fumble percentages.
- **It returns a full split every round.** A split that does not sum to 100 gets a neutral error and a retry, so a bad call is never read as a decision. Rounds where the split matches the one before are counted afterwards as rounds it left the plan alone.
- **The split is its belief.** A small share on a new channel is a look. A large share is a switch. No cut-off decides which is which.
- **The budget is the same every round.** Output does not carry over, so an early lucky round cannot snowball. See [scoring](scoring.md).
- **The agent sees every channel's level every round**, not just total output, in the record described under [tools](#tools).
- **Nothing tells the agent the world might change.** The prompt asks for a split, not for a view on change.

## Channels

- **There are ten.** The shape on the [scenarios](scenarios.md) page describes the channel with the highest level at round 1. In switch and drift another channel climbs as that one falls. The other eight are ordinary noise, and in calm one of them dips and recovers, so there is always something to over react to.
- **Where to go is a real question.** With three channels a switch is a coin flip between the other two. With ten the agent has to pick, which is Grove's problem: not just out of memory, but into processors.
- **The calm floor separates models.** More series means more runs of noise that look like a change, so jumpiness has something to show up on.
- **Drift hides.** One line sagging among nine wobbling ones is a boiling frog. One line sagging among two flat ones is a chart.
- **It reads as real.** Ten channels is a portfolio, a product line, a fund. Three is a toy.
- **Not more than ten.** Past that the work is scanning rows, which is a search skill, not judgement.

## Tools

- **Each round is a fresh call.** The agent gets the rules, the skin and the record, then calls one tool. Nothing carries over between rounds and nothing is compacted, so a run is the same whichever round you replay it from.
- **The record is in the prompt, not behind a tool.** It is a CSV of the agent's own play so far: the round, its split, each channel's level and the output. Round 1 has an empty record.
- **This is the same shape Jev and Timestral get.** History in, split out. See [below](#models-that-cannot-write-a-split).
- **Tool descriptions never say check, change or anomaly.** A lint on the prompt and tool text keeps them out.

| Tool | Takes | Returns |
|---|---|---|
| `submit(split)` | Ten whole numbers that sum to 100 | Each channel's level this round and the output. A neutral error and a retry if the sum is off |

## Pilot: notepad and compute

A deployed agent would have a scratchpad and a calculator at the very least, so a bare harness may not be a fair test. The pilot checks.

| Tool | What it does |
|---|---|
| `notes(text)` | Replaces a file the agent keeps between rounds. It comes back next round as a tool message, never as the agent's own words. Length is capped and logged |
| `compute(code)` | Runs Python in a sandbox that sees the record as a file and nothing else. No network, no engine, no seeds |

- **Bare against both.** One model, a handful of seeds, with and without the pair.
- **If the score moves, the headline runs with the tools.** Jev and Timestral then become floors rather than peers.
- **If it does not, the headline runs bare.** Cheaper, and every model gets the same input.
- **Split the two only if the pair moves the score.** Four cells for an answer we may not need is a waste.

## Models that cannot write a split

Jev and Timestral are stateless and do not write text, so each gets a thin adapter that turns what it does produce into a split. The engine and the score are the same for all three.

| Model | How it plays |
|---|---|
| Classic LLM | Reads the record, returns a split |
| [Jev](https://docs.typesafe.ai/introduction) | Gets the record as state and one choice question, "which channel should the budget go on". Its probability map over the ten channels is read as the split, normalised in our code |
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
| Three channels | Where to go is a coin flip, there is no room for a decoy, and calm saturates so it stops separating models |
| A `read_record` tool | Lets a model never look, and then lazy and confident read the same. A default row count is a hidden choice about how far back it can see, which is the thing drift tests |
| A rolling conversation | The agent's own reasoning piles up, and that is the one place a model will not question a claim ([Self-Correction Illusion](../prior/past-in-the-prompt.md#the-self-correction-illusion-2026-the-same-claim-under-a-different-role)). Cost grows with the square of the game length |
| Notes in the headline | Notes an agent wrote itself scored below the full history ([Liu](../prior/past-in-the-prompt.md#liu-et-al-2026-history-that-never-becomes-experience)), rewrites wipe detail ([ACE](../prior/past-in-the-prompt.md#ace-2025-notes-that-collapse-when-rewritten)) and progress summaries did not free the agent ([Fork-and-Flush](../prior/past-in-the-prompt.md#fork-and-flush-2026-a-fresh-session-on-old-work)). Parked in the pilot |
| A `read_notes` tool | The notes are in the prompt |
| Pasting data into `compute` | Retyping hundreds of rows measures tedium, not judgement. The sandbox gets the record as a file instead |
