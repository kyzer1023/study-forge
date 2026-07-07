from __future__ import annotations

from dataclasses import dataclass

from scripts.pastyear_proof_common import (
    OUT_OF_SCOPE_REASON_FIELDS,
    OUT_OF_SCOPE_SYLLABUS_FIELDS,
    SOURCE_GAP_STATUSES,
    evidence_text,
    has_evidence_value,
    normalized,
    string_list_field,
    text_field,
)
from scripts.pastyear_proof_inventory import expected_subparts, inventory_subparts, ledger_entries
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData


@dataclass(frozen=True, slots=True)
class ClassifiedEntry:
    question_id: str
    status: str
    source: str
    record: JsonObject


def current_syllabus_ids(source_inventory: JsonValue) -> tuple[str, ...]:
    if not isinstance(source_inventory, dict):
        return ()
    authority = source_inventory.get("current_syllabus_authority")
    if not isinstance(authority, dict):
        return ()
    ids: list[str] = []
    source_id = text_field(authority, "source_id")
    if source_id is not None:
        ids.append(source_id)
    ids.extend(string_list_field(authority, "source_refs"))
    return tuple(ids)


def has_out_of_scope_reason(entry: JsonObject) -> bool:
    return any(text_field(entry, field) is not None for field in OUT_OF_SCOPE_REASON_FIELDS)


def has_syllabus_authority_tie(entry: JsonObject, source_inventory: JsonValue) -> bool:
    authority_ids = current_syllabus_ids(source_inventory)
    for field in OUT_OF_SCOPE_SYLLABUS_FIELDS:
        value = entry.get(field)
        if not has_evidence_value(value):
            continue
        text = evidence_text(value)
        if any(authority_id.casefold() in text for authority_id in authority_ids):
            return True
        if "current" in text and "syllabus" in text:
            return True
    return False


def has_lookup_evidence(entry: JsonObject) -> bool:
    return any(has_evidence_value(entry.get(field)) for field in ("failed_lookup_evidence", "failed_lookup_refs", "lookup_attempts"))


def has_complete_source_gap_evidence(entry: JsonObject) -> bool:
    return has_lookup_evidence(entry) and has_evidence_value(entry.get("inspection_evidence")) and has_evidence_value(entry.get("synthesis_evidence"))


def sidecar_reason_covers_source_gap_path(value: JsonValue | None) -> bool:
    text = evidence_text(value)
    return "lookup" in text and "inspection" in text and "synthesis" in text


def qa_sidecar_has_source_gap_reason(qa_report: JsonObject, question_id: str) -> bool:
    for field in ("source_gap_reasons", "source_gap_sidecar", "gap_reasons"):
        value = qa_report.get(field)
        if isinstance(value, dict):
            direct = value.get(question_id)
            if sidecar_reason_covers_source_gap_path(direct):
                return True
            entries = value.get("entries")
            if isinstance(entries, list) and any(
                isinstance(entry, dict)
                and text_field(entry, "question_id") == question_id
                and (has_complete_source_gap_evidence(entry) or sidecar_reason_covers_source_gap_path(entry.get("sidecar_reason")))
                for entry in entries
            ):
                return True
        if isinstance(value, list) and any(
            isinstance(entry, dict)
            and text_field(entry, "question_id") == question_id
            and (has_complete_source_gap_evidence(entry) or sidecar_reason_covers_source_gap_path(entry.get("sidecar_reason")))
            for entry in value
        ):
            return True
    return False


def has_source_gap_evidence(entry: JsonObject, qa_report: JsonObject, question_id: str) -> bool:
    return has_complete_source_gap_evidence(entry) or sidecar_reason_covers_source_gap_path(entry.get("sidecar_reason")) or qa_sidecar_has_source_gap_reason(qa_report, question_id)


def classified_entries(data: ProofData) -> tuple[ClassifiedEntry, ...]:
    entries: list[ClassifiedEntry] = []
    for subpart in expected_subparts(data.question_inventory):
        entries.append(ClassifiedEntry(subpart.question_id, subpart.status, "expected_answerable_subparts", subpart.record))
    for subpart in inventory_subparts(data.question_inventory):
        entries.append(ClassifiedEntry(subpart.question_id, subpart.status, "question-inventory.json", subpart.record))
    for entry in ledger_entries(data.answer_ledger):
        question_id = text_field(entry, "question_id")
        if question_id is not None:
            entries.append(ClassifiedEntry(question_id, normalized(text_field(entry, "status")), "answer-ledger.json", entry))
    return tuple(entries)


def add_classification_issues(data: ProofData, issues: list[Issue]) -> None:
    seen: set[tuple[IssueCode, str]] = set()
    for entry in classified_entries(data):
        if entry.status == "out_of_scope" and (
            not has_out_of_scope_reason(entry.record)
            or not has_syllabus_authority_tie(entry.record, data.source_inventory)
        ):
            key = (IssueCode.OUT_OF_SCOPE_MISSING_SYLLABUS_AUTHORITY, entry.question_id)
            if key not in seen:
                seen.add(key)
                issues.append(
                    Issue(
                        IssueCode.OUT_OF_SCOPE_MISSING_SYLLABUS_AUTHORITY,
                        entry.source,
                        f"{entry.question_id} is Out of scope without reason tied to current syllabus authority",
                    )
                )
        if entry.status in SOURCE_GAP_STATUSES and not has_source_gap_evidence(entry.record, data.qa_report, entry.question_id):
            key = (IssueCode.SOURCE_GAP_MISSING_EVIDENCE, entry.question_id)
            if key not in seen:
                seen.add(key)
                issues.append(
                    Issue(
                        IssueCode.SOURCE_GAP_MISSING_EVIDENCE,
                        entry.source,
                        f"{entry.question_id} is Source gap without failed lookup, inspection, synthesis, or sidecar reason",
                    )
                )
