from pathlib import Path

import pytest


@pytest.fixture
def public_root() -> Path:
    return Path(__file__).resolve().parents[2]

