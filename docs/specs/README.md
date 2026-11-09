# Specs

The contract each layer of the code is written to, and tested against.

- **[design](../design/) is why.** The decisions and the reasons.
- **[harness](../harness/) is how it is built.** Layers, tools, commands.
- **specs is what.** Exactly what each layer must do, precisely enough that someone can write the code and the tests from these pages alone.

## How we use them

- **Spec first.** A layer gets a spec before it gets code. Tests are written from the spec's Tests section, then the code is written until they pass.
- **A spec never contradicts a design page.** If one has to move, the design page moves first, then the spec, then the code.
- **Code and spec move together.** When they differ, one of them is wrong. Fix it in the same PR, and say which one was wrong.
- **The pilot fills the numbers.** A spec proposes a default for every knob so the code runs on day one. Each is marked "pilot to confirm" and links to the check in [engine checks](../pilot/engine-checks.md) or [provider checks](../pilot/provider-checks.md) that settles it. Once [decisions](../pilot/decisions.md) has the number, the spec takes it and drops the mark.

## Shape of a spec page

Every page has the same sections, in this order. A section with nothing to say is left out.

| Section | What goes in it |
|---|---|
| Purpose | One paragraph. What this part does and what it does not do |
| Interface | Every public name, with its signature and types |
| Behaviour | The rules, as bullets. One rule per bullet |
| Invariants | What is always true, however the rules are implemented |
| Tests | What the test suite checks. Listed in full on the layer's `tests.md` |
| Open | What the pilot decides, with a link to the check |

## Rules

- The same rules as [CONTRIBUTING](../../CONTRIBUTING.md): [glossary](../glossary.md) words only, files under 300 lines, bullets and tables over prose, links over re-explaining.
- Write for an implementer who has never read the study. Say what, link to why.
- Names in a spec are the names in the code. A rename is a spec change.

## Layers

One folder per layer, in the order they are built, see [layout](../harness/layout.md).

| Layer | Spec | Status |
|---|---|---|
| engine | [engine/](engine/) | Written, no code yet |
| skins | [skins/](skins/) | Written, no code yet |
| harness | | To come |
| analysis | | To come |
