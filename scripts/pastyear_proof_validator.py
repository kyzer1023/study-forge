from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Final, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

REQUIRED_FILES: Final = ("source-inventory.json", "question-inventory.json", "source-index.json", "answer-ledger.json", "qa-report.json")
CLAIMED_READINESS: Final = frozenset((
    "independent_verified",
    "fallback_local_reviewed",
))
ANSWERED_STATUSES: Final = frozenset({"answered from source", "answered_from_source", "answered"})
CHILD_PROOF_FIELDS: Final = ("child_agent_id", "child_thread_id", "raw_child_report_path")


class IssueCode(StrEnum):
    ANSWERED_WITHOUT_SOURCE_REFS = "answered_without_source_refs"
    BLOCKING_FINDING_IN_READY_REPORT = "blocking_finding_in_ready_report"
    CONFLICTING_TOOLING_PREFLIGHT = "conflicting_tooling_preflight"
    FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD = "fallback_local_without_independent_child"
    INDEPENDENT_REPORT_MISSING_CHILD_PROOF = "independent_report_missing_child_proof"
    INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE = "independent_report_missing_session_linkage"
    INVALID_JSON = "invalid_json"
    MISSING_PREFLIGHT_FOR_CLAIMED_READINESS = "missing_preflight_for_claimed_readiness"
    MISSING_REQUIRED_DOC = "missing_required_doc"
    USAGE_ERROR = "usage_error"


@dataclass(frozen=True, slots=True)
class Issue:
    code: IssueCode
    path: str
    detail: str


@dataclass(frozen=True, slots=True)
class ProofData:
    proof_dir: Path
    qa_report: JsonObject
    answer_ledger: JsonValue
    verifier_reports: tuple[JsonObject, ...]
    session_summary: JsonObject | None


def load_json(path: Path, issues: list[Issue]) -> JsonValue:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(path), "file is required"))
    except json.JSONDecodeError as exc:
        issues.append(Issue(IssueCode.INVALID_JSON, str(path), f"{exc.msg} at line {exc.lineno}"))
    return None


def as_object(value: JsonValue, path: Path, issues: list[Issue]) -> JsonObject:
    if isinstance(value, dict):
        return value
    issues.append(Issue(IssueCode.INVALID_JSON, str(path), "expected JSON object"))
    return {}


def text_field(container: JsonObject, field: str) -> str | None:
    value = container.get(field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def normalized(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower().replace("-", "_")


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


def load_proof(proof_dir: Path, session_summary: Path | None, issues: list[Issue]) -> ProofData:
    for name in REQUIRED_FILES:
        if not (proof_dir / name).is_file():
            issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(proof_dir / name), "file is required"))
    reports_dir = proof_dir / "verifier-reports"
    if not reports_dir.is_dir():
        issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(reports_dir), "directory is required"))
        reports: tuple[JsonObject, ...] = ()
    else:
        reports = tuple(as_object(load_json(path, issues), path, issues) for path in sorted(reports_dir.glob("*.json")))
        if not reports:
            issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(reports_dir), "at least one verifier report is required"))

    qa_path = proof_dir / "qa-report.json"
    ledger_path = proof_dir / "answer-ledger.json"
    summary = None
    if session_summary is not None:
        summary = as_object(load_json(session_summary, issues), session_summary, issues)
    return ProofData(
        proof_dir=proof_dir,
        qa_report=as_object(load_json(qa_path, issues), qa_path, issues),
        answer_ledger=load_json(ledger_path, issues),
        verifier_reports=reports,
        session_summary=summary,
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


def ledger_entries(value: JsonValue) -> tuple[JsonObject, ...]:
    if isinstance(value, list):
        return tuple(entry for entry in value if isinstance(entry, dict))
    if isinstance(value, dict):
        for key in ("answers", "entries", "items"):
            entries = value.get(key)
            if isinstance(entries, list):
                return tuple(entry for entry in entries if isinstance(entry, dict))
    return ()


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


def add_readiness_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
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
        if mode == "fallback_local" and (available is True or readiness == "independent_verified" or report_readiness == "independent_verified"):
            issues.append(Issue(IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD, f"verifier-reports/{lane}.json", "fallback_local report cannot satisfy independent readiness or readiness while tooling_preflight.available is true"))
        report_claims_readiness = report_readiness in CLAIMED_READINESS
        if (readiness in CLAIMED_READINESS or report_claims_readiness) and "blocking" in report_statuses(report):
            issues.append(Issue(IssueCode.BLOCKING_FINDING_IN_READY_REPORT, f"verifier-reports/{lane}.json", "claimed readiness cannot include BLOCKING report or finding status"))
        if report_is_independent(report, readiness):
            for field in CHILD_PROOF_FIELDS:
                if text_field(report, field) is None:
                    issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", f"missing {field}"))
            if report.get("parent_validated") is not True:
                issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", "parent_validated must be true"))
            raw_path = text_field(report, "raw_child_report_path")
            if raw_path is not None and not (data.proof_dir / raw_path).is_file():
                issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_CHILD_PROOF, f"verifier-reports/{lane}.json", f"raw child report path does not exist: {raw_path}"))
            child_thread = text_field(report, "child_thread_id")
            child_agent = text_field(report, "child_agent_id")
            independent_readiness_claimed = readiness == "independent_verified" or report_readiness == "independent_verified"
            if independent_readiness_claimed and (linked_children is None or not ({child_thread, child_agent} & linked_children)):
                issues.append(Issue(IssueCode.INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE, f"verifier-reports/{lane}.json", "independent_verified requires session summary linkage for child id/thread id"))


def add_answer_issues(data: ProofData, issues: list[Issue]) -> None:
    for entry in ledger_entries(data.answer_ledger):
        status = normalized(text_field(entry, "status"))
        if status in ANSWERED_STATUSES:
            refs = entry.get("source_refs")
            if not isinstance(refs, list) or len(refs) == 0:
                question_id = text_field(entry, "question_id") or "<unknown question>"
                issues.append(Issue(IssueCode.ANSWERED_WITHOUT_SOURCE_REFS, "answer-ledger.json", f"{question_id} is Answered from source but has no source_refs"))


def validate(proof_dir: Path, session_summary: Path | None) -> tuple[str, tuple[Issue, ...]]:
    issues: list[Issue] = []
    data = load_proof(proof_dir, session_summary, issues)
    add_readiness_issues(data, issues)
    add_answer_issues(data, issues)
    return readiness_state(data.qa_report), tuple(issues)
