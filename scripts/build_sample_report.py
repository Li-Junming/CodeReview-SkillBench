from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillbench.planner import build_plan  # noqa: E402
from skillbench.report import write_reports  # noqa: E402
from skillbench.runner import run_replay  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="skillbench-public-demo-") as temp:
        run_root = Path(temp) / "runs"
        for job in build_plan(ROOT)["jobs"]:
            response_name = (
                "response.json" if job["condition"] == "C_forced" else "missed_response.json"
            )
            run_replay(ROOT, run_root, job, ROOT / "examples/public_demo" / response_name)
        write_reports(ROOT, run_root, ROOT / "reports/sample")
    print("Sample report written to reports/sample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
