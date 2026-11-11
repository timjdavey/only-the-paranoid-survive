# Command

## Purpose

`paranoid analyse` is the analysis layer's subcommand. It loads logs, prints what it loaded, and writes the results page and CSV, the pilot results or the cost table. The harness's `main` finds it through the `paranoid.commands` entry point and never imports this layer itself, see [subcommands](../harness/command.md#subcommands). How to run it is in [running](../../harness/running.md#commands).

## Interface

```
paranoid analyse [results] [logs ...] [--out docs/results] [--name poc]
                 [--models configs/models/poc.toml] [--recognition logs/pilot/recognition.csv]
                 [--plots] [--eci-read-on YYYY-MM-DD] [--dry-run]
paranoid analyse pilot [--logs logs/pilot] [--out docs/pilot] [--main <logs>] [--dry-run]
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
3. `write_results(runs, out, name, models=..., recognition=..., plots=..., eci_read_on=..., dry_run=...)`, then print each path written. `--name` must be a bare file stem, see [tables](tables.md#the-results-page).
4. **`--plots` with a models file that has `eci` values needs `--eci-read-on`**, the date the values were read from Epoch's CSV, for the credit on the ECI plot, see [trend plots](plots.md#trend-plots). Without it `write_results` raises, so the command returns 1 before writing anything. The ECI values themselves come from the models file. The analysis never fetches them.
5. **`--dry-run`** passes `dry_run` on. It does steps 1 and 2, prints the paths step 3 would write, and writes nothing.

### `pilot`

`write_pilot(logs, out, main=..., dry_run=...)`, then print each path written.

- **`--logs`** is the folder the pilot cells wrote to, the harness's `--out`, see [pilot cells](../harness/pilot.md#shared-rules).
- **`--main`** is a folder of logs from `paranoid run`, which the inertia table reads, see [reading the inputs](pilot.md#reading-the-inputs). Without it that one table is left out.
- **`--dry-run`** prints the paths a real run would write, so the sections whose input exists, and writes nothing.

### `cost`

`load_runs(logs)`, the report, then `write_cost(runs, models=..., seeds=..., prices=...)` on the table as loaded, printed as a table. Nothing is written to disk. The pilot section does that, see [pilot](pilot.md#sections).

- **No prices file means no `cost` column.** `--prices` defaults to `configs/prices.toml`. When that default is not there the command passes no prices and prints one line saying so. A path typed by hand that does not exist returns 1.
- **With prices**, the line under the table gives the date they were read on, from the table's `attrs["read_on"]`, see [cost](tables.md#cost).

### `gap`

`load_runs([a, b])`, then `paired_gap` between the two logs' result rows, printed as a table with one row per scenario and the headline.

- **Each log must hold exactly one result row**, else `ValueError` naming the log and the keys it holds.
- **The two logs must not share a key**, else `ValueError` naming it. Two logs of one key are one result row, or a duplicate the loader has already dropped, see [duplicates](runs.md#duplicates), so the gap would be a row against itself and print zeros for two runs that differ. To compare two reruns of one key, analyse each on its own.

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
