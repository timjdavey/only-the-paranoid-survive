# Specs

The contract each layer of the code is written to, and tested against.

- **[design](../design/) is why.** The decisions and the reasons.
- **[harness](../harness/) is how it is built.** Layers, tools, commands.
- **specs is what.** Exactly what each layer must do, precisely enough that someone can write the code and the tests from these pages alone.

## How we use them

- **Spec first.** A layer gets a spec before it gets code. Tests are written from the layer's `tests.md`, then the code is written until they pass.
- **A spec never contradicts a design page.** If one has to move, the design page moves first, then the spec, then the code.
- **Code and spec move together.** When they differ, one of them is wrong. Fix it in the same PR, and say which one was wrong.
- **The pilot fills the numbers.** A spec proposes a default for every knob so the code runs on day one. Each is marked "pilot to confirm" and listed under the page's "Pilot decides" heading with a link to the check in [engine checks](../pilot/engine-checks.md) or [provider checks](../pilot/provider-checks.md) that settles it. Once [decisions](../pilot/decisions.md) has the number, the spec takes it and drops the mark.
- **Nothing rests on a guess about a dependency.** An assumption about inspect_ai, numpy, an SDK or a model API that nobody has checked goes under "Verify before code", and the code that rests on it waits until someone has.

## Shape of a spec page

Every page has the same sections, in this order. A section with nothing to say is left out.

| Section | What goes in it |
|---|---|
| Purpose | One paragraph. What this part does and what it does not do |
| Interface | Every public name, with its signature and types |
| Behaviour | The rules, as bullets. One rule per bullet |
| Defaults | Every number the page proposes, why that number, and the check that settles it. Only on pages that propose numbers |
| Invariants | What is always true, however the rules are implemented. Never a restatement of a rule above |
| Pilot decides | The numbers the pilot settles, each with a link to its check |
| Not decided | Design questions still open. Each says when it gets decided |
| Verify before code | Facts about a dependency that nobody has checked. Each names the code that waits on it |

- **Tests have no section on a page.** They live on the layer's `tests.md`, one row per test, and every row links to the section it checks. So the page says what is true and the tests page says how we know.

## Rules

- The same rules as [CONTRIBUTING](../../CONTRIBUTING.md): [glossary](../glossary.md) words only, files under 300 lines, bullets and tables over prose, links over re-explaining.
- Write for an implementer who has never read the study. Say what, link to why.
- Names in a spec are the names in the code. A rename is a spec change.
- **One home per rule.** A rule two layers care about lives in one section. Every other mention links to it and adds nothing, so there is one place to change.
- **Boundaries are two-sided.** Each layer's README lists the names it takes from the layer below and the names the layer above reads from it. A duty one layer hands another is written on both sides, and tested on the side that does it.
- **Test ids are unique across the repo.** The first letter is the layer, the second the page, so any page can name any test: `ET3` is engine tape test 3.

| Layer | Prefix | Pages |
|---|---|---|
| engine | `E` | `EC` config, `ET` tape, `EG` game, `EV` view, `EH` property |
| baselines | `B` | `BP` policies, `BR` rules, `BF` forecast, `BH` property |
| skins | `K` | `KS` skin, `KR` render, `KL` lint, `KH` property |
| harness | `H` | `HK` task, `HS` solver, `HR` providers, `HO` scorer, `HM` command, `HY` property |

## What a log carries

Every identifier that says what a run played, in one place. Each is owned by one layer and defined on one page.

| Identifier | Owner | What it covers | What changes it | Pinned by |
|---|---|---|---|---|
| `engine_hash` | [engine](engine/config.md#engine-hash) | The config that made the tape, `GENERATOR_VERSION` included | Any config field, or a `GENERATOR_VERSION` bump | `EC3`, `EC4` |
| `GENERATOR_VERSION` | [engine](engine/config.md#engine-hash) | What `make_tape` produces for a config it already accepted | A change to the draws or their order | `EC3`, through the hash |
| `numpy_version` | [harness](harness/task.md#dataset) logs it | Bit equality of tapes, which the hash does not promise across numpy versions | A numpy upgrade | `HK1` |
| `prompt_hash` | [skins](skins/render.md#prompt-hash) | Every word the model reads from a skin, and the layout it reads them in | Any covered field, or a `RENDER_VERSION` bump | `KS2`, `KR7`, `HK10` |
| `RENDER_VERSION` | [skins](skins/render.md#prompt-hash) | The joins of the system prompt and the shape of the record | A layout change with no skin word moved | `KR7` |
| `harness_version` | [harness](harness/task.md#dataset) | The round loop, which neither hash covers | A release, or a commit when run from a checkout | `HK10` |

## What never reaches a log or a prompt

The secrecy rules, each with the one section that owns it and the tests that prove it. The reasons are in [contamination](../harness/contamination.md#why).

| Never | Rule | Owner | Tests |
|---|---|---|---|
| A tape or a view | Regenerated from config and seed, never serialised | [engine](engine/tape.md#interface) | `ET28`, `HK11` |
| A level the agent did not bet on | The record holds only what the agent saw | [engine](engine/game.md#record) | `EG5` |
| A held-out seed's value | Position in the list only, the value read from the seed file at run time | [harness](harness/task.md#dataset) | `HK6`, `HO11` |
| A held-out skin's text | A failing test names the skin, never its words. A log is as private as its skin | [skins](skins/tests.md) | `KL12` |
| The canary GUID | In no text the model reads | [skins](skins/lint.md#canary) | `KL9`, `KL12` |
| The engine's error text | The model reads the skin's `bad_call`, never the engine's message | [harness](harness/solver.md#submit) | `HS7` |
| A Timestral forecast of a held-out run | The cache stays on the machine, like the log | [harness](harness/providers.md#timestral) | |

## Layers

One folder per layer, in the order they are built, see [layout](../harness/layout.md).

| Layer | Spec | Status | Verify before code |
|---|---|---|---|
| engine | [engine/](engine/) | Written, no code yet | Nothing |
| baselines | [baselines/](baselines/) | Written, no code yet | Timestral's quantile levels, which `QUANTILE_LEVELS` assumes. See the [forecast](baselines/forecast.md#verify-before-code) page |
| skins | [skins/](skins/) | Written, no code yet | Nothing |
| harness | [harness/](harness/) | Written, no code yet | Whether inspect's store is in scope inside `generate`, Timestral's quantile levels and call signature, the `typesafe-sdk` call shape, the reasoning budgets and effort names per provider, and which providers refuse a forced tool with thinking on. See the [providers](harness/providers.md#verify-before-code), [command](harness/command.md#verify-before-code) and [solver](harness/solver.md#verify-before-code) pages |
| analysis | | To come | |
