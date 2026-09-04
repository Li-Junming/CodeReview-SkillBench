from pathlib import Path


def test_frontend_uses_current_api_contract(public_root: Path) -> None:
    api = (public_root / "frontend/lib/api.ts").read_text(encoding="utf-8")
    assert "/api/skills" in api
    assert "/api/runs" in api
    assert "/report?format=html" in api
    assert "/api/skills/upload" not in api
    assert "/api/judge/" not in api


def test_frontend_explains_evaluation_chain(public_root: Path) -> None:
    page = (public_root / "frontend/app/page.tsx").read_text(encoding="utf-8")
    for phrase in ("D0", "C_auto", "C_forced", "证据链", "责任归因"):
        assert phrase in page


def test_frontend_has_reproducible_build_files(public_root: Path) -> None:
    required = (
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/tsconfig.json",
        "frontend/.env.example",
    )
    assert all((public_root / path).is_file() for path in required)


def test_frontend_allows_both_local_development_hosts(public_root: Path) -> None:
    config = (public_root / "frontend/next.config.ts").read_text(encoding="utf-8")
    assert 'allowedDevOrigins: ["127.0.0.1", "localhost"]' in config
