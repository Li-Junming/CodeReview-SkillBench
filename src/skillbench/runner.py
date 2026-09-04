from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from skillbench.common import (
    canonical_sha256,
    load_json,
    resolve_under,
    sha256_file,
    write_json,
)


def _input_record(root: Path, job: dict[str, Any]) -> dict[str, Any]:
    visible = resolve_under(root, job["candidate_visible_path"])
    files = sorted(path for path in visible.rglob("*") if path.is_file())
    skill = None
    if job["condition"] != "D0":
        skill = {
            "skill_id": job["skill_id"],
            "path": job["skill_path"],
            "sha256": job["skill_sha256"],
        }
    return {
        "schema_version": "0.1",
        "run_id": job["run_id"],
        "case_id": job["case_id"],
        "condition": job["condition"],
        "model_profile": job["model_profile"],
        "repetition": job["repetition"],
        "skill": skill,
        "candidate_visible_files": [
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
            }
            for path in files
        ],
    }


def _create_run_dir(output_root: Path, run_id: str) -> Path:
    run_dir = output_root / run_id
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise FileExistsError(f"append-only run already exists: {run_dir}") from error
    return run_dir


def run_replay(
    root: Path,
    output_root: Path,
    job: dict[str, Any],
    response_file: Path,
) -> dict[str, Any]:
    root = root.resolve()
    response = load_json(response_file)
    input_record = _input_record(root, job)
    trace = {
        "schema_version": "0.1",
        "run_id": job["run_id"],
        "adapter": "replay",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.system(),
        },
        "input_sha256": canonical_sha256(input_record),
        "response_sha256": canonical_sha256(response),
    }
    completion = {
        "schema_version": "0.1",
        "run_id": job["run_id"],
        "case_id": job["case_id"],
        "skill_id": job["skill_id"],
        "condition": job["condition"],
        "model_profile": job["model_profile"],
        "repetition": job["repetition"],
        "adapter": "replay",
        "status": "CAPTURED",
        "response_sha256": trace["response_sha256"],
    }

    run_dir = _create_run_dir(output_root, job["run_id"])
    write_json(run_dir / "input.json", input_record)
    write_json(run_dir / "response.json", response)
    write_json(run_dir / "trace.json", trace)
    write_json(run_dir / "completion.json", completion)
    return completion
