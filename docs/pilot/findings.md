# Pilot findings

What the pilot has taught us so far, in the order we learned it. Each finding says what we saw, why it matters and what we did about it.

- **The other pilot pages hold the pieces.** [Decisions](decisions.md) holds each frozen number, [results](results.md) the generated tables and [`TODO.md`](../../TODO.md#pilot) the next steps. This page holds the story that ties them together.
- **Add a finding when a run teaches us something**, scratch or formal. Say the run's settings, so anyone can play it again.
- **Each finding has three parts.** *Saw* is the numbers and the run behind them. *Means* is why it matters. *Did* or *Open* is what changed or what is still to decide.

## Where we are

- **The engine knobs are set,** as proposals in [decisions](decisions.md). Three moved so every scenario is worth reading.
- **The best blind reader sits near the ceiling.** The Bayesian baseline scores 0.93 to 0.98 on No change, One shock and Down switch, and more noise barely touches it.
- **The shape knobs are built and off.** They make a shock and a switch look alike, and they beat the hedge rule but not the Bayesian baseline.
- **The first model misread the game until one sentence fixed it.** Haiku spread its bets because the frame never said a market's price ignores how much you send.
- **With that sentence, the game is not too easy for a model.** Haiku scores 0.52 on Down switch against the Bayesian baseline's 0.94, because it stops looking and never finds the new best.
- **Haiku gives no reason to turn the shape knobs on.** It does a little worse on a shock in the new world and better on a switch.
- **The provider checks wait** on the frame fact and a decision on the shape knobs.

## The engine pilot

Ten cells on 1000 public seeds, no model. Tables in [results](results.md).

### Three scenarios were not worth reading

- **Saw.** At an onset of rounds 12 to 20, [reachable gain](engine-checks.md#reachable-gain) was under the floor of 0.3 on three of six scenarios. Up switch was 0.14 and Slow drift 0.12.
- **Means.** A scenario where moving at the right time earns little cannot tell a good reader from a stubborn one.
- **Did.** Three knobs moved: onset to rounds 8 to 12, the sleeper's rise to 3 to 6 sigmas, and the drift's fall to 2 to 4 sigmas, was 1 to 3. Every scenario now clears the floor: Down switch 0.60, Switch then shock 0.61, Up switch then down switch 0.48, Shock then switch 0.39, Up switch 0.33, Slow drift 0.31.
- **Open.** Up switch and Slow drift sit just over the floor, so a different seed list could put either under it.

### More noise does not make the game much harder

- **Saw.** Across the [noise grid](engine-checks.md#noise-grid), the hedge rule's Down switch score falls from 0.91 at setting 2 to 0.82 at setting 8. Half way to the Complacent baseline is 0.70, so it never gets there. The Bayesian baseline stays at 0.94 across the whole grid.
- **Means.** The leader falls by the runner-up gap plus the switch size, 12 to 28 points, which shows through any weather the [luck check](engine-checks.md#luck-on-offer) allows. A scratch sweep found luck at 0.28 at setting 12 and 0.5 at 16. A good reader may sit "off the noisy end" at every setting.
- **Did.** Kept the grid at 2, 3, 4, 6 and 8.
- **Open.** Whether the grid pins a smaller runner-up gap, see [`TODO.md`](../../TODO.md#pilot).

### The tell is a weak clue

- **Saw.** [The tell](engine-checks.md#the-tell), the hedge rising while the field falls, stops every alarm on only 0.37 of One shock seeds. No shared-factor scale or threshold set moves that much. It is false on 0.002 of switches.
- **Means.** A miss is cheap: the hedge rule scouts for a round and nearly always comes back, so it scores 0.95 on One shock beside 0.97 on No change. So the check now judges the tell by score, not by a hit rate of nine in ten.
- **Did.** Scale 3 and the hedge rule's thresholds, kept.
- **Open.** A scratch sweep found a hedge loading of −1.0 to −0.6 lifts the hit rate to about 0.6, but the shock cap then bites on 0.41 of shocks against 0.14. Wait for the provider checks to show whether a model reads the tell at all.

### The cheapest look is the best one

- **Saw.** In [reading roughness](engine-checks.md#reading-roughness), at every read noise, the hedge rule's Down switch output falls as its explore bet grows. One scout round earns more than two or three.
- **Means.** No read noise makes a bigger explore bet pay. Looking is worth it only in small doses.
- **Did.** The hedge rule's `explore` and `scout_rounds` went from 2 to 1. Read noise k of 8, kept.

### Three baseline order lines could not hold

- **Saw.** No knob could make three lines of the [baseline order](engine-checks.md#baseline-order) hold. One point on the hedge costs about 0.02 of a scenario score on its own.
- **Did.** Reworded all three:
  - ≈ and ≥ now allow 0.05, not 0.02. At 0.02 the hedge rule could never match the Complacent baseline on No change.
  - In Up switch then down switch the Stayer is the yardstick, as never moving is right once the change undoes itself.
  - On Up switch the hedge rule sits beside the Complacent baseline, not below it, as a false alarm after the rise finds the sleeper.

### The Bayesian baseline is the best blind reader, near the ceiling

- **Saw.** On the [Bayesian frontier](engine-checks.md#bayesian-frontier), a hazard of 0.01 with the `odds` rule has the best headline, 0.937 on the picking half and 0.944 on the reporting half. It is the best blind baseline in every scenario. Its irreducible lag is 0.057.
- **Means.** A benchmark is too easy when its best blind reader sits near 1. This is the first sign the game needs a harder shape.
- **Did.** The hazard went from 0.025 to 0.01. Three players on ten seeds could not tell 0.005 from 0.025, so the cell now plays all five hazards on a hundred seeds.
- **Open.** It joins the scorer's marks, decided and not built.

### Smaller ones

- **The streaks measure reads the run's length.** Rounds until the leader stays below the runner-up went from a median of 3 to 8 when onset moved earlier, as more rounds follow the switch. No persistence makes a three round streak common on No change: 0.10 at 0.8 and at 0.9.
- **The Scout rule's `n` of 3 stays.** An `n` of 5 gains 0.005 on No change and loses 0.03 to 0.05 on every switch.

## The shapes

Why the game is easy, and the shape knobs that try to fix it. Pictures and every measure are in [`shapes/`](../../shapes/README.md).

### A shock and a switch look nothing alike today

- **Saw.** On 1000 public seeds, in today's engine:
  - A shock is a parallel fall. Nine channels fall together and the hedge rises. The leader is overtaken at the trough on 5% of shocks.
  - At onset a switch moves 1.4 channels by more than a sigma and a shock moves 7.1. Three rounds of the field tell them apart every time, an AUC of 1.00.
  - Weather rarely takes the leader off the top: 3% of rounds.
  - The leader often barely falls in a shock. Its own loading is 0.3 to 1.0, so it falls less than three sigmas on 0.32 of shocks.
- **Means.** One look at the field says which it is, and holding through a shock is always safe. Nothing tempts a reader to leave.

### The shape knobs make them alike, and cost a little elsewhere

- **Did.** Built [shape knobs](../design/mechanics.md#shape-knobs), all off by default. The leader falls about as far as a storm is deep, `leader_loading`. Each channel comes back at its own speed, sometimes the leader last. One channel can pop to just under the leader. A switch arrives in a storm, so its first rounds match a shock's on the same seed.
- **Saw.** With the knobs on, 16 of 18 bands are met, see [the test](../../shapes/README.md#the-test). The leader falls less than three sigmas on no shock, and a switch now takes 3 to 8 rounds to change the climate leader, against 0 to 2.
- **Saw, the two that fail.**
  - Calm weather matches a storm's first three rounds on 0.16 of seeds, under the band's 0.2. That is the price of a deeper fall on the leader.
  - Looking barely helps tell a shock from a switch, as the field comes back in both by design. What tells them apart is whether the leader comes back.
- **Saw, the costs.** The shock cap bites on 0.41 of shocks, against 0.14 today. `recovery` had to narrow from 0.5 to 2.0 to 0.5 to 1.5, as a leader that comes back four times slower looks like a switch too long.

### The new shapes beat a rule, not a reader

- **Saw.** [Two readers](../../shapes/README.md#two-readers) on 100 seeds, scores on No change, One shock and Down switch:

  | Reader | Today | New |
  |---|---|---|
  | Hedge rule | 0.96, 0.95, 0.91 | 0.96, 0.89, 0.75 |
  | Bayesian at 0.01 | 0.97, 0.96, 0.94 | 0.97, 0.94, 0.93 |

- **Means.** A shock costs the Bayesian baseline 0.02 to 0.04 in the new world, against 0.01 to 0.02 today. A storm switch delays the fall by about four rounds out of 40, so waiting is nearly free. The hedge rule loses more, as its tell no longer works.
- **Open.** What would make a shock tempt a patient reader to move, such as [inertia](provider-checks.md#inertia) or a shorter game. And turning the knobs on, see [`TODO.md`](../../TODO.md#pilot).

## Timestral, first numbers

A smoke test of the real Timestral at its pins, ahead of the [Timestral checks](provider-checks.md#timestral-checks). The full numbers are in [`TODO.md`](../../TODO.md#pilot).

- **Its spread widens over blanks, but not round by round.** After thirty blanks it is 2.1 to 3.0 times wider with the channels joint. Whether that is enough for Timestral odds is open.
- **It is deterministic**, so the cache keys on the inputs alone.
- **Odds rounded out on every round of every run, 468 of 468,** so `rounded_out` is now a count of channels, not a yes or no.
- **Four seeds are too few to rank the policies.** Top pick scored 0.85 against the hedge rule's 0.88.

## The first model: Haiku 5.5

A scratch probe of `claude-haiku-5-5` on the example skin, before any formal provider check. Every run used public seeds 0 to 9, `low` reasoning, notes and compute on. "Today" is the engine's defaults, "new" is the shape knobs on at the values in [`shapes/src/worlds.py`](../../shapes/src/worlds.py). The probe's scripts and logs were scratch and are not kept, so the settings here are what you need to play it again.

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
- **Open.** Agree the wording, then add it to [what every skin must say](../harness/prompts.md#what-every-skin-must-say), the lint's [frame facts](../specs/skins/lint.md#frame-facts), the example skin and the five held-out skins, each in its own words. That changes the frame, so it must land before the pilot freezes it.
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
- **The new world's switch is also kinder in itself.** The Complacent baseline scores 0.60 there, against 0.42 today.
- **Means.** None of the outcomes we planned for fits. The knobs neither tempt Haiku off the leader in a shock nor make a switch harder to read. Haiku gives no reason to turn them on.
- **Limits.** One model, one skin, `low` reasoning and ten seeds, so gaps under about 0.1 can't be read.
- **Open.** Whether a stronger model finds the new best without the storm's help. Ten Sonnet 5.5 runs on Down switch in each world would cost about $10 at list prices. Until then the knobs stay off and the engine rows in [decisions](decisions.md) stay proposals.

### Cost

- **About $4.40 at list prices** for the whole probe. The rerun with the price half was about $1.90 of that.
- **Every run was on the Anthropic OAuth token**, so it drew on the plan, not a bill. Only public seeds and the example skin were played, so nothing held-out left the machine.

## Lessons on method

- **Probe with a cheap model before freezing anything.** A few dollars of Haiku found a frame gap that would have sat under every provider check.
- **Read a model's bet size beside its score.** "All in on its top bet" told reading from bet size in one column. It belongs in the analysis beside the run score.
- **Ask the model why, in a fresh call.** Its reasoning came back encrypted, but asked directly it named the missing fact.
- **Test each half of a fix.** The frame fact should say no more than it needs to, and the half that did nothing also leaned on the patience we measure.
- **Look at what the model sent its points to, not just the score.** The switch loss came from one seed's record: it left the leader for the wrong market and never looked at the right one.
- **Ten seeds show gaps of about 0.1 or more.** That is enough for a probe, not for a decision. Three players on ten seeds could not tell the Bayesian hazards apart either.
- **Judge a knob by score, not by a rate alone.** The tell's hit rate looked bad and cost little.

## Still open

Each is in [`TODO.md`](../../TODO.md#pilot) with its next step.

- **The frame fact**: the price half as its wording, and writing it into the prompts page, the lint and every skin.
- **A stronger model on Down switch** in both worlds, before any knob decision.
- **The shape knobs**: whether to turn them on, the two failing bands, with the looking band held, and reworking the hedge rule's tell.
- **A harder game for a patient reader**, such as inertia or a shorter game. Haiku says the game is hard enough for a model, so this is now about the baselines.
- **The noise grid**, and whether it pins a smaller runner-up gap.
