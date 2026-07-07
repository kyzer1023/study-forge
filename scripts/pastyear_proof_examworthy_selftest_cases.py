from __future__ import annotations

from pathlib import Path

from scripts.pastyear_proof_model import JsonValue
from scripts.pastyear_proof_selftest_cases import rewrite_json


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
