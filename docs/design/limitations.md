# Limitations

**What this design gives up, why we accepted each one, and which tier fixes it.**

| Limitation | Why we accepted it | How to overcome, and at which tier |
|---|---|---|
| **A headline that tops out at 1.** Performance can't be plotted over releases once models match the reference bot | No model will be near it before the full study exists, and one continuous number is what a proof of concept needs. See [Why two tiers](decisions.md#why-two-tiers) | Full study: discernment |
| **One kind of change in the proof of concept.** A per-unit tracker can find a level change, so insight is weaker than it will be | The level change is the one with a known bot and one paragraph to explain. See [Why a change is a typed event](decisions.md#why-a-change-is-a-typed-event) | Full study: coupling, gain and observation |
| **No human baseline.** A score says how models compare with each other, not with people | Comparing models over time needs no human anchor, and recruiting people costs time a proof of concept doesn't have | Beyond the full study: human baseline |
| **One reasoning setting per model.** Scores are a lower bound for models that do better with more thinking | Budget. Each model runs at its standard high setting, so the comparison is fair even if it isn't complete | Full study: reasoning sweep |
| **One generator.** A model could be good at this game and nothing else | Four skins widen the surface without the cost of a second game. See [Why four skins over one interface](decisions.md#why-four-skins-over-one-interface) | Full study: one real agentic task with a stale handoff note. Beyond: a second game. See [future work](future.md#whether-it-holds-outside-our-game) |
| **Four skins, none free of priors.** A plant says stable and a market says drifting | The abstract skin is the anchor, the fictional skin the headline, and the spread is a result | Beyond: the time unit and shown inputs as factors |
| **Test awareness can be measured, not removed** | The no-change run prices any experimenting it causes, and the scan reports it. See [Why the game is hard to game](decisions.md#why-the-game-is-hard-to-game) | Full study: every transcript read |
| **A small sample.** Twenty seeds on a few models | We are aiming to only show the measure works, so model comparisons are early reads | Full study: every model on release, more seeds and amplitudes |
| **The change never reacts to the agent.** Real plans often wear out because they are leaned on, and real units pay out late | A reflexive change muddies the no-change run, the reference bot and the error bars. See [Why the change is not reflexive](decisions.md#why-the-change-is-not-reflexive) | Beyond: reflexive change, lagged units |
| **A past the agent read, not lived**, per Schubert | The record gives every model the same grounding and cuts cost to one briefing and the live horizon. See [Why the agent writes its own notes](decisions.md#why-the-agent-writes-its-own-notes) | Beyond: full live run |
| **The record demonstrates a style** | Its author is the reference bot, so the style is the right amount, and the pilot sizes the cue. See [Why the record comes from a bot](decisions.md#why-the-record-comes-from-a-bot-and-its-style-is-a-factor) | Beyond: a history style sweep |
| **A switch is never sticky** | A wrong split forgoes output every round it stands, and the 40 round limit prices time. See [Why no lock-in](decisions.md#why-no-lock-in) | Beyond: cost ratio |
| **Our generator could set a fake target** | The catch rate backup reads only the agent's own shares, and every skin runs in the pilot | Full study: real-task check. Beyond: realism ladder, second game |
