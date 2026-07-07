from __future__ import annotations

from pathlib import Path

from scripts.pastyear_proof_model import JsonValue
from scripts.pastyear_proof_selftest_cases import rewrite_json

__all__ = (
    "make_coding_answer_hint_only",
    "make_duplicate_inventory_question_id",
    "make_duplicate_ledger_question_id",
    "make_nested_duplicate_ledger_question_id",
    "make_nested_paper_reports_ledger",
    "make_placeholder_learner_html",
    "make_placeholder_question_text",
    "make_ledger_question_text_drift",
    "make_stale_verifier_report",
    "make_unresolved_major_report",
    "make_visual_inspected_answer",
    "make_visual_inspected_unreadable",
    "write_full_answer_html",
)

PLACEHOLDER_QUESTION_TEXT = (
    "Question text was compacted in the worker report; see .study-forge\\tmp\\extract\\fixture.txt for B2(a)(i)."
)


def write_full_answer_html(proof_dir: Path) -> None:
    html = """<!doctype html>
<html lang="en">
<body class="past-year-script">
  <section id="B2-a-i">TCP uses acknowledgements to confirm delivery and trigger retransmission when data is missing.</section>
  <section id="B2-a-ii">UDP avoids connection setup and delivery tracking, so it has less protocol overhead.</section>
  <section id="B2-a-iii">TCP provides reliable ordered delivery, while UDP provides best-effort datagram delivery.</section>
</body>
</html>
"""
    _ = (proof_dir / "index.html").write_text(html, encoding="utf-8")

    def mutate_qa(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["learner_html_path"] = "index.html"
            data["rendered_artifact_updated_at"] = "2026-07-07T09:00:00+00:00"
            data["final_gate_updated_at"] = "2026-07-07T09:05:00+00:00"

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["checked_at"] = "2026-07-07T09:06:00+00:00"

    rewrite_json(proof_dir / "qa-report.json", mutate_qa)
    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_placeholder_learner_html(proof_dir: Path) -> None:
    write_full_answer_html(proof_dir)
    html_path = proof_dir / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html = html.replace("</body>", f"  <section>{PLACEHOLDER_QUESTION_TEXT}</section>\n</body>")
    _ = html_path.write_text(html, encoding="utf-8")


def make_coding_answer_hint_only(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if isinstance(first, dict):
            first["question_type"] = "coding"
            first["answer"] = "Search each item until found."
            first["student_explanation"] = "Scan the list."

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_duplicate_ledger_question_id(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if isinstance(first, dict):
            entries.insert(
                1,
                {
                    "question_id": first.get("question_id"),
                    "question_type": "subjective",
                    "question_text": "Explain why a routing table lookup is needed.",
                    "answer": "The router consults the table to select the next hop.",
                    "status": "Answered from source",
                    "student_explanation": "The lookup maps a destination to an outgoing path.",
                    "source_refs": ["lecture-ch3:p7"],
                },
            )

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_nested_paper_reports_ledger(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list):
            return
        data.clear()
        data["schema_version"] = "selftest.nested-ledger"
        data["paper_reports"] = [{"paper_id": "fixture-paper", "entries": entries}]

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_nested_duplicate_ledger_question_id(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if not isinstance(first, dict):
            return
        duplicate = dict(first)
        duplicate["question_text"] = "Explain why a routing table lookup is needed."
        entries.insert(1, duplicate)
        data.clear()
        data["schema_version"] = "selftest.nested-ledger"
        data["paper_reports"] = [{"paper_id": "fixture-paper", "entries": entries}]

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_placeholder_question_text(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if isinstance(first, dict):
            first["question_text"] = PLACEHOLDER_QUESTION_TEXT

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_duplicate_inventory_question_id(proof_dir: Path) -> None:
    def mutate_inventory(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        papers = data.get("papers")
        if not isinstance(papers, list) or not papers:
            return
        paper = papers[0]
        if not isinstance(paper, dict):
            return
        questions = paper.get("questions")
        if not isinstance(questions, list) or not questions:
            return
        first = questions[0]
        if not isinstance(first, dict):
            return
        subparts = first.get("subparts")
        if not isinstance(subparts, list) or not subparts:
            return
        original = subparts[0]
        if not isinstance(original, dict):
            return
        subparts.insert(
            1,
            {
                "question_id": original.get("question_id"),
                "parent_question_id": first.get("question_id"),
                "question_type": "subjective",
                "question_text": "Explain why a switch learns MAC addresses.",
                "marks": 2,
                "status": "Answerable",
            },
        )

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)


def make_ledger_question_text_drift(proof_dir: Path) -> None:
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
                    if isinstance(subpart, dict) and subpart.get("question_id") == "B2(a)(i)":
                        subpart["question_text"] = "Explain why TCP uses acknowledgements."
                        return

    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list):
            return
        for entry in entries:
            if isinstance(entry, dict) and entry.get("question_id") == "B2(a)(i)":
                entry["question_text"] = "State the time complexity of bubble sort."
                return

    rewrite_json(proof_dir / "question-inventory.json", mutate_inventory)
    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_visual_inspected_answer(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if isinstance(first, dict):
            first["question_type"] = "structured"
            first["question_text"] = "Using the AVL tree shown below, give the traversal after insertion."
            first["answer"] = "After insertion, the balanced AVL tree has root 30; the inorder traversal is 10, 20, 30, 40."
            first["visual_locator"] = "fixture-avl:p3#q2-a-i"
            first["rendered_page_image"] = "rendered-pages/fixture-avl-p3.png"
            first["visual_inspection_status"] = "inspected_supported"
            first["visual_worker_report_path"] = "raw-child/evidence.json"

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_visual_inspected_unreadable(proof_dir: Path) -> None:
    def mutate_ledger(data: JsonValue) -> None:
        if not isinstance(data, dict):
            return
        entries = data.get("answers")
        if not isinstance(entries, list) or not entries:
            return
        first = entries[0]
        if isinstance(first, dict):
            first["question_type"] = "structured"
            first["question_text"] = "Using the AVL tree shown below, give the traversal after insertion."
            first["answer"] = ""
            first["status"] = "Unreadable"
            first["student_explanation"] = "The rendered visual was inspected but the crop is too blurry to recover node labels."
            first["visual_locator"] = "fixture-avl:p3#q2-a-i"
            first["rendered_page_image"] = "rendered-pages/fixture-avl-p3.png"
            first["visual_inspection_status"] = "inspected_unusable"
            first["unreadable_reason"] = "Rendered image inspected; crop is too blurry and unusable."

    rewrite_json(proof_dir / "answer-ledger.json", mutate_ledger)


def make_stale_verifier_report(proof_dir: Path) -> None:
    write_full_answer_html(proof_dir)

    def mutate_qa(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["rendered_artifact_updated_at"] = "2026-07-07T10:00:00+00:00"
            data["final_gate_updated_at"] = "2026-07-07T09:00:00+00:00"

    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["checked_at"] = "2026-07-07T09:01:00+00:00"

    rewrite_json(proof_dir / "qa-report.json", mutate_qa)
    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)


def make_unresolved_major_report(proof_dir: Path) -> None:
    def mutate_report(data: JsonValue) -> None:
        if isinstance(data, dict):
            data["status"] = "MAJOR"
            data["findings"] = [
                {
                    "status": "MAJOR",
                    "question_id": "B2(a)(i)",
                    "required_fix": "Render the full model answer.",
                }
            ]

    rewrite_json(proof_dir / "verifier-reports/evidence.json", mutate_report)
