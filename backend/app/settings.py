from __future__ import annotations

import os
from pathlib import Path


def default_data_root() -> Path:
    return Path(os.getenv("SKILLBENCH_DATA_DIR", ".skillbench-data")).resolve()


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def live_provider_configured() -> bool:
    return bool(os.getenv("SKILLBENCH_PROVIDER"))

