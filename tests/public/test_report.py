import json
from pathlib import Path

from jsonschema import validate

from skillbench.planner import build_plan
from skillbench.report import write_reports
from skillbench.runner import run_replay


def _build_demo_runs(public_root: Path, run_root: Path) -> None:
    for job in build_plan(public_root)["jobs"]:
        response_name = "response.json" if job["condition"] == "C_forced" else "missed_response.json"
        run_replay(
            public_root,
            run_root,
            job,
            public_root / "examples/public_demo" / response_name,
        )


def test_report_is_schema_valid_and_html_is_self_contained(public_root, tmp_path):
    run_root = tmp_path / "runs"
    output_root = tmp_path / "report"
    _build_demo_runs(public_root, run_root)

    json_path, html_path = write_reports(public_root, run_root, output_root)

    schema = json.loads(
        (public_root / "schemas/report.schema.json").read_text(encoding="utf-8")
    )
    report = json.loads(json_path.read_text(encoding="utf-8"))
    validate(report, schema)
    assert report["summary"] == {
        "eligible_runs": 3,
        "passed_runs": 1,
        "pass_rate": 1 / 3,
        "total_runs": 3,
    }
    assert [run["condition"] for run in report["runs"]] == [
        "D0",
        "C_auto",
        "C_forced",
    ]
    html = html_path.read_text(encoding="utf-8")
    assert "<html" in html.lower()
    assert "CodeReview SkillBench" in html
    assert "演示数据，不代表商业模型排名" in html
    assert "file://" not in html
    assert "C:\\Users" not in html


def test_failed_qualified_run_is_attributed_to_model(public_root, tmp_path):
    run_root = tmp_path / "runs"
    output_root = tmp_path / "report"
    _build_demo_runs(public_root, run_root)

    json_path, _ = write_reports(public_root, run_root, output_root)
    report = json.loads(json_path.read_text(encoding="utf-8"))
    d0 = next(item for item in report["runs"] if item["condition"] == "D0")

    assert d0["judge_results"][0]["verdict"] == "FAIL"
    assert d0["qualification"]["scoring_eligible"] is True
    assert d0["attribution"]["root_cause"] == "VALID_MODEL_FAILURE"
