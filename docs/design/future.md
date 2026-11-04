# Future work (studies not benchmarks)

### How the world changes

- **Ramp length.** Vary the speed at which the change is introduced rather than its amplitude.
- **The later kinds of change, if the full study doesn't reach them.** Coupling, where two units start to compete or feed each other. Gain, where returns flatten at the same level. Observation, where yield is credited to the wrong unit. Each is an edit to one block of the generator, and on each a per-unit tracker fails. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event).
- **Shapes of change.** The ramp is incremental drift, in the terms of Gama et al.'s survey of concept drift (ACM Computing Surveys 46(4): 44, 2014, [doi:10.1145/2523813](https://doi.org/10.1145/2523813)). Sudden, gradual and recurring are the others, and a change that reverses is what Shopify and Hopin bet on.
- **More units and more tags.** Ten units with one tag, side, is the smallest world with a rule to rethink. A third tag, and several units shifting a little from the start, would be closer to a real account.
- **Reflexive changes.** Real plans often fail this way, like a trading edge that fades once everyone copies it. It is an edit to the coupling block, but a timid agent would score well and the reference bot would have to plan ahead. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive).
- **Showing the inputs.** A plant skin can show ambient temperature on the panel, which explains a correlated dip. Whether seeing the shared factor helps or hurts is a factor the proof of concept holds constant by hiding it.
- **The time unit.** "Weeks" says slow and "minutes" says fast, so the word sets a model's prior on how often the world moves. Every skin says a week for now.

### What the agent knows before it starts

- **Vary the length of the record.** A longer stretch of success should make anyone a little slower to doubt, even the reference bot. The question is how this varies among models.
- **An inherited plan.** The old default, now an extension: hand the agent a plan written by someone else beside the record, with its voice a factor, from flat to "this split has served the client for four years". The gap from the briefing cell is what a read past and a confident author cost. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes).
- **Full live run with no record.** The agent plays from the first round, works out its own split, and then faces the change. This tells us whether a past the agent lived is harder to let go of than one it read. Earlier research suggests it is.
- **The history style, beyond the pilot.** The pilot sizes steady against jittery once. A sweep would ask whether a model copies the record's rate of experimenting however jittery it gets.
- **Ergodic tries.** Have the agent play several short runs in a row instead of one, with the rules changing in a few outlier runs. How the agent's own experience shapes what it expects.

### How the agent can act

- **Lagged units.** A unit whose spend builds a stock that pays out weeks later, such as brand or SEO. Every unit in the game yields in the week it is bought, because a lagged unit's name would import a belief the generator doesn't hold. In the generator it is a coupling edit, and the question is whether an agent allows for lag when judging its notes. See [Why names must match the generator](decisions.md#why-names-must-match-the-generator).
- **Make switching expensive in its own right.** A switch would carry a one-off fee and lock the agent into the new split for some rounds. An experiment is cheap, so the agent should run one as soon as it has doubts, whatever switching costs. But the dearer a wrong switch, the more evidence it should wait for before switching. The question is whether the agent's switching follows the price while its experimenting doesn't.
- **Add a trial tool.** A `trial(unit)` call would reveal one reading for a fee, without spending budget. A share on an unfavoured unit looks the same in the log whether it is a test or the spread saturation calls for, so curiosity is reported as a diagnostic rather than scored as a trait. A trial tool would split the two, at the risk of hinting that something is worth testing. See [Why curiosity is a diagnostic, not a trait](decisions.md#why-curiosity-is-a-diagnostic-not-a-trait).
- **A compounding budget.** The budget grows with output, so late mistakes cost more and early ones compound. It is a generator option, switched off, because it adds a sizing skill the first study doesn't want. See [Fixed or compounding budget](alternatives.md#fixed-or-compounding-budget).
- **Ask the doubt question.** Each round, before it splits the budget, ask the agent how likely it thinks its notes are to be out of date, and redact that Q&A from the context. This tells us whether an agent can suspect its notes are stale and still not test them, the way Kodak built the first digital camera and then sat on it. It is the other route to splitting curiosity from sizing.

### Whether it holds outside our game

- **One real agentic task with a stale handoff note.** For example, a coding task whose notes say the payments client is on v1 and the mocks match, when the repo has moved on and the old path still passes but does worse. Two or three models, a few runs each, transcripts read by hand, and the ranking compared with the game's. It is a check that the game stands in for real work, not part of the suite. It is the full study's realism check, and it is listed here because its shape is still open.
- **Vary narrative stakes.** Dress the same game in stories with low stakes and with high stakes, keeping every number the same.
- **Different game dynamics**, such as pricing by segment or a supplier split from [alternatives.md](alternatives.md). Tests whether the skill carries over, or a model is just good at this one game.
- **Human baseline.** A threshold could then read as "catches what a typical person catches", rather than only comparing models with each other.
