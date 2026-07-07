from __future__ import annotations

from scripts.pastyear_proof_common import ANSWERED_STATUSES, evidence_text, has_evidence_value, normalized, text_field
from scripts.pastyear_proof_inventory import expected_subparts, inventory_subparts, ledger_entries
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData

VISUAL_EVIDENCE_FIELDS = (
    "visual_locator",
    "rendered_page_image",
    "visual_payload",
    "visual_crop",
    "page_image",
)
VISUAL_INSPECTION_FIELDS = (
    "visual_inspection_status",
    "visual_inspection_result",
    "visual_inspection_evidence",
    "visual_worker_report_path",
)
VISUAL_CONTEXT_TERMS = (
    "avl tree",
    "b-tree",
    "diagram",
    "figure",
    "image",
    "rendered page",
    "route map",
    "shown below",
    "table",
    "the following graph",
    "the following tree",
)
UNUSABLE_VISUAL_TERMS = ("blurry", "cropped", "unusable", "illegible", "cannot read", "too low resolution")


def records_by_question_id(question_inventory: JsonValue, answer_ledger: JsonValue) -> dict[str, tuple[JsonObject, ...]]:
    records: dict[str, list[JsonObject]] = {}
    for subpart in expected_subparts(question_inventory):
        records.setdefault(subpart.question_id, []).append(subpart.record)
    for subpart in inventory_subparts(question_inventory):
        records.setdefault(subpart.question_id, []).append(subpart.record)
    for entry in ledger_entries(answer_ledger):
        question_id = text_field(entry, "question_id")
        if question_id is not None:
            records.setdefault(question_id, []).append(entry)
    return {question_id: tuple(items) for question_id, items in records.items()}


def record_has_visual_evidence(record: JsonObject) -> bool:
    return any(has_evidence_value(record.get(field)) for field in VISUAL_EVIDENCE_FIELDS)


def record_has_visual_inspection(record: JsonObject) -> bool:
    return any(has_evidence_value(record.get(field)) for field in VISUAL_INSPECTION_FIELDS)


def record_requires_visual(record: JsonObject) -> bool:
    if record.get("visual_dependency") is True or record_has_visual_evidence(record):
        return True
    text = evidence_text(
        [
            record.get("question_text"),
            record.get("prompt"),
            record.get("instruction"),
            record.get("context"),
        ]
    )
    return any(term in text for term in VISUAL_CONTEXT_TERMS)


def visual_status_is_inspected_unusable(records: tuple[JsonObject, ...]) -> bool:
    payload: list[JsonValue] = [record for record in records]
    text = evidence_text(payload)
    return "inspect" in text and any(term in text for term in UNUSABLE_VISUAL_TERMS)


def has_visual_worker_lane(data: ProofData, question_id: str, records: tuple[JsonObject, ...]) -> bool:
    for record in records:
        worker_path = text_field(record, "visual_worker_report_path")
        if worker_path is not None and (data.proof_dir / worker_path).is_file():
            return True
    payload: list[JsonValue] = [data.qa_report]
    payload.extend(data.verifier_reports)
    text = evidence_text(payload)
    return question_id.casefold() in text and "visual" in text and ("child" in text or "worker" in text or "lane" in text)


def add_visual_issues(data: ProofData, issues: list[Issue]) -> None:
    records_by_id = records_by_question_id(data.question_inventory, data.answer_ledger)
    for question_id, records in records_by_id.items():
        if not any(record_requires_visual(record) for record in records):
            continue
        has_visual_payload = any(record_has_visual_evidence(record) for record in records)
        has_inspection = any(record_has_visual_inspection(record) for record in records)
        ledger_statuses = {
            normalized(text_field(record, "status"))
            for record in records
            if text_field(record, "status") is not None
        }
        if "source_gap" in ledger_statuses or "out_of_scope" in ledger_statuses:
            continue
        if "unreadable" in ledger_statuses:
            if has_visual_payload and not has_inspection and not visual_status_is_inspected_unusable(records):
                issues.append(
                    Issue(
                        IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD,
                        "answer-ledger.json",
                        f"{question_id} is Unreadable from text extraction even though rendered visual payload exists without inspection evidence",
                    )
                )
            continue
        if ledger_statuses & ANSWERED_STATUSES and (not has_inspection or not has_visual_worker_lane(data, question_id, records)):
            issues.append(
                Issue(
                    IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD,
                    "answer-ledger.json",
                    f"{question_id} is visual-dependent but lacks visual inspection or visual worker evidence",
                )
            )
