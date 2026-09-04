import json

from skillbench.cli import main


def test_verify_command(public_root, capsys):
    assert main(["verify", "--root", str(public_root)]) == 0
    assert "Verification passed" in capsys.readouterr().out


def test_plan_command_writes_three_jobs(public_root, tmp_path):
    output = tmp_path / "plan.json"
    assert main(["plan", "--root", str(public_root), "--output", str(output)]) == 0
    plan = json.loads(output.read_text(encoding="utf-8"))
    assert len(plan["jobs"]) == 3


def test_demo_command_requires_no_credentials(public_root, tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SKILLBENCH_PROVIDER", raising=False)
    assert (
        main(["demo", "--root", str(public_root), "--output", str(tmp_path)])
        == 0
    )
    assert (tmp_path / "report.json").is_file()
    assert (tmp_path / "report.html").is_file()


def test_live_evaluate_explains_missing_provider(public_root, tmp_path, capsys):
    skill = public_root / "examples/public_demo/skill"
    code = main(
        [
            "evaluate",
            "--root",
            str(public_root),
            "--skill",
            str(skill),
            "--profile",
            "development",
            "--output",
            str(tmp_path),
        ]
    )
    assert code == 2
    assert "Live provider is not configured" in capsys.readouterr().err


def test_live_evaluate_explains_beta_boundary(
    public_root, tmp_path, capsys, monkeypatch
):
    monkeypatch.setenv("SKILLBENCH_PROVIDER", "example")
    skill = public_root / "examples/public_demo/skill"
    code = main(
        [
            "evaluate",
            "--root",
            str(public_root),
            "--skill",
            str(skill),
            "--profile",
            "development",
            "--output",
            str(tmp_path),
        ]
    )
    assert code == 2
    assert "Live provider execution is not enabled in this beta" in capsys.readouterr().err
