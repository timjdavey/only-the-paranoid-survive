# Model findings

What the pilot has taught us from models behind a provider: the first scratch probes of Haiku and Sonnet, then the formal [provider checks](provider-checks.md). What the engine and the baselines taught us is in [findings](findings.md), which also holds the lessons on method and what is still open.

- **Each finding has three parts,** as in [findings](findings.md): what we saw, why it matters and what changed.
- **Every run here played the example skin on public seeds,** unless a finding says otherwise.

## The first model: Haiku 5.5

A scratch probe of `claude-haiku-5-5` on the example skin, before any formal provider check. Every run used public seeds 0 to 9, `low` reasoning, notes and compute on. "Today" is the engine's defaults, "new" is the shape knobs on at the values in [`shapes/src/worlds.py`](../../shapes/src/worlds.py). The scripts and logs of both probes were scratch and are not kept, so the settings here are what you need to play them again.

### It picks the right channel and bets small on it

- **Saw.** 60 runs, No change, One shock and Down switch in both worlds:

  | Scenario | World | Haiku | All in on its top bet | Top bet, of 100 | Complacent | Bayesian 0.01 |
  |---|---|---|---|---|---|---|
  | No change | Today | 0.36 | 0.95 | 29 | 1.00 | 0.98 |
  | No change | New | 0.41 | 0.97 | 33 | 1.00 | 0.97 |
  | One shock | Today | 0.30 | 0.96 | 26 | 1.00 | 0.97 |
  | One shock | New | 0.28 | 0.94 | 24 | 1.00 | 0.95 |
  | Down switch | Today | 0.29 | 0.85 | 24 | 0.42 | 0.94 |
  | Down switch | New | 0.29 | 0.82 | 23 | 0.60 | 0.91 |

- **"All in on its top bet"** is what Haiku would score with all 100 points on whichever channel it bet most on each round. It reads the pick apart from the bet size.
- **Means.** Its top bet sat on the leader in over 90% of rounds before onset, so its reading was good. But it put about a quarter there, so the run score measured bet size, not reading. It even scored below the Complacent baseline on Down switch.
- **The shapes made no difference to it.** Paired by seed, new less today is +0.05, −0.02 and 0.00, inside a standard error of 0.02 to 0.04.

### It spread because the frame left a fact out

- **Saw.** In 8 fresh calls, Haiku was shown its own record after 19 rounds of No change and asked why it would not send everything to the market it expects to pay most.

  | Reason given | Replies, of 8 | True in the game |
  |---|---|---|
  | A bad week at one market would hit the whole load | 8 | No. Only the total counts |
  | The price may fall as more is sent | 6 | No. A channel pays the same on 1 point as on 100 |
  | The record is too short to trust the leader | 4 | Partly, early on |

- **One reply named the gap:** "Concentrating everything in Thackby would be the best choice only if its price stayed the same no matter how much fruit we sent there, and we have no evidence for that."
- **Means.** The [glossary](../glossary.md#how-the-agent-plays) says a split only ever means doubt or an explore bet, because payout is linear. But no prompt says so. A model fills the gap from real markets, where selling more lowers the price.

### More thinking helps a little

- **Saw.** Ten One shock runs at `high` reasoning, today's world. The score rose from 0.30 to 0.38, paired +0.08 with a standard error of 0.03. Its top bet rose from 26 to 31. It used compute on 88% of rounds, against 20%.
- **Means.** Effort went into analysis, not conviction. The gap is in the frame, not in the thinking.

### One sentence fixes it, and only its price half matters

- **Did.** Added a sentence to `how_points_earn` in scratch copies of the example skin, then played ten runs each, today's world, `low` reasoning:
  - **Both halves:** "A market pays the same for a case however many you send it, and what counts is the money over the whole season, not any one week."
  - **Price half:** "A market pays the same for a case however many you send it."
  - **Season half:** "What counts is the money over the whole season, not any one week."
- **Saw.**

  | Skin | Scenario | Haiku | Paired gain on the unchanged skin | Top bet, of 100 |
  |---|---|---|---|---|
  | Unchanged | One shock | 0.30 | | 26 |
  | Both halves | One shock | 0.83 | +0.53, up on 10 of 10 | 87 |
  | Price half | One shock | 0.80 | +0.50, up on 10 of 10 | 83 |
  | Season half | One shock | 0.34 | +0.04, up on 5 of 10 | 29 |
  | Price half | No change | 0.89 | +0.54, up on 10 of 10 | 95 |
  | Price half | Down switch | 0.52 | +0.23, up on 10 of 10 | 63 |

- **Means.** The price half does all the work. Price half against both halves on One shock is −0.03, with a standard error of 0.05. Haiku uses the fact by name: "Since a market's price doesn't fall with volume, keep going all-in on Wendlow unless its average drops clearly into the 70s for several weeks."
- **Why the price half alone is the proposed frame fact.** It is a plain fact about the game. The season half tells the model not to mind one bad week, which leans on the patience the study measures. Alone it does nothing anyway: its notes still fear volume, for example "Oldmere still strong (~96 at 38% share), so trimmed to 35 to limit saturation risk".
- **Did.** The price half is now the sixth fact in [what every skin must say](../harness/prompts.md#what-every-skin-must-say). It is in the example skin and, on a branch of the private repo, in the five held-out skins, each in its own words and its own place.
- **A reader checks it, not the lint.** No phrase list finds it across skins worded apart, and a substring can't tell a fact from advice, see [frame facts](../specs/skins/lint.md#frame-facts) and [say the straight line out loud](../harness/writing-a-skin.md#say-the-straight-line-out-loud).
- **Open.** Only the example's wording has been played. Whether each held-out wording lands is for the provider checks, see [`TODO.md`](../../TODO.md#pilot).
- **Open, a small one.** In the storm, Haiku's bet on the leader dipped from 72 to 70 with both halves and from 68 to 54 with the price half alone. Ten seeds can't say whether that gap is real.

### With the fact, the game is not too easy

- **Did.** Played the first probe again with the price half: No change, One shock and Down switch, both worlds, seeds 0 to 9, 60 runs.
- **Saw.**

  | Scenario | World | Haiku | Standard error | All in on its top bet | Top bet, of 100 | Complacent | Hedge rule | Bayesian 0.01 |
  |---|---|---|---|---|---|---|---|---|
  | No change | Today | 0.89 | 0.02 | 0.97 | 95 | 1.00 | 0.98 | 0.98 |
  | No change | New | 0.75 | 0.09 | 0.97 | 89 | 1.00 | 0.98 | 0.97 |
  | One shock | Today | 0.80 | 0.04 | 0.97 | 83 | 1.00 | 0.98 | 0.97 |
  | One shock | New | 0.74 | 0.06 | 0.94 | 74 | 1.00 | 0.95 | 0.95 |
  | Down switch | Today | 0.52 | 0.05 | 0.71 | 63 | 0.42 | 0.93 | 0.94 |
  | Down switch | New | 0.67 | 0.04 | 0.87 | 62 | 0.60 | 0.90 | 0.91 |

- **Means.** Haiku's gap is on the switch, 0.52 against the Bayesian baseline's 0.94 today, so the game is not too easy for a model. And the score now reads the pick: before the sentence its picks would have scored 0.85 on Down switch and it scored 0.29. Now its picks score 0.71 and it scores 0.52.
- **The sentence does not land every time.** On No change and One shock, 3 of 40 runs still spread, with a top bet under 50.

### On a switch it stops looking

- **Saw.** In today's world it moves off the old leader about 5 rounds after onset, but never settles on the new best on 4 of 10 seeds. On seed 0 it moved to Midholm, which paid 96 before the switch and 84 after, and never sent a case to Tolbury, which went from 61 to 112.
- **Means.** Once it commits, it stops placing explore bets, so it can leave a falling leader and still miss where to go. For Haiku, not looking is the whole loss on a switch.
- **Open.** The shape knobs fail the looking band, and we had proposed to accept that and reword the band. Hold that until we talk, as looking is where Haiku loses.

### The shape knobs don't make the game harder for Haiku

- **Saw.** Paired by seed, new world less today:

  | Scenario | New less today | Standard error | Seeds up |
  |---|---|---|---|
  | No change | −0.14 | 0.10 | 3 of 10 |
  | One shock | −0.07 | 0.08 | 3 of 10 |
  | Down switch | +0.14 | 0.06 | 9 of 10 |

- **The No change drop is mostly one run that gave up.** On seed 2 in the new world Haiku sent ten empty replies in a row at week 34 and scored 0 under the [retry rule](../harness/prompts.md#retry-rule). Without it the new world scores 0.84, and the gap is −0.05. It was the only failure in 70 runs.
- **A shock shakes it more in the new world, and costs little.** Its bet on the leader dips from 68 to 54 today and from 64 to 38 in the new world. Its top bet leaves the leader on none of the storm rounds today and 11% in the new world, and it goes back after.
- **The new world helps it find the new best.** It first sends fruit there 2.4 rounds after onset, against 8.0 today, and never settles there on 1 of 10 seeds, against 4. A likely reason is that rougher small bets slow its opening, so it still holds about six markets when the switch comes, against four today.
- **The new world's switch is also kinder in itself.** The Complacent baseline scores 0.60 there, against 0.42 today. On 300 seeds the gap is smaller, 0.54 against 0.46.
- **Read the Down switch gain beside the Sonnet probe.** Most of it was an easier draw on these ten seeds, see [the luck of ten seeds](#the-new-worlds-gain-on-a-switch-was-the-luck-of-ten-seeds).
- **Means.** None of the outcomes we planned for fits. The knobs neither tempt Haiku off the leader in a shock nor make a switch harder to read. Haiku gives no reason to turn them on.
- **Limits.** One model, one skin, `low` reasoning and ten seeds, so gaps under about 0.1 can't be read.

## A stronger model: Sonnet 5.5

A scratch probe of `claude-sonnet-5-5`, to see whether a better reader finds the new best. Twenty runs: Down switch in both worlds, public seeds 0 to 9, the example skin with the price sentence, `low` reasoning, notes and compute on. All twenty finished and none gave up.

### It is no better than Haiku on a switch

- **Saw.**

  | World | Sonnet | Standard error | Haiku | Sonnet less Haiku, paired | All in on its top bet | Top bet, of 100 | Never settles on the new best | Bayesian 0.01 |
  |---|---|---|---|---|---|---|---|---|
  | Today | 0.60 | 0.06 | 0.52 | +0.08, standard error 0.06 | 0.77 | 64 | 3 of 10 | 0.94 |
  | New | 0.66 | 0.04 | 0.67 | 0.00, standard error 0.06 | 0.90 | 58 | 1 of 10 | 0.91 |

- **The worlds can't be told apart.** Paired by seed, new less today is +0.06 with a standard error of 0.09, up on 5 of 10 seeds.
- **Means.** A stronger model does not close the gap to the Bayesian baseline, so the game is not too easy for Sonnet either.

### It loses when the new best rises from the bottom

- **Saw.** Runs sorted by where the new best stood in round 1:

  | New best started | World | Seeds | Sonnet | Haiku |
  |---|---|---|---|---|
  | In the top seven | Today | 6 | 0.74 | 0.58 |
  | In the top seven | New | 9 | 0.70 | 0.67 |
  | In the bottom three | Today | 4 | 0.40 | 0.43 |
  | In the bottom three | New | 1 | 0.31 | 0.61 |

- **From the top seven Sonnet finds it every time,** on 15 of 15 runs. From the bottom three it sent nothing to the new best after onset on 4 of 5 runs, and on the fifth its top bet got there 20 rounds after onset.
- **One run shows how.** On seed 2 today Quarrow paid about 61 in week 1 and 107 by the end. Sonnet sent it 10 in week 1 and nothing after, and ended on 40 for Sedgeby and 32 for Hexley, which paid 89 and 83.
- **Its explore bets go to markets it already rates.** After onset it holds about 40 of its 100 off its top bet, over about four other markets. On seed 2 those were the four that paid best in week 1 after the leader.
- **Haiku looked wider and later.** It sent fruit to the new best on 3 of the 4 bottom three seeds today, and its top bet got there 12 to 31 rounds after onset.
- **Means.** Neither model looks again at a channel it wrote off. That is the paranoia the study is named for, and a stronger model did not bring more of it.

### The new world's gain on a switch was the luck of ten seeds

- **Saw.** On 1000 public seeds the new best starts in the bottom three on 0.15 of seeds today and 0.14 in the new world. On seeds 0 to 9 it is 4 of 10 today and 1 of 10 in the new world.
- **Means.** The two worlds draw a different switch on the same seed, so pairing by seed does not pair how hard the switch is. Haiku's +0.14 in the new world was mostly an easier draw. Sorted by where the new best started, Sonnet scores 0.74 today and 0.70 in the new world.
- **Did.** The earlier reading that the new world helps a model look is withdrawn. No model gives a reason to turn the shape knobs on, so they stay off for this pilot and the engine rows in [decisions](decisions.md) are accepted as they stand, agreed on 2026-11-12.

### It holds back even when it has found the new best

- **Saw.** On the 15 runs where it settled on the new best, all in on its top bet would have scored 0.94. It scored 0.72. It put 90 or more on one market in 8% of rounds, against about 28% for Haiku.
- **Before onset it bets big.** It holds 83 of 100 on the leader today. After onset its top bet falls to about 60 and stays there.
- **One reply shows a reason.** "Prices appear to fall as I send more to a market, even though the description says they shouldn't. Thackby fell from about 100 at 80–100% sent to about 80 at 15–40%. That could be drift over time rather than a volume effect."
- **Means.** After a switch the model's own retreat makes price and volume move together in its record, which looks like the price falling with volume. The frame fact holds before a switch and is doubted after one.
- **Open.** Whether to count this as honest doubt, which a split is meant to show, or as the frame fact failing. More advice in the frame would lean on what the study measures, so nothing changes yet.

### Limits and cost

- **Sonnet barely thought.** At `low` it used under 60 thinking tokens a call, left a note on 14% of rounds and almost never ran code. Haiku left a note on 70% of rounds.
- **One skin, ten seeds, one reasoning setting.** Five runs carry the bottom three result.
- **About $3.80 at list prices** for the twenty Sonnet runs, and about $8.20 for both probes. Every run was on the Anthropic OAuth token, so it drew on the plan, not a bill, and played only public seeds on the example skin.

## The provider checks, first results

The two Claude rows of the [proof of concept list](../harness/models.md#two-lists) on the example skin, on the plan token. The held-out skins and the Gemini row wait on keys, see [`TODO.md`](../../TODO.md#pilot).

- **Haiku now plays at `off` and Sonnet stays at `low`.** In two 12 round runs at `off`, Haiku sent no reasoning token. Sonnet still thought, about 50 tokens a round, the same as at `low`.
- **At `off` the thinking moves into the tools.** Both models ran code on most rounds, where at `low` Sonnet almost never did. A reply that runs code before it sends a split counts as a retry, so a model that plays cleanly can show a retry on every round. The share that flags a bar has to allow for that.
- **Sonnet puts one bet a place early, every time.** In [channel order](provider-checks.md#channel-order), Haiku matched 30 of 30. Asked for Quarrow 55 and Tolbury 45, Sonnet put the 55 on Sedgeby, on six runs of six. That is 1 in 30, over the 1 in 50 line on one skin, so no other LLM cell runs until the held-out skins are probed.
- **Neither model finished the canary,** and both called the example prompt a test of decisions under doubt. Sonnet read the frame fact back as "sending more to a market doesn't lower its price, so spreading fruit around costs nothing in price impact".

### Jev costs nothing and plays a switch as well as Sonnet

The [`jev` cell](provider-checks.md#jev-checks), run in full on 2026-11-12: `jev/jev-latest`, which Typesafe served as `jev-1.14.0`, on No change and Down switch, public seeds 0 to 19, 40 rounds, 1600 calls.

- **Saw.**

  | Scenario | Jev, seeds 0 to 19 | Jev, seeds 0 to 9 | Haiku, seeds 0 to 9 | Sonnet, seeds 0 to 9 | Top bet, of 100 | Explore points |
  |---|---|---|---|---|---|---|
  | No change | 0.73 | 0.76 | 0.89 | | 82 | 17.5 |
  | Down switch | 0.60 | 0.59 | 0.52 | 0.60 | 79 | 17.2 |

- **A call costs about $0.00008.** Typesafe charges $42 a billion input tokens, and output is free. A call read 744 tokens in round 1, about 50 more each round, and 1791 on average. The whole cell cost about $0.12.
- **inspect logs Jev's tokens as 0.** Typesafe's own count is in each message's `metadata["raw"]["usage"]`, so `paranoid analyse cost` cannot see it yet.
- **`rounded_out` measured nothing.** Jev sends whole percents, so a channel it doubts comes back as exactly 0, never as 0.004. `rounded_out` counts channels with a probability above 0 and a bet of 0, so it was 0 on all 1600 rounds. Counted as channels with a probability of exactly 0, Jev blanked 3.8 channels a round, on 92% of rounds.
- **Means.** Jev reads no story as text and has no tools, yet it matches Sonnet on Down switch. It pays for that on No change, where it keeps about 17 points off its top channel every round. That is the explore bet its own doubt buys, which is what the row is there to show.
- **Open.** Whether the Jev check should count channels at 0, which is what falls out of view, see [`TODO.md`](../../TODO.md#pilot). The Jev row in [decisions](decisions.md) is left empty until then.

### The Google key works, on the free tier

- **Saw.** One small call per Google row and setting in `configs/models/`, on 2026-11-12:

  | Model | Setting | Result |
  |---|---|---|
  | `gemini-3.5-flash-lite` | `low` | Works, 65 to 83 reasoning tokens on a one word reply |
  | `gemini-3.5-flash-lite` | `minimal` | Works, 0 reasoning tokens |
  | `gemini-3.5-flash-lite` | `none`, which is what `off` sends | 400, invalid argument |
  | `gemini-3.1-pro-preview`, `gemini-4-argon` | Every setting | Free tier quota, with a limit of 0 |
  | `gemini-3.8-flash` | Every setting | A client error after retries, likely the same quota |

- **A 12 round probe of `gemini-3.5-flash-lite` at `low`** on One shock, seed 0, scored 0.52. It used 47,280 tokens, 1853 of them reasoning, and ran code on 11 of 12 rounds.
- **Means.** The key's project has no billing, so the full study's Google rows cannot run. Google may also use free tier prompts to improve its products, so no held-out skin may go through this key. Both runs above played the example skin on a public seed.
- **`minimal` may be the off Flash Lite lacks.** It sent no reasoning token on a one word reply. A 12 round run at `minimal`, as Haiku's off check was, would say whether it holds on a real round.
