import json
from pathlib import Path

import pytest

from skillbench.planner import build_plan
from skillbench.runner import run_replay


def test_replay_is_append_only(public_root: Path, tmp_path: Path) -> None:
    job = build_plan(public_root)["jobs"][0]
    response = public_root / "examples/public_demo/response.json"
    run_replay(public_root, tmp_path, job, response)
    with pytest.raises(FileExistsError, match="append-only"):
        run_replay(public_root, tmp_path, job, response)


def test_replay_persists_unjudged_evidence(public_root: Path, tmp_path: Path) -> None:
    job = build_plan(public_root)["jobs"][1]
    response = public_root / "examples/public_demo/response.json"

    completion = run_replay(public_root, tmp_path, job, response)
    run_dir = tmp_path / job["run_id"]

    assert completion["status"] == "CAPTURED"
    assert "judge" not in completion
    assert {path.name for path in run_dir.iterdir()} == {
        "completion.json",
        "input.json",
        "response.json",
        "trace.json",
    }
    trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
    assert trace["adapter"] == "replay"
    assert len(trace["input_sha256"]) == 64
    assert len(trace["response_sha256"]) == 64


def test_no_skill_condition_records_no_skill_hash(public_root: Path, tmp_path: Path) -> None:
    job = next(job for job in build_plan(public_root)["jobs"] if job["condition"] == "D0")
    response = public_root / "examples/public_demo/response.json"
    run_replay(public_root, tmp_path, job, response)
    record = json.loads((tmp_path / job["run_id"] / "input.json").read_text(encoding="utf-8"))
    assert record["skill"] is None
