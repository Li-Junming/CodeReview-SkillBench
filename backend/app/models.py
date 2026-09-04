from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class SkillRecord(BaseModel):
    skill_id: str
    name: str
    sha256: str
    file_count: int


class RunRequest(BaseModel):
    profile: Literal["offline-demo", "development"] = "offline-demo"
    skill_id: str | None = None


class RunRecord(BaseModel):
    run_id: str
    profile: str
    status: Literal["COMPLETED", "FAILED"]
    report_json: str
    report_html: str

