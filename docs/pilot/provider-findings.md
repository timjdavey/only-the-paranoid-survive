# Provider findings

What the full run of the [provider checks](provider-checks.md) taught us, on 2026-11-12 and 2026-11-13. The scratch probes and the first example skin results before it are in [model findings](model-findings.md). Tables and plots are in [results](results.md).

- **Each finding has three parts,** as in [findings](findings.md): what we saw, what it means and what changed or is still open.
- **Every Claude call went through the plan token,** so it drew on the plan, not a bill. Haiku 5.5 plays at `off` and Sonnet 5.5 at `low`, as in `poc.toml`.
- **Six skins:** the example and five held out, `amber`, `indigo`, `ochre`, `umber` and `viridian`. Only names and numbers are written here. No held-out skin's text, and no reply to one, leaves the private logs.
- **The eval cells played the example skin on public seeds 0 to 19,** as the [pilot spec](../specs/harness/pilot.md#shared-rules) says. Only `recognition` and `channel-order` played the held-out skins.

## The record is cut into blocks for Anthropic's cache

- **Saw.** Both checks left in the [solver spec](../specs/harness/solver.md#checked) passed on `claude-haiku-5-5`:
  - `count_tokens` on a forty row record gave 1,969 tokens as one block, as 41 blocks and as a plain string.
  - A three round run, with thirty `uniform` warm up rounds so the prompt clears the cache minimum:

    | Round | Cache read, cut | Cache read, one block |
    |---|---|---|
    | 1 | 754 | 754 |
    | 2 | 2,902 | 754 |
    | 3 | 2,964 | 754 |

- **Means.** As one block only the system prompt is ever read from the cache, and the record is written to it again each round. Cut, all but the newest row is read. The token count is the same, so the model reads the same prompt.
- **Changed.** `BLOCK_CACHE_APIS` is `("anthropic",)`, so every pilot cell after it played with the cut.

## Channel order: `submit` keeps its list

- **Saw.** 360 probes, 30 per model and skin, see [channel order](provider-checks.md#channel-order):

  | Model | Valid calls | Matched | Slipped | Slip share |
  |---|---|---|---|---|
  | Haiku 5.5 | 154 of 180 | 154 | 0 | 0 |
  | Sonnet 5.5 | 180 of 180 | 179 | 1 | 0.006 |

- **Sonnet's one slip is the one seen before,** on the example skin: asked for 55 on channel 8 and 45 on channel 1, it put the 55 on channel 7. On the five held-out skins it matched 150 of 150.
- **No model sent numbers of its own.** Every valid call that did not match was a slip.
- **Haiku's 26 probes with no valid call are all on `umber`,** see [the next finding](#haikus-content-filter-stops-the-umber-skin).
- **Means.** Both rows are under the 1 in 50 line, pooled over skins and shapes, so `submit` keeps its list of ten numbers in channel order and every other LLM cell could run.

## Haiku's content filter stops the `umber` skin

- **Saw.** On `umber`, Haiku's replies stopped with `content_filter`:
  - Both recognition probes came back empty. Replayed three times, the round 1 prompt with the question stopped every time, and the round 1 prompt alone stopped twice of two.
  - In channel order it began a call on 29 of 30 probes and finished 4. Replayed, the filter cut the list part way, after `[` on one probe.
  - Sonnet played `umber` cleanly: 30 of 30 matched, and every recognition reply was whole.
- **Means.** Haiku cannot play `umber`. A run would give up on round 1, and its score would read as a model that failed the game, not a filter. No other skin tripped it.
- **Open.** Rework `umber`'s wording in the private repo, or keep it out of the two held-out skins the proof of concept plays, see [`TODO.md`](../../TODO.md#code). Whether another provider's filter trips on it is not known.

## Recognition: no reply named the study

- **Saw.** 36 probes, see [recognition](provider-checks.md#recognition). Of the 24 round probes, 22 replies were whole and two were Haiku's empty `umber` replies.
  - **No canary was finished**, on any skin.
  - **No reply named the benchmark, the repo, or a shock that fades against a new normal.**
  - **Sonnet called it a multi-armed bandit,** an explore against exploit task, on 6 of 12 replies, the two example probes and four held-out. Haiku called it a test of exploration against exploitation once, on a held-out skin.
  - **The lint hit Sonnet on 10 of 12 round probes and Haiku on 1 of 10,** on everyday words: `shift` on 8, and `chang`, `check` and `stabl`. Every canary reply hit, as the canary line itself holds `benchmark` and `canar`.
- **Means.** The skins hide the study, but a model still sees a bandit task, which is a fair read of any game where bets are paid by what a channel earns. The lint share measures how a model talks, not what it recognised. At today's `RECOGNITION_FLAG` of 0.25 it would put `§` on every Sonnet score.
- **Open.** The share that flags a bar, see [decisions](decisions.md#provider-checks). The report proposes a hit be a reply that names the study or what it tests, not a banned word.

## Seeds: the widest spread is Haiku on One shock

- **Saw.** 80 runs, both rows on One shock and Up switch, public seeds 0 to 19, see [seeds](provider-checks.md#seeds). Every run finished bar one:

  | Model | Scenario | Score | SD of run score | Lowest | Highest |
  |---|---|---|---|---|---|
  | Haiku 5.5 | One shock | 0.44 | 0.163 | 0.00 | 0.71 |
  | Haiku 5.5 | Up switch | 0.40 | 0.119 | 0.24 | 0.75 |
  | Sonnet 5.5 | One shock | 0.85 | 0.057 | 0.72 | 0.93 |
  | Sonnet 5.5 | Up switch | 0.74 | 0.145 | 0.46 | 0.94 |

- **One run gave up.** Haiku on One shock seed 14 ran out of its ten tries in round 6 with no valid call, and scored 0. Without it Haiku's One shock SD is 0.128, and Sonnet's Up switch is the widest.
- **The seed count follows from the target error bar**, at 1.5 × (0.163 ÷ target)²:

  | Target | 0.05 | 0.04 | 0.03 | 0.02 |
  |---|---|---|---|---|
  | Seeds | 16 | 25 | 45 | 100 |

- **Means.** The check measures what it should. A weaker model spreads wider, and the run that gave up widens it more.
- **Open.** The target, which [seeds](provider-checks.md#seeds) sets at a fraction of the smallest baseline gap worth reading. The hedge rule sits 0.05 under the Complacent baseline on One shock here, so a fifth of that is 0.01, which would take 400 seeds.

## Repeats: half the spread is Haiku's own dice

- **Saw.** `repeats` picked Haiku on One shock, ten seeds across its range, each played four times, see [repeats](provider-checks.md#repeats). All 40 runs finished.
  - Within a seed the run score's SD is 0.080, against 0.112 over all 40 runs.
  - So the sampling share, within variance over total, is 0.51.
  - Seed 14, which gave up in `seeds`, finished all four repeats, at 0.31 to 0.49.
- **Means.** For Haiku a per-seed dot says as much about the roll as about the world. Pairing by seed buys less than hoped, so a paired gap on Haiku has a wider bar than its seed count suggests. The headline still plays each seed once, as more seeds beat repeats.

## Cost: the cut cache makes a run cheap

- **Saw.** `paranoid analyse cost logs/pilot/seeds`, per run, priced from `configs/prices.toml`:

  | Model | Input | Cache read | Cache write | Output | Cached share | Wall time, 40 runs | Cost a run |
  |---|---|---|---|---|---|---|---|
  | Haiku 5.5 at `off` | 1,106 | 198,034 | 25,737 | 15,264 | 0.88 | 27 minutes | $0.013 |
  | Sonnet 5.5 at `low` | 160 | 82,383 | 4,318 | 6,231 | 0.95 | 17 minutes | $0.082 |

- **No reply was cut off by max tokens.** Sonnet used about 1,700 reasoning tokens a run.
- **Haiku reads more than twice Sonnet's tokens,** as it runs code on 95% of rounds and every tool turn sends the prompt again.
- **Means.** The `seeds` cell cost about $3.80 at list prices, against the $10 to $15 planned for three rows. Output is most of the bill now that the record is cached: 59% of Haiku's and 76% of Sonnet's.

## The retry share flags Haiku for running code

- **Saw.** Haiku's retry share was 0.95 on both scenarios, Sonnet's under 0.01. Haiku ran code on 95% of rounds, and a reply that runs code before it sends a split counts as a retry. Its replies with no call to `submit` averaged 38 a run, and bad calls 2.
- **Means.** At today's `RETRY_FLAG` of 0.1, `‡` would go on every Haiku score, though it plays the tool cleanly. As [model findings](model-findings.md#the-provider-checks-first-results) warned, the share measures tool use as well as trouble.
- **Open.** The share that flags a bar, see [decisions](decisions.md#provider-checks). The report proposes counting only the tries that were bad calls or plain text, not a tool turn.

## Jev and Decision Models: two decision models beat Sonnet on a switch

- **Saw.** The `jev` cell, six rows on No change and Down switch, public seeds 0 to 19, 1600 calls a row. All 240 runs finished. Explore points are the points off the top channel a round:

  | Row | No change | Down switch | Explore points, No change | Channels rounded out a round | Rounds with one |
  |---|---|---|---|---|---|
  | `jev-latest` | 0.74 | 0.59 | 19.7 | 0 | 0% |
  | `s1-pro-5` | 0.83 | 0.64 | 18.2 | 3.7 | 93% |
  | `s1-pro-3` | 0.91 | 0.72 | 10.2 | 5.1 | 97% |
  | `s1-fast-2` | 0.66 | 0.59 | 27.1 | 1.4 | 56% |
  | `reax-1-20261021` | 0.87 | 0.79 | 13.6 | 1.4 | 80% |
  | `reax-1.3` | 0.94 | 0.83 | 8.3 | 6.0 | 98% |

- **`jev-latest` played as it did in its first run,** 0.73 and 0.60 then. Its `rounded_out` is 0 again, as it sends whole percents, see [Jev](model-findings.md#jev-costs-nothing-and-plays-a-switch-as-well-as-sonnet).
- **The Decision Models rows send fine probabilities,** so `rounded_out` reads here. `reax-1.3` rounds six channels out of view a round and still scores best.
- **Means.** Two decision models, `reax-1.3` and `reax-1-20261021`, beat the Complacent baseline's 0.48 on Down switch by 0.3 and more, with no text, no tools and no story. On No change the order of the rows by explore points is the reverse of their order by score, so a sharp reader beats a curious one there.
- **Open.** The Jev row in [decisions](decisions.md#provider-checks) still waits on whether the check counts channels at exactly 0, see [`TODO.md`](../../TODO.md#pilot).

## Up against down: Haiku finds the riser and pays to look

- **Saw.** 100 Haiku runs on five scenarios, public seeds 0 to 19, with the One shock rows from `seeds`, see [up against down](provider-checks.md#up-against-down). All finished but two Up switch runs, which gave up.

  | Scenario | Switch kind | Seeds | Haiku |
  |---|---|---|---|
  | No change | | 20 | 0.50 |
  | One shock | | 20 | 0.44 |
  | Down switch | Fall alone | 10 | 0.51 |
  | Down switch | Fall with a riser | 10 | 0.26 |
  | Up switch | Rise past the leader | 14 | 0.28 |
  | Up switch | Rise that stops short | 6 | 0.45 |
  | Up switch then down switch | Rise | 20 | 0.43 |
  | Switch then shock | Fall alone | 10 | 0.47 |
  | Switch then shock | Fall with a riser | 10 | 0.25 |

- **It reached the sleeper on 85% to 90% of runs,** in a median round of 9 to 11, so at or just after onset, which falls on 8 to 12.
- **It explores whether or not anything is wrong.** It held 58 points off its top bet a round on No change and 69 to 73 before onset on the rest.
- **Paired by seed,** Up switch scores 0.18 under No change, bar −0.30 to −0.06, and Up switch then down switch 0.17 over Up switch, bar 0.07 to 0.28.
- **Means.** Haiku is not paranoid in the study's sense, as it never commits. Its wide spread finds nearly every riser, and costs it half the gain on offer on No change. A fall with a riser scores half what a fall alone does, so it finds the riser and does not move enough onto it.
- **Read beside its bet size.** As in [the first model](model-findings.md#it-picks-the-right-channel-and-bets-small-on-it), a score near 0.5 on No change says more about bet size than reading.

## Timestral: one explore point pays, and joint forecasting adds nothing

- **Saw.** The `timestral` cell, run locally on CPU in about three hours: the two probes, then seven rows at every grid setting on One shock, Down switch and Up switch, public seeds 0 to 19, see [Timestral checks](provider-checks.md#timestral-checks).
- **Gap test.** The spread, last quantile less first, averaged over channels:

  | Blanks | 1 | 5 | 10 | 15 | 20 | 30 |
  |---|---|---|---|---|---|---|
  | Joint | 44 | 40 | 40 | 56 | 74 | 121 |
  | Alone | 43 | 59 | 82 | 109 | 130 | 219 |

- **Determinism.** The same input twice gave equal output, on both shapes.
- **Rounding.** The three odds rows rounded 6.5 to 6.6 channels out of view a round, on 98% of rounds. Top pick and the explore rows never did, as they bet no probability.
- **On the grid,** scored as gain over the Discerning baseline's, pooled over seeds:

  | Player | Down switch | One shock | Up switch | Mean |
  |---|---|---|---|---|
  | Bayesian baseline | 0.94 | 0.96 | 0.93 | 0.95 |
  | Hedge rule | 0.90 | 0.95 | 0.72 | 0.86 |
  | Timestral explore 1 | 0.84 | 0.87 | 0.86 | 0.85 |
  | Timestral top pick | 0.67 | 0.96 | 0.69 | 0.77 |
  | Timestral explore 2 | 0.76 | 0.78 | 0.77 | 0.77 |
  | Timestral odds alone | 0.69 | 0.89 | 0.70 | 0.76 |
  | Timestral odds | 0.68 | 0.89 | 0.70 | 0.76 |
  | Timestral odds, bet aware | 0.69 | 0.89 | 0.70 | 0.76 |
  | Complacent baseline | 0.43 | 1.00 | 0.72 | 0.72 |
  | Timestral explore 5 | 0.48 | 0.49 | 0.49 | 0.49 |

- **The grid barely moves them.** Explore 1 stays level with the hedge rule at every setting, both at 0.85 to 0.87 from setting 2 to 8, and no row moves by more than 0.05 across the grid.
- **Means.**
  - **The joint shape barely widens.** Its spread holds flat for ten blanks and grows 2.7 times by thirty. Alone it grows 5 times and from the first blank. Odds can still explore, so it stays, but through the joint shape it explores late.
  - **Top pick and odds land between the hedge rule and the Complacent baseline,** as the [baseline order](engine-checks.md#baseline-order) asks.
  - **One explore point is worth its cost for a forecaster too.** It lifts top pick from 0.77 to 0.85, level with the hedge rule. Two points give the gain back, and five cost over a third of the score.
  - **Forecasting the channels together adds nothing,** and nor does showing the bets. Odds, odds alone and bet aware sit within 0.01 of each other in every scenario.
- **Open.** Whether the joint shape's late widening is enough, see [`TODO.md`](../../TODO.md#pilot), and the Timestral row in [decisions](decisions.md#provider-checks).
