from pathlib import Path

from scripts.check_release_manifest import audit_tree


def test_repository_tree_matches_public_allowlist() -> None:
    root = Path(__file__).resolve().parents[2]
    violations = audit_tree(root, root / "release" / "public_promotion_manifest.yaml")
    assert violations == []


def test_env_example_is_public_but_local_env_is_denied(tmp_path: Path) -> None:
    manifest = Path(__file__).resolve().parents[2] / "release" / "public_promotion_manifest.yaml"
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / ".env.example").write_text("NEXT_PUBLIC_API=http://127.0.0.1:8000\n", encoding="utf-8")
    (frontend / ".env.local").write_text("SECRET=do-not-publish\n", encoding="utf-8")

    violations = audit_tree(tmp_path, manifest)

    assert "DENIED_PATH: frontend/.env.example" not in violations
    assert "DENIED_PATH: frontend/.env.local" in violations
