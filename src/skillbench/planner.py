from __future__ import annotations

from pathlib import Path
from typing import Any

from skillbench.common import canonical_sha256, load_json, resolve_under, sha256_file


def verify_freeze(root: Path) -> None:
    root = root.resolve()
    experiment = load_json(root / "config" / "experiment.json")
    skills = load_json(root / "config" / "skills.json")
    freeze = load_json(root / "freeze_manifest.json")

    if experiment.get("status") != "FROZEN" or freeze.get("status") != "FROZEN":
        raise ValueError("freeze status is not FROZEN")
    if freeze.get("experiment_id") != experiment.get("experiment_id"):
        raise ValueError("freeze experiment does not match experiment config")
    if freeze.get("skill_bundle_id") != skills.get("bundle_id"):
        raise ValueError("freeze skill bundle does not match skills config")

    recorded_files = freeze.get("files", {})
    for relative_path, expected_hash in recorded_files.items():
        path = resolve_under(root, relative_path)
        if not path.is_file():
            raise FileNotFoundError(f"frozen file is missing: {relative_path}")
        if sha256_file(path) != expected_hash:
            raise ValueError(f"frozen file hash mismatch: {relative_path}")

    for skill in skills["skills"]:
        path = resolve_under(root, skill["skill_path"])
        if sha256_file(path) != skill["skill_sha256"]:
            raise ValueError(f"skill hash mismatch: {skill['skill_id']}")


def build_plan(root: Path) -> dict[str, Any]:
    root = root.resolve()
    verify_freeze(root)
    experiment = load_json(root / "config" / "experiment.json")
    skills = load_json(root / "config" / "skills.json")
    cases = {item["case_id"]: item for item in experiment["cases"]}
    jobs: list[dict[str, Any]] = []

    for case_id in experiment["case_ids"]:
        case = cases[case_id]
        for skill in skills["skills"]:
            for condition in experiment["conditions"]:
                for model_profile in experiment["model_profiles"]:
                    for repetition in range(1, experiment["repetitions"] + 1):
                        run_id = (
                            f"{case_id}__{skill['skill_id']}__{condition}__"
                            f"{model_profile}__R{repetition}"
                        )
                        jobs.append(
                            {
                                "run_id": run_id,
                                "case_id": case_id,
                                "candidate_visible_path": case["candidate_visible_path"],
                                "skill_id": skill["skill_id"],
                                "skill_path": skill["skill_path"],
                                "skill_sha256": skill["skill_sha256"],
                                "condition": condition,
                                "model_profile": model_profile,
                                "repetition": repetition,
                            }
                        )

    return {
        "schema_version": "0.1",
        "experiment_id": experiment["experiment_id"],
        "freeze_fingerprint_sha256": canonical_sha256(
            {"experiment": experiment, "skills": skills, "freeze": load_json(root / "freeze_manifest.json")}
        ),
        "jobs": jobs,
    }

