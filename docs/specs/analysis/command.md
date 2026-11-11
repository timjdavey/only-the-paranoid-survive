# Command

## Purpose

`paranoid analyse` is the analysis layer's subcommand. It loads logs, prints what it loaded, and writes the results page and CSV, the pilot results or the cost table. The harness's `main` finds it through the `paranoid.commands` entry point and never imports this layer itself, see [subcommands](../harness/command.md#subcommands). How to run it is in [running](../../harness/running.md#commands).

## Interface

```
paranoid analyse [results] [logs ...] [--out docs/results] [--name poc]
                 [--models configs/models/poc.toml] [--recognition logs/pilot/recognition.csv]
                 [--plots] [--eci-read-on YYYY-MM-DD] [--dry-run]
paranoid analyse pilot [--logs logs/pilot] [--out docs/pilot] [--dry-run]
paranoid analyse cost [logs ...] [--models configs/models/poc.toml] [--seeds N] [--prices configs/prices.toml]
paranoid analyse gap <log-a> <log-b>
```

```python
def analyse(argv: Sequence[str]) -> int
```

## Behaviour

### Dispatch

- **Registered** in `pyproject.toml` as `analyse = "paranoid.analysis.cli:analyse"` in the `paranoid.commands` group. The harness's `main` passes the arguments after `analyse`.
- **The subcommand defaults to `results`.** `paranoid analyse logs/` is `paranoid analyse results logs/`, as [running](../../harness/running.md#commands) shows. A first argument that is a subcommand name is the subcommand, even when a path of that name exists, so a folder called `cost` is passed as `./cost` or after `results`. Anything else is a path.
- **`logs` defaults to `logs/`** for `results` and `cost`.
- **Returns 0 on success and 1 on a `ValueError`**, whose message it prints, as the harness command does, see [subcommands](../harness/command.md#subcommands). Any other exception propagates.

### `results`

1. `load_runs(logs)`, then print the report: logs read with sample counts, logs skipped, logs dropped as duplicates and which won, errored samples per log, mixed numpy versions, see [the report](runs.md#the-report).
2. `load_recognition(--recognition)` when the file exists, for the `§` and `¶` flags, see [flags](scores.md#flags).
3. `write_results(runs, out, name, models=..., recognition=..., plots=...)`, then print each path written. `--name` must be a bare file stem, see [tables](tables.md#the-results-page).
4. **`--plots` with a models file that has `eci` values needs `--eci-read-on`**, the date the values were read from Epoch's CSV, for the credit on the ECI plot, see [trend plots](plots.md#trend-plots). Without it the command returns 1 before writing anything. The ECI values themselves come from the models file. The analysis never fetches them.
5. **`--dry-run`** does steps 1 and 2 and prints what step 3 would write, and writes nothing.

### `pilot`

`write_pilot(logs, out)`, then print each path written. `--dry-run` prints the sections whose input exists and writes nothing.

### `cost`

`load_runs(logs)`, the report, then `write_cost(runs, models=..., seeds=..., prices=...)` printed as a table. Nothing is written to disk; the pilot section does that, see [pilot](pilot.md#sections).

### `gap`

`load_runs([a, b])`, then `paired_gap` between the two logs' result rows, printed as a table with one row per scenario and the headline. Each log must hold exactly one result row, else `ValueError` naming the log and the keys it holds. The two rows may be the same key, which prints zeros, see [paired gap](scores.md#paired-gap).

## Invariants

- `analyse` reads no key and opens no network connection.
- Nothing is written outside `--out`, for any `--name`, and nothing at all with `--dry-run`.
- `paranoid analyse` twice on the same logs writes the same bytes, see [tables](tables.md#invariants).
- No subcommand prints a recognition reply, a seed value from a held-out set or a word of a skin but its name.

## Not decided

- Whether `results` should refuse to write when a log's `harness_version` is older than the installed package, or only say so in the report. It only says so here. Decide when the first release ships.

## Checked

Run on 2026-11-11 with uv 0.10.12 and hatchling, on a scratch package installed as this one is.

| Question | Answer |
|---|---|
| Does `entry_points(group="paranoid.commands")` see `analyse` in an editable install | Yes, after `uv sync`. `uv run` syncs first, so `uv run paranoid analyse` and `uv run pytest` both see it |
| Is a group added to `pyproject.toml` seen before the next sync | No. The entry points are written to the install's metadata at sync time, so a stale environment run with `.venv/bin/python` misses it |
