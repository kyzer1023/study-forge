from __future__ import annotations

import json
from pathlib import Path
from typing import Final, cast

from scripts.pastyear_proof_common import text_field
from scripts.pastyear_proof_model import Issue, IssueCode, JsonValue, ProofData
from scripts.pastyear_proof_readiness import readiness_state, report_is_independent

CONCRETE_CHILD_FIELDS: Final = (
    "question_ids",
    "subpart_ids",
    "supported_question_ids",
    "candidate_answers",
    "findings",
    "coverage_counts",
    "paper_reports",
    "entries",
)


def load_raw_child_report(path: Path) -> JsonValue:
    try:
        return cast(JsonValue, json.loads(path.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def has_concrete_lane_findings(value: JsonValue) -> bool:
    if isinstance(value, dict):
        for field in CONCRETE_CHILD_FIELDS:
            field_value = value.get(field)
            if isinstance(field_value, list) and field_value:
                return True
            if isinstance(field_value, dict) and field_value:
                return True
        return any(has_concrete_lane_findings(child) for child in value.values())
    if isinstance(value, list):
        return any(has_concrete_lane_findings(child) for child in value)
    return False


def add_raw_child_report_issues(data: ProofData, issues: list[Issue]) -> None:
    readiness = readiness_state(data.qa_report)
    for report in data.verifier_reports:
        if not report_is_independent(report, readiness):
            continue
        raw_path = text_field(report, "raw_child_report_path")
        lane = text_field(report, "lane") or "<unknown lane>"
        if raw_path is None:
            continue
        raw_report = load_raw_child_report(data.proof_dir / raw_path)
        if raw_report is None:
            continue
        if not has_concrete_lane_findings(raw_report):
            detail = (
                f"{raw_path} lacks concrete question ids, candidate answers, findings, " +
                "or coverage counts"
            )
            issues.append(
                Issue(
                    IssueCode.RAW_CHILD_REPORT_LACKS_LANE_FINDINGS,
                    f"verifier-reports/{lane}.json",
                    detail,
                )
            )
