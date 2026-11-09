# Plots

## Purpose

Four plots: the strip of run scores behind every bar, the trait profile, the two trend plots and the noise curve. Each is one function from a table to an SVG file. What each shows is in [spread](../../design/scoring.md#spread), [trend plots](../../harness/models.md#trend-plots) and [noise threshold](../../design/scoring.md#noise-threshold).

## Interface

```python
def strip_plot(runs: pd.DataFrame, key: ResultKey, out: Path) -> Path
def profile_plot(scores: pd.DataFrame, out: Path) -> Path
def trend_plot(headlines: pd.DataFrame, models: Path, x: Literal["released", "eci"], out: Path) -> Path
def noise_plot(runs: pd.DataFrame, thresholds: Sequence[Threshold], out: Path) -> Path
```

## Behaviour

### Strip plot

One result row, eight panels in `SCENARIOS` order, one per scenario.

- **Dots** are the run scores, one per seed, jittered on a fixed rng seeded `BOOTSTRAP_SEED`, so the picture is the same on every run.
- **The bar** is the pooled score with its interval, see [scenario scores](scores.md#scenario-scores).
- **Marks** are ticks across the panel for the Complacent, hedge rule, Scout rule and Perfect baselines, each labelled once in the legend. The Complacent mark is always the same grey.
- **Flags** are the panel title's suffix, with the legend's words under the figure.
- **The axis** runs from a little below 0 to a little above 1, the same on every panel, with 0 and 1 drawn as lines named for the Uniform and Discerning baselines. A dot outside is drawn where it lands, as [scoring](../../design/scoring.md#why-these-two-baselines) says scores outside 0 to 1 are reported as they come.

### Profile plot

The trait profile: eight traits on the x axis in `SCENARIOS` order, named by trait, one line per result row with its bars, see [traits](../../design/scoring.md#traits). The Complacent baseline's marks are one grey line, so a reader sees where a model acted at all.

### Trend plots

- **One point per result row**, headline on the y axis with its bar, `released` or `eci` from the models file on the x axis, see [trend plots](../../harness/models.md#trend-plots). A row whose model has no value for `x` is left out and listed in the figure's footer.
- **Settings of one model are joined by a line**, in `REASONING` order. On the ECI plot they stack in a column, as the design says.
- **Provider rows** have neither date nor ECI, so they are drawn as horizontal lines across the plot, named.
- **The ECI plot credits Epoch AI**: a footer reading `ECI from Epoch AI, CC BY 4.0, read on <date>`, the date from the models file's own comment or the `read_on` the caller passes. Never a plot without it.

### Noise plot

- **One line per model**: headline against signal to noise on a log x axis, one point per grid setting with its bar, and the logistic fit from [noise threshold](scores.md#noise-threshold) drawn through it.
- **The floor** is a grey line at the Complacent baseline's headline, and the half way mark a dotted one.
- **Each threshold** is a tick on the x axis with the model's name. A model off the grid is named at the end it fell off.
- **The axis label says signal to noise**, with the own-weather scale as a second axis along the top, so the grid's settings can be read straight off.

### Every plot

- **SVG only**, written with `metadata={"Date": None}` and `rcParams["svg.hashsalt"]` fixed to `"paranoid"`, so a rerun gives equal bytes.
- **Fixed figure sizes**: the strip plot 12 by 3 inches, the rest 6 by 4. No tight layout that depends on font metrics the machine may not share; margins are set by hand.
- **One palette** of eight colours, colour-blind safe, used in order. Baseline marks are greys. Text is the default font with a fallback list, so a missing font changes glyphs and never layout.
- **The title names the skin and seed set**, and the noise setting when it is not the default. Nothing else from a skin, and no seed value, appears on any plot.
- **Returns the path written.**

## Invariants

- Each function called twice on the same inputs writes byte-identical files.
- No plot reads anything the run table does not hold.
- The ECI plot's SVG contains the credit text.

## Not decided

- Whether to also write PNGs for pages that cannot show SVG. Decide when the first results page is published.

## Verify before code

- **matplotlib SVG determinism.** That `svg.hashsalt` and `metadata={"Date": None}` give equal bytes across runs and machines with the same matplotlib version, and what else, such as font embedding, has to be pinned. Every plot function waits on it.
