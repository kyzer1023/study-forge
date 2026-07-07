from __future__ import annotations

from datetime import datetime

from scripts.pastyear_proof_common import (
    CLAIMED_READINESS,
    DEGRADED_REPORT_MODES,
    evidence_text,
    normalized,
    text_field,
)
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData
from scripts.pastyear_proof_readiness import readiness_state, report_mode, report_statuses

READY_CLAIM_TERMS = ("exam-ready", "exam ready", "ready", "independent_verified", "independent verified")
FALLBACK_MODE_TERMS = ("fallback_local", "fallback local", "fallback_local_reviewed", "fallback local reviewed")
RENDERED_TIME_FIELDS = ("rendered_artifact_updated_at", "rendered_html_updated_at", "artifact_updated_at", "index_html_updated_at")
FINAL_GATE_TIME_FIELDS = ("final_gate_updated_at", "final_parent_gate_updated_at", "verified_at", "checked_at")
RESOLUTION_FIELDS = ("resolved_findings", "retained_findings", "finding_resolution_map", "intentionally_retained_findings")


def parse_iso_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def first_time(container: JsonObject, fields: tuple[str, ...]) -> datetime | None:
    for field in fields:
        parsed = parse_iso_datetime(text_field(container, field))
        if parsed is not None:
            return parsed
    return None


def json_object_entries(value: JsonValue | None) -> tuple[JsonObject, ...]:
    if isinstance(value, list):
        return tuple(entry for entry in value if isinstance(entry, dict))
    if isinstance(value, dict):
        entries = value.get("entries")
        if isinstance(entries, list):
            return tuple(entry for entry in entries if isinstance(entry, dict))
    return ()


def has_fallback_exam_ready_overclaim(data: ProofData) -> bool:
    payload: list[JsonValue] = [data.qa_report]
    payload.extend(data.verifier_reports)
    text = evidence_text(payload)
    if not any(term in text for term in FALLBACK_MODE_TERMS):
        return False
    return any(term in text for term in READY_CLAIM_TERMS)


def answer_production_entries(qa_report: JsonObject) -> tuple[JsonObject, ...]:
    return json_object_entries(qa_report.get("answer_production"))


def has_fallback_answer_production(data: ProofData) -> bool:
    for entry in answer_production_entries(data.qa_report):
        if normalized(text_field(entry, "invocation_mode")) in DEGRADED_REPORT_MODES:
            return True
    return any(report_mode(report) in DEGRADED_REPORT_MODES for report in data.verifier_reports)


def has_resolution_map(report: JsonObject, qa_report: JsonObject) -> bool:
    return any(report.get(field) is not None or qa_report.get(field) is not None for field in RESOLUTION_FIELDS)


def add_stale_report_issues(data: ProofData, issues: list[Issue]) -> None:
    rendered_time = first_time(data.qa_report, RENDERED_TIME_FIELDS)
    if rendered_time is None:
        return
    final_gate_time = first_time(data.qa_report, FINAL_GATE_TIME_FIELDS)
    if final_gate_time is not None and final_gate_time <= rendered_time:
        issues.append(
            Issue(
                IssueCode.STALE_VERIFIER_REPORT,
                "qa-report.json",
                "final gate evidence is not newer than the rendered artifact",
            )
        )
    for report in data.verifier_reports:
        report_time = first_time(report, FINAL_GATE_TIME_FIELDS)
        if report_time is not None and report_time <= rendered_time:
            lane = text_field(report, "lane") or "<unknown lane>"
            issues.append(
                Issue(
                    IssueCode.STALE_VERIFIER_REPORT,
                    f"verifier-reports/{lane}.json",
                    "verifier report is not newer than the rendered artifact",
                )
            )


def add_unresolved_major_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    if readiness not in CLAIMED_READINESS:
        return
    for report in data.verifier_reports:
        statuses = set(report_statuses(report))
        if "major" in statuses and not has_resolution_map(report, data.qa_report):
            lane = text_field(report, "lane") or "<unknown lane>"
            issues.append(
                Issue(
                    IssueCode.UNRESOLVED_FINDING_IN_READY_REPORT,
                    f"verifier-reports/{lane}.json",
                    "claimed readiness cannot supersede MAJOR findings without resolved or retained finding metadata",
                )
            )


def add_readiness_contract_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    if has_fallback_answer_production(data) and (
        readiness == "independent_verified" or has_fallback_exam_ready_overclaim(data)
    ):
        issues.append(
            Issue(
                IssueCode.FALLBACK_LOCAL_EXAM_READY_OVERCLAIM,
                "qa-report.json",
                "fallback-local answer production is claimed as independent or exam-ready",
            )
        )
    add_stale_report_issues(data, issues)
    add_unresolved_major_issues(data, issues)
