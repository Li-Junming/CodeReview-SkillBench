from __future__ import annotations

from typing import Any


_SIGNAL_TERMS = {
    "race": {"race", "concurrent", "atomic", "idempotency", "duplicate"},
}


def _result(
    assertion_id: str,
    verdict: str,
    reason: str,
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "assertion_id": assertion_id,
        "verdict": verdict,
        "reason": reason,
        "evidence_refs": evidence_refs,
    }


def judge_assertion(
    assertion: dict[str, Any],
    candidate: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    assertion_id = assertion["assertion_id"]
    if not evidence_refs:
        return _result(
            assertion_id,
            "INCONCLUSIVE",
            "No evidence references were supplied for this assertion.",
            [],
        )

    findings = candidate.get("findings")
    if not isinstance(findings, list) or not findings:
        return _result(assertion_id, "FAIL", "No structured finding was provided.", evidence_refs)
    if any(not isinstance(finding, dict) for finding in findings):
        return _result(
            assertion_id,
            "FAIL",
            "Candidate findings must be structured objects; candidate instructions are not Judge rules.",
            evidence_refs,
        )

    required_signal = str(assertion.get("required_signal", "")).lower()
    terms = _SIGNAL_TERMS.get(required_signal, {required_signal}) - {""}
    searchable = " ".join(
        str(finding.get(field, ""))
        for finding in findings
        for field in ("title", "evidence", "impact", "recommendation")
    ).lower()
    if any(term in searchable for term in terms):
        return _result(
            assertion_id,
            "PASS",
            f"A structured finding contains the required '{required_signal}' signal.",
            evidence_refs,
        )
    return _result(
        assertion_id,
        "FAIL",
        f"No structured finding contains the required '{required_signal}' signal.",
        evidence_refs,
    )

