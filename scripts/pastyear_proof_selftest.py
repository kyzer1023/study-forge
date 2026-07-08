from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
from typing import Final

from scripts.pastyear_proof_cli import print_result
from scripts.pastyear_proof_model import IssueCode
from scripts.pastyear_proof_examworthy_selftest_cases import (
    make_bilingual_mirror_question_duplicate,
    make_coding_answer_hint_only,
    make_duplicate_inventory_question_id,
    make_duplicate_ledger_question_id,
    make_generic_visual_fallback_answer,
    make_high_mark_illustration_answer_without_steps,
    make_ledger_question_text_drift,
    make_nested_duplicate_ledger_question_id,
    make_nested_paper_reports_ledger,
    make_option_only_answer_without_choices,
    make_placeholder_learner_html,
    make_placeholder_question_text,
    make_question_inventory_order_drift,
    make_raw_child_report_lacks_lane_findings,
    make_stale_verifier_report,
    make_unresolved_major_report,
    make_visual_inspected_answer,
    make_visual_inspected_unreadable,
    write_full_answer_html,
)
from scripts.pastyear_proof_selftest_cases import (
    Case,
    IssuesCase,
    MutatedCase,
    SuppressedSubpartCase,
    make_baseline_report_inside_independent,
    make_conflicting_preflight,
    make_degraded_parent_shell_report_inside_independent,
    make_fallback_inside_independent,
    make_fallback_report_claims_independent,
    make_fallback_reviewed_report_inside_independent,
    make_generic_source_gap_reason,
    make_generic_objective_explanations,
    make_no_subparts_detected_paper,
    make_report_level_independent_blocking,
    make_report_level_independent_missing_link,
    remove_expected_answerable_subparts,
    remove_extraction_granularity,
    remove_ledger_entries,
    set_subpart_status,
)
from scripts.pastyear_proof_validator import validate

SELF_TEST_ROOT: Final = Path("scripts/fixtures/pastyear-proof")


def expect_issue(case: Case) -> bool:
    readiness, issues = validate(case.proof_dir, case.session_summary)
    if case.code in {issue.code for issue in issues}:
        print(f"SELF-TEST RED {case.label}: PASS expected {case.code.value}")
        return True
    print("FAIL self-test")
    print(f"expected missing issue code: {case.code.value}")
    print_result(readiness, issues)
    return False


def expect_issues(case: IssuesCase) -> bool:
    readiness, issues = validate(case.proof_dir, case.session_summary)
    present = {issue.code for issue in issues}
    missing = tuple(code for code in case.codes if code not in present)
    if not missing:
        expected = ", ".join(code.value for code in case.codes)
        print(f"SELF-TEST RED {case.label}: PASS expected {expected}")
        return True
    print("FAIL self-test")
    print(f"expected missing issue code(s): {', '.join(code.value for code in missing)}")
    print_result(readiness, issues)
    return False


def expect_mutated_issue(case: MutatedCase) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        proof_dir = Path(temp_dir) / case.source.name
        _ = shutil.copytree(case.source, proof_dir)
        case.mutator(proof_dir)
        return expect_issue(Case(case.label, proof_dir, proof_dir / "session-summary.json", case.code))


def expect_mutated_green(case: MutatedCase) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        proof_dir = Path(temp_dir) / case.source.name
        _ = shutil.copytree(case.source, proof_dir)
        case.mutator(proof_dir)
        readiness, issues = validate(proof_dir, proof_dir / "session-summary.json")
    if not issues:
        print(f"SELF-TEST GREEN {case.label}: PASS {readiness}")
        return True
    print("FAIL self-test")
    print_result(readiness, issues)
    return False


def expect_missing_subpart_suppressed(case: SuppressedSubpartCase) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        proof_dir = Path(temp_dir) / case.source.name
        _ = shutil.copytree(case.source, proof_dir)
        remove_ledger_entries(proof_dir, (case.exempt_question_id, *case.remaining_question_ids))
        set_subpart_status(proof_dir, case.exempt_question_id, case.status)
        readiness, issues = validate(proof_dir, proof_dir / "session-summary.json")
    missing_details = tuple(
        issue.detail
        for issue in issues
        if issue.code == IssueCode.ANSWERABLE_SUBPART_MISSING_LEDGER_ENTRY
    )
    exempt_is_absent = all(not detail.startswith(case.exempt_question_id) for detail in missing_details)
    remaining_are_present = all(
        any(detail.startswith(question_id) for detail in missing_details)
        for question_id in case.remaining_question_ids
    )
    if exempt_is_absent and remaining_are_present:
        print(f"SELF-TEST RED {case.label}: PASS expected status {case.status} suppresses {case.exempt_question_id}")
        return True
    print("FAIL self-test")
    print_result(readiness, issues)
    return False


def run_self_test() -> int:
    cpt212_avl_unchecked_visual = SELF_TEST_ROOT / "cpt212-2011-avl-unchecked-visual"
    collapsed_parent_shell = SELF_TEST_ROOT / "collapsed-parent-shell"
    fallback_exam_ready_overclaim = SELF_TEST_ROOT / "fallback-local-exam-ready-overclaim"
    syllabus_fit_classification = SELF_TEST_ROOT / "syllabus-fit-classification"
    html_drops_model_answer = SELF_TEST_ROOT / "html-drops-model-answer"
    missing_worker_coverage = SELF_TEST_ROOT / "missing-worker-coverage"
    green = SELF_TEST_ROOT / "independent-verified"
    checks = (
        expect_mutated_issue(MutatedCase("missing-extraction-granularity", green, remove_extraction_granularity, IssueCode.MISSING_EXTRACTION_GRANULARITY)),
        expect_mutated_issue(MutatedCase("missing-expected-answerable-subparts", green, remove_expected_answerable_subparts, IssueCode.MISSING_EXTRACTION_GRANULARITY)),
        expect_issues(
            IssuesCase(
                "collapsed-parent-shell",
                collapsed_parent_shell,
                collapsed_parent_shell / "session-summary.json",
                (
                    IssueCode.DEGRADED_EXTRACTION_GRANULARITY,
                    IssueCode.EXPECTED_SUBPART_MISSING_INVENTORY_ROW,
                    IssueCode.ANSWERABLE_SUBPART_MISSING_LEDGER_ENTRY,
                ),
            )
        ),
        expect_issues(
            IssuesCase(
                "syllabus-fit-classification",
                syllabus_fit_classification,
                syllabus_fit_classification / "session-summary.json",
                (
                    IssueCode.OUT_OF_SCOPE_MISSING_SYLLABUS_AUTHORITY,
                    IssueCode.SOURCE_GAP_MISSING_EVIDENCE,
                ),
            )
        ),
        expect_mutated_green(MutatedCase("no-subparts-detected", green, make_no_subparts_detected_paper, IssueCode.MISSING_EXTRACTION_GRANULARITY)),
        expect_issue(Case("missing-worker-coverage", missing_worker_coverage, missing_worker_coverage / "session-summary.json", IssueCode.MISSING_WORKER_COVERAGE_METADATA)),
        expect_missing_subpart_suppressed(
            SuppressedSubpartCase(
                "out-of-scope-status",
                green,
                "Out of scope",
                "B2(a)(i)",
                ("B2(a)(ii)", "B2(a)(iii)"),
            )
        ),
        expect_mutated_issue(MutatedCase("duplicate-ledger-question-id", green, make_duplicate_ledger_question_id, IssueCode.DUPLICATE_LEDGER_QUESTION_ID)),
        expect_mutated_green(MutatedCase("nested-paper-reports-ledger", green, make_nested_paper_reports_ledger, IssueCode.DUPLICATE_LEDGER_QUESTION_ID)),
        expect_mutated_issue(MutatedCase("nested-duplicate-ledger-question-id", green, make_nested_duplicate_ledger_question_id, IssueCode.DUPLICATE_LEDGER_QUESTION_ID)),
        expect_mutated_issue(MutatedCase("duplicate-inventory-question-id", green, make_duplicate_inventory_question_id, IssueCode.DUPLICATE_QUESTION_INVENTORY_ID)),
        expect_mutated_issue(
            MutatedCase(
                "bilingual-mirror-question-duplicate",
                green,
                make_bilingual_mirror_question_duplicate,
                IssueCode.BILINGUAL_MIRROR_QUESTION_DUPLICATE,
            )
        ),
        expect_mutated_issue(
            MutatedCase(
                "question-inventory-order-drift",
                green,
                make_question_inventory_order_drift,
                IssueCode.QUESTION_INVENTORY_ORDER_DRIFT,
            )
        ),
        expect_mutated_issue(MutatedCase("ledger-question-text-drift", green, make_ledger_question_text_drift, IssueCode.LEDGER_QUESTION_TEXT_DRIFT)),
        expect_mutated_issue(MutatedCase("placeholder-question-text", green, make_placeholder_question_text, IssueCode.PLACEHOLDER_QUESTION_TEXT)),
        expect_mutated_issue(MutatedCase("placeholder-learner-html", green, make_placeholder_learner_html, IssueCode.PLACEHOLDER_QUESTION_TEXT)),
        expect_mutated_issue(MutatedCase("generic-objective-explanations", green, make_generic_objective_explanations, IssueCode.GENERIC_OBJECTIVE_EXPLANATION)),
        expect_mutated_issue(MutatedCase("generic-source-gap-reason", green, make_generic_source_gap_reason, IssueCode.SOURCE_GAP_MISSING_EVIDENCE)),
        expect_issue(Case("html-drops-model-answer", html_drops_model_answer, html_drops_model_answer / "session-summary.json", IssueCode.HTML_DROPS_MODEL_ANSWER)),
        expect_mutated_green(MutatedCase("html-renders-model-answer", green, write_full_answer_html, IssueCode.HTML_DROPS_MODEL_ANSWER)),
        expect_mutated_issue(MutatedCase("coding-answer-hint-only", green, make_coding_answer_hint_only, IssueCode.MODEL_ANSWER_LACKS_EXAM_STRUCTURE)),
        expect_mutated_issue(MutatedCase("option-only-answer-without-choices", green, make_option_only_answer_without_choices, IssueCode.MODEL_ANSWER_LACKS_EXAM_STRUCTURE)),
        expect_mutated_issue(MutatedCase("high-mark-illustration-without-steps", green, make_high_mark_illustration_answer_without_steps, IssueCode.MODEL_ANSWER_LACKS_EXAM_STRUCTURE)),
        expect_issue(Case("cpt212-2011-avl-unchecked-visual", cpt212_avl_unchecked_visual, cpt212_avl_unchecked_visual / "session-summary.json", IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD)),
        expect_mutated_issue(MutatedCase("generic-visual-fallback-answer", green, make_generic_visual_fallback_answer, IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD)),
        expect_mutated_green(MutatedCase("visual-inspected-answer", green, make_visual_inspected_answer, IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD)),
        expect_mutated_green(MutatedCase("visual-inspected-unreadable", green, make_visual_inspected_unreadable, IssueCode.UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD)),
        expect_issue(Case("fallback-local-exam-ready-overclaim", fallback_exam_ready_overclaim, fallback_exam_ready_overclaim / "session-summary.json", IssueCode.FALLBACK_LOCAL_EXAM_READY_OVERCLAIM)),
        expect_mutated_issue(MutatedCase("stale-verifier-report", green, make_stale_verifier_report, IssueCode.STALE_VERIFIER_REPORT)),
        expect_mutated_issue(MutatedCase("unresolved-major-report", green, make_unresolved_major_report, IssueCode.UNRESOLVED_FINDING_IN_READY_REPORT)),
        expect_mutated_issue(
            MutatedCase(
                "raw-child-report-lacks-lane-findings",
                green,
                make_raw_child_report_lacks_lane_findings,
                IssueCode.RAW_CHILD_REPORT_LACKS_LANE_FINDINGS,
            )
        ),
        expect_mutated_issue(MutatedCase("fallback-inside-independent", green, make_fallback_inside_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)),
        expect_mutated_issue(MutatedCase("fallback-report-claims-independent", green, make_fallback_report_claims_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)),
        expect_mutated_issue(MutatedCase("fallback-reviewed-inside-independent", green, make_fallback_reviewed_report_inside_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)),
        expect_mutated_issue(MutatedCase("baseline-inside-independent", green, make_baseline_report_inside_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)),
        expect_mutated_issue(MutatedCase("degraded-parent-shell-inside-independent", green, make_degraded_parent_shell_report_inside_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)),
        expect_mutated_issue(MutatedCase("report-independent-blocking", green, make_report_level_independent_blocking, IssueCode.BLOCKING_FINDING_IN_READY_REPORT)),
        expect_mutated_issue(MutatedCase("report-independent-missing-link", green, make_report_level_independent_missing_link, IssueCode.INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE)),
        expect_mutated_issue(MutatedCase("conflicting-preflight", green, make_conflicting_preflight, IssueCode.CONFLICTING_TOOLING_PREFLIGHT)),
    )
    green_readiness, green_issues = validate(green, green / "session-summary.json")
    if green_issues:
        print("FAIL self-test")
        print_result(green_readiness, green_issues)
        return 1
    print(f"SELF-TEST GREEN independent-verified: PASS {green_readiness}")
    if not all(checks):
        return 1
    print("PASS self-test")
    return 0
