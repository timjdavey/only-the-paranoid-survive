# Command

## Purpose

`paranoid analyse` is the analysis layer's subcommand. It loads logs, prints what it loaded, and writes the results page and CSV, the pilot results or the cost table. The harness's `main` finds it through the `paranoid.commands` entry point and never imports this layer itself, see [subcommands](../harness/command.md#subcommands). How to run it is in [running](../../harness/running.md#commands).

## Interface

```
paranoid analyse [results] [logs ...] [--out docs/results] [--name poc]
                 [--models configs/models/poc.toml] [--recognition logs/pilot/recognition.csv]
                 [--plots] [--dry-run]
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
- **The subcommand defaults to `results`.** `paranoid analyse logs/` is `paranoid analyse results logs/`, as [running](../../harness/running.md#commands) shows. A first argument that is not a known subcommand is taken as a path.
- **`logs` defaults to `logs/`** for `results` and `cost`.
- **Returns 0 on success and 1 on a `ValueError`**, whose message it prints, as the harness command does, see [subcommands](../harness/command.md#subcommands). Any other exception propagates.

### `results`

1. `load_runs(logs)`, then print the report: logs read with sample counts, logs skipped, logs dropped as duplicates and which won, errored samples per log, see [the report](runs.md#the-report).
2. Load `--recognition` when the file exists, for the `¶` flag, see [flags](scores.md#flags).
3. `write_results(runs, out, name, models=..., recognition=..., plots=...)`, then print each path written.
4. **`--dry-run`** does step 1 and 2 and prints what step 3 would write, and writes nothing.

### `pilot`

`write_pilot(logs, out)`, then print each path written. `--dry-run` prints the sections whose input exists and writes nothing.

### `cost`

`load_runs(logs)`, the report, then `write_cost(runs, models=..., seeds=..., prices=...)` printed as a table. Nothing is written to disk; the pilot section does that, see [pilot](pilot.md#sections).

### `gap`

`load_runs([a, b])`, then `paired_gap` between the two logs' result rows, printed as a table with one row per scenario and the headline. The two logs must be one result row each, else `ValueError` naming what differs, see [paired gap](scores.md#paired-gap).

## Invariants

- `analyse` reads no key and opens no network connection.
- Nothing is written outside `--out`, and nothing at all with `--dry-run`.
- `paranoid analyse` twice on the same logs writes the same bytes, see [tables](tables.md#invariants).

## Not decided

- Whether `results` should refuse to write when a log's `harness_version` is older than the installed package, or only say so in the report. It only says so here. Decide when the first release ships.

## Verify before code

- **Entry point discovery in an editable install.** That `importlib.metadata.entry_points(group="paranoid.commands")` sees `analyse` after `uv sync`, so the harness's HM7 and this layer's AM1 pass without a rebuild. `analyse` waits on it.
