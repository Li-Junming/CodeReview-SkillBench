from skillbench.qualification import qualify


def test_platform_failure_is_not_scored():
    result = qualify(
        {
            "runner_ok": False,
            "asset_ok": True,
            "skill_loaded": True,
            "evidence_sufficient": True,
        }
    )
    assert result == {"scoring_eligible": False, "reason": "PLATFORM_ERROR"}


def test_insufficient_evidence_is_inconclusive():
    result = qualify(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_loaded": True,
            "evidence_sufficient": False,
        }
    )
    assert result == {"scoring_eligible": False, "reason": "INCONCLUSIVE"}


def test_valid_failure_is_scoring_eligible():
    result = qualify(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_loaded": True,
            "evidence_sufficient": True,
        }
    )
    assert result == {"scoring_eligible": True, "reason": "QUALIFIED"}


def test_d0_does_not_require_a_skill_to_be_loaded():
    result = qualify(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_required": False,
            "skill_loaded": False,
            "evidence_sufficient": True,
        }
    )
    assert result == {"scoring_eligible": True, "reason": "QUALIFIED"}
