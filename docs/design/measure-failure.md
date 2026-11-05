# Failure measures

[Performance](measure-headline.md#performance-the-proof-of-concept-headline) says how much of the gain on offer a model took. The measures we design here are like a stack trace, enabling us to work out where the model went wrong if it did so. Each trace is in the same currency as performance, so the pieces add up to the whole.

## Where the output went

The gap between a model and the reference bot is output, and output is scored a round at a time. Cut each run's rounds at the moments the seed fixes, the change start and the dip start, and the gap falls into three leaks. Each is a share of the reference bot's gain, the same denominator as [performance](measure-headline.md#performance-the-proof-of-concept-headline), so performance plus the three leaks equals 1.

| Leak | Rounds it is read in | What it says | Old names it absorbs |
|---|---|---|---|
| **Doubt tax** | The change runs before the change starts, and the no-change run before the dip | Output spent doubting notes that were working | Paranoia's rates, hedging, calibration, curiosity |
| **Change leak** | The change runs from the change start to the end | Output lost once the world had changed, whether by waiting, moving to the wrong unit, moving too little, or moving and moving back | Caution, conviction, insight |
| **False alarm leak** | The no-change run from the dip onwards | Output lost by moving on a dip, and by taking long to come back | Paranoia's dip reading, steadiness |

- **The cuts are the seed's, never the model's.** The change start and the dip start are fixed per seed, so the partition is exact and claims nothing about when the model noticed. Waiting and timidity both land in the change leak, and the readings under it say which happened.
- **We wanted four leaks**, with the change leak split into waiting and acting badly. That split needs the round the model switched, and there is no such round, so we took three. No measure beats an inaccurate one. See [Why three leaks, not four](decisions.md#why-three-leaks-not-four).
- **A leak can be negative** where the model beat the reference bot in that stretch.
- **The doubt tax reads from three runs a seed**, not one. Before the change starts, a change run is the same world as the no-change run on the same dice.

## What the agent did

Each leak carries a few readings of behaviour that explain it. None is a score, and each comes from the log without a judge.

### Under the doubt tax

Did it learn what normal looks like, and look at the right rate?

- **The briefing read.** A string check of the notes it wrote at the briefing for four things: the standing split, the second rate units by name, the resolved changes in the record, and that a bad stretch is ordinary. A model whose notes miss the weather will look jumpy later, and this is the only way to tell that apart from a jumpy temperament.
- **Say and do at round 1.** Whether its first split matches the split its notes said.
- **Looking and experimenting**, split by target. Record reads a round, and the share a round put on units beyond the standing split: on C0, which could matter, against D and E, the red herrings. Doubt aimed at the right unit is cheap. Doubt sprayed across the red herrings is the expensive kind.

### Under the change leak

Why was output lost once the world had changed? Each change run goes in one bucket, and the funnel is reported.

| Bucket | What places a run there |
|---|---|
| Never doubted | No experiment before the round the reference bot moved |
| Doubted the wrong thing | Experimented, but never funded C0 above the threshold |
| Looked too small to hear | Funded C0, but at a volume that couldn't tell 0.55 from the new level in the rounds it held. The rule is fixed in [next step 1](../../TODO.md#next-steps) |
| Found it | Funded C0 at a volume that could |

Beside the funnel:

- **Which unit.** Where the largest share on side 0 ended: on C0, on B0, or spread. Moving A0's share to B0 is a retune. Finding C0 is a rethink. The retune bot, the reference bot with sides pooled, can only retune, and the output between it and the reference bot is what rethinking was worth.
- **How full.** Its share on C0 against the reference bot's, round by round. A slow creep and a timid hold both show here.
- **Side spillover.** Share moved on side 1, where nothing changed. A model that over-generalised the rule to "C now leads everywhere" pays here.
- **Reversals.** Moved and moved back, and the output each cost.
- **The notes.** Whether the rewritten notes state the new rule, such as "on side 0, C now leads", in the skin's nouns, and the round they changed against the round the shares did. A model that says the new rule and doesn't play it is the Kodak case. The reverse is a guess that paid.
- **Rounds and the CUSUM line**, for runs with a clean switch only. The CUSUM bot is the textbook change detector, fed the weather model so a dip adds little. It sums how much each round favours a shifted level over the old one, and fires when the sum crosses a line. The height of the line that would fire on the round the model moved is how much evidence it demanded, in the same unit for every run. Rounds from the change start sit beside it because anyone can read them. A model that eased in has no clean switch, and reads from "how full" instead.

### Under the false alarm leak

Did it back down?

- **Moved during the dip.** The share it moved off the dipping unit in the rounds where the dip is the change, as far as the agent can tell. The reference bot moves a little and looks.
- **Recovery.** Rounds from the dip recovering to the model restoring the standing split, against the reference bot.
- **Notes churn.** Whether the notes were rewritten for the dip and then rewritten back, or left stating a rule the shares no longer follow.

## Diagnostics

These say nothing about where output went, and sit beside the scores.

| Diagnostic | What it shows |
|---|---|
| **Anchoring** | Whether a longer record slows it more than it slows the reference bot. Measured once, by varying the record's length |
| **Skin and history spread** | How far each number moves across the four skins and the two history styles, from the pilot |
| **Tool use** | How often it calls `compute`, and whether runs that use it score better |
| **Test awareness** | How often its reasoning says it is being tested, or that the rules may change, before there is any evidence. A lower bound |
| **Dollar cost** | API spend per run, in its own column. Not a measure of skill |

## A profile, not a ranking

Two leaks place a model in one of four boxes.

| | Small change leak | Large change leak |
|---|---|---|
| **Small doubt tax and false alarm leak** | The target | Complacent, like Blockbuster, which turned Netflix down. Or knows and doesn't act, like Kodak, which built the digital camera. The notes reading tells them apart |
| **Large doubt tax or false alarm leak** | Nervy but right. It pays for its doubt and still catches the change | Jumpy and wrong, like Shopify and Hopin after COVID |

The companies illustrate each box. They are not evidence that a model behaves like them.

A made up results table. The top block is what the proof of concept reports, and the bottom block what the full study adds:

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

Model P took 62% of the gain on offer, and the three leaks say where the other 38% went. It doubts working notes and pays a little for it, but it finds the change in most runs, so it is nervy but right. Model Q is calm and loses most of its gain after the change starts, and a third of its runs never doubted, so it is complacent.

A made up log from one 12 point change run, showing the two side 0 units that matter. The other eight stay at the standing split throughout, and C0 is dark until the agent funds it. Yield is shown as won out of volume bought.

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
