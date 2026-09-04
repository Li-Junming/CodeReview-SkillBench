from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote


LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IGNORED_DIRS = {".git", ".venv", ".worktrees", ".uv-cache", "node_modules", ".next", "build"}


def _markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if not any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            yield path


def check_links(root: Path) -> list[str]:
    root = root.resolve()
    violations: list[str] = []
    for source in _markdown_files(root):
        for target in LINK_RE.findall(source.read_text(encoding="utf-8")):
            target = target.strip().strip("<>").split()[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_text = unquote(target.split("#", 1)[0])
            if not path_text:
                continue
            destination = (source.parent / path_text).resolve()
            try:
                destination.relative_to(root)
            except ValueError:
                violations.append(
                    f"OUTSIDE_ROOT: {source.relative_to(root).as_posix()} -> {target}"
                )
                continue
            if not destination.exists():
                violations.append(
                    f"MISSING: {source.relative_to(root).as_posix()} -> {target}"
                )
    return sorted(violations)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local links in Markdown files")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    violations = check_links(args.root)
    if violations:
        print("\n".join(violations))
        return 1
    print("0 broken links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

