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
    FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD = "fallback_local_without_independent_child"
    GENERIC_OBJECTIVE_EXPLANATION = "generic_objective_explanation"
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
