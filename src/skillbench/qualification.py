from __future__ import annotations

from typing import Any


def qualify(signals: dict[str, Any]) -> dict[str, Any]:
    if not signals.get("runner_ok", False):
        return {"scoring_eligible": False, "reason": "PLATFORM_ERROR"}
    if not signals.get("asset_ok", False):
        return {"scoring_eligible": False, "reason": "EVALUATION_ASSET"}
    if signals.get("skill_required", True) and not signals.get("skill_loaded", False):
        return {"scoring_eligible": False, "reason": "SKILL_EXECUTION"}
    if not signals.get("evidence_sufficient", False):
        return {"scoring_eligible": False, "reason": "INCONCLUSIVE"}
    return {"scoring_eligible": True, "reason": "QUALIFIED"}
