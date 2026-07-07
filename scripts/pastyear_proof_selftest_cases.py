from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
from typing import TypeAlias, cast

from scripts.pastyear_proof_model import IssueCode, JsonValue

JsonMutator: TypeAlias = Callable[[JsonValue], None]
ProofMutator: TypeAlias = Callable[[Path], None]


@dataclass(frozen=True, slots=True)
class Case:
    label: str
    proof_dir: Path
    session_summary: Path
    code: IssueCode


@dataclass(frozen=True, slots=True)
class IssuesCase:
    label: str
    proof_dir: Path
    session_summary: Path
    codes: tuple[IssueCode, ...]


@dataclass(frozen=True, slots=True)
class MutatedCase:
    label: str
    source: Path
    mutator: ProofMutator
    code: IssueCode


@dataclass(frozen=True, slots=True)
class SuppressedSubpartCase:
    label: str
    source: Path
    status: str
    exempt_question_id: str
    remaining_question_ids: tuple[str, ...]


def rewrite_json(path: Path, mutator: JsonMutator) -> None:
    data = cast(JsonValue, json.loads(path.read_text(encoding="utf-8")))
    mutator(data)
    _ = path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def set_preflight_unavailable(data: JsonValue) -> None:
    if isinstance(data, dict):
        data["tooling_preflight"] = {"available": False}


def make_fallback_inside_independent(proof_dir: Path) -> None:
    for name in ("qa-report.json", "session-summary.json", "verifier-reports/evidence.json"):
        rewrite_json(proof_dir / name, set_preflight_unavailable)

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["invocation_mode"] = "fallback_local"

    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_fallback_report_claims_independent(proof_dir: Path) -> None:
    for name in ("qa-report.json", "session-summary.json", "verifier-reports/evidence.json"):
        rewrite_json(proof_dir / name, set_preflight_unavailable)

    def mutate_qa(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["readiness_state"] = "fallback_local_reviewed"

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["invocation_mode"] = "fallback_local"
            data["readiness_state"] = "independent_verified"

    rewrite_json(proof_dir / "qa-report.json", mutate_qa)
    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_baseline_report_inside_independent(proof_dir: Path) -> None:
    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["invocation_mode"] = "baseline_unverified"

    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_degraded_parent_shell_report_inside_independent(proof_dir: Path) -> None:
    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["invocation_mode"] = "degraded_parent_shell"

    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_fallback_reviewed_report_inside_independent(proof_dir: Path) -> None:
    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["invocation_mode"] = "fallback_local_reviewed"

    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_report_level_independent_blocking(proof_dir: Path) -> None:
    def mutate_qa(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["readiness_state"] = "baseline_unverified"

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["readiness_state"] = "independent_verified"
            data["status"] = "BLOCKING"
            data["findings"] = [{"status": "BLOCKING", "question_id": "fixture-q1"}]

    rewrite_json(proof_dir / "qa-report.json", mutate_qa)
    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_report_level_independent_missing_link(proof_dir: Path) -> None:
    def mutate_qa(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["readiness_state"] = "baseline_unverified"

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["readiness_state"] = "independent_verified"

    def mutate_summary(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["thread_spawn_edges"] = []
            data["spawn_wait_close_calls"] = []

    rewrite_json(proof_dir / "qa-report.json", mutate_qa)
    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)
    rewrite_json(proof_dir / "session-summary.json", mutate_summary)


def make_conflicting_preflight(proof_dir: Path) -> None:
    rewrite_json(proof_dir / "qa-report.json", set_preflight_unavailable)


def make_generic_source_gap_reason(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list):
            return
        for entry in entries:
            if isinstance(entry, dict) and entry.get("question_id") == "B2(a)(i)":
                entry["status"] = "Source gap"
                entry["answer"] = ""
                entry["student_explanation"] = ""
                entry["source_refs"] = []
                entry["source_gap_reason"] = "Not found in current materials."
                return

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_no_subparts_detected_paper(proof_dir: Path) -> None:
    def mutate_inventory(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        papers = data.get("papers")
        if not isinstance(papers, list) or not papers:
            return
        paper = papers[0]
        if not isinstance(paper, dict):
            return
        paper["extraction_granularity"] = {
            "status": "no_subparts_detected",
            "source_structure_evidence": [
                {
                    "locator": "fixture:p1",
                    "text": "The source paper contains no nested mark-bearing child subparts.",
                }
            ],
            "expected_answerable_subparts": [],
        }
        paper["questions"] = []

    def mutate_ledger(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["answers"] = []

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)
    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def remove_extraction_granularity(proof_dir: Path) -> None:
    def mutate_inventory(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        papers = data.get("papers")
        if not isinstance(papers, list):
            return
        for paper in papers:
            if isinstance(paper, dict):
                _ = paper.pop("extraction_granularity", None)

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)


def remove_expected_answerable_subparts(proof_dir: Path) -> None:
    def mutate_inventory(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        papers = data.get("papers")
        if not isinstance(papers, list):
            return
        for paper in papers:
            if not isinstance(paper, dict):
                continue
            granularity = paper.get("extraction_granularity")
            if isinstance(granularity, dict):
                _ = granularity.pop("expected_answerable_subparts", None)

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)


def make_generic_objective_explanations(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        data["answers"] = [
            {
                "question_id": "B2(a)(i)",
                "question_type": "objective",
                "question_text": "Which transport-layer protocol is connection oriented?",
                "answer": "TCP",
                "status": "Answered from source",
                "student_explanation": "The answer follows directly from the lecture evidence.",
                "source_refs": ["lecture-ch2:p12"],
            },
            {
                "question_id": "B2(a)(ii)",
                "question_type": "objective",
                "question_text": "Which transport-layer protocol is connectionless?",
                "answer": "UDP",
                "status": "Answered from source",
                "student_explanation": "The answer follows directly from the lecture evidence.",
                "source_refs": ["lecture-ch2:p13"],
            },
            {
                "question_id": "B2(a)(iii)",
                "question_type": "subjective",
                "question_text": "Explain the delivery guarantee difference.",
                "answer": "TCP tracks delivery while UDP does not.",
                "status": "Answered from source",
                "student_explanation": "TCP has acknowledgement and retransmission behavior.",
                "source_refs": ["lecture-ch2:p14"],
            },
        ]

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def remove_ledger_entries(proof_dir: Path, question_ids: tuple[str, ...]) -> None:
    removed_ids = set(question_ids)

    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list):
            return
        data["answers"] = [
            entry
            for entry in entries
            if not isinstance(entry, dict) or entry.get("question_id") not in removed_ids
        ]

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def set_subpart_status(proof_dir: Path, question_id: str, status: str) -> None:
    def mutate_inventory(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        papers = data.get("papers")
        if not isinstance(papers, list):
            return
        for paper in papers:
            if not isinstance(paper, dict):
                continue
            questions = paper.get("questions")
            if not isinstance(questions, list):
                continue
            for question in questions:
                if not isinstance(question, dict):
                    continue
                subparts = question.get("subparts")
                if not isinstance(subparts, list):
                    continue
                for subpart in subparts:
                    if isinstance(subpart, dict) and subpart.get("question_id") == question_id:
                        subpart["status"] = status
                        return

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)
