from __future__ import annotations

from typing import Final

from scripts.pastyear_proof_common import ANSWERED_STATUSES, evidence_text, has_evidence_value, normalized, text_field
from scripts.pastyear_proof_inventory import expected_subparts, inventory_subparts, ledger_entries
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData
from scripts.pastyear_proof_worker_reports import has_concrete_lane_findings, load_raw_child_report

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
CONCRETE_VISUAL_STATUSES: Final = frozenset(
    {
        "inspected_supported",
        "inspected_unusable",
        "manual_visual_reviewed",
        "visual_inspected",
        "visual_verified",
    }
)
GENERIC_VISUAL_FALLBACK_TERMS: Final = (
    "fallback local inspection recorded",
    "local answer depends on a tree, graph, diagram, or similar visual",
    "retained with local visual lane sidecar",
)
INDEPENDENT_VISUAL_MODES: Final = frozenset(
    {
        "independent_subagent",
        "independent_verified",
        "installed_toml_agent",
        "installed_verifier",
    }
)
VISUAL_REPORT_LANES: Final = frozenset(
    {
        "correctness",
        "evidence",
        "extraction",
        "learner_surface",
        "visual",
    }
)
VISUAL_WORKER_TERMS: Final = (
    "diagram",
    "figure",
    "graph",
    "image",
    "rendered",
    "route map",
    "table",
    "tree",
    "visual",
)


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


def visual_inspection_text(record: JsonObject) -> str:
    return evidence_text([record.get(field) for field in VISUAL_INSPECTION_FIELDS])


def record_has_concrete_visual_inspection(record: JsonObject) -> bool:
    if not record_has_visual_inspection(record):
        return False
    text = visual_inspection_text(record)
    if any(term in text for term in GENERIC_VISUAL_FALLBACK_TERMS):
        return False
    status = normalized(text_field(record, "visual_inspection_status"))
    if status in CONCRETE_VISUAL_STATUSES:
        return True
    return record_has_visual_evidence(record) and any(term in text for term in VISUAL_WORKER_TERMS)


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
    return any(record_has_concrete_visual_inspection(record) for record in records) and any(
        term in text for term in UNUSABLE_VISUAL_TERMS
    )


def visual_child_report_is_concrete(data: ProofData, worker_path: str, question_id: str) -> bool:
    child_report = load_raw_child_report(data.proof_dir / worker_path)
    if child_report is None or not has_concrete_lane_findings(child_report):
        return False
    text = evidence_text(child_report)
    return question_id.casefold() in text and any(term in text for term in VISUAL_WORKER_TERMS)


def report_has_visual_worker_lane(data: ProofData, report: JsonObject, question_id: str) -> bool:
    mode = normalized(text_field(report, "invocation_mode") or text_field(report, "mode"))
    report_readiness = normalized(text_field(report, "readiness_state"))
    if mode not in INDEPENDENT_VISUAL_MODES and report_readiness != "independent_verified":
        return False
    if report.get("parent_validated") is not True:
        return False
    report_text = evidence_text(report)
    if question_id.casefold() not in report_text:
        return False
    lane = normalized(text_field(report, "lane"))
    if "visual" not in report_text and lane not in VISUAL_REPORT_LANES:
        return False
    raw_path = text_field(report, "raw_child_report_path")
    return raw_path is not None and visual_child_report_is_concrete(data, raw_path, question_id)


def has_visual_worker_lane(data: ProofData, question_id: str, records: tuple[JsonObject, ...]) -> bool:
    for record in records:
        worker_path = text_field(record, "visual_worker_report_path")
        if worker_path is not None and visual_child_report_is_concrete(data, worker_path, question_id):
            return True
    return any(report_has_visual_worker_lane(data, report, question_id) for report in data.verifier_reports)


def add_visual_issues(data: ProofData, issues: list[Issue]) -> None:
    records_by_id = records_by_question_id(data.question_inventory, data.answer_ledger)
    for question_id, records in records_by_id.items():
        if not any(record_requires_visual(record) for record in records):
            continue
        has_visual_payload = any(record_has_visual_evidence(record) for record in records)
        has_inspection = any(record_has_concrete_visual_inspection(record) for record in records)
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
