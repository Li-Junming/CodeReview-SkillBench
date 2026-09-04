from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4

from backend.app.models import RunRecord, SkillRecord
from skillbench.common import load_json, write_json
from skillbench.planner import build_plan
from skillbench.report import write_reports
from skillbench.runner import run_replay


MAX_ARCHIVE_BYTES = 2 * 1024 * 1024
MAX_EXPANDED_BYTES = 4 * 1024 * 1024
MAX_FILES = 100


class SkillArchiveError(ValueError):
    pass


def _safe_archive_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name.replace("\\", "/"))
    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or ":" in path.parts[0]
    ):
        raise SkillArchiveError("Archive contains an unsafe path")
    return path


def _skill_name(markdown: str) -> str:
    if not markdown.startswith("---"):
        raise SkillArchiveError("SKILL.md must contain YAML frontmatter")
    match = re.search(r"(?m)^name:\s*([^\r\n]+)$", markdown)
    if not match:
        raise SkillArchiveError("SKILL.md frontmatter must define name")
    return match.group(1).strip().strip('"\'')


def store_skill(data_root: Path, archive_bytes: bytes) -> SkillRecord:
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise SkillArchiveError("ZIP archive exceeds the 2 MB upload limit")
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as error:
        raise SkillArchiveError("Upload must be a valid ZIP archive") from error

    extracted: list[tuple[PurePosixPath, bytes]] = []
    skill_files: list[tuple[PurePosixPath, bytes]] = []
    total_size = 0
    with archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        if len(members) > MAX_FILES:
            raise SkillArchiveError("ZIP archive contains too many files")
        for info in members:
            path = _safe_archive_path(info.filename)
            mode = (info.external_attr >> 16) & 0o170000
            if stat.S_ISLNK(mode):
                raise SkillArchiveError("Archive contains a symbolic link")
            if info.flag_bits & 0x1:
                raise SkillArchiveError("Encrypted ZIP archives are not supported")
            total_size += info.file_size
            if total_size > MAX_EXPANDED_BYTES:
                raise SkillArchiveError("ZIP archive exceeds the 4 MB expanded limit")
            content = archive.read(info)
            extracted.append((path, content))
            if path.name == "SKILL.md":
                skill_files.append((path, content))

    if len(skill_files) != 1:
        raise SkillArchiveError("Archive must contain exactly one SKILL.md")
    try:
        markdown = skill_files[0][1].decode("utf-8")
    except UnicodeDecodeError as error:
        raise SkillArchiveError("SKILL.md must be UTF-8 encoded") from error

    skill_id = uuid4().hex
    skill_dir = data_root.resolve() / "skills" / skill_id
    content_root = skill_dir / "content"
    content_root.mkdir(parents=True, exist_ok=False)
    for relative, content in extracted:
        target = content_root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    record = SkillRecord(
        skill_id=skill_id,
        name=_skill_name(markdown),
        sha256=hashlib.sha256(skill_files[0][1]).hexdigest(),
        file_count=len(extracted),
    )
    write_json(skill_dir / "metadata.json", record.model_dump())
    return record


def load_skill(data_root: Path, skill_id: str) -> SkillRecord | None:
    metadata = data_root.resolve() / "skills" / skill_id / "metadata.json"
    if not metadata.is_file():
        return None
    return SkillRecord.model_validate(load_json(metadata))


def run_offline_demo(data_root: Path, project_root: Path) -> RunRecord:
    run_id = uuid4().hex
    evaluation_root = data_root.resolve() / "evaluations" / run_id
    captured_root = evaluation_root / "captured"
    report_root = evaluation_root / "report"
    for job in build_plan(project_root)["jobs"]:
        response_name = (
            "response.json" if job["condition"] == "C_forced" else "missed_response.json"
        )
        run_replay(
            project_root,
            captured_root,
            job,
            project_root / "examples/public_demo" / response_name,
        )
    json_path, html_path = write_reports(project_root, captured_root, report_root)
    record = RunRecord(
        run_id=run_id,
        profile="offline-demo",
        status="COMPLETED",
        report_json=json_path.relative_to(evaluation_root).as_posix(),
        report_html=html_path.relative_to(evaluation_root).as_posix(),
    )
    write_json(evaluation_root / "metadata.json", record.model_dump())
    return record


def load_run(data_root: Path, run_id: str) -> RunRecord | None:
    metadata = data_root.resolve() / "evaluations" / run_id / "metadata.json"
    if not metadata.is_file():
        return None
    return RunRecord.model_validate(load_json(metadata))


def load_report(data_root: Path, run: RunRecord) -> dict:
    report_path = data_root.resolve() / "evaluations" / run.run_id / run.report_json
    return json.loads(report_path.read_text(encoding="utf-8"))


def html_report_path(data_root: Path, run: RunRecord) -> Path:
    return data_root.resolve() / "evaluations" / run.run_id / run.report_html

