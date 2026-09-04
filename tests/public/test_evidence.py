import json
from pathlib import Path

from skillbench.evidence import build_evidence_bundle
from skillbench.planner import build_plan
from skillbench.runner import run_replay


def _captured_run(public_root: Path, tmp_path: Path) -> Path:
    job = build_plan(public_root)["jobs"][1]
    response = public_root / "examples/public_demo/response.json"
    run_replay(public_root, tmp_path, job, response)
    return tmp_path / job["run_id"]


def test_evidence_bundle_verifies_captured_hashes(public_root: Path, tmp_path: Path) -> None:
    bundle = build_evidence_bundle(_captured_run(public_root, tmp_path))
    assert bundle["integrity"] is True
    assert bundle["violations"] == []
    assert {item["role"] for item in bundle["artifacts"]} == {
        "completion",
        "input",
        "response",
        "trace",
    }


def test_evidence_bundle_detects_response_tampering(public_root: Path, tmp_path: Path) -> None:
    run_dir = _captured_run(public_root, tmp_path)
    response_path = run_dir / "response.json"
    response = json.loads(response_path.read_text(encoding="utf-8"))
    response["summary"] = "tampered"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    bundle = build_evidence_bundle(run_dir)

    assert bundle["integrity"] is False
    assert "response hash does not match trace" in bundle["violations"]

