from skillbench.attribution import first_deviation


def test_first_deviation_respects_causal_order():
    result = first_deviation(
        {
            "runner_ok": True,
            "asset_ok": False,
            "skill_loaded": False,
            "outcome_ok": False,
        }
    )
    assert result["root_cause"] == "EVALUATION_ASSET"
    assert result["first_deviation"] == "asset_ok"


def test_model_failure_requires_all_upstream_gates_to_pass():
    result = first_deviation(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_loaded": True,
            "outcome_ok": False,
        }
    )
    assert result["root_cause"] == "VALID_MODEL_FAILURE"


def test_insufficient_evidence_stops_before_model_attribution():
    result = first_deviation(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_loaded": True,
            "evidence_sufficient": False,
            "outcome_ok": False,
        }
    )
    assert result == {
        "root_cause": "INCONCLUSIVE",
        "first_deviation": "evidence_sufficient",
    }


def test_no_failure_has_no_root_cause():
    result = first_deviation(
        {
            "runner_ok": True,
            "asset_ok": True,
            "skill_loaded": True,
            "outcome_ok": True,
        }
    )
    assert result == {"root_cause": None, "first_deviation": None}
