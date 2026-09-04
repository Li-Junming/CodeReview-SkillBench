from pathlib import Path

from skillbench.planner import build_plan, verify_freeze


def test_plan_has_unique_run_ids(public_root: Path) -> None:
    plan = build_plan(public_root)
    run_ids = [job["run_id"] for job in plan["jobs"]]
    assert len(run_ids) == len(set(run_ids))
    assert len(run_ids) == 3


def test_plan_preserves_three_controlled_conditions(public_root: Path) -> None:
    plan = build_plan(public_root)
    assert [job["condition"] for job in plan["jobs"]] == [
        "D0",
        "C_auto",
        "C_forced",
    ]


def test_public_demo_freeze_is_valid(public_root: Path) -> None:
    verify_freeze(public_root)

