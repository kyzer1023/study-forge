from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class IssueCode(StrEnum):
    ANSWERED_WITHOUT_SOURCE_REFS = "answered_without_source_refs"
    ANSWERABLE_SUBPART_MISSING_LEDGER_ENTRY = "answerable_subpart_missing_ledger_entry"
    BLOCKING_FINDING_IN_READY_REPORT = "blocking_finding_in_ready_report"
    CONFLICTING_TOOLING_PREFLIGHT = "conflicting_tooling_preflight"
    DEGRADED_EXTRACTION_GRANULARITY = "degraded_extraction_granularity"
    DUPLICATE_LEDGER_QUESTION_ID = "duplicate_ledger_question_id"
    DUPLICATE_QUESTION_INVENTORY_ID = "duplicate_question_inventory_id"
    EXPECTED_SUBPART_MISSING_INVENTORY_ROW = "expected_subpart_missing_inventory_row"
    FALLBACK_LOCAL_EXAM_READY_OVERCLAIM = "fallback_local_exam_ready_overclaim"
    FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD = "fallback_local_without_independent_child"
    GENERIC_OBJECTIVE_EXPLANATION = "generic_objective_explanation"
    HTML_DROPS_MODEL_ANSWER = "html_drops_model_answer"
    INDEPENDENT_REPORT_MISSING_CHILD_PROOF = "independent_report_missing_child_proof"
    INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE = "independent_report_missing_session_linkage"
    INVALID_JSON = "invalid_json"
    LEDGER_QUESTION_TEXT_DRIFT = "ledger_question_text_drift"
    MISSING_EXTRACTION_GRANULARITY = "missing_extraction_granularity"
    MISSING_PREFLIGHT_FOR_CLAIMED_READINESS = "missing_preflight_for_claimed_readiness"
    MISSING_REQUIRED_DOC = "missing_required_doc"
    MISSING_WORKER_COVERAGE_METADATA = "missing_worker_coverage_metadata"
    MODEL_ANSWER_LACKS_EXAM_STRUCTURE = "model_answer_lacks_exam_structure"
    OUT_OF_SCOPE_MISSING_SYLLABUS_AUTHORITY = "out_of_scope_missing_syllabus_authority"
    PLACEHOLDER_QUESTION_TEXT = "placeholder_question_text"
    SOURCE_GAP_MISSING_EVIDENCE = "source_gap_missing_evidence"
    STALE_VERIFIER_REPORT = "stale_verifier_report"
    UNRESOLVED_FINDING_IN_READY_REPORT = "unresolved_finding_in_ready_report"
    UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD = "unreadable_with_unchecked_visual_payload"
    USAGE_ERROR = "usage_error"


@dataclass(frozen=True, slots=True)
class Issue:
    code: IssueCode
    path: str
    detail: str


@dataclass(frozen=True, slots=True)
class ProofData:
    proof_dir: Path
    source_inventory: JsonValue
    question_inventory: JsonValue
    qa_report: JsonObject
    answer_ledger: JsonValue
    verifier_reports: tuple[JsonObject, ...]
    session_summary: JsonObject | None


@dataclass(frozen=True, slots=True)
class ObjectiveExplanation:
    question_id: str
    question_text: str
    answer: str
    fingerprint: str
