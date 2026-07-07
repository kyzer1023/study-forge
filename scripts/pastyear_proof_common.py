from __future__ import annotations

from typing import Final

from scripts.pastyear_proof_model import JsonObject, JsonValue

CLAIMED_READINESS: Final = frozenset((
    "independent_verified",
    "fallback_local_reviewed",
))
DEGRADED_REPORT_MODES: Final = frozenset((
    "baseline_unverified",
    "degraded_parent_shell",
    "fallback_local",
    "fallback_local_reviewed",
))
ANSWERED_STATUSES: Final = frozenset({"answered from source", "answered_from_source", "answered"})
NON_ANSWERABLE_STATUSES: Final = frozenset({"unreadable", "duplicate", "out_of_scope"})
OBJECTIVE_QUESTION_TYPES: Final = frozenset({"objective", "mcq", "multiple_choice", "multiple choice"})
JUSTIFIED_DUPLICATE_STATUSES: Final = frozenset({"accepted", "acceptable", "justified", "pass"})
CHILD_PROOF_FIELDS: Final = ("child_agent_id", "child_thread_id", "raw_child_report_path")
DEGRADED_GRANULARITY_STATUSES: Final = frozenset({"collapsed", "degraded_parent_shell"})
SUBPART_EXPECTING_GRANULARITY_STATUSES: Final = frozenset(
    {"atomic_subparts", "complete_child_subparts", "collapsed", "degraded_parent_shell"}
)
SOURCE_GAP_STATUSES: Final = frozenset({"source_gap"})
OUT_OF_SCOPE_REASON_FIELDS: Final = ("reason", "out_of_scope_reason", "classification_reason")
OUT_OF_SCOPE_SYLLABUS_FIELDS: Final = (
    "syllabus_authority_ref",
    "current_syllabus_authority",
    "syllabus_evidence",
    "syllabus_refs",
    "scope_evidence",
)
SOURCE_GAP_EVIDENCE_FIELDS: Final = (
    "failed_lookup_evidence",
    "failed_lookup_refs",
    "inspection_evidence",
    "synthesis_evidence",
    "lookup_attempts",
    "source_gap_reason",
    "gap_reason",
    "sidecar_reason",
)
WORKER_COVERAGE_TEXT_FIELDS: Final = (
    "assignment_id",
    "lane",
    "expected_output_path",
    "child_thread_id",
    "child_agent_id",
    "raw_child_report_path",
    "harvest_status",
    "validation_result",
)
WORKER_COVERAGE_INT_FIELDS: Final = ("wait_attempts", "continuation_attempts")


def text_field(container: JsonObject, field: str) -> str | None:
    value = container.get(field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def normalized(value: str | None) -> str:
    if value is None:
        return ""
    return "_".join(value.strip().lower().replace("-", " ").replace("_", " ").split())


def evidence_text(value: JsonValue | None) -> str:
    if isinstance(value, str):
        return value.casefold()
    if isinstance(value, list):
        return " ".join(evidence_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(evidence_text(item) for item in value.values())
    if value is None:
        return ""
    return str(value).casefold()


def has_evidence_value(value: JsonValue | None) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(has_evidence_value(item) for item in value)
    if isinstance(value, dict):
        return any(has_evidence_value(item) for item in value.values())
    return value is not None and value is not False


def string_list_field(container: JsonObject, field: str) -> tuple[str, ...]:
    value = container.get(field)
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def has_string_key(container: JsonObject, field: str) -> bool:
    return isinstance(container.get(field), str)


def non_negative_int_field(container: JsonObject, field: str) -> bool:
    value = container.get(field)
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def explanation_fingerprint(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.casefold().replace("-", " ").split())
