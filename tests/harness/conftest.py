"""Fixtures for the harness suite, see docs/specs/harness/tests.md.

Every test runs from the repo root with PARANOID_SKINS, PARANOID_SEEDS and PARANOID_PILOT_SEEDS cleared,
and a temporary forecast cache, so a developer's .env never reaches a test.
"""

from pathlib import Path

import pytest

from paranoid.skins import Skin, load_skins

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def isolated(tmp_path_factory, monkeypatch):
    """Empty values, not unset ones, so `main` loading .env cannot fill them in."""
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("PARANOID_SKINS", "")
    monkeypatch.setenv("PARANOID_SEEDS", "")
    monkeypatch.delenv("PARANOID_PILOT_SEEDS", raising=False)
    monkeypatch.setenv("PARANOID_CACHE", str(tmp_path_factory.mktemp("cache")))


@pytest.fixture(scope="session")
def example(tmp_path_factory) -> Skin:
    """The example skin, loaded beside an empty held-out folder."""
    return load_skins(tmp_path_factory.mktemp("no-skins"))["example"]


@pytest.fixture
def configs(tmp_path, monkeypatch):
    """A copy of configs/ in a temp working directory, for tests that rewrite a config file."""

    def make(*, seeds: list[int] | None = None, grid: str | None = None) -> Path:
        (tmp_path / "configs" / "seeds").mkdir(parents=True)
        public = seeds if seeds is not None else range(1000)
        (tmp_path / "configs" / "seeds" / "public.txt").write_text("".join(f"{s}\n" for s in public))
        grid_text = grid if grid is not None else (ROOT / "configs" / "grid.toml").read_text()
        (tmp_path / "configs" / "grid.toml").write_text(grid_text)
        monkeypatch.chdir(tmp_path)
        return tmp_path

    return make
