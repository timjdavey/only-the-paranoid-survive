# Public and private

What is published and what is held back, and why.

## The split

| Part | Where | Public |
|---|---|---|
| Engine, harness, analysis, docs | This repo | Yes |
| Seeds and tapes | This repo. Tapes are regenerated from seed and engine hash | Yes |
| The example skin | This repo | Yes |
| The held-out skins | A private repo, see [skins](harness/skins.md) | No |
| Logs from the example skin | `results/logs/` | Yes |
| Logs from held-out skins | Nowhere. They stay on the machine that ran them | No |
| Results tables | `docs/results/` | Yes, with skin names only |

## Why

- **The engine is the science.** Anyone should be able to rerun it and check the baselines.
- **The skin is what a model could memorise.** Publishing the engine and holding back the skin is the cheapest guard against [contamination](glossary.md) there is.
- **A log is a prompt.** It holds the whole skin, so a held-out skin's log is as private as the skin.

## Canary

- Every published file that holds prompt text carries a canary GUID, the same string every time.
- If a model can repeat the GUID, it has seen our data. Ask it before trusting a score.
- The GUID lives in `paranoid.skins.canary` and is listed here once it exists.
