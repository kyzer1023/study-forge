from __future__ import annotations

from .io_utils import normalized_json_text, object_list_json, text_json
from .model import Issue, JsonObject, JsonValue


def flattened_json_text(value: JsonValue) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {flattened_json_text(nested)}" for key, nested in value.items())
    if isinstance(value, list):
        return " ".join(flattened_json_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def has_answer_production_evidence(qa_report: JsonObject | None) -> bool:
    if qa_report is None:
        return False
    lowered = " ".join(flattened_json_text(qa_report).casefold().replace("_", " ").replace("-", " ").split())
    evidence_tokens = (
        "answer synthesis",
        "source pack lookup",
        "original source inspection",
        "synthesis attempted",
    )
    acceptance_tokens = (
        "explicit degraded acceptance",
        "explicit user acceptance",
        "accepted degraded output",
        "user accepted degraded",
    )
    negated_evidence_tokens = (
        "answer synthesis was skipped",
        "answer synthesis skipped",
        "answer synthesis not run",
        "answer synthesis did not run",
        "no answer synthesis",
        "without answer synthesis",
        "source pack lookup skipped",
        "original source inspection skipped",
    )
    has_acceptance = any(token in lowered for token in acceptance_tokens)
    has_evidence = any(token in lowered for token in evidence_tokens)
    has_negated_evidence = any(token in lowered for token in negated_evidence_tokens)
    return has_acceptance or (has_evidence and not has_negated_evidence)


def past_year_answer_production_issues(
    label: str,
    answer_ledger: JsonObject,
    qa_report: JsonObject | None,
) -> tuple[Issue, ...]:
    entries = object_list_json(answer_ledger, "entries")
    if not entries:
        return ()
    if has_answer_production_evidence(qa_report):
        return ()
    by_paper: dict[str, list[JsonObject]] = {}
    for entry in entries:
        paper_id = text_json(entry, "paper_id") or "unknown-paper"
        by_paper.setdefault(paper_id, []).append(entry)
    issues: list[Issue] = []
    for paper_id, paper_entries in sorted(by_paper.items()):
        if len(paper_entries) < 3:
            continue
        source_gap_count = sum(1 for entry in paper_entries if normalized_json_text(entry, "status") == "source_gap")
        if source_gap_count == len(paper_entries):
            message = (
                f"over-gapped fallback: paper {paper_id} has {source_gap_count}/{len(paper_entries)} "
                "Source gap entries without answer-production evidence or explicit degraded acceptance"
            )
            issues.append(Issue(label, message))
    return tuple(issues)
