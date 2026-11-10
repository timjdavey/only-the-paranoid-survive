"""Checks the scaffold, until the engine suite in docs/specs/engine/tests.md replaces it."""

import numpy

import paranoid.engine


def test_engine_package_imports():
    assert paranoid.engine.__doc__


def test_numpy_is_installed():
    assert numpy.__version__
