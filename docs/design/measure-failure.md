# Failure measures

**When a model scores below the reference bot, this page says which rounds the output went missing in and what the model was doing at the time.**

[Performance](measure-headline.md#performance-the-proof-of-concept-headline) says how much of the gain on offer a model took. If a model took 60% of it, this page is the stack trace for the other 40%. Every measure here is in the same unit as performance, a share of the reference bot's gain, so the pieces add up to the whole.

## In brief

Each model plays the game on a set of seeds, counted in [runs-and-cost.md](../spec/runs-and-cost.md). A seed fixes one setup. It sets the dice and the weather, the record the model reads before it starts, and the rounds on which the change and the dip begin. On each seed the model plays one run where nothing changes, and runs where one unit quietly stops paying as well and a unit the model has never funded starts to pay better. We call these the no-change run and the change runs.

The no-change run holds a trap. On the same round and the same unit as the change, it has a dip, a fall that recovers on its own after a few rounds. So for the first rounds the two runs look the same, and a model cannot tell them apart until the evidence builds.

Every run is measured against the reference bot, the best player we can build. Output is scored a round at a time, on what the model's split was worth at the true rates with the luck left out. So any gap between a model and the bot can be dated to a round.

## Where the output went

The gap between a model and the reference bot is output the model did not win, and each round of it can be dated. Two rounds on every seed are fixed before any model plays: the round the change starts and the round the dip starts. Cutting each run's rounds at those two moments sorts every lost round into one of three leaks. We call them the doubt tax, the change leak and the false alarm leak.

Each leak is a share of the reference bot's gain, the same denominator as performance. So performance plus the three leaks equals 1.

| Leak | Rounds it is read from | What it tells you |
|---|---|---|
| **Doubt tax** | The change runs before the change starts, and the no-change run before the dip starts | How much output went on doubting notes that were still working |
| **Change leak** | The change runs from the change start to the end | How much output was lost once the world had changed. Waiting too long, moving to the wrong unit, moving too little, and moving then moving back all land here |
| **False alarm leak** | The no-change run from the dip start to the end | How much output was lost by moving on a dip, and by taking a long time to move back |

- **The cuts belong to the seed, not the model.** The change start and the dip start are fixed per seed, so the split is exact and claims nothing about when the model noticed. A model that waited and a model that moved too little both land in the change leak. The readings under it say which happened.
- **We wanted four leaks**, with the change leak split into waiting and acting badly. That split needs the round the model switched, and there is no such round. Suspicion grows a little each round, and a model that eases in crosses any switch rule late. So we took three, because no measure beats an inaccurate one. See [Why three leaks, not four](decisions.md#why-three-leaks-not-four).
- **A leak can be negative.** If the model beat the reference bot in that stretch, the leak shows it as a gain.
- **The doubt tax is read from three runs a seed, not one.** Before the change starts, a change run is the same world as the no-change run on the same dice. So the rounds before the change count in every run.

## What the agent did

Each leak carries a few readings of what the model did in those rounds, to explain the leak. None of them is a score. Each one is read from the log by a rule, with no judge.

### Under the doubt tax

Did the model learn what normal looks like, and did it look at the right rate?

- **The briefing read.** Before round 1 the model reads a record of 200 rounds played by the previous operator and writes its own notes on how to split and why. We check those notes with a string match for four things. Do they state the split the record ends on? Do they name the units outside that split and their rates? Do they mention the changes the previous operator caught and moved for? And do they say that a bad stretch is ordinary? A model whose notes miss that last point will look jumpy later, and this reading is the only way to tell that apart from a jumpy temperament.
- **Say and do at round 1.** We compare the first split the model plays with the split its notes said it would play. A model that writes one plan and plays another has told us something before any evidence has arrived.
- **Looking and experimenting, split by target.** Looking is how many times a round the model reads the record. Experimenting is the share of the budget it puts on units the standing split leaves out. We split that share by where it went. C0 is the one unit that could matter. The D and E units are red herrings that never change in any run. Doubt aimed at the right unit is cheap. Doubt sprayed across the red herrings is the expensive kind.

### Under the change leak

Why was output lost once the world had changed? We sort every change run into one bucket by how far the model got, and report the counts as a funnel.

| Bucket | What places a run there |
|---|---|
| Never doubted | No experiment before the round the reference bot moved |
| Doubted the wrong thing | Experimented, but never put C0 above the threshold |
| Looked too small to hear | Put C0 above the threshold, but at too small a volume to tell its new rate from its old one |
| Found it | Put C0 above the threshold at a volume that could tell them apart |

The threshold is the share below which a unit buys no volume and reports nothing. How much volume is enough to tell C0's old rate of 0.55 from its new one is fixed in [next step 1](../../TODO.md#next-steps).

Beside the funnel sit six more readings.

- **Which unit.** Where the largest share on side 0 ended up: on C0, on B0, or spread about. Each kind of unit, A to E, has one unit on each of two sides. The change happens on side 0 only. Moving share from A0 to B0, a unit the notes already favoured, is a retune. Finding C0, a unit the notes ignored, is a rethink. The retune bot is the reference bot with the two sides pooled, so it can only retune. The output between it and the reference bot is what rethinking was worth.
- **How full.** The model's share on C0 against the reference bot's, round by round. A slow creep and a timid hold both show up here.
- **Side spillover.** Share moved on side 1, where nothing changed. A model that over-generalised the rule to "C now leads everywhere" pays here.
- **Reversals.** Whether the model moved and then moved back, and what each reversal cost in output.
- **The notes.** Whether the rewritten notes state the new rule in the nouns of the skin the game is dressed in, such as "on side 0, C now leads". We also read the round the notes changed against the round the shares changed. A model that writes the new rule and does not play it is the Kodak case below. The reverse, playing the new rule without writing it, is a guess that paid.
- **Rounds and the CUSUM line**, for runs with a clean switch only. The plain reading is the number of rounds from the change start to the round the model moved. Beside it sits a reading in units of evidence. Picture a detector that adds up how much each round's result favours a shifted rate over the old one. It fires when the total crosses a line. That is the textbook change detector, called CUSUM, and ours is fed the weather model so a dip adds little to the total. The height of the line that would have fired on the round the model moved is how much evidence the model demanded, in the same unit for every run. A model that eased in has no clean switch, so it reads from "how full" instead.

### Under the false alarm leak

Did the model back down?

- **Moved during the dip.** The share it moved off the dipping unit in the rounds where the dip and the change still look the same. The reference bot moves a little and looks.
- **Recovery.** How many rounds passed from the dip recovering to the model restoring the standing split, against the reference bot.
- **Notes churn.** Whether the notes were rewritten for the dip and then rewritten back, or left stating a rule the shares no longer follow.

## Diagnostics

These say nothing about where output went. They sit beside the scores to help explain them.

| Diagnostic | What it shows |
|---|---|
| **Anchoring** | Whether a longer record slows the model more than it slows the reference bot |
| **Skin and history spread** | How far each number moves across the four skins and the two styles of record |
| **Tool use** | How often it calls `compute`, and whether runs that use it score better |
| **Test awareness** | How often its reasoning says it is being tested, or that the rules may change, before there is any evidence |
| **Dollar cost** | API spend per run, in its own column |

Anchoring is measured once, by varying the record's length. The skin and history spread come from the pilot. Test awareness is a lower bound, since a model can register a test without saying so. Dollar cost is not a measure of skill.

## A profile, not a ranking

Two of the leaks place a model in one of four boxes. The change leak says whether it caught the change. The doubt tax and the false alarm leak together say whether it paid for doubt along the way.

| | Small change leak | Large change leak |
|---|---|---|
| **Small doubt tax and false alarm leak** | The target | Complacent, or knows and doesn't act |
| **Large doubt tax or false alarm leak** | Nervy but right | Jumpy and wrong |

The companies in the README illustrate the boxes. Blockbuster, which turned Netflix down, was complacent. Kodak, which built the digital camera and kept selling film, knew and did not act. The notes reading tells those two apart, because Kodak's notes would state the new rule and its shares would not follow. Shopify and Hopin, which bet on a COVID change that reversed, were jumpy and wrong. The companies are illustrations, not evidence that any model behaves like them.

Here is a made up results table for two models. The top block is what the proof of concept reports, and the bottom block is what the full study adds.

| | Model P | Model Q | Reference bot |
|---|---|---|---|
| Performance | 0.62 | 0.41 | 1 |
| Doubt tax | 0.08 | 0.01 | 0 |
| Change leak | 0.25 | 0.55 | 0 |
| False alarm leak | 0.05 | 0.03 | 0 |
| Funnel, 40 change runs | 2 never doubted, 6 too small, 32 found it | 14 never doubted, 10 wrong thing, 16 found it | 40 found it |
| Notes state the new rule | 30 of 32 | 12 of 16 | n/a |
| Discernment at 50%, bits a round | 0.15 | 0.40 | Off the left end |
| Discernment at 80%, bits a round | 0.35 | Off the right end | Off the left end |
| Catch rate, half caught, bits a round | 0.18 | 0.45 | 0.05 |

Model P took 62% of the gain on offer, and the three leaks say where the other 38% went. It doubts working notes and pays a little for that, but it finds the change in most runs, so it is nervy but right. Model Q is calm and loses most of its gain after the change starts. A third of its runs never doubted, so it is complacent.

Here is a made up log from one change run of 12 points, showing the two side 0 units that matter. The other eight units stay at the standing split throughout. C0 is dark, meaning it reports nothing, until the model funds it above the threshold. Yield is shown as the count won out of the volume bought, and the note on each row says which reading it feeds.

    Round  A0                  C0                  Output
    3      25%   27 of 43      0     dark          118
    6      25%   26 of 43      0     dark          117   the change starts, unseen. The doubt tax ends here
    9      25%   23 of 43      0     dark          114   two bad weeks on A0, ordinary weather or the ramp
    12     25%   22 of 43      0     dark          113   the no-change run has matched until here
    13     20%   18 of 36      5%    8 of 10       114   a look at C0, aimed at the right unit
    19     8%    9 of 15       22%   32 of 39      121   a clean switch, so the CUSUM line is read here
    19     rewrites the notes: "on side 0, C now leads"             the notes reading, same round as the shares
    20     8%    8 of 15       22%   33 of 39      122   side 1 stays on A and B, so no spillover
    21 to 40   C leads on side 0 and A and B on side 1 in 19 of 20 rounds   found it, and nearly as full as the bot
