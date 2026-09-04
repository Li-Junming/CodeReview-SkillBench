from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _public_file(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe frozen path: {relative_path}")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"frozen path escapes root: {relative_path}") from error
    return candidate


def _frozen_paths(root: Path) -> list[str]:
    experiment = _read_json(root / "config" / "experiment.json")
    skills = _read_json(root / "config" / "skills.json")
    paths = list(experiment["frozen_paths"])
    paths.extend(skill["skill_path"] for skill in skills["skills"])
    return sorted(set(paths))


def build_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    experiment = _read_json(root / "config" / "experiment.json")
    skills = _read_json(root / "config" / "skills.json")
    files: dict[str, str] = {}
    for relative_path in _frozen_paths(root):
        path = _public_file(root, relative_path)
        if not path.is_file():
            raise FileNotFoundError(f"frozen file is missing: {relative_path}")
        files[Path(relative_path).as_posix()] = _sha256(path)
    return {
        "schema_version": "0.1",
        "status": "FROZEN",
        "experiment_id": experiment["experiment_id"],
        "skill_bundle_id": skills["bundle_id"],
        "files": files,
    }


def verify_manifest(root: Path) -> list[str]:
    root = root.resolve()
    manifest_path = root / "freeze_manifest.json"
    if not manifest_path.is_file():
        return ["freeze manifest is missing"]
    recorded = _read_json(manifest_path)
    try:
        actual = build_manifest(root)
    except (FileNotFoundError, ValueError) as error:
        return [str(error)]

    violations: list[str] = []
    for field in ("status", "experiment_id", "skill_bundle_id"):
        if recorded.get(field) != actual.get(field):
            violations.append(f"freeze {field} mismatch")
    if recorded.get("files") != actual.get("files"):
        violations.append("freeze file hashes mismatch")

    skills = _read_json(root / "config" / "skills.json")
    for skill in skills["skills"]:
        current_hash = _sha256(_public_file(root, skill["skill_path"]))
        if skill.get("skill_sha256") != current_hash:
            violations.append(f"skill hash mismatch: {skill['skill_id']}")
    return sorted(violations)


def write_freeze(root: Path) -> None:
    root = root.resolve()
    skills_path = root / "config" / "skills.json"
    skills = _read_json(skills_path)
    for skill in skills["skills"]:
        skill["skill_sha256"] = _sha256(_public_file(root, skill["skill_path"]))
    _write_json(skills_path, skills)
    _write_json(root / "freeze_manifest.json", build_manifest(root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze or verify public demo assets")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        write_freeze(args.root)
        print("Freeze written")
        return 0
    violations = verify_manifest(args.root)
    if violations:
        print("\n".join(violations))
        return 1
    print("Freeze verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
