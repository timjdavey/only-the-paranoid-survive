# Prior work

Our game asks one question. When results drop, is it a shock that will pass or a switch to a new normal? Hold on through a switch and you are Kodak. Jump at a shock and you are Peloton. The [motivation](../../README.md#motivation) tells the Intel story behind it.

These pages collect what others have found on that question, in LLMs, in people and in animals. Start here for the big picture, then dip into a page for the detail on any one study.

| Page | What's in it |
|---|---|
| [Worlds that change](worlds-that-change.md) | Agent benchmarks where the world moves under the agent |
| [Learning from results](learning-from-results.md) | How LLMs learn from noisy results, in bandits and belief tasks |
| [A past in the prompt](past-in-the-prompt.md) | What a record, notes or a plan in the prompt does to a model |
| [People, and ideal observers](people.md) | Studies of people and rats, and the maths of spotting a change |
| [Measuring agents](measuring-agents.md) | METR's time horizon, and studies of models that suspect a test |
| [Themes](themes.md) | Bigger open questions about agents that this game speaks to |

## What the literature says

- **Models fail both ways.** Some studies find them too slow to let go of an old option. Others find them pulled hard by the latest result. Often the same model does both. See [which way do models fail](#which-way-do-models-fail).
- **Most studies only count being late.** A false alarm is left out of the score or can't happen at all.
- **Bad luck almost never comes in streaks.** Nearly every study draws each result fresh, so three bad rounds in a row are strong evidence. Only STOCKTAKE has a false alarm that looks real for a while.
- **The old plan usually stops working outright.** Once the change lands, the old option loses or fails. Real businesses rarely get that clear a signal.
- **Warning the agent changes everything.** One line in the prompt saying "switch when a tool fails" moved one model from 0.14 to 0.86 ([Set-shifting](worlds-that-change.md#set-shifting-2026-tool-groups-that-stop-working)). Many studies give that warning.

## How our game differs

If you know the field, our game may look like a drifting bandit: an agent picks between options whose payoffs wander, as in [Zhang et al. 2025](learning-from-results.md#zhang-et-al-2025-llms-in-a-drifting-bandit). It looks like that, but no study below has all of these.

- **Both mistakes cost.** The No change and One shock scenarios sit in the same headline as the Down switch and Slow drift scenarios. The weakest trait is reported beside the headline, so a model can't hide false alarms behind quick switches ([scoring](../design/scoring.md#how-we-score)).
- **Bad luck comes in streaks, and the whole market has bad weeks.** Each channel's weather has persistence, so a bad stretch fades rather than stops. A shared factor moves every channel at once ([generator](../design/mechanics.md#each-round)).
- **An explore bet costs, and an explore bet tells a shock from a switch.** The agent sees only the channels it bets on, and a small bet gives a rough reading. A shock moves every channel and lifts the hedge. A switch moves one. So a small bet on the field, or the hedge, settles which it is ([what the agent sees](../design/mechanics.md#what-the-agent-sees), [events](../design/mechanics.md#events)).
- **The old plan keeps paying.** After a switch the leader is still well above zero. Staying put costs a little every round, not everything at once. That is Grove's case, not Blockbuster's.
- **Nothing tells the agent the world might change.** No prompt, story or tool mentions it ([interface](../design/interface.md#how-the-agent-plays)).
- **A right lesson can go wrong.** In the Shock then switch scenario, an agent that rightly held through the shock has learnt "dips recover", and is primed to miss the real change ([scenarios](../design/scenarios.md#scenarios-we-test)).

## Studies where the world changes

Studies where nothing changes are on their own pages.

| Study | Setting | Change | Old plan still pays? | Feedback | Told change may come? | Scored against | Does a false alarm cost? |
|---|---|---|---|---|---|---|---|
| [Wang, Ward and Zhang 2026](learning-from-results.md#wang-ward-and-zhang-2026-reversal-learning) | Two options that swap, LLMs | Many swaps | No, the old option wins 20% | Noisy | Yes | People | No, a switch after a loss counts as good |
| [Gupta et al. 2025](learning-from-results.md#gupta-et-al-2025-coin-flips-and-bayes) | Coin flips, beliefs only | Down switch, in one experiment | No, 75% heads becomes 25% | Noisy | No | Beta posterior | n/a |
| [Zhang et al. 2025](learning-from-results.md#zhang-et-al-2025-llms-in-a-drifting-bandit) | Four-armed bandit, LLMs and people | Every arm drifts all the time | Partly, a good arm fades rather than fails | Noisy | Not stated | People, and fitted exploration models | No |
| [Zhang, Yang and Wang 2025](learning-from-results.md#zhang-yang-and-wang-2025-discounted-bayesian-filters) | Die rolls and samples, beliefs only | One change | No | Noisy | No | Discounted Bayesian filter | n/a |
| [Set-shifting 2026](worlds-that-change.md#set-shifting-2026-tool-groups-that-stop-working) | Tool groups in an agent harness | Up to 3 silent shifts | No, old tools always fail | Exact | No, except one arm | Task success | Hardly, one failed call reveals the change |
| [AdaExploreBench 2026](worlds-that-change.md#adaexplorebench-2026-hidden-rules-that-drift) | Hidden decision rules | One drift | No, accuracy falls 27 points | Exact | Yes, "may or may not change" | Oracle that knows the rule | No |
| [STOCKTAKE 2026](worlds-that-change.md#stocktake-2026-a-fair-oracle-for-supply-chains) | 26 week supply chain | Six hidden factors drift | Partly, the supplier degrades by bands | Noisy, with a week-long false alarm | Not stated | Bayes filter on the agent's own view | No, calm-week overreactions are left out |
| [KellyBench 2026](worlds-that-change.md#kellybench-grady-et-al-2026-a-season-of-football-bets) | A season of football bets | The real season | Unclear, no model had an edge | Noisy | Not stated | Bankroll, people and an expert rubric | Not separately |
| [Bazaar 2026](worlds-that-change.md#bazaar-ahmed-et-al-2026-pricing-when-customers-tastes-swap) | Pricing for hidden customers | Half the customers swap tastes once | No, the old offer loses | Partial, the winning offer only | No | Oracle that knows each customer | No, unchanged customers get no result |
| [CoffeeBench 2026](worlds-that-change.md#coffeebench-sugiura-et-al-2026-a-coffee-supply-chain-with-a-demand-surge) | A coffee supply chain | A demand surge that passes | n/a | Market results | Yes, the dates are in the prompt | Net income, no oracle | No |
| [Allen and McDonald 2026](worlds-that-change.md#allen-and-mcdonald-2026-a-strategy-class-simulation) | Business school strategy game | The core business declines, a new one grows | Yes, the core still earns | Scripted, the same every run | No | MBA students | No |
| [Goel et al. 2026](worlds-that-change.md#goel-et-al-2026-a-teammate-who-switches-tasks) | Kitchen game with a teammate | The teammate switches tasks | No, the stale task is wasted | The teammate's moves | n/a | A replanning agent, RL agents | Only as extra replans |
| [Haq et al. 2025](worlds-that-change.md#haq-et-al-2025-mental-sets-in-llms) | 12 arithmetic problems | Problem type switches | Yes, the long method still works | Exact | No | Nothing | n/a |
| [Behrens et al. 2007](people.md#behrens-et-al-2007-people-learn-faster-when-the-world-is-volatile) | People, blue or green | Many swaps | No | Noisy | No | Hierarchical Bayesian learner | Stable phase reported |
| [Bleser et al. 2026](people.md#bleser-et-al-2026-true-and-false-beliefs-about-volatility) | People, told the rule will or won't change | One flip per block | No | Noisy | Yes, half the time falsely | Fitted learning rates | Yes, stable blocks reported |
| [Massey and Wu 2005](people.md#massey-and-wu-2005-system-neglect) | People, spotting a switch | At most one shift | n/a, beliefs only | Noisy | Yes | Bayesian posterior | Yes, overreaction is a finding |
| [Brown and Steyvers 2009](people.md#brown-and-steyvers-2009-naming-a-change-versus-predicting-through-it) | People, a hidden source that jumps | Many jumps | No | Noisy | Not stated | Particle filter fits | No |
| [Gallistel et al. 2001](people.md#gallistel-et-al-2001-rats-that-have-seen-no-change) | Rats, two levers | The reward ratio jumps | No | Noisy | n/a | Ideal detector | No |
| [Nassar et al. 2010](people.md#nassar-et-al-2010-a-learning-rate-that-rises-with-surprise) | People, predicting the next number | The mean jumps | No | Noisy | Yes | Reduced Bayesian learner | Yes, through prediction error |
| [Gallistel et al. 2014](people.md#gallistel-et-al-2014-step-hold-and-take-it-back) | People, tracking a hidden share | The odds jump rarely | No | Noisy | Yes | Their own model | Yes, false alarm rates reported |
| **Our game** | Bets of 100 points across ten channels | A shock, switch or drift, alone or in a row | Yes, the leader stays well above zero | Noisy and streaky, only on channels bet on, rougher on small bets | No | Discerning baseline above, Uniform baseline below, Complacent and Perfect baselines as marks, on the same seeds | Yes, the No change and One shock scenarios are in the headline |

### The closest studies

- **STOCKTAKE is closest in method.** Every player faces the same event tape, and it has a false alarm that looks real for a week, much like a shock. Its yardstick sees only what the agent sees, which makes it depend on what the agent chose to explore. Ours, the [Discerning baseline](../design/baselines.md#fixed-baselines), knows the climate but not the weather, so it is the same for every player and reachable in expectation.
- **AdaExploreBench is closest in design.** One silent change, and a score that runs from a floor to a ceiling. Theirs is all-knowing. Ours, the Discerning baseline, knows the climate but not the weather.
- **Set-shifting is the only one with a matched no-change copy** of every run. It reports that copy beside the score, not inside it. Our No change and One shock scenarios are inside the headline.

## Which way do models fail?

Most studies only count being too slow. Wang counts a switch after a loss as good. STOCKTAKE leaves calm-week overreactions out of every score. AdaExploreBench doesn't count false alarms. Yet the studies disagree about which way models fail.

- **Too slow.** Wang finds models rarely switch after a loss. Set-shifting finds many lock into one routine. Bazaar's fastest learners adapted worst after the change.
- **Too jumpy.** Gupta finds some models forget after a couple of flips. [Kumaran](past-in-the-prompt.md#kumaran-et-al-2025-whose-first-answer-it-was) finds they give too much weight to advice that disagrees with them. [Horowitz and Plonsky](learning-from-results.md#horowitz-and-plonsky-2025-a-pull-towards-the-latest-result) find a strong pull towards the latest result.

People research offers a way to predict the direction. Massey and Wu find people overreact when the world is stable and the signals are noisy, and underreact when it is changeable and the signals are precise. The No change and One shock scenarios are the first case. A switch at low noise is the second. Because every scenario feeds the headline, our score settles which way each model leans.

## Where each study bears on the design

| Part of the design | Studies |
|---|---|
| [Weather with persistence](../design/mechanics.md#each-round) | STOCKTAKE, Zhang 2025, Massey and Wu, Horowitz and Plonsky |
| [Shock or switch, the shared factor and the hedge](../design/mechanics.md#events) | Mellor and Shapiro (all arms switch or one), Schmied (trying every arm once), Zhang 2025, AdaExploreBench |
| [The old plan keeps paying](../design/mechanics.md#events) | Allen and McDonald, STOCKTAKE, Zhang 2025, Haq. The opposite: Wang, Set-shifting, Bazaar |
| [An explore bet costs](../design/mechanics.md#what-the-agent-sees) | BanditBench, Krishnamurthy, Zhang 2025, Horowitz and Plonsky |
| [Linear payout](../design/mechanics.md#payout) and [no bankroll](../design/interface.md#rejected) | KellyBench, Haghani and Dewey |
| [Bets are belief](../design/interface.md#how-the-agent-plays) | Gallistel 2014 (step and hold) |
| [Nothing tells the agent](../design/interface.md#how-the-agent-plays) | Set-shifting, AdaExploreBench, Wang, Bleser, Nassar |
| [Not asking for a chance of change](../design/interface.md#rejected) | Brown and Steyvers, Bleser, STALE, Goel, STOCKTAKE, Schmied |
| [A fresh call each round, record in the prompt](../design/interface.md#tools) | Self-Correction Illusion, IBIS, Kumaran, Schubert, Barkett, Horowitz and Plonsky |
| [No change and One shock scenarios](../design/scenarios.md#scenarios-we-test) | Massey and Wu, Nassar, Haghani and Dewey, Gupta, Kumaran |
| [Shock then switch scenario](../design/scenarios.md#scenarios-we-test) | Gallistel 2001, Behrens, Wilson, Coda-Forno, Bazaar |
| [Switch then shock scenario](../design/scenarios.md#scenarios-we-test) | Gallistel 2014 (taking it back), Schubert (own choices), Bazaar (revision) |
| [Up switch then down switch scenario](../design/scenarios.md#scenarios-we-test) | Set-shifting (going back), Gama (recurring drift) |
| [Scenarios we skip](../design/scenarios.md#scenarios-we-skip) | Behrens, Wang |
| [Score from a floor to a ceiling on the same seeds](../design/scoring.md#how-we-score) | AdaExploreBench, STOCKTAKE |
| [Pairing models by seed](../design/scoring.md#error-bars) | METR (correlated errors), STOCKTAKE (event tape) |
| [Fixed baselines](../design/baselines.md#fixed-baselines) | BanditBench, Bazaar (Thompson sampling) |
| [Bayesian baseline, parked](../design/baselines.md#not-yet) | Adams and MacKay, Wilson, Mellor and Shapiro, Nassar, Gallistel 2014 |
| [Notepad and compute](../pilot/provider-checks.md#notepad-and-compute) | Liu, ACE, Fork-and-Flush, Bazaar, Krishnamurthy |
| [Warm-up record](../../TODO.md#pilot) | BanditBench (example runs), Coda-Forno, Schmied (frequency bias), Fork-and-Flush |
| [Reasoning setting](../harness/models.md#reasoning) | Mazaheri, Ge, Schmied, Zhang 2025 |
| [Skins and contamination](../harness/contamination.md) | Allen and McDonald (masking), Needham, Schoen, Heidari |

## Ideas we parked

Some studies mattered most to ideas the design has since dropped or parked. They stay here in case those ideas come back.

| Idea | Where it stands | Studies |
|---|---|---|
| Ask the agent how likely a change is | Rejected, as it tells the agent change is the question ([interface](../design/interface.md#rejected)) | STALE, Goel, STOCKTAKE, Schmied, KellyBench, Bleser, Brown and Steyvers |
| Hand the agent a plan written by someone else | Not in the design. The record is the agent's own play | Kumaran, Barkett, Fresh Memory Stale Plans, STALE, Self-Correction Illusion, Ge, ACE |
| Let the agent keep notes | Out of the headline, tried in the [pilot](../pilot/provider-checks.md#notepad-and-compute) | Liu, ACE, Fork-and-Flush, Bazaar |
| A cost to switch | A conversion fee is rejected ([interface](../design/interface.md#rejected)). A cap on moves is the [inertia](../pilot/provider-checks.md#inertia) extension | Barkett, KellyBench |
| A second game | A controller with feedback is kept as a second game ([interface](../design/interface.md#rejected)) | STOCKTAKE, Bazaar, CoffeeBench, Allen and McDonald |
| A human baseline | Not in the design | Behrens, Bleser, Wang, Haghani and Dewey, Zhang 2025, Allen and McDonald |

## Gaps

- **Not yet read in full.** Massey and Wu, Brown and Steyvers, Gallistel 2001 and the Kumaran journal version.
- **Claude system cards.** What happened when the Sonnet 4.5 card suppressed eval awareness (sections 7.6.4 and 7.6.5) is unread, and so are later cards.
- **Reward hacking.** The [themes table](themes.md) links METR's, Anthropic's and Epoch's reports, but we haven't reviewed that literature.
- **Noise with persistence.** Apart from STOCKTAKE's one week-long false alarm, every study here draws each result fresh. Whether models tell a bad stretch from a change, when the noise itself has stretches, looks open.
- **A shared factor.** No LLM study we found has a market-wide bad week, where an explore bet on other options tells you the dip is everyone's.
- **A record from someone else.** BanditBench's example runs are the only test we found of a past that shows how to play. Whether a model copies the habits of a record it reads is untested. The [warm-up cell](../../TODO.md#pilot) is a first look.
- **Forecasters as agents.** We read nothing on time-series models like Timestral, or on Jev, making decisions. Their [providers](../design/interface.md#models-that-cannot-place-bets) rest on the design alone.
- **Base rates.** No study here measures how often a dip turns out to be a switch in any real setting. Equal weights across scenarios are a prior, see [limits](../design/limits.md).
- **Business strategy.** The motivation leans on Grove and on famous company stories. Apart from Allen and McDonald, we haven't reviewed the strategy research behind it.
