from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from skillbench.attribution import first_deviation
from skillbench.common import load_json, write_json
from skillbench.evidence import build_evidence_bundle
from skillbench.judge import judge_assertion
from skillbench.planner import verify_freeze
from skillbench.qualification import qualify


def _case_configs(root: Path) -> dict[str, dict[str, Any]]:
    experiment = load_json(root / "config" / "experiment.json")
    return {case["case_id"]: case for case in experiment["cases"]}


def _evidence_refs(response: dict[str, Any]) -> list[str]:
    refs = [
        f"response:findings/{index}"
        for index, finding in enumerate(response.get("findings", []))
        if isinstance(finding, dict)
    ]
    refs.append("source:payment_service.py#L26-L36")
    return refs


def _evaluate_run(root: Path, run_dir: Path, asset_ok: bool) -> dict[str, Any]:
    completion = load_json(run_dir / "completion.json")
    input_record = load_json(run_dir / "input.json")
    response = load_json(run_dir / "response.json")
    evidence = build_evidence_bundle(run_dir)
    case = _case_configs(root)[completion["case_id"]]
    rubric = load_json(root / case["rubric_path"])
    evidence_refs = _evidence_refs(response) if evidence["integrity"] else []
    judge_results = [
        judge_assertion(assertion, response, evidence_refs)
        for assertion in rubric["assertions"]
    ]
    skill_required = completion["condition"] != "D0"
    skill_loaded = input_record.get("skill") is not None
    qualification = qualify(
        {
            "runner_ok": completion.get("status") == "CAPTURED",
            "asset_ok": asset_ok,
            "skill_required": skill_required,
            "skill_loaded": skill_loaded,
            "evidence_sufficient": evidence["integrity"],
        }
    )
    outcome_ok = bool(judge_results) and all(
        item["verdict"] == "PASS" for item in judge_results
    )
    attribution = first_deviation(
        {
            "runner_ok": completion.get("status") == "CAPTURED",
            "asset_ok": asset_ok,
            "skill_required": skill_required,
            "skill_loaded": skill_loaded,
            "evidence_sufficient": evidence["integrity"],
            "outcome_ok": outcome_ok,
        }
    )
    return {
        "run_id": completion["run_id"],
        "case_id": completion["case_id"],
        "condition": completion["condition"],
        "model_profile": completion["model_profile"],
        "response_summary": str(response.get("summary", "")),
        "judge_results": judge_results,
        "qualification": qualification,
        "attribution": attribution,
        "evidence": evidence,
    }


def _render_html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    run_cards = []
    for run in report["runs"]:
        verdict = run["judge_results"][0]["verdict"] if run["judge_results"] else "INCONCLUSIVE"
        cause = run["attribution"]["root_cause"] or "NONE"
        run_cards.append(
            """
            <article class="run-card">
              <div class="run-head">
                <span class="condition">{condition}</span>
                <span class="verdict verdict-{verdict_class}">{verdict}</span>
              </div>
              <h3>{case_id}</h3>
              <p>{response_summary}</p>
              <dl>
                <div><dt>Qualification</dt><dd>{qualification}</dd></div>
                <div><dt>Attribution</dt><dd>{cause}</dd></div>
                <div><dt>Evidence</dt><dd>{evidence}</dd></div>
              </dl>
            </article>
            """.format(
                condition=html.escape(run["condition"]),
                verdict=html.escape(verdict),
                verdict_class=html.escape(verdict.lower()),
                case_id=html.escape(run["case_id"]),
                response_summary=html.escape(run["response_summary"]),
                qualification=html.escape(run["qualification"]["reason"]),
                cause=html.escape(cause),
                evidence="verified" if run["evidence"]["integrity"] else "invalid",
            )
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CodeReview SkillBench · Demo Report</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, "Segoe UI", sans-serif; background:#07111f; color:#e8f0ff; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:radial-gradient(circle at top right,#12356a 0,#07111f 42%); }}
    main {{ width:min(1080px,calc(100% - 32px)); margin:0 auto; padding:64px 0 80px; }}
    .eyebrow {{ color:#5eead4; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
    h1 {{ margin:.35rem 0; font-size:clamp(2.2rem,6vw,4.5rem); line-height:1; }}
    .boundary {{ color:#a9bbd6; max-width:760px; line-height:1.7; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:34px 0; }}
    .metric,.run-card {{ border:1px solid #24436c; background:rgba(9,25,47,.82); border-radius:18px; padding:20px; box-shadow:0 18px 50px rgba(0,0,0,.18); }}
    .metric strong {{ display:block; font-size:2rem; margin-top:8px; }}
    .runs {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
    .run-head {{ display:flex; justify-content:space-between; align-items:center; }}
    .condition {{ color:#7dd3fc; font-family:ui-monospace,monospace; }}
    .verdict {{ padding:5px 10px; border-radius:999px; font-size:.78rem; font-weight:800; }}
    .verdict-pass {{ background:#064e3b; color:#6ee7b7; }} .verdict-fail {{ background:#581c1c; color:#fca5a5; }}
    .run-card p {{ min-height:72px; color:#afc0d8; line-height:1.55; }}
    dl div {{ display:flex; justify-content:space-between; gap:16px; border-top:1px solid #1d3658; padding:10px 0; }}
    dt {{ color:#8298b8; }} dd {{ margin:0; text-align:right; font-family:ui-monospace,monospace; font-size:.82rem; }}
    footer {{ margin-top:32px; color:#7890b2; }}
    @media(max-width:800px) {{ .summary,.runs {{ grid-template-columns:1fr 1fr; }} }}
    @media(max-width:520px) {{ .summary,.runs {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body><main>
  <div class="eyebrow">Evidence-backed evaluation</div>
  <h1>CodeReview SkillBench</h1>
  <p class="boundary">演示数据，不代表商业模型排名。该报告用于展示固定资产、运行取证、原子判定、计分资格与责任归因链路。</p>
  <section class="summary">
    <div class="metric">Total<strong>{summary['total_runs']}</strong></div>
    <div class="metric">Eligible<strong>{summary['eligible_runs']}</strong></div>
    <div class="metric">Passed<strong>{summary['passed_runs']}</strong></div>
    <div class="metric">Pass rate<strong>{summary['pass_rate']:.1%}</strong></div>
  </section>
  <section class="runs">{''.join(run_cards)}</section>
  <footer>Generated deterministically from the public offline demo.</footer>
</main></body></html>"""


def write_reports(
    root: Path,
    run_root: Path,
    output_root: Path,
) -> tuple[Path, Path]:
    root = root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    try:
        verify_freeze(root)
        asset_ok = True
    except (FileNotFoundError, KeyError, ValueError):
        asset_ok = False

    run_dirs = sorted(path.parent for path in run_root.glob("*/completion.json"))
    runs = [_evaluate_run(root, run_dir, asset_ok) for run_dir in run_dirs]
    eligible = [run for run in runs if run["qualification"]["scoring_eligible"]]
    passed = [
        run
        for run in eligible
        if run["judge_results"]
        and all(result["verdict"] == "PASS" for result in run["judge_results"])
    ]
    report = {
        "schema_version": "0.1",
        "report_type": "PUBLIC_OFFLINE_DEMO",
        "claim_boundary": "演示数据，不代表商业模型排名",
        "summary": {
            "eligible_runs": len(eligible),
            "passed_runs": len(passed),
            "pass_rate": len(passed) / len(eligible) if eligible else 0.0,
            "total_runs": len(runs),
        },
        "runs": runs,
    }
    json_path = output_root / "report.json"
    html_path = output_root / "report.html"
    write_json(json_path, report)
    html_path.write_text(_render_html(report), encoding="utf-8")
    return json_path, html_path

