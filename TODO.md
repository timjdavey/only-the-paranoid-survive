Keep a running list of TODOs in here.

- We are in the middle of a complete rewrite of the project. Only the README is up to date currently.

## Deleted design and spec docs
- We deleted `docs/design/` and `docs/spec/` because we're rebuilding the study from a very different starting point.
- You can still read them at commit `5eaceb4`, e.g. `git show 5eaceb4:docs/design/requirements.md`.
- Links to them from README and `docs/prior/` are now broken. Fix these as the new docs land.

## Pilot
The [generator](docs/design/mechanics.md#generator) leaves these to the pilot:
- Run length, how many events a run holds, and the minimum gap between them.
- Memory, own-weather spread and shared-factor spread, per scenario.
- The loading range and the base ladder ranges.
- Warm up: one cell starts round 1 with an empty record, one with a record pre-filled by a baseline.
