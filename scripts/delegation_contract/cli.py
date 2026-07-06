from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from .checks import validate
from .model import (
    CliArgs,
    DELEGATED_EXERCISE_COMMANDS,
    HOOK_AUTHORIZATION_SENTENCE,
    HOOK_OPT_OUT_PHRASES,
    HookDecision,
    INHERENTLY_SOURCE_HEAVY_COMMAND_PATTERNS,
    Issue,
    LOCAL_EXERCISE_COMMANDS,
    OPT_OUT_EXERCISE_COMMANDS,
    SOURCE_SCOPED_STUDY_COMMAND_PATTERNS,
    SOURCE_SCOPE_HINTS,
)
from .self_test import run_self_test


def usage() -> str:
    return "usage: scripts/validate-delegation-contract.py <repo-root> | --self-test | --hook-exercise <delegated|opt-out>"


def parse_args(argv: Sequence[str]) -> CliArgs | Issue:
    repo_root: Path | None = None
    self_test = False
    for token in argv:
        if token == "--self-test":
            self_test = True
        elif token.startswith("--"):
            return Issue(token, "unknown option")
        elif repo_root is None:
            repo_root = Path(token)
        else:
            return Issue(token, "unexpected positional argument")
    if not self_test and repo_root is None:
        return Issue("<repo-root>", "repo root is required")
    return CliArgs(repo_root=repo_root, self_test=self_test)


def decide_hook(command: str) -> HookDecision:
    lowered = command.casefold()
    if any(phrase in lowered for phrase in HOOK_OPT_OUT_PHRASES):
        return HookDecision(command, False, None, "user restricts tool use")
    if any(pattern in lowered for pattern in INHERENTLY_SOURCE_HEAVY_COMMAND_PATTERNS):
        return HookDecision(command, True, HOOK_AUTHORIZATION_SENTENCE, "source-heavy Study Forge command")
    scoped_command = any(pattern in lowered for pattern in SOURCE_SCOPED_STUDY_COMMAND_PATTERNS)
    scoped_source = any(hint in lowered for hint in SOURCE_SCOPE_HINTS)
    if scoped_command and scoped_source:
        return HookDecision(command, True, HOOK_AUTHORIZATION_SENTENCE, "source-scoped Study Forge command")
    return HookDecision(command, False, None, "not a source-heavy Study Forge command")


def expect_hook_decision(command: str, expected_delegate: bool) -> bool:
    decision = decide_hook(command)
    if decision.delegate != expected_delegate:
        print(f"FAIL hook decision command={command} expected_delegate={expected_delegate} reason={decision.reason}")
        return False
    if decision.delegate and decision.authorization != HOOK_AUTHORIZATION_SENTENCE:
        print(f"FAIL hook decision command={command} missing authorization")
        return False
    if not decision.delegate and decision.authorization is not None:
        print(f"FAIL hook decision command={command} applied authorization during local route")
        return False
    print(f"SELF-TEST HOOK command={command} delegate={str(decision.delegate).lower()}: PASS")
    return True


def run_hook_self_tests() -> int:
    hook_ok = True
    for command in DELEGATED_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, True) and hook_ok
    for command in OPT_OUT_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, False) and hook_ok
    for command in LOCAL_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, False) and hook_ok
    return 0 if hook_ok else 1


def print_hook_decision(decision: HookDecision) -> None:
    route = "delegated" if decision.delegate else "opt-out"
    print(f"HOOK_EXERCISE route={route} command={decision.command} delegate={str(decision.delegate).lower()}")
    if decision.authorization is None:
        print(f"authorization=not applied because {decision.reason}")
    else:
        print(f"authorization={decision.authorization}")
    print("context=fork_context:false")


def print_hook_exercise(kind: str) -> int:
    if kind == "delegated":
        commands = DELEGATED_EXERCISE_COMMANDS
        expected_delegate = True
    elif kind == "opt-out":
        commands = OPT_OUT_EXERCISE_COMMANDS
        expected_delegate = False
    else:
        print_result((Issue("--hook-exercise", f"unsupported hook exercise: {kind}"),))
        return 2
    exit_code = 0
    for command in commands:
        decision = decide_hook(command)
        if decision.delegate != expected_delegate:
            print_result((Issue(command, f"hook decision mismatch: {decision.reason}"),))
            exit_code = 1
            continue
        print_hook_decision(decision)
    return exit_code


def print_result(issues: Sequence[Issue]) -> None:
    if not issues:
        print("PASS delegation contract")
        return
    print("FAIL delegation contract")
    for issue in issues:
        print(f"ISSUE path={issue.path} detail={issue.detail}")


def main(argv: Sequence[str]) -> int:
    if argv and argv[0] == "--hook-exercise":
        if len(argv) != 2:
            print(usage())
            print_result((Issue("--hook-exercise", "expected hook exercise: delegated or opt-out"),))
            return 2
        return print_hook_exercise(argv[1])
    args = parse_args(argv)
    if isinstance(args, Issue):
        print(usage())
        print_result((args,))
        return 2
    if args.self_test:
        self_test_code = run_self_test()
        hook_test_code = run_hook_self_tests()
        return 1 if self_test_code or hook_test_code else 0
    if args.repo_root is None:
        print(usage())
        return 2
    issues = validate(args.repo_root)
    print_result(issues)
    return 1 if issues else 0
