from pathlib import Path


def test_ci_checks_python_frontend_and_release_safety(public_root: Path) -> None:
    workflow = public_root / ".github/workflows/ci.yml"
    text = workflow.read_text(encoding="utf-8")
    for phrase in (
        "actions/checkout@v7",
        "actions/setup-python@v7",
        "actions/setup-node@v7",
        "ubuntu-latest",
        "windows-latest",
        'python-version: ["3.11", "3.12"]',
        "python -m pytest -q",
        "check_release_manifest.py",
        "scan_public_tree.py",
        "check_markdown_links.py",
        "npm run lint",
        "npm run build",
    ):
        assert phrase in text
