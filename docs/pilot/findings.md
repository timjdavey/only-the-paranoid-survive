# Pilot findings

What the pilot has taught us so far, in the order we learned it. Each finding says what we saw, why it matters and what we did about it.

- **The other pilot pages hold the pieces.** [Model findings](model-findings.md) holds what models behind a provider taught us, [decisions](decisions.md) holds each frozen number, [results](results.md) the generated tables and [`TODO.md`](../../TODO.md#pilot) the next steps. This page holds the story that ties them together.
- **Add a finding when a run teaches us something**, scratch or formal. Say the run's settings, so anyone can play it again.
- **Each finding has three parts.** *Saw* is the numbers and the run behind them. *Means* is why it matters. *Did* or *Open* is what changed or what is still to decide.

## Where we are

- **The engine knobs are set and accepted,** see [decisions](decisions.md). Three moved so every scenario is worth reading.
- **The best blind reader sits near the ceiling.** The Bayesian baseline scores 0.93 to 0.98 on No change, One shock and Down switch, and more noise barely touches it.
- **The shape knobs are built and stay off for this pilot.** They make a shock and a switch look alike, and they beat the hedge rule but not the Bayesian baseline.
- **The first model misread the game until one sentence fixed it.** Haiku spread its bets because the frame never said a market's price ignores how much you send. That sentence is now a frame fact in every skin.
- **With that sentence, the game is not too easy for a model.** On Down switch Haiku scores 0.52 and Sonnet 0.60, against the Bayesian baseline's 0.94.
- **Both models lose where the new best rises from the bottom.** They write a channel off after one poor round and never look at it again. Sonnet is no better at this than Haiku.
- **Neither model gives a reason to turn the shape knobs on.** The gain on a switch in the new world was mostly the luck of ten seeds.
- **The provider checks have started.** Jev is run and costs about $0.12 a cell. The rest wait on channel order, where Sonnet slips, and channel order waits on keys that may play a held-out skin, see [model findings](model-findings.md#the-provider-checks-first-results).

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

## Models

The model probes and the provider checks have their own page, [model findings](model-findings.md), so that each page stays short.

## Lessons on method

- **Probe with a cheap model before freezing anything.** A few dollars of Haiku found a frame gap that would have sat under every provider check.
- **Read a model's bet size beside its score.** "All in on its top bet" told reading from bet size in one column. It belongs in the analysis beside the run score.
- **Ask the model why, in a fresh call.** Its reasoning came back encrypted, but asked directly it named the missing fact.
- **Test each half of a fix.** The frame fact should say no more than it needs to, and the half that did nothing also leaned on the patience we measure.
- **Look at what the model sent its points to, not just the score.** The switch loss came from one seed's record: it left the leader for the wrong market and never looked at the right one.
- **Ten seeds show gaps of about 0.1 or more.** That is enough for a probe, not for a decision. Three players on ten seeds could not tell the Bayesian hazards apart either.
- **Judge a knob by score, not by a rate alone.** The tell's hit rate looked bad and cost little.
- **Pairing by seed pairs only what the seed fixes.** Two worlds draw different switches on one seed, so check the draw on the whole seed list first. Then sort runs by what made them hard: where the new best started turned a blurred 0.60 into 0.74 and 0.40.

## Still open

Each is in [`TODO.md`](../../TODO.md#pilot) with its next step.

- **The frame fact in the held-out skins**: merging the private repo's pull request, and whether each wording lands.
- **Looking again at a written off channel**: how the analysis should report it.
- **The shape knobs**, for a later pilot: the two failing bands, with the looking band held, and the hedge rule's tell.
- **A harder game for a patient reader**, such as inertia or a shorter game. Haiku says the game is hard enough for a model, so this is now about the baselines.
- **The noise grid**, and whether it pins a smaller runner-up gap.
