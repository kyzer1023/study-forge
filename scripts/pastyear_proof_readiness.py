from __future__ import annotations

from scripts.pastyear_proof_common import (
    CHILD_PROOF_FIELDS,
    CLAIMED_READINESS,
    DEGRADED_GRANULARITY_STATUSES,
    DEGRADED_REPORT_MODES,
    SUBPART_EXPECTING_GRANULARITY_STATUSES,
    WORKER_COVERAGE_INT_FIELDS,
    WORKER_COVERAGE_TEXT_FIELDS,
    has_evidence_value,
    has_string_key,
    non_negative_int_field,
    normalized,
    string_list_field,
    text_field,
)
from scripts.pastyear_proof_inventory import paper_entries, paper_id
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, ProofData


def bool_from_preflight(container: JsonObject) -> bool | None:
    preflight = container.get("tooling_preflight")
    if isinstance(preflight, dict):
        value = preflight.get("available")
        if isinstance(value, bool):
            return value
    return None


def readiness_state(qa_report: JsonObject) -> str:
    value = text_field(qa_report, "readiness_state") or text_field(qa_report, "readiness")
    if value is None:
        return "baseline_unverified"
    return normalized(value)


def report_mode(report: JsonObject) -> str:
    value = text_field(report, "invocation_mode") or text_field(report, "mode")
    return normalized(value)


def report_is_independent(report: JsonObject, overall_readiness: str) -> bool:
    mode = report_mode(report)
    report_readiness = normalized(text_field(report, "readiness_state"))
    return (
        overall_readiness == "independent_verified"
        or report_readiness == "independent_verified"
        or mode in {"independent_subagent", "independent_verified", "installed_verifier"}
    )


def tooling_preflight_values(data: ProofData) -> tuple[bool, ...]:
    sources: list[JsonObject] = []
    if data.session_summary is not None:
        sources.append(data.session_summary)
    sources.append(data.qa_report)
    sources.extend(data.verifier_reports)
    values: list[bool] = []
    for source in sources:
        value = bool_from_preflight(source)
        if value is not None:
            values.append(value)
    return tuple(values)


def tooling_available(data: ProofData) -> bool | None:
    values = tooling_preflight_values(data)
    if not values:
        return None
    return values[0]


def report_statuses(report: JsonObject) -> tuple[str, ...]:
    statuses = [normalized(text_field(report, "status"))]
    findings = report.get("findings")
    if isinstance(findings, list):
        statuses.extend(normalized(text_field(item, "status")) for item in findings if isinstance(item, dict))
    return tuple(status for status in statuses if status)


def session_child_ids(summary: JsonObject | None) -> set[str] | None:
    if summary is None:
        return None
    child_ids: set[str] = set()
    for key in ("thread_spawn_edges", "spawn_wait_close_calls"):
        entries = summary.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, str) and entry.strip():
                child_ids.add(entry.strip())
            if isinstance(entry, dict):
                child_ids.update(str(entry[field]).strip() for field in ("child_thread_id", "child_agent_id", "target") if entry.get(field))
    return child_ids


def granularity_status(paper: JsonObject) -> str:
    granularity = paper.get("extraction_granularity")
    if isinstance(granularity, dict):
        return normalized(text_field(granularity, "status"))
    return ""


def has_degraded_granularity(data: ProofData) -> bool:
    return any(granularity_status(paper) in DEGRADED_GRANULARITY_STATUSES for paper in paper_entries(data.question_inventory))


def add_extraction_granularity_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    for index, paper in enumerate(paper_entries(data.question_inventory)):
        current_paper_id = paper_id(paper, index)
        granularity = paper.get("extraction_granularity")
        if not isinstance(granularity, dict):
            issues.append(
                Issue(
                    IssueCode.MISSING_EXTRACTION_GRANULARITY,
                    "question-inventory.json",
                    f"{current_paper_id} missing extraction_granularity object",
                )
            )
            continue
        missing_fields: list[str] = []
        status = normalized(text_field(granularity, "status"))
        if not status:
            missing_fields.append("status")
        if not has_evidence_value(granularity.get("source_structure_evidence")):
            missing_fields.append("source_structure_evidence")
        expected = granularity.get("expected_answerable_subparts")
        has_expected = isinstance(expected, list) and any(
            isinstance(entry, dict) and text_field(entry, "question_id") is not None
            for entry in expected
        )
        if status in SUBPART_EXPECTING_GRANULARITY_STATUSES and not has_expected:
            missing_fields.append("expected_answerable_subparts")
        if missing_fields:
            issues.append(
                Issue(
                    IssueCode.MISSING_EXTRACTION_GRANULARITY,
                    "question-inventory.json",
                    f"{current_paper_id} extraction_granularity missing {', '.join(missing_fields)}",
                )
            )
        if status in DEGRADED_GRANULARITY_STATUSES:
            issues.append(
                Issue(
                    IssueCode.DEGRADED_EXTRACTION_GRANULARITY,
                    "question-inventory.json",
                    f"{current_paper_id} extraction_granularity.status={status} cannot support readiness {readiness}",
                )
            )


def worker_coverage_entries(qa_report: JsonObject) -> tuple[JsonObject, ...]:
    for field in ("worker_coverage", "worker_coverage_metadata"):
        value = qa_report.get(field)
        if isinstance(value, list):
            return tuple(entry for entry in value if isinstance(entry, dict))
        if isinstance(value, dict):
            entries = value.get("entries")
            if isinstance(entries, list):
                return tuple(entry for entry in entries if isinstance(entry, dict))
    return ()


def worker_coverage_missing_fields(entry: JsonObject) -> tuple[str, ...]:
    missing: list[str] = []
    for field in WORKER_COVERAGE_TEXT_FIELDS:
        if text_field(entry, field) is None:
            missing.append(field)
    for field in WORKER_COVERAGE_INT_FIELDS:
        if not non_negative_int_field(entry, field):
            missing.append(field)
    if not string_list_field(entry, "paper_ids"):
        missing.append("paper_ids")
    if text_field(entry, "question_id_range") is None and not string_list_field(entry, "subpart_ids"):
        missing.append("question_id_range or subpart_ids")
    if entry.get("parent_validated") is not True:
        missing.append("parent_validated")
    if not has_string_key(entry, "missing_report_reason"):
        missing.append("missing_report_reason")
    return tuple(missing)


def add_worker_coverage_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    if readiness not in CLAIMED_READINESS or has_degraded_granularity(data):
        return
    entries = worker_coverage_entries(data.qa_report)
    if not entries:
        issues.append(
            Issue(
                IssueCode.MISSING_WORKER_COVERAGE_METADATA,
                "qa-report.json",
                "claimed non-degraded readiness requires worker_coverage metadata",
            )
        )
        return
    for index, entry in enumerate(entries):
        missing = worker_coverage_missing_fields(entry)
        if missing:
            issues.append(
                Issue(
                    IssueCode.MISSING_WORKER_COVERAGE_METADATA,
                    "qa-report.json",
                    f"worker_coverage[{index}] missing {', '.join(missing)}",
                )
            )
        raw_path = text_field(entry, "raw_child_report_path")
        if raw_path is not None and not (data.proof_dir / raw_path).is_file():
            issues.append(
                Issue(
                    IssueCode.MISSING_WORKER_COVERAGE_METADATA,
                    "qa-report.json",
                    f"worker_coverage[{index}] raw child report path does not exist: {raw_path}",
                )
            )


def add_report_child_proof_issues(
    data: ProofData,
    issues: list[Issue],
    report: JsonObject,
    lane: str,
    linked_children: set[str] | None,
) -> None:
    for field in CHILD_PROOF_FIELDS:
        if text_field(report, field) is None:
            issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", f"missing {field}"))
    if report.get("parent_validated") is not True:
        issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", "parent_validated must be true"))
    raw_path = text_field(report, "raw_child_report_path")
    if raw_path is not None and not (data.proof_dir / raw_path).is_file():
        issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", f"raw child report path does not exist: {raw_path}"))
    child_ids = {value for value in (text_field(report, "child_thread_id"), text_field(report, "child_agent_id")) if value is not None}
    report_readiness = normalized(text_field(report, "readiness_state"))
    if report_readiness == "independent_verified" and (linked_children is None or not (child_ids & linked_children)):
        issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE, f"verifier-reports/{lane}.json", "independent_verified requires session summary linkage for child id/thread id"))


def add_readiness_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    add_extraction_granularity_issues(data, issues)
    add_worker_coverage_issues(data, issues)
    preflight_values = tooling_preflight_values(data)
    available = tooling_available(data)
    if len(set(preflight_values)) > 1:
        issues.append(Issue(IssueCode.CONFLICTING_TOOLING_PREFLIGHT, "tooling_preflight.available", "conflicting tooling_preflight.available values across session, QA, or verifier reports"))
    report_claimed_readiness = any(normalized(text_field(report, "readiness_state")) in CLAIMED_READINESS for report in data.verifier_reports)
    if (readiness in CLAIMED_READINESS or report_claimed_readiness) and available is None:
        issues.append(Issue(IssueCode.MISSING_PREFLIGHT_FOR_CLAIMED_READINESS, "qa-report.json", "claimed readiness requires tooling_preflight.available"))
    linked_children = session_child_ids(data.session_summary)
    for report in data.verifier_reports:
        lane = text_field(report, "lane") or "<unknown lane>"
        mode = report_mode(report)
        report_readiness = normalized(text_field(report, "readiness_state"))
        if mode in DEGRADED_REPORT_MODES and (available is True or readiness == "independent_verified" or report_readiness == "independent_verified"):
            issues.append(Issue(IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD, f"verifier-reports/{lane}.json", f"{mode} report cannot satisfy independent readiness or readiness while tooling_preflight.available is true"))
        report_claims_readiness = report_readiness in CLAIMED_READINESS
        if (readiness in CLAIMED_READINESS or report_claims_readiness) and "blocking" in report_statuses(report):
            issues.append(Issue(IssueCode.BLOCKING_FINDING_IN_READY_REPORT, f"verifier-reports/{lane}.json", "claimed readiness cannot include BLOCKING report or finding status"))
        if report_is_independent(report, readiness):
            add_report_child_proof_issues(data, issues, report, lane, linked_children)
