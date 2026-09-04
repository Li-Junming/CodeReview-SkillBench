from __future__ import annotations

from pathlib import Path
from typing import Any

from skillbench.common import canonical_sha256, load_json, sha256_file


_ARTIFACTS = {
    "input": "input.json",
    "response": "response.json",
    "trace": "trace.json",
    "completion": "completion.json",
}


def build_evidence_bundle(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    artifacts: list[dict[str, str]] = []
    violations: list[str] = []

    for role, name in _ARTIFACTS.items():
        path = run_dir / name
        if not path.is_file():
            violations.append(f"missing artifact: {name}")
            continue
        artifacts.append(
            {
                "role": role,
                "path": name,
                "sha256": sha256_file(path),
            }
        )

    trace_path = run_dir / "trace.json"
    if trace_path.is_file():
        trace = load_json(trace_path)
        input_path = run_dir / "input.json"
        response_path = run_dir / "response.json"
        if input_path.is_file() and canonical_sha256(load_json(input_path)) != trace.get("input_sha256"):
            violations.append("input hash does not match trace")
        if response_path.is_file() and canonical_sha256(load_json(response_path)) != trace.get(
            "response_sha256"
        ):
            violations.append("response hash does not match trace")
        run_id = trace.get("run_id", run_dir.name)
    else:
        run_id = run_dir.name

    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "integrity": not violations,
        "artifacts": artifacts,
        "violations": sorted(violations),
    }

