from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.models import HealthResponse, RunRecord, RunRequest, SkillRecord
from backend.app.services import (
    MAX_ARCHIVE_BYTES,
    SkillArchiveError,
    html_report_path,
    load_report,
    load_run,
    load_skill,
    run_offline_demo,
    store_skill,
)
from backend.app.settings import (
    default_data_root,
    default_project_root,
    live_provider_configured,
)


def create_app(
    data_root: Path | None = None,
    project_root: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="CodeReview SkillBench API", version="0.1.0-beta")
    app.state.data_root = (data_root or default_data_root()).resolve()
    app.state.project_root = (project_root or default_project_root()).resolve()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version="0.1.0-beta")

    @app.post("/api/skills", response_model=SkillRecord, status_code=201)
    async def upload_skill(file: UploadFile = File(...)) -> SkillRecord:
        content = await file.read(MAX_ARCHIVE_BYTES + 1)
        try:
            return store_skill(app.state.data_root, content)
        except SkillArchiveError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/api/skills/{skill_id}", response_model=SkillRecord)
    def get_skill(skill_id: str) -> SkillRecord:
        record = load_skill(app.state.data_root, skill_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        return record

    @app.post("/api/runs", response_model=RunRecord, status_code=201)
    def create_run(request: RunRequest) -> RunRecord:
        if request.profile != "offline-demo":
            if not live_provider_configured():
                raise HTTPException(status_code=422, detail="Live provider is not configured")
            raise HTTPException(status_code=501, detail="Live provider execution is not enabled in this beta")
        return run_offline_demo(app.state.data_root, app.state.project_root)

    @app.get("/api/runs/{run_id}", response_model=RunRecord)
    def get_run(run_id: str) -> RunRecord:
        record = load_run(app.state.data_root, run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return record

    @app.get("/api/runs/{run_id}/report")
    def get_report(run_id: str, format: str = Query("json", pattern="^(json|html)$")):
        record = load_run(app.state.data_root, run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Run not found")
        if format == "html":
            return FileResponse(html_report_path(app.state.data_root, record), media_type="text/html")
        return load_report(app.state.data_root, record)

    return app


app = create_app()
