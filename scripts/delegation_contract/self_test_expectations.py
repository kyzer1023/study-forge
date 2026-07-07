from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tempfile

from .answer_production import past_year_answer_production_issues
from .learner_surface import artifact_boundary_issues
from .model import FixtureCase, Issue, JsonObject
from .self_test_fixtures import write_valid_fixture


def print_result(issues: tuple[Issue, ...] | list[Issue]) -> None:
    if not issues:
        print("PASS delegation contract")
        return
    print("FAIL delegation contract")
    for issue in issues:
        print(f"ISSUE path={issue.path} detail={issue.detail}")


def expect_issue(case: FixtureCase, collect_issues: Callable[[Path], tuple[Issue, ...]]) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_valid_fixture(root)
        case.mutate(root)
        issues = collect_issues(root)
    if any(case.expected in issue.detail for issue in issues):
        print(f"SELF-TEST RED {case.label}: PASS expected {case.expected}")
        return True
    print(f"FAIL self-test {case.label}: expected {case.expected}")
    print_result(issues)
    return False


def expect_clean_fixture(label: str, mutate: Callable[[Path], None], validate: Callable[[Path], tuple[Issue, ...]]) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_valid_fixture(root)
        mutate(root)
        issues = validate(root)
    if not issues:
        print(f"SELF-TEST GREEN {label}: PASS")
        return True
    print(f"FAIL self-test {label}: expected clean fixture")
    print_result(issues)
    return False


def expect_artifact_boundary_issues(
    label: str,
    learner_html: str,
    sidecar_proof: JsonObject | None,
    expected: tuple[str, ...],
) -> bool:
    issues = artifact_boundary_issues(label, learner_html, sidecar_proof)
    missing = tuple(token for token in expected if not any(token in issue.detail for issue in issues))
    if not missing:
        print(f"SELF-TEST RED {label}: PASS expected {', '.join(expected)}")
        return True
    print(f"FAIL self-test {label}: expected {', '.join(missing)}")
    print_result(issues)
    return False


def expect_artifact_boundary_clean(label: str, learner_html: str, sidecar_proof: JsonObject) -> bool:
    issues = artifact_boundary_issues(label, learner_html, sidecar_proof)
    if not issues:
        print(f"SELF-TEST GREEN {label}: PASS")
        return True
    print(f"FAIL self-test {label}: expected artifact boundary pass")
    print_result(issues)
    return False


def expect_past_year_answer_production_issue(
    label: str,
    answer_ledger: JsonObject,
    qa_report: JsonObject | None,
    expected: str,
) -> bool:
    issues = past_year_answer_production_issues(label, answer_ledger, qa_report)
    if any(expected in issue.detail for issue in issues):
        print(f"SELF-TEST RED {label}: PASS expected {expected}")
        return True
    print(f"FAIL self-test {label}: expected {expected}")
    print_result(issues)
    return False


def expect_past_year_answer_production_clean(label: str, answer_ledger: JsonObject, qa_report: JsonObject) -> bool:
    issues = past_year_answer_production_issues(label, answer_ledger, qa_report)
    if not issues:
        print(f"SELF-TEST GREEN {label}: PASS")
        return True
    print(f"FAIL self-test {label}: expected past-year answer-production pass")
    print_result(issues)
    return False
