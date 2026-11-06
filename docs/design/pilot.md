# Pilot

A short run before the full study to settle the knobs. Each check names what we measure and what we decide from it.

## Seeds

- **Question.** How many seeds a scenario needs, and whether a model's own sampling adds enough spread to need repeats on the same seed.
- **Run.** One model, one scenario, say shock. Twenty seeds played once, and one seed played ten times.
- **Measure.** The spread of the run score across seeds, against the spread across repeats of one seed.
- **Decide.** The number of seeds per scenario: enough that the standard error is small next to the gaps between [baselines](baselines.md). If the same-seed spread is near the seed spread, the model's dice matter and we note it, but the headline still plays each seed once. See [scoring](scoring.md#seeds).

## Other checks

| Check | Question | Where it lives |
|---|---|---|
| Notepad and compute | Does a scratchpad or a calculator change how a model plays | [interface](interface.md#pilot-notepad-and-compute) |
| Noise | Is the base score flat enough that we need to raise the noise knob | [mechanics](mechanics.md#noise) |
| Inertia | Is the base score too flat to separate models, so a cap on movement is needed | [scoring](scoring.md#extension-inertia) |
| Baseline order | Do the fixed baselines land in the expected order on switch and calm | [baselines](baselines.md#ordering-sniff-test) |
| Timestral gap test | Do the quantiles widen over blanks, so probability of best can look | [baselines](baselines.md#checks-before-we-trust-design) |
