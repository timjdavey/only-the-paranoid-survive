"""The forecast cache on disk. See docs/specs/forecasters/policy.md#the-cache.

It is as private as a log: after a held-out run it stays on the machine.
"""

import hashlib
import os
import tempfile
from pathlib import Path

import numpy as np


def folder() -> Path:
    root = os.environ.get("PARANOID_CACHE")
    return (Path(root) if root else Path.home() / ".cache" / "paranoid") / "forecasts"


def as_bytes(array: np.ndarray) -> bytes:
    return np.ascontiguousarray(array, dtype="<f8").tobytes()


def cache_key(forecaster_key: str, readings: np.ndarray, bets: np.ndarray | None) -> str:
    """SHA-256 of the forecaster's key, the readings and their shape, and the bets when passed."""
    digest = hashlib.sha256()
    for part in (forecaster_key.encode(), repr(readings.shape).encode(), as_bytes(readings)):
        digest.update(part + b"\0")
    digest.update(b"no bets" if bets is None else b"bets\0" + as_bytes(bets))
    return digest.hexdigest()


def load(key: str) -> np.ndarray | None:
    path = folder() / f"{key}.npy"
    return np.load(path) if path.exists() else None


def save(key: str, quantiles: np.ndarray) -> None:
    """Written whole: to a temporary name in the same folder, then moved into place."""
    target = folder()
    target.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target, suffix=".tmp")
    with os.fdopen(handle, "wb") as file:
        np.save(file, quantiles)
    os.replace(temporary, target / f"{key}.npy")
