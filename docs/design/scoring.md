# Scoring

## How we score

- **Each round the agent splits a fixed budget across channels**, see [interface](interface.md). Its split is its belief: a small share on a channel is a look, a large one is a switch.
- **Each scenario scores output as a fraction of what the [oracle](baselines.md), which knows each round's mean levels, would earn.** This sits between 0 and 1, strips out luck, and reads directly as the scenario's failure mode: the gap in calm is jumpiness, in shock overreaction, in switch underreaction.
- **The headline is the geometric mean across [scenarios](scenarios.md).** A model must do well on every shape to score highly. One bad scenario drags the whole figure down.

## Extension: inertia

A fixed budget is forgiving. A model that never moves still earns most of the output, so being late costs less than it cost Kodak. To amplify the lateness signal:

- **Cap how far shares can move each round**, say 10 points. Moving takes time, so the agent has to decide early.
- **Switched off by default.** It is a generator option, added once the pilot shows the base score is too flat to separate models.
- **Cost.** The cap is a rule the agent must be told, and it mixes planning into every trait.
