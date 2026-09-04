from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath

import yaml


def _matches(relative_path: str, pattern: str) -> bool:
    """Match exact paths and directory trees using POSIX-style patterns."""
    normalized = pattern.rstrip("/")
    if normalized.endswith("/**"):
        prefix = normalized[:-3]
        return relative_path == prefix or relative_path.startswith(f"{prefix}/")
    return PurePosixPath(relative_path).match(normalized)


def _matches_any(relative_path: str, patterns: list[str]) -> bool:
    return any(_matches(relative_path, pattern) for pattern in patterns)


def audit_tree(root: Path, manifest_path: Path) -> list[str]:
    """Return stable, sorted release-policy violations for files under root."""
    root = root.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    allowed = list(manifest.get("allowed_now", []))
    denied = list(manifest.get("always_denied", []))
    ignored = list(manifest.get("ignored_local_only", []))
    violations: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if _matches_any(relative, ignored):
            continue
        if _matches_any(relative, denied):
            violations.append(f"DENIED_PATH: {relative}")
        elif not _matches_any(relative, allowed):
            violations.append(f"NOT_ALLOWLISTED: {relative}")

    return sorted(violations)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the public release tree")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    manifest = args.manifest or args.root / "release" / "public_promotion_manifest.yaml"
    violations = audit_tree(args.root, manifest)
    if violations:
        print("\n".join(violations))
        return 1
    print("Release manifest check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
