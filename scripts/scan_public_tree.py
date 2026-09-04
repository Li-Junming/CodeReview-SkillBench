from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".venv",
    ".worktrees",
    ".uv-cache",
    ".pytest_cache",
    ".next",
    ".skillbench-data",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
}
TEXT_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
DENIED_PARTS = {"evaluator_only", "holdout", "private", "raw_transcripts"}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret)\s*[=:]\s*['\"][^'\"\r\n]{12,}"),
)
WINDOWS_USER_PATH = re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+\\")
FILE_URI = re.compile("(?i)" + "file:" + "///")


@dataclass(frozen=True, order=True)
class Violation:
    path: str
    rule: str
    line: int

    def __str__(self) -> str:
        location = f":{self.line}" if self.line else ""
        return f"{self.rule}: {self.path}{location}"


def _candidate_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        yield path, relative


def scan_tree(root: Path) -> list[Violation]:
    root = root.resolve()
    violations: list[Violation] = []
    for path, relative in _candidate_files(root):
        relative_text = relative.as_posix()
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & DENIED_PARTS:
            violations.append(Violation(relative_text, "PRIVATE_ASSET_PATH", 0))
        if path.name.lower() == "eval-secrets.ps1":
            violations.append(Violation(relative_text, "SECRET_FILE", 0))
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(Violation(relative_text, "NON_UTF8_TEXT", 0))
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                violations.append(Violation(relative_text, "SECRET", line_number))
            if WINDOWS_USER_PATH.search(line):
                violations.append(Violation(relative_text, "WINDOWS_USER_PATH", line_number))
            if FILE_URI.search(line):
                violations.append(Violation(relative_text, "FILE_URI", line_number))
    return sorted(set(violations))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan the release tree for sensitive material")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    violations = scan_tree(args.root)
    if violations:
        print("\n".join(str(item) for item in violations))
        return 1
    print("Public tree scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
