# Prior work

| Page | What's in it |
|---|---|
| [Worlds that change](worlds-that-change.md) | Studies that change the world under the agent |
| [People, and the reference bot](people.md) | Studies of people, and the methods behind the reference bot |
| [A past in the prompt](past-in-the-prompt.md) | Studies that put a past in front of the model |
| [Measuring agents](measuring-agents.md) | METR's time horizon, and studies of models that suspect a test |
| [Themes](themes.md) | How the game connects to bigger questions about agents, each a claim to test |
| [Glossary](../glossary.md) | The one word we use for each idea in the design |

## At a glance

Our game asks for three things that no study below has together.

1. **The noise has memory.** A bad month is ordinary, so a run of bad results is not evidence by itself, and the no-change run holds a dip that starts exactly like the change. Elsewhere each result is drawn fresh, apart from STOCKTAKE's week-long false alarm.
2. **The standing split keeps paying.** It never falls below 0.55, so it loses only to the best split available. Elsewhere the old plan mostly stops paying once the change lands: a reversed option wins 20% of the time, a tool group fails every call.
3. **The headline is read against the best bot we can build**, with the no-change run on the same luck inside it, so a false alarm costs as much as a miss.

A reader who skims will file the game beside Zhang, Mellor and Shapiro and BanditBench. [Why this is more than a drifting bandit](../design/decisions.md#why-this-is-more-than-a-drifting-bandit) says what else sets it apart: a change that edits how the units work, not just one unit's level, and silence about change in every prompt, skin and tool.

| Study | Setting | Change | Old plan still pays after it? | Feedback | Agent's past | Scored against | No-change control |
|---|---|---|---|---|---|---|---|
| [Coda-Forno et al. 2023](past-in-the-prompt.md#coda-forno-et-al-2023-meta-in-context-learning) | Bandits and regression, GPT-3 | None | n/a | Noisy | Up to 4 earlier tasks | UCB, greedy, Bayesian regression | No |
| [Mazaheri and Mazaheri 2026](past-in-the-prompt.md#mazaheri-and-mazaheri-2026-one-past-audit-makes-verifiers-lenient) | Checking maths proofs | None | n/a | None | One earlier episode | Human labels | Filler of the same length |
| [Schubert et al. 2024](past-in-the-prompt.md#schubert-et-al-2024-asymmetric-belief-updating) | Two-armed bandits, Claude v1.3 | None | n/a | Noisy | Own or someone else's choices | Fitted learning rates | No |
| [IBIS 2026](past-in-the-prompt.md#ibis-2026-inertia-in-search-agents) | Web search agents | None | n/a | None | Own action or results handed over | Human labels | No |
| [Kumaran et al. 2025](past-in-the-prompt.md#kumaran-et-al-2025-whose-first-answer-it-was) | Two-option questions with advice | None | n/a | Advice from another model | Own first answer, shown, hidden or credited to another model | Ideal observer | First answer hidden |
| [Ge, Zhang and Vorobeychik 2026](past-in-the-prompt.md#ge-zhang-and-vorobeychik-2026-the-description-history-gap) | One-shot lotteries | None | n/a | None | Stated odds or a list of past payoffs | Expected value maximiser | No |
| [Liu et al. 2026](past-in-the-prompt.md#liu-et-al-2026-history-that-never-becomes-experience) | ALFWorld, WebShop and others | None | n/a | Exact | Within the episode | Task success | Shuffled history |
| [Haq et al. 2025](past-in-the-prompt.md#haq-et-al-2025-mental-sets-in-llms) | 12 arithmetic problems | Problem type switches | Yes, the long method still works | Exact | Earlier problems | Nothing | Problems with no lead-in |
| [BanditBench 2025](worlds-that-change.md#banditbench-nie-et-al-2025-in-context-exploration) | Bandits | None | n/a | Noisy | None | UCB and LinUCB | No |
| [Wang, Ward and Zhang 2026](worlds-that-change.md#wang-ward-and-zhang-2026-reversal-learning) | Two options that swap | Many swaps | No, the old option wins 20% | Noisy | Within the run | People | No |
| [Set-shifting 2026](worlds-that-change.md#set-shifting-2026-tool-groups-that-stop-working) | Tool groups in an agent harness | Up to 3 silent shifts | No, old tools always fail | Exact | Within the session | Nothing | Resumed copies, beside the score |
| [AdaExploreBench 2026](worlds-that-change.md#adaexplorebench-2026-hidden-rules-that-drift) | Hidden decision rules | One drift | No, accuracy falls 27 points | Exact | None | All-knowing oracle | No-drift setting, averages only |
| [STOCKTAKE 2026](worlds-that-change.md#stocktake-2026-a-fair-oracle-for-supply-chains) | 26-week supply chain | Six hidden factors drift | Partly, the supplier degrades by bands | Noisy | None | Bayes filter on the agent's own view | Same event tape for every policy |
| [Gupta et al. 2025](worlds-that-change.md#gupta-et-al-2025-coin-flips-and-bayes) | Coin flips, beliefs only | One switch, in one experiment | No, 75% heads becomes 25% | Noisy | None | Beta posterior | No |
| [Zhang et al. 2025](worlds-that-change.md#zhang-et-al-2025-llms-in-a-drifting-bandit) | Four-armed bandit | Every arm drifts all the time | Partly, a good arm fades rather than fails | Noisy | None | People, and fitted exploration models | No |
| [KellyBench 2026](worlds-that-change.md#kellybench-grady-et-al-2026-a-season-of-football-bets) | A season of football bets | The real season, which shifts | Unclear, no model had an edge to begin with | Noisy | None | Final bankroll, human baselines and an expert rubric | No |
| [Behrens et al. 2007](people.md#behrens-et-al-2007-people-learn-faster-when-the-world-is-volatile) | People, blue or green | Many swaps | No | Noisy | None | Hierarchical Bayesian learner | Stable phase |
| [Bleser et al. 2026](people.md#bleser-et-al-2026-true-and-false-beliefs-about-volatility) | People, told the rule will or won't change | One flip per block | No | Noisy | None | Rescorla-Wagner fits | Stable blocks |
| [Massey and Wu 2005](people.md#massey-and-wu-2005-system-neglect) | People, spotting a regime shift | At most one shift | n/a, beliefs only | Noisy | None | Bayesian posterior | No |
| [Brown and Steyvers 2009](people.md#brown-and-steyvers-2009-naming-a-change-versus-predicting-through-it) | People, a hidden source that jumps | Many jumps | No | Noisy | None | Particle filter fits | No |
| [Gallistel et al. 2001](people.md#gallistel-et-al-2001-rats-that-have-seen-no-change) | Rats, two levers | Ratio of reward rates jumps | No | Noisy | Many earlier sessions, with or without change | Ideal detector | No |
| **Our game** | A budget split across ten units, after a briefing on a 200 round record | One unit slowly falls and an ignored one rises past it, or a dip that recovers | Yes, never below 0.55 | Noisy, with memory | A record written by a bot, and notes the agent wrote itself | The reference bot as yardstick and the no-update bot as floor, on the same shared luck | No-change run, inside the headline, with a yoked dip |

STOCKTAKE comes closest on method: an oracle that sees only what the agent sees, one event tape shared by every policy, and a false alarm that looks real for a week, the shape of our yoked dip. AdaExploreBench comes closest in shape, with one silent change and a score from a floor policy to an oracle, like performance. Set-shifting is the only one whose no-change copy is matched run for run, and it keeps that copy beside the score. [Bazaar](worlds-that-change.md#bazaar-ahmed-et-al-2026-pricing-when-customers-tastes-swap)'s unshocked customers share a run with the shocked ones and get no result of their own. None shares the luck between the two.

The too jumpy side is the least tested. Wang treats a switch after a loss as good, STOCKTAKE leaves calm-week overreactions out of every metric, and AdaExploreBench doesn't count false alarms. Yet the studies disagree on which way LLMs fail. Wang finds models rarely switch after a loss, which predicts too slow. Gupta finds some models forget after a couple of flips, Kumaran finds they overweight advice that disagrees with them, and [Horowitz and Plonsky](worlds-that-change.md#horowitz-and-plonsky-2025-a-pull-towards-the-latest-result) find a strong pull towards the latest result, which all predict too jumpy. Bleser tests both directions in people, but by telling them how volatile the world is. Massey and Wu predict which way people fail from the world alone: they overreact in a stable world with noisy signals, which is exactly our no-change run. Our headline makes the question unavoidable: what the no-change run loses is counted in it.

### Where each study bears on the design

| Part of the design | Studies |
|---|---|
| [Why weather has memory](../design/decisions.md#why-weather-has-memory) | STOCKTAKE (a false alarm that looks real for a week), Massey and Wu (system neglect in a stable world), Zhang (slow drift) |
| [Why a change is a typed event](../design/decisions.md#why-a-change-is-a-typed-event) | AdaExploreBench (swapped fields noticed three times as often as reversals) |
| [Why the yoked dip](../design/decisions.md#why-the-yoked-dip) | STOCKTAKE (canal closure and false alarm), Set-shifting (resumed copies), Bazaar (unshocked customers), Massey and Wu |
| [Why the agent writes its own notes](../design/decisions.md#why-the-agent-writes-its-own-notes) | Schubert, IBIS, Barkett, Kumaran, Fresh Memory, Stale Plans, STALE, ACE, Fork-and-Flush |
| [Why the record comes from a bot](../design/decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor) | BanditBench (example runs in the prompt), Coda-Forno, Liu |
| [Why a budget split](../design/decisions.md#why-a-budget-split) | Haghani and Dewey, KellyBench, Wang (lose-shift), all from the [coin flip game we dropped](../design/alternatives.md#why-the-coin-flip-game-was-dropped) |
| [Why split doubting from switching](../design/decisions.md#why-split-doubting-from-switching) | Mazaheri, STOCKTAKE, Set-shifting |
| [Why two bots bound the game](../design/decisions.md#why-two-bots-bound-the-game) | Adams and MacKay, Wilson, Behrens, STOCKTAKE, Mellor and Shapiro, Nassar, Gallistel 2014 |
| [Complacency as a parameter, not a history](../design/decisions.md#complacency-as-a-parameter-not-a-history) | Coda-Forno, Behrens, Wilson, Gallistel, Massey and Wu |
| [Why discernment is the full study headline](../design/decisions.md#why-discernment-is-the-full-study-headline) | METR, Wichmann and Hill, Mazaheri (sensitivity and bar), Miller (paired error bars) |
| [Why the game is hard to game](../design/decisions.md#why-the-game-is-hard-to-game) | Set-shifting and AdaExploreBench (what a hint in the prompt does), Bleser (false warnings), the papers on [test awareness](measuring-agents.md) |
| [Why the bots set the difficulty](../design/decisions.md#why-the-bots-set-the-difficulty) | Bazaar, BanditBench |
| [Why four skins over one interface](../design/decisions.md#why-four-skins-over-one-interface) | Allen and McDonald (a masked game models couldn't name) |
| [Future work](../design/future.md): [an inherited plan](../design/future.md#what-the-agent-knows-before-it-starts) | Ge, BanditBench, Krishnamurthy, Liu, the Self-Correction Illusion, Kumaran (whose notes they are), ACE, Fresh Memory, Stale Plans |
| Future work: [full live run](../design/future.md#what-the-agent-knows-before-it-starts) | Schubert, IBIS |
| Future work: [doubt question](../design/future.md#how-the-agent-can-act) | STOCKTAKE, STALE, Bleser, Brown and Steyvers, Schmied, Goel, KellyBench |
| Future work: [later kinds of change](../design/future.md#how-the-world-changes) | Wang, AdaExploreBench |
| Future work: [expensive switching](../design/future.md#how-the-agent-can-act) | Barkett |
| Future work: [ergodic tries](../design/future.md#what-the-agent-knows-before-it-starts) | Coda-Forno, Mazaheri |
| Future work: [human baseline](../design/future.md#whether-it-holds-outside-our-game) | Behrens, Bleser, Wang, Haghani and Dewey, Zhang |
| Future work: [real task and second game](../design/future.md#whether-it-holds-outside-our-game) | STOCKTAKE, Bazaar, CoffeeBench, Allen and McDonald |

## Gaps

- **Not yet read in full.** Massey and Wu, Brown and Steyvers, Gallistel 2001 and the Kumaran journal version.
- **Claude system cards.** What happened when the Sonnet 4.5 card suppressed eval awareness (sections 7.6.4 and 7.6.5) is unread, and so are later cards.
- **Reward hacking.** The last strand of the [themes table](themes.md) still has a literature we haven't reviewed.
- **LLMs on a biased coin.** We found no one who has run LLMs on the Haghani and Dewey game, nor an LLM study of a bandit that switches once and stays switched. Both look open.
- **Noise with memory.** Apart from STOCKTAKE's one week-long false alarm, every study above draws each result fresh. Whether models tell a bad stretch from a change when the noise itself has stretches looks open.
- **Copying a demonstrated style.** BanditBench's example runs are the only test we found of a past that demonstrates how to play. Whether a model copies the experimentation rate of a record it reads is untested, and the pilot's history style cell is a first look.
