from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from skillbench.common import write_json
from skillbench.planner import build_plan, verify_freeze
from skillbench.report import write_reports
from skillbench.runner import run_replay


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillbench",
        description="Evidence-backed evaluation for Code Review Agent Skills",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    verify = subcommands.add_parser("verify", help="verify frozen public assets")
    verify.add_argument("--root", type=Path, default=Path.cwd())

    plan = subcommands.add_parser("plan", help="write the deterministic run plan")
    plan.add_argument("--root", type=Path, default=Path.cwd())
    plan.add_argument("--output", type=Path, required=True)

    demo = subcommands.add_parser("demo", help="run the offline public demonstration")
    demo.add_argument("--root", type=Path, default=Path.cwd())
    demo.add_argument("--output", type=Path, required=True)

    evaluate = subcommands.add_parser("evaluate", help="run a live development evaluation")
    evaluate.add_argument("--root", type=Path, default=Path.cwd())
    evaluate.add_argument("--skill", type=Path, required=True)
    evaluate.add_argument("--profile", default="development")
    evaluate.add_argument("--output", type=Path, required=True)

    report = subcommands.add_parser("report", help="build reports from captured runs")
    report.add_argument("--root", type=Path, default=Path.cwd())
    report.add_argument("--runs", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)

    serve = subcommands.add_parser("serve", help="start the local API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def _run_demo(root: Path, output: Path) -> None:
    run_root = output / ".runs"
    for job in build_plan(root)["jobs"]:
        response_name = (
            "response.json" if job["condition"] == "C_forced" else "missed_response.json"
        )
        run_replay(root, run_root, job, root / "examples/public_demo" / response_name)
    write_reports(root, run_root, output)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "verify":
            verify_freeze(args.root)
            print("Verification passed")
            return 0
        if args.command == "plan":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.output, build_plan(args.root))
            print(f"Plan written: {args.output}")
            return 0
        if args.command == "demo":
            _run_demo(args.root.resolve(), args.output.resolve())
            print(f"Demo report written: {args.output / 'report.html'}")
            return 0
        if args.command == "evaluate":
            if not os.getenv("SKILLBENCH_PROVIDER"):
                print(
                    "Live provider is not configured. Set SKILLBENCH_PROVIDER and the provider credentials, or run 'skillbench demo'.",
                    file=sys.stderr,
                )
                return 2
            print(
                "Live provider execution is not enabled in this beta; use 'skillbench demo' for the credential-free workflow.",
                file=sys.stderr,
            )
            return 2
        if args.command == "report":
            write_reports(args.root.resolve(), args.runs.resolve(), args.output.resolve())
            print(f"Report written: {args.output / 'report.html'}")
            return 0
        if args.command == "serve":
            try:
                import uvicorn
            except ImportError:
                print("Server dependencies are not installed.", file=sys.stderr)
                return 2
            uvicorn.run("backend.app.main:app", host=args.host, port=args.port)
            return 0
    except (FileExistsError, FileNotFoundError, KeyError, ValueError) as error:
        print(f"SkillBench error: {error}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
