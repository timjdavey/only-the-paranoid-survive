# Themes

The game measures one narrow skill, but the skill sits under several bigger questions about agents. It serves **part of the wider field** ([design principles](../design/requirements.md#design-principles)). Each link below is a claim to test, not a finding.

| Theme | The link | What we'd check |
|---|---|---|
| **METR's time horizon** | METR measures how long a task an agent can finish, and credits part of the rise in horizons to agents adapting to their own mistakes. Noticing that the world has moved under a plan is that skill, isolated | Whether a model's discernment explains why it sits above or below the time horizon trend. See [Why older models and a general ability check](../design/decisions.md#why-older-models-and-a-general-ability-check) |
| **The same headline form** | The full study's discernment copies their recipe: a curve of success against a natural unit, read at a set level and plotted against release date | The two lines can sit side by side on one chart |
| **Agent handoffs** | Long-running agents hand over through notes, summaries and memory files when their context runs out. The game is a controlled takeover of a record, and the agent's notes are the memory file it writes for itself | Whether an inherited plan, with its voice, changes the play, in the inherited plan extension |
| **Test awareness** | Frontier models increasingly say they think they are being tested, which can change what they do | How often they say so here, and whether it drives experimenting. See [Why the game is hard to game](../design/decisions.md#why-the-game-is-hard-to-game) |
| **Reward hacking** | Agents exploit the scoring when they can | Transcript review for tool misuse and steering text in the notes |
| **Deference to a confident source** | A plan written by someone else is an authority, like a user who sounds sure. Sycophancy work asks whether models defer too long. The game removes that author by default | Whether a plan written in a more confident voice slows the switch, in the inherited plan extension |
| **Belief updating in context** | Schubert et al. found Claude v1.3 learns more from good news than bad about its own choices, but symmetrically about choices someone else made. See [Schubert et al. 2024](past-in-the-prompt.md#schubert-et-al-2024-asymmetric-belief-updating) | Whether the agent discounts losses on its notes once it has staked on them itself, so a read record stops counting as someone else's choice |
