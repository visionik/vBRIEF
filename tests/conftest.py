"""Shared pytest fixtures for libxbrief tests."""

from __future__ import annotations

from pathlib import Path

import pytest

# Root of the repository (two levels up from tests/)
_REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture
def examples_dir() -> Path:
    """Return the path to the examples/ directory."""
    return _REPO_ROOT / "examples"


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return _REPO_ROOT
