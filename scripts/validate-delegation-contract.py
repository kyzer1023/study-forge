#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# --- How to run ---
# python scripts/validate-delegation-contract.py --self-test
# python scripts/validate-delegation-contract.py .

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile
import tomllib
from typing import Final


REQUIRED_SECTIONS: Final = (
    "# Delegation",
    "## Orchestrator Contract",
    "## Tooling Preflight",
    "## Worker Prompt Shape",
    "## Lane Catalog",
    "## Command Trigger Matrix",
    "## Fallback And Readiness States",
    "## Parent Verification",
    "## Evidence Metadata",
    "## Anti-Rules",
)
PROMPT_TOKENS: Final = ("TASK:", "DELIVERABLE", "SCOPE", "VERIFY", "fork_context:false")
SHARED_TOKENS: Final = (
    "source_research",
    "source_index",
    "qa_executor",
    "final_reviewer",
    "fallback_local",
    "baseline_unverified",
    "installed_toml_agent",
    "parent_validated",
    "tooling_preflight",
)
COMMAND_REQUIREMENTS: Final = {
    "skills/references/artifact.md": ("source_research", "verifier", "qa_executor", "final_reviewer", "fallback_local"),
    "skills/references/distill.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/map.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/deconstruct.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/trace.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/drill.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/mark.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/rescue.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/sheet.md": ("source_research", "verifier", "qa_executor", "fallback_local"),
    "skills/references/index.md": ("source_index", "indexer", "verifier", "qa_executor", "final_reviewer", "fallback_local"),
}
READINESS_FILES: Final = (
    "README.md",
    "skills/SKILL.md",
    "skills/references/delegation.md",
    "skills/references/index.md",
    "skills/references/studyforge-indexer.md",
    "skills/references/studyforge-verifier.md",
    "agents/studyforge-indexer.toml",
    "agents/studyforge-verifier.toml",
)
FALLBACK_CLAIM_PHRASES: Final = ("independent verification", "independently verified", "independent_verified")
FALLBACK_NEGATORS: Final = ("not independent", "not independently", "not present", "not claim", "not call", "cannot be called", "must not")


@dataclass(frozen=True, slots=True)
class Issue:
    path: str
    detail: str


@dataclass(frozen=True, slots=True)
class CliArgs:
    repo_root: Path | None
    self_test: bool


@dataclass(frozen=True, slots=True)
class FixtureCase:
    label: str
    mutate: Callable[[Path], None]
    expected: str


def usage() -> str:
    return "usage: scripts/validate-delegation-contract.py <repo-root> | --self-test"


def parse_args(argv: Sequence[str]) -> CliArgs | Issue:
    repo_root: Path | None = None
    self_test = False
    for token in argv:
        match token:
            case "--self-test":
                self_test = True
            case value if value.startswith("--"):
                return Issue(value, "unknown option")
            case value if repo_root is None:
                repo_root = Path(value)
            case value:
                return Issue(value, "unexpected positional argument")
    if not self_test and repo_root is None:
        return Issue("<repo-root>", "repo root is required")
    return CliArgs(repo_root=repo_root, self_test=self_test)


def read_text(root: Path, relative_path: str, issues: list[Issue]) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(Issue(relative_path, "missing required file"))
    except UnicodeDecodeError as error:
        issues.append(Issue(relative_path, f"cannot read UTF-8 text: {error}"))
    return ""


def require_tokens(text: str, relative_path: str, tokens: Sequence[str], issues: list[Issue]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(Issue(relative_path, f"missing required token: {token}"))


def check_delegation(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/delegation.md"
    text = read_text(root, relative_path, issues)
    require_tokens(text, relative_path, REQUIRED_SECTIONS, issues)
    require_tokens(text, relative_path, PROMPT_TOKENS, issues)
    require_tokens(text, relative_path, SHARED_TOKENS, issues)


def check_skill_routing(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/SKILL.md"
    text = read_text(root, relative_path, issues)
    require_tokens(
        text,
        relative_path,
        ("references/delegation.md", "source-heavy", "second user approval", "validates worker output"),
        issues,
    )


def check_command_refs(root: Path, issues: list[Issue]) -> None:
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        text = read_text(root, relative_path, issues)
        require_tokens(text, relative_path, tokens, issues)


def line_requires_user_approval(line: str) -> bool:
    lowered = line.casefold()
    approval_phrases = ("ask user approval before", "require second user approval", "wait for a second user approval")
    if not any(phrase in lowered for phrase in approval_phrases):
        return False
    allowed_phrases = ("do not", "without", "no second")
    return not any(phrase in lowered for phrase in allowed_phrases)


def check_truthfulness(root: Path, issues: list[Issue]) -> None:
    for relative_path in READINESS_FILES:
        text = read_text(root, relative_path, issues)
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.casefold()
            claims_independent = any(phrase in lowered for phrase in FALLBACK_CLAIM_PHRASES)
            if "fallback_local" in lowered and claims_independent and not any(negator in lowered for negator in FALLBACK_NEGATORS):
                issues.append(Issue(f"{relative_path}:{line_number}", "fallback_local claimed as independent verification"))
            if line_requires_user_approval(line):
                issues.append(Issue(f"{relative_path}:{line_number}", "requires second user approval before warranted delegation"))


def check_toml_roles(root: Path, issues: list[Issue]) -> None:
    agent_paths = sorted((root / "agents").glob("*.toml"))
    if not agent_paths:
        issues.append(Issue("agents", "missing TOML role definitions"))
        return
    for path in agent_paths:
        relative_path = path.relative_to(root).as_posix()
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
            issues.append(Issue(relative_path, f"cannot parse TOML: {error}"))
            continue
        for field in ("name", "developer_instructions"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(Issue(relative_path, f"missing TOML field: {field}"))
        instructions = data.get("developer_instructions")
        if isinstance(instructions, str):
            require_tokens(instructions, relative_path, ("optional role wording", "Do not invent", "source"), issues)


def validate(root: Path) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    check_delegation(root, issues)
    check_skill_routing(root, issues)
    check_command_refs(root, issues)
    check_truthfulness(root, issues)
    check_toml_roles(root, issues)
    return tuple(issues)


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_valid_fixture(root: Path) -> None:
    delegation = "\n".join((*REQUIRED_SECTIONS, *PROMPT_TOKENS, *SHARED_TOKENS, "second user approval"))
    write_file(root, "skills/references/delegation.md", delegation)
    write_file(root, "skills/SKILL.md", "references/delegation.md source-heavy second user approval validates worker output")
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        write_file(root, relative_path, " ".join(tokens))
    safe_line = "fallback_local is not independent verification; do not wait for a second user approval."
    for relative_path in READINESS_FILES:
        if relative_path.startswith("agents/"):
            continue
        path = root / relative_path
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        write_file(root, relative_path, f"{existing}\n{safe_line}\n")
    toml = 'name = "role"\ndeveloper_instructions = """optional role wording. Do not invent child IDs. Preserve source policy."""\n'
    write_file(root, "agents/studyforge-indexer.toml", toml)
    write_file(root, "agents/studyforge-verifier.toml", toml)


def remove_delegation(root: Path) -> None:
    (root / "skills/references/delegation.md").unlink()


def remove_prompt_shape(root: Path) -> None:
    write_file(root, "skills/references/delegation.md", "\n".join((*REQUIRED_SECTIONS, *SHARED_TOKENS)))


def claim_fallback_independent(root: Path) -> None:
    write_file(root, "skills/references/studyforge-verifier.md", "fallback_local is independent verification")


def require_approval(root: Path) -> None:
    write_file(root, "skills/SKILL.md", "references/delegation.md source-heavy validates worker output ask user approval before spawning")


def expect_issue(case: FixtureCase) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_valid_fixture(root)
        case.mutate(root)
        issues = validate(root)
    if any(case.expected in issue.detail for issue in issues):
        print(f"SELF-TEST RED {case.label}: PASS expected {case.expected}")
        return True
    print(f"FAIL self-test {case.label}: expected {case.expected}")
    print_result(issues)
    return False


def run_self_test() -> int:
    cases = (
        FixtureCase("missing-delegation", remove_delegation, "missing required file"),
        FixtureCase("missing-worker-prompt-shape", remove_prompt_shape, "missing required token: TASK:"),
        FixtureCase("fallback-local-claimed-independent", claim_fallback_independent, "fallback_local claimed"),
        FixtureCase("approval-before-spawn", require_approval, "requires second user approval"),
    )
    if not all(expect_issue(case) for case in cases):
        return 1
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_valid_fixture(root)
        issues = validate(root)
    if issues:
        print("FAIL self-test delegation contract")
        print_result(issues)
        return 1
    print("PASS self-test delegation contract")
    return 0


def print_result(issues: Sequence[Issue]) -> None:
    if not issues:
        print("PASS delegation contract")
        return
    print("FAIL delegation contract")
    for issue in issues:
        print(f"ISSUE path={issue.path} detail={issue.detail}")


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if isinstance(args, Issue):
        print(usage())
        print_result((args,))
        return 2
    if args.self_test:
        return run_self_test()
    if args.repo_root is None:
        print(usage())
        return 2
    issues = validate(args.repo_root)
    print_result(issues)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
