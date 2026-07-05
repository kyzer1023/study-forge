#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Final, Sequence

from pastyear_proof_validator import Issue, IssueCode, JsonValue, validate

SELF_TEST_ROOT: Final = Path(".omo/evidence/studyforge-pastyear-verifier-enforcement/fixtures")


@dataclass(frozen=True, slots=True)
class CliArgs:
    proof_dir: Path | None
    session_summary: Path | None
    self_test: bool


@dataclass(frozen=True, slots=True)
class Case:
    label: str
    proof_dir: Path
    session_summary: Path
    code: IssueCode


@dataclass(frozen=True, slots=True)
class MutatedCase:
    label: str
    source: Path
    mutator: Callable[[Path], None]
    code: IssueCode


def usage() -> str:
    return "usage: scripts/validate-pastyear-proof.py <proof_dir> [--session-summary <path>] [--self-test]"


def parse_args(argv: Sequence[str]) -> CliArgs | Issue:
    proof_dir: Path | None = None
    session_summary: Path | None = None
    self_test = False
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--self-test":
            self_test = True
            index += 1
        elif token == "--session-summary":
            if index + 1 >= len(argv):
                return Issue(IssueCode.USAGE_ERROR, "--session-summary", "missing path")
            session_summary = Path(argv[index + 1])
            index += 2
        elif token.startswith("--"):
            return Issue(IssueCode.USAGE_ERROR, token, "unknown option")
        elif proof_dir is None:
            proof_dir = Path(token)
            index += 1
        else:
            return Issue(IssueCode.USAGE_ERROR, token, "unexpected positional argument")
    if not self_test and proof_dir is None:
        return Issue(IssueCode.USAGE_ERROR, "<proof_dir>", "proof directory is required")
    return CliArgs(proof_dir=proof_dir, session_summary=session_summary, self_test=self_test)


def print_result(readiness: str, issues: tuple[Issue, ...]) -> None:
    if issues:
        print(f"FAIL {readiness}")
        for issue in issues:
            print(f"ISSUE {issue.code.value} path={issue.path} detail={issue.detail}")
        return
    print(f"PASS {readiness}")


def expect_issue(case: Case) -> bool:
    readiness, issues = validate(case.proof_dir, case.session_summary)
    if case.code in {issue.code for issue in issues}:
        print(f"SELF-TEST RED {case.label}: PASS expected {case.code.value}")
        return True
    print("FAIL self-test")
    print_result(readiness, issues)
    return False


def rewrite_json(path: Path, mutator: Callable[[JsonValue], None]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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


def expect_mutated_issue(case: MutatedCase) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        proof_dir = Path(temp_dir) / case.source.name
        shutil.copytree(case.source, proof_dir)
        case.mutator(proof_dir)
        return expect_issue(Case(case.label, proof_dir, proof_dir / "session-summary.json", case.code))


def run_self_test() -> int:
    fallback = SELF_TEST_ROOT / "fallback-local"
    blocking = SELF_TEST_ROOT / "smoke-blocking"
    green = SELF_TEST_ROOT / "independent-verified"
    if not expect_issue(Case("fallback-local", fallback, fallback / "session-summary.json", IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)):
        return 1
    if not expect_mutated_issue(MutatedCase("fallback-inside-independent", green, make_fallback_inside_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)):
        return 1
    if not expect_mutated_issue(MutatedCase("fallback-report-claims-independent", green, make_fallback_report_claims_independent, IssueCode.FALLBACK_LOCAL_WITHOUT_INDEPENDENT_CHILD)):
        return 1
    if not expect_mutated_issue(MutatedCase("report-independent-blocking", green, make_report_level_independent_blocking, IssueCode.BLOCKING_FINDING_IN_READY_REPORT)):
        return 1
    if not expect_mutated_issue(MutatedCase("report-independent-missing-link", green, make_report_level_independent_missing_link, IssueCode.INDEPENDENT_REPORT_MISSING_SESSION_LINKAGE)):
        return 1
    if not expect_mutated_issue(MutatedCase("conflicting-preflight", green, make_conflicting_preflight, IssueCode.CONFLICTING_TOOLING_PREFLIGHT)):
        return 1
    if not expect_issue(Case("blocking-ready", blocking, blocking / "session-summary.json", IssueCode.BLOCKING_FINDING_IN_READY_REPORT)):
        return 1
    green_readiness, green_issues = validate(green, green / "session-summary.json")
    if green_issues:
        print("FAIL self-test")
        print_result(green_readiness, green_issues)
        return 1
    print(f"SELF-TEST GREEN independent-verified: PASS {green_readiness}")
    print("PASS self-test")
    return 0


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if isinstance(args, Issue):
        print(usage())
        print_result("usage_error", (args,))
        return 2
    if args.self_test:
        return run_self_test()
    if args.proof_dir is None:
        print(usage())
        return 2
    readiness, issues = validate(args.proof_dir, args.session_summary)
    print_result(readiness, issues)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
