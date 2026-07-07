from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from scripts.pastyear_proof_model import Issue, IssueCode

Validator: TypeAlias = Callable[[Path, Path | None], tuple[str, tuple[Issue, ...]]]
SelfTestRunner: TypeAlias = Callable[[], int]


@dataclass(frozen=True, slots=True)
class CliArgs:
    proof_dir: Path | None
    session_summary: Path | None
    self_test: bool


@dataclass(frozen=True, slots=True)
class CliSpec:
    command: str
    allow_self_test: bool


@dataclass(frozen=True, slots=True)
class CliRuntime:
    spec: CliSpec
    validator: Validator
    self_test_runner: SelfTestRunner | None


def usage(spec: CliSpec) -> str:
    suffix = " [--self-test]" if spec.allow_self_test else ""
    return f"usage: {spec.command} <proof_dir> [--session-summary <path>]{suffix}"


def parse_args(argv: Sequence[str], spec: CliSpec) -> CliArgs | Issue:
    proof_dir: Path | None = None
    session_summary: Path | None = None
    self_test = False
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--self-test":
            if not spec.allow_self_test:
                return Issue(IssueCode.USAGE_ERROR, token, "unknown option")
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


def run_validation_cli(argv: Sequence[str], runtime: CliRuntime) -> int:
    args = parse_args(argv, runtime.spec)
    if isinstance(args, Issue):
        print(usage(runtime.spec))
        print_result("usage_error", (args,))
        return 2
    if args.self_test:
        if runtime.self_test_runner is None:
            print(usage(runtime.spec))
            print_result("usage_error", (Issue(IssueCode.USAGE_ERROR, "--self-test", "unknown option"),))
            return 2
        return runtime.self_test_runner()
    if args.proof_dir is None:
        print(usage(runtime.spec))
        return 2
    readiness, issues = runtime.validator(args.proof_dir, args.session_summary)
    print_result(readiness, issues)
    return 1 if issues else 0
