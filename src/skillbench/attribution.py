from __future__ import annotations

from typing import Any


_CAUSAL_ORDER = (
    ("runner_ok", "PLATFORM_ERROR", False),
    ("asset_ok", "EVALUATION_ASSET", False),
    ("skill_loaded", "SKILL_EXECUTION", False),
    ("evidence_sufficient", "INCONCLUSIVE", True),
    ("outcome_ok", "VALID_MODEL_FAILURE", False),
)


def first_deviation(signals: dict[str, Any]) -> dict[str, Any]:
    for field, root_cause, default in _CAUSAL_ORDER:
        if field == "skill_loaded" and not signals.get("skill_required", True):
            continue
        if not signals.get(field, default):
            return {"root_cause": root_cause, "first_deviation": field}
    return {"root_cause": None, "first_deviation": None}
