from __future__ import annotations

from typing import Final

from pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ObjectiveExplanation, ProofData

CLAIMED_READINESS: Final = frozenset((
    "independent_verified",
    "fallback_local_reviewed",
))
ANSWERED_STATUSES: Final = frozenset({"answered from source", "answered_from_source", "answered"})
NON_ANSWERABLE_STATUSES: Final = frozenset({"unreadable", "duplicate", "out_of_scope"})
OBJECTIVE_QUESTION_TYPES: Final = frozenset({"objective", "mcq", "multiple_choice", "multiple choice"})
JUSTIFIED_DUPLICATE_STATUSES: Final = frozenset({"accepted", "acceptable", "justified", "pass"})
CHILD_PROOF_FIELDS: Final = ("child_agent_id", "child_thread_id", "raw_child_report_path")


def text_field(container: JsonObject, field: str) -> str | None:
    value = container.get(field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def normalized(value: str | None) -> str:
    if value is None:
        return ""
    return "_".join(value.strip().lower().replace("-", " ").replace("_", " ").split())


def explanation_fingerprint(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.casefold().replace("-", " ").split())


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


def ledger_entries(value: JsonValue) -> tuple[JsonObject, ...]:
    if isinstance(value, list):
        return tuple(entry for entry in value if isinstance(entry, dict))
    if isinstance(value, dict):
        for key in ("answers", "entries", "items"):
            entries = value.get(key)
            if isinstance(entries, list):
                return tuple(entry for entry in entries if isinstance(entry, dict))
    return ()


def ledger_question_ids(value: JsonValue) -> set[str]:
    ids: set[str] = set()
    for entry in ledger_entries(value):
        question_id = text_field(entry, "question_id")
        if question_id is not None:
            ids.add(question_id)
    return ids


def objective_explanations(value: JsonValue) -> tuple[ObjectiveExplanation, ...]:
    answers: list[ObjectiveExplanation] = []
    for entry in ledger_entries(value):
        status = normalized(text_field(entry, "status"))
        question_type = normalized(text_field(entry, "question_type"))
        question_id = text_field(entry, "question_id")
        fingerprint = explanation_fingerprint(text_field(entry, "student_explanation"))
        if status in ANSWERED_STATUSES and question_type in OBJECTIVE_QUESTION_TYPES and question_id is not None and fingerprint:
            answers.append(
                ObjectiveExplanation(
                    question_id=question_id,
                    question_text=text_field(entry, "question_text") or "",
                    answer=text_field(entry, "answer") or "",
                    fingerprint=fingerprint,
                )
            )
    return tuple(answers)


def answerable_subpart_ids(value: JsonValue) -> tuple[str, ...]:
    ids: list[str] = []

    def collect(item: JsonValue, inside_subparts: bool) -> None:
        if isinstance(item, list):
            for child in item:
                collect(child, inside_subparts)
            return
        if not isinstance(item, dict):
            return
        marks = item.get("marks")
        question_id = text_field(item, "question_id")
        parent_id = text_field(item, "parent_question_id")
        status = normalized(text_field(item, "status"))
        if question_id is not None and (inside_subparts or parent_id is not None) and status not in NON_ANSWERABLE_STATUSES and isinstance(marks, int | float) and not isinstance(marks, bool):
            ids.append(question_id)
        for key, child in item.items():
            collect(child, key in {"subparts", "children"})

    collect(value, False)
    return tuple(ids)


def justified_duplicate_entries(report: JsonObject) -> tuple[JsonObject, ...]:
    entries: list[JsonObject] = []
    for key in ("accepted_duplicate_explanations", "generic_objective_explanation_justifications", "findings"):
        value = report.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, dict))
    return tuple(entries)


def duplicate_explanation_is_justified(reports: tuple[JsonObject, ...], fingerprint: str, question_ids: set[str]) -> bool:
    for report in reports:
        for entry in justified_duplicate_entries(report):
            status = normalized(text_field(entry, "status"))
            code = normalized(text_field(entry, "issue_code") or text_field(entry, "code"))
            entry_fingerprint = explanation_fingerprint(
                text_field(entry, "normalized_student_explanation")
                or text_field(entry, "student_explanation")
                or text_field(entry, "explanation")
            )
            ids = entry.get("question_ids")
            justified_ids = {str(item).strip() for item in ids if str(item).strip()} if isinstance(ids, list) else set()
            has_issue_code = code in {"generic_objective_explanation", ""}
            if status in JUSTIFIED_DUPLICATE_STATUSES and has_issue_code and entry_fingerprint == fingerprint and question_ids <= justified_ids and text_field(entry, "justification") is not None:
                return True
    return False


def add_generic_objective_explanation_issues(data: ProofData, issues: list[Issue]) -> None:
    by_fingerprint: dict[str, list[ObjectiveExplanation]] = {}
    for answer in objective_explanations(data.answer_ledger):
        by_fingerprint.setdefault(answer.fingerprint, []).append(answer)
    for fingerprint, answers in by_fingerprint.items():
        question_ids = {answer.question_id for answer in answers}
        question_texts = {answer.question_text for answer in answers if answer.question_text}
        answer_texts = {answer.answer for answer in answers if answer.answer}
        if len(question_ids) >= 2 and (len(question_texts) >= 2 or len(answer_texts) >= 2) and not duplicate_explanation_is_justified(data.verifier_reports, fingerprint, question_ids):
            issues.append(
                Issue(
                    IssueCode.GENERIC_OBJECTIVE_EXPLANATION,
                    "answer-ledger.json",
                    f"answered objective questions {', '.join(sorted(question_ids))} reuse the same normalized student_explanation",
                )
            )


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
    ledger_ids = ledger_question_ids(data.answer_ledger)
    for question_id in answerable_subpart_ids(data.question_inventory):
        if question_id not in ledger_ids:
            issues.append(Issue(IssueCode.ANSWERABLE_SUBPART_MISSING_LEDGER_ENTRY, "answer-ledger.json", f"{question_id} is a mark-bearing answerable subpart but has no ledger entry"))
    add_generic_objective_explanation_issues(data, issues)
    for entry in ledger_entries(data.answer_ledger):
        status = normalized(text_field(entry, "status"))
        if status in ANSWERED_STATUSES:
            refs = entry.get("source_refs")
            if not isinstance(refs, list) or len(refs) == 0:
                question_id = text_field(entry, "question_id") or "<unknown question>"
                issues.append(Issue(IssueCode.ANSWERED_WITHOUT_SOURCE_REFS, "answer-ledger.json", f"{question_id} is Answered from source but has no source_refs"))
