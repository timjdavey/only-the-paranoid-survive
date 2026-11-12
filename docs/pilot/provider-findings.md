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
