from pathlib import Path

from scripts.check_markdown_links import check_links


def test_readme_contains_a_credential_free_quickstart(public_root: Path) -> None:
    readme = (public_root / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "pip install",
        "skillbench verify",
        "skillbench demo",
        "不需要 API Key",
        "PRIVATE BETA",
    ):
        assert phrase in readme


def test_all_local_markdown_links_resolve(public_root: Path) -> None:
    assert check_links(public_root) == []


def test_documentation_covers_user_and_maintainer_workflows(public_root: Path) -> None:
    required = (
        "docs/getting-started.md",
        "docs/user-guide.md",
        "docs/architecture.md",
        "docs/methodology.md",
        "docs/judge-and-evidence.md",
        "docs/bad-case-attribution.md",
        "docs/model-configuration.md",
        "docs/api-reference.md",
        "docs/faq.md",
        "docs/project-background.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "THIRD_PARTY_NOTICES.md",
        "LICENSE",
    )
    assert all((public_root / path).is_file() for path in required)

