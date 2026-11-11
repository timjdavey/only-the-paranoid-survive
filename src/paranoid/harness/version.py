"""harness_version, the one id that says which round loop played. See docs/specs/harness/task.md#dataset."""

import subprocess
from functools import cache
from importlib.metadata import version
from pathlib import Path

CHECKOUT = Path(__file__).resolve().parents[3]  # the repo root, when run from a checkout


@cache
def harness_version() -> str:
    """The package version, plus `+<short sha>` when run from a git checkout, as `0.1.0+2f13c9a`."""
    base = version("paranoid")
    if not (CHECKOUT / ".git").exists():
        return base
    try:
        sha = subprocess.run(
            ["git", "-C", str(CHECKOUT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return base
    return f"{base}+{sha}" if sha else base
