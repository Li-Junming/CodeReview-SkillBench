import json

from scripts.freeze_public_demo import verify_manifest


def test_public_demo_is_complete_and_frozen(public_root):
    assert (public_root / "examples/public_demo/skill/SKILL.md").is_file()
    assert (
        public_root
        / "testcases/public/DEMO-CONCURRENCY-001/candidate_visible/case.json"
    ).is_file()
    assert verify_manifest(public_root) == []


def test_public_demo_has_three_controlled_conditions(public_root):
    experiment = json.loads(
        (public_root / "config/experiment.json").read_text(encoding="utf-8")
    )
    assert experiment["conditions"] == ["D0", "C_auto", "C_forced"]


def test_public_case_contains_no_hidden_answer(public_root):
    visible = public_root / "testcases/public/DEMO-CONCURRENCY-001/candidate_visible"
    public_text = "\n".join(
        path.read_text(encoding="utf-8") for path in visible.rglob("*") if path.is_file()
    ).lower()
    assert "answer_key" not in public_text
    assert "expected_finding" not in public_text
