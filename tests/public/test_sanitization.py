from pathlib import Path

from scripts.scan_public_tree import scan_tree


def test_public_tree_contains_no_sensitive_material(public_root: Path) -> None:
    assert scan_tree(public_root) == []


def test_scanner_reports_a_secret_and_absolute_user_path(tmp_path: Path) -> None:
    unsafe = tmp_path / "unsafe.txt"
    fake_secret = "sk-" + "test-secret-value-1234567890"
    unsafe.write_text(
        f"Authorization: Bearer {fake_secret}\n"
        "C:\\Users\\someone\\private\\run.json\n",
        encoding="utf-8",
    )
    violations = scan_tree(tmp_path)
    rules = {violation.rule for violation in violations}
    assert {"SECRET", "WINDOWS_USER_PATH"} <= rules
