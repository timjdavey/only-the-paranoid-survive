"""harness_version, the one id that says which round loop played. See docs/specs/harness/task.md#dataset."""

import subprocess
from functools import cache
from importlib.metadata import version
from pathlib import Path

CHECKOUT = Path(__file__).resolve().parents[3]  # the repo root, when run from a checkout


@cache
def harness_version() -> str:
    """The package version, plus `+<short sha>` when run from a git checkout, as `0.1.0+2f13c9a`.

    `.dirty` follows when the code has changes not committed, as `0.1.0+2f13c9a.dirty`.
    """
    base = version("paranoid")
    if not (CHECKOUT / ".git").exists():
        return base
    try:
        sha = git("rev-parse", "--short", "HEAD").strip()
        dirty = git("status", "--porcelain", "--", "src/paranoid").strip()
    except (OSError, subprocess.SubprocessError):
        return base
    if not sha:
        return base
    return f"{base}+{sha}.dirty" if dirty else f"{base}+{sha}"


def git(*args: str) -> str:
    """What `git <args>` prints, run in the checkout."""
    command = ["git", "-C", str(CHECKOUT), *args]
    return subprocess.run(command, capture_output=True, text=True, timeout=5, check=True).stdout
