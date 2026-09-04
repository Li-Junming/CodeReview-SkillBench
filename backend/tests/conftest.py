from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture
def public_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def client(tmp_path, public_root):
    return TestClient(create_app(data_root=tmp_path, project_root=public_root))


@pytest.fixture
def valid_skill_zip() -> io.BytesIO:
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr(
            "sample-skill/SKILL.md",
            "---\nname: sample-review\ndescription: Review code.\n---\n\n# Sample\n",
        )
    payload.seek(0)
    return payload


@pytest.fixture
def malicious_zip() -> io.BytesIO:
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("../outside.txt", "escaped")
        archive.writestr("SKILL.md", "# Unsafe")
    payload.seek(0)
    return payload
