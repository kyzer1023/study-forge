from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pastyear_proof_model import (
    Issue,
    IssueCode,
    JsonObject,
    JsonValue,
    ProofData,
)
from pastyear_proof_rules import (
    add_answer_issues,
    add_readiness_issues,
    readiness_state,
)

REQUIRED_FILES: Final = ("source-inventory.json", "question-inventory.json", "source-index.json", "answer-ledger.json", "qa-report.json")


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


def load_verifier_reports(proof_dir: Path, issues: list[Issue]) -> tuple[JsonObject, ...]:
    reports_dir = proof_dir / "verifier-reports"
    if not reports_dir.is_dir():
        issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(reports_dir), "directory is required"))
        return ()
    reports = tuple(as_object(load_json(path, issues), path, issues) for path in sorted(reports_dir.glob("*.json")))
    if not reports:
        issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(reports_dir), "at least one verifier report is required"))
    return reports


def load_proof(proof_dir: Path, session_summary: Path | None, issues: list[Issue]) -> ProofData:
    for name in REQUIRED_FILES:
        if not (proof_dir / name).is_file():
            issues.append(Issue(IssueCode.MISSING_REQUIRED_DOC, str(proof_dir / name), "file is required"))
    summary = None
    if session_summary is not None:
        summary = as_object(load_json(session_summary, issues), session_summary, issues)
    return ProofData(
        proof_dir=proof_dir,
        question_inventory=load_json(proof_dir / "question-inventory.json", issues),
        qa_report=as_object(load_json(proof_dir / "qa-report.json", issues), proof_dir / "qa-report.json", issues),
        answer_ledger=load_json(proof_dir / "answer-ledger.json", issues),
        verifier_reports=load_verifier_reports(proof_dir, issues),
        session_summary=summary,
    )


def validate(proof_dir: Path, session_summary: Path | None) -> tuple[str, tuple[Issue, ...]]:
    issues: list[Issue] = []
    data = load_proof(proof_dir, session_summary, issues)
    add_readiness_issues(data, issues)
    add_answer_issues(data, issues)
    return readiness_state(data.qa_report), tuple(issues)
