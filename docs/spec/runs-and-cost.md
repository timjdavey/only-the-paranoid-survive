# Runs and cost

## Runs per seed

| | Proof of concept | Full study |
|---|---|---|
| Briefings | 1 | 1 |
| No-change runs | 1 | 5, one at each noise setting |
| Change runs | 2: at 12 points and at 5 points (8 if 5 isn't worth catching) | 5: at 12 points, one at each noise setting |
| **Runs a seed** | **3** | **10** |
| Rounds a run | 40 | 40 |

## Runs per model

| | Proof of concept | Full study |
|---|---|---|
| Seeds | 20 | About 30 |
| Runs | 60 | About 300, plus extra runs where a model starts to miss |
| Briefings | 20 | About 30 |
| No-change runs | 20 | About 150 |
| Calls, one a round | About 2,400, plus briefings, reads and code calls | About 12,000, plus the same |
| Reasoning settings | 1 | A sweep, which multiplies every row above |
| Kinds of change | Level | Level, coupling, gain and observation, which multiply again |

## Cost inputs

| Input | Value |
|---|---|
| Target | About $100 a model, since the benchmark is run out of pocket |
| Thinking | 3,000 to 5,000 tokens a round |
| Prompt caching | On |
| Typical prices | $4 in, $20 out, per million tokens |
| Top prices | $10 in, $50 out, per million tokens |
| Bots | Free: no API calls |

## Cost per model

At one reasoning setting and one kind of change.

| | A run | Proof of concept, 60 runs | Full study, about 300 runs |
|---|---|---|---|
| Typical prices | $3 to $4.50 | $180 to $270 | $900 to $1,350 |
| Top prices | $7 to $11 | $420 to $660 | $2,100 to $3,300 |
| One more run a seed, typical prices | | $60 to $90 | $90 to $135 |

- **Neither tier meets the target yet.** The proof of concept is about twice it at typical prices.
- **The full study is a funded figure**, and the reason the discernment threshold waits.

## If cost runs over

1. **The pilot measures real thinking first.** A first run on two models over a few seeds.
2. **Then choose:** a higher target or fewer seeds. [Next step 2](../../TODO.md#next-steps) says how far seeds can fall before the error bars break.
3. **Cut seeds, not thinking.** A model run below its best says little.
4. **Never cut the no-change run.**

## Why these counts

| Count | Reason |
|---|---|
| 20 seeds, proof of concept | Gives a standard error near 0.05 on performance. [Why performance is the proof of concept headline](../design/decisions.md#why-performance-is-the-proof-of-concept-headline) |
| 20 no-change runs, not 10 | Halves the error bar on the [doubt tax and the false alarm leak](../design/measure-failure.md#where-the-output-went) |
| New seeds, not repeats of one | A new seed is a new item as well as a new sample, at the same price. [Why more seeds, not repeats](../design/decisions.md#why-more-seeds-not-repeats) |
| About 30 seeds, full study | Enough to fit discernment's curve. Checked on bots in [next step 2](../../TODO.md#next-steps) |
