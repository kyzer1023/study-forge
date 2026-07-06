from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tempfile

from .checks import artifact_boundary_issues, check_truthfulness, validate
from .harness_contract import check_harness_contract
from .io_utils import write_file
from .model import (
    FixtureCase,
    HOOK_AUTHORIZATION_SENTENCE,
    Issue,
    JsonObject,
    OPT_OUT_TOKENS,
    PROMPT_TOKENS,
    REQUIRED_SECTIONS,
    SHARED_TOKENS,
)
from .self_test_fixtures import (
    fallback_pack_without_indexer,
    incomplete_preflight_pack,
    json_fixture,
    missing_sidecar_proof,
    valid_sidecar_proof,
    write_valid_fixture,
    write_valid_pack,
)
from .self_test_harness_cases import clean_harness_cases, harness_contract_cases, production_harness_cases


def remove_delegation(root: Path) -> None:
    (root / "skills/references/delegation.md").unlink()


def remove_prompt_shape(root: Path) -> None:
    write_file(root, "skills/references/delegation.md", "\n".join((*REQUIRED_SECTIONS, *SHARED_TOKENS)))


def claim_fallback_independent(root: Path) -> None:
    write_file(root, "skills/references/studyforge-verifier.md", "fallback_local is independent verification")


def claim_fallback_reviewed_independent(root: Path) -> None:
    write_file(root, "README.md", "fallback_local_reviewed is independent verification")


def require_approval(root: Path) -> None:
    write_file(root, "skills/SKILL.md", "references/delegation.md source-heavy validates worker output ask user approval before spawning")


def remove_hook_authorization(root: Path) -> None:
    write_file(root, "skills/SKILL.md", "references/delegation.md source-heavy second user approval validates worker output local only no subagents no delegation user restricts tool use fallback_local")


def remove_opt_out(root: Path) -> None:
    write_file(root, "skills/SKILL.md", f"references/delegation.md source-heavy second user approval validates worker output {HOOK_AUTHORIZATION_SENTENCE}")


def write_missing_indexer_construction(root: Path) -> None:
    hook_line = f"{HOOK_AUTHORIZATION_SENTENCE} local only no subagents no delegation restricts tool use"
    delegation = "\n".join((*REQUIRED_SECTIONS, *PROMPT_TOKENS, *SHARED_TOKENS, hook_line, "| `source_index` | Challenge source-pack inventory. | index. | findings. |", "| `index` or `source-index` over a PDF-heavy or multi-source folder | Delegate source-pack construction by file, file bundle, or page range; then run a separate source-pack challenge before readiness. | `source_index`, `qa_executor`, `final_reviewer` |"))
    write_file(root, "skills/references/delegation.md", delegation)


def write_source_index_builds_pack(root: Path) -> None:
    text = "\n".join((*REQUIRED_SECTIONS, *PROMPT_TOKENS, *SHARED_TOKENS, HOOK_AUTHORIZATION_SENTENCE, *OPT_OUT_TOKENS, "| `source_index` | Build or refresh `.study-forge/source-pack/` records by file, file bundle, or page range, then challenge them. | index. | records or findings. |", "| `index` or `source-index` over a PDF-heavy or multi-source folder | Run `studyforge-indexer` construction by file, file bundle, or page range first; then run `studyforge-verifier` with lane `source_index`. | `studyforge-indexer`, `source_index`, `studyforge-verifier`, `qa_executor`, `final_reviewer` |"))
    write_file(root, "skills/references/delegation.md", text)


def write_verifier_before_indexer(root: Path) -> None:
    text = "source_index indexer verifier qa_executor final_reviewer fallback_local\nRun studyforge-verifier with lane source_index before construction.\nThen run studyforge-indexer lanes by file, file bundle, or page range.\nTopics are outputs after extraction, not primary sharding keys.\n"
    write_file(root, "skills/references/index.md", text)


def write_fallback_local_pack_without_indexer(root: Path) -> None:
    write_file(root, ".study-forge/source-pack/verifier-reports/source-index.json", "{}\n")
    write_file(
        root,
        ".study-forge/source-pack/pack-verification.json",
        json_fixture(fallback_pack_without_indexer()),
    )


def write_missing_raw_report_pack(root: Path) -> None:
    write_valid_pack(root)
    (root / ".study-forge/source-pack/indexer-reports/indexer-child.json").unlink()


def write_incomplete_preflight_pack(root: Path) -> None:
    write_valid_pack(root)
    write_file(
        root,
        ".study-forge/source-pack/pack-verification.json",
        json_fixture(incomplete_preflight_pack()),
    )


def require_audit_heavy_learner_html(root: Path) -> None:
    write_file(root, "skills/references/artifact.md", "source_research verifier qa_executor final_reviewer fallback_local Source Basis visible Scope Boundaries visible Verification Notes section Manual QA status")


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


def delegation_harness_issues(root: Path) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    relative_path = "skills/references/delegation.md"
    text = (root / relative_path).read_text(encoding="utf-8")
    check_harness_contract(text, relative_path, issues)
    return tuple(issues)


def truthfulness_issues(root: Path) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    check_truthfulness(root, issues)
    return tuple(issues)


def expect_direct_issue(case: FixtureCase, collect_issues: Callable[[Path], tuple[Issue, ...]]) -> bool:
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


def expect_clean_fixture(label: str, mutate: Callable[[Path], None]) -> bool:
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


def expect_artifact_boundary_issue(label: str, learner_html: str, sidecar_proof: JsonObject | None, expected: str) -> bool:
    issues = artifact_boundary_issues(label, learner_html, sidecar_proof)
    if any(expected in issue.detail for issue in issues):
        print(f"SELF-TEST RED {label}: PASS expected {expected}")
        return True
    print(f"FAIL self-test {label}: expected {expected}")
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


def self_test_cases() -> tuple[FixtureCase, ...]:
    return (
        *production_harness_cases(),
        FixtureCase("missing-delegation", remove_delegation, "missing required file"),
        FixtureCase("missing-worker-prompt-shape", remove_prompt_shape, "missing required token: TASK:"),
        FixtureCase("fallback-local-claimed-independent", claim_fallback_independent, "fallback_local claimed"),
        FixtureCase("approval-before-spawn", require_approval, "requires second user approval"),
        FixtureCase("missing-hook-authorization", remove_hook_authorization, f"missing required token: {HOOK_AUTHORIZATION_SENTENCE}"),
        FixtureCase("missing-opt-out-coverage", remove_opt_out, "missing required token: local only"),
        FixtureCase("missing-indexer-construction", write_missing_indexer_construction, "missing-indexer-construction"),
        FixtureCase("source-index-lane-builds-pack", write_source_index_builds_pack, "source_index lane must not construct"),
        FixtureCase("verifier-before-indexer", write_verifier_before_indexer, "verifier-before-indexer"),
        FixtureCase("cpt212-fallback-local-pack", write_fallback_local_pack_without_indexer, "missing indexer construction evidence"),
        FixtureCase("missing-raw-child-report", write_missing_raw_report_pack, "raw child report path does not exist"),
        FixtureCase("incomplete-tooling-preflight", write_incomplete_preflight_pack, "tooling_preflight.checked"),
        FixtureCase("artifact-audit-heavy-contract", require_audit_heavy_learner_html, "audit scaffold"),
    )


def truthfulness_cases() -> tuple[FixtureCase, ...]:
    return (
        FixtureCase("fallback-reviewed-claimed-independent", claim_fallback_reviewed_independent, "fallback_local_reviewed claimed"),
    )


def run_self_test() -> int:
    if not all(expect_direct_issue(case, delegation_harness_issues) for case in harness_contract_cases()):
        return 1
    if not all(expect_direct_issue(case, truthfulness_issues) for case in truthfulness_cases()):
        return 1
    if not all(expect_clean_fixture(label, mutate) for label, mutate in clean_harness_cases()):
        return 1
    if not all(expect_issue(case) for case in self_test_cases()):
        return 1
    audit_free_html = "<main><h1>Revision Atlas</h1><p>Source gap: unreadable note.</p></main>"
    audit_heavy_html = "<main><h2>Source Basis</h2><p>Manual QA status and raw verifier lane status.</p></main>"
    sidecar_proof = valid_sidecar_proof()
    missing_sidecar = missing_sidecar_proof()
    if not expect_artifact_boundary_issue("audit-heavy-learner", audit_heavy_html, sidecar_proof, "audit scaffold"):
        return 1
    if not expect_artifact_boundary_issue("artifact-sidecar-missing-proof", audit_free_html, missing_sidecar, "sidecar proof missing field"):
        return 1
    if not expect_artifact_boundary_clean("audit-free-learner artifact-sidecar-proof", audit_free_html, sidecar_proof):
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


def print_result(issues: tuple[Issue, ...] | list[Issue]) -> None:
    if not issues:
        print("PASS delegation contract")
        return
    print("FAIL delegation contract")
    for issue in issues:
        print(f"ISSUE path={issue.path} detail={issue.detail}")
