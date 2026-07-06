from __future__ import annotations

from pathlib import Path
import tempfile

from .checks import artifact_boundary_issues, validate
from .io_utils import write_file
from .model import (
    COMMAND_REQUIREMENTS,
    FixtureCase,
    HOOK_AUTHORIZATION_SENTENCE,
    Issue,
    JsonObject,
    OPT_OUT_TOKENS,
    PROMPT_TOKENS,
    READINESS_FILES,
    REQUIRED_SECTIONS,
    SHARED_TOKENS,
)


def write_valid_fixture(root: Path) -> None:
    hook_line = f"{HOOK_AUTHORIZATION_SENTENCE} If the user says local only, no subagents, no delegation, or otherwise restricts tool use, record fallback_local instead."
    delegation = "\n".join((
        *REQUIRED_SECTIONS,
        *PROMPT_TOKENS,
        *SHARED_TOKENS,
        "second user approval",
        hook_line,
        "| `source_index` | Challenge source-pack inventory, freshness, coverage, page accounting, and consumer fallback behavior after studyforge-indexer construction. | PDF-heavy or multi-source `index`. | PASS, MAJOR, BLOCKING, or NOT_RUN findings. |",
        "| `index` or `source-index` over a PDF-heavy or multi-source folder | Run `studyforge-indexer` construction by file, file bundle, or page range first, then run `studyforge-verifier` with lane `source_index`. | `studyforge-indexer`, `source_index`, `studyforge-verifier`, `qa_executor`, `final_reviewer` |",
    ))
    write_file(root, "skills/references/delegation.md", delegation)
    write_file(root, "skills/SKILL.md", f"references/delegation.md source-heavy second user approval validates worker output {hook_line}")
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        write_command_reference(root, relative_path, tokens)
    write_valid_pack(root)
    write_artifact_fixtures(root)
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


def write_command_reference(root: Path, relative_path: str, tokens: tuple[str, ...]) -> None:
    if relative_path == "skills/references/index.md":
        text = "Run studyforge-indexer construction by file, file bundle, or page range first. Topics are outputs after extraction, not primary sharding keys. Then run studyforge-verifier with lane source_index. "
        write_file(root, relative_path, text + " ".join(tokens) + "\n")
        return
    if relative_path == "skills/references/artifact.md":
        text = " ".join(tokens) + "\nLearner HTML is audit-free by default. Source Basis, Scope Boundaries, Verification Notes, Manual QA status, raw verifier lane status, lane_evidence, and raw_report references stay in sidecar proof files, qa-report.json, verifier-reports, and answer-ledger.json.\n"
        write_file(root, relative_path, text)
        return
    write_file(root, relative_path, " ".join(tokens))


def write_valid_pack(root: Path) -> None:
    write_file(root, ".study-forge/source-pack/indexer-reports/indexer-child.json", "{}\n")
    write_file(root, ".study-forge/source-pack/verifier-reports/source-index.json", "{}\n")
    write_file(root, ".study-forge/source-pack/pack-verification.json", "{\n"
        '  "invocation_mode": "independent_subagent",\n'
        '  "tooling_preflight": {"available": true, "checked": ["multi_agent_v1.spawn_agent"]},\n'
        '  "readiness_state": "independent_verified",\n'
        '  "indexer_lanes": [{"role": "studyforge-indexer", "lane": "source_index", "invocation_mode": "independent_subagent", "child_agent_id": "indexer-child", "raw_child_report_path": "indexer-reports/indexer-child.json", "parent_validated": true}],\n'
        '  "verifier_lanes": [{"role": "studyforge-verifier", "lane": "source_index", "invocation_mode": "independent_subagent", "child_agent_id": "verifier-child", "raw_child_report_path": "verifier-reports/source-index.json", "parent_validated": true}]\n'
        "}\n")


def write_artifact_fixtures(root: Path) -> None:
    write_file(root, "scripts/fixtures/delegation/audit-free-learner.html", "<!doctype html><html><body><main><h1>Revision Atlas</h1><p>Source gap: unreadable annotation.</p></main></body></html>")
    write_file(root, "scripts/fixtures/delegation/artifact-sidecar-proof.json", "{\n"
        '  "Source Basis": ["lecture slides"],\n'
        '  "Scope Boundaries": ["revision topics"],\n'
        '  "Verification Notes": ["learner surface checked"],\n'
        '  "Manual QA status": "PASS",\n'
        '  "lane_evidence": [{"lane": "learner_surface", "status": "PASS"}],\n'
        '  "raw_report_references": ["qa-report.json"]\n'
        "}\n")


def remove_delegation(root: Path) -> None:
    (root / "skills/references/delegation.md").unlink()


def remove_prompt_shape(root: Path) -> None:
    write_file(root, "skills/references/delegation.md", "\n".join((*REQUIRED_SECTIONS, *SHARED_TOKENS)))


def claim_fallback_independent(root: Path) -> None:
    write_file(root, "skills/references/studyforge-verifier.md", "fallback_local is independent verification")


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
    write_file(root, ".study-forge/source-pack/pack-verification.json", "{\n"
        '  "invocation_mode": "fallback_local",\n'
        '  "tooling_preflight": {"available": true, "checked": ["multi_agent_v1.spawn_agent"]},\n'
        '  "readiness_state": "independent_verified",\n'
        '  "verifier_lanes": [{"role": "studyforge-verifier", "lane": "source_index", "invocation_mode": "independent_subagent", "child_agent_id": "verifier-child", "raw_child_report_path": "verifier-reports/source-index.json", "parent_validated": true}],\n'
        '  "indexer_lanes": []\n'
        "}\n")


def write_missing_raw_report_pack(root: Path) -> None:
    write_valid_pack(root)
    (root / ".study-forge/source-pack/indexer-reports/indexer-child.json").unlink()


def write_incomplete_preflight_pack(root: Path) -> None:
    write_valid_pack(root)
    write_file(root, ".study-forge/source-pack/pack-verification.json", "{\n"
        '  "invocation_mode": "independent_subagent",\n'
        '  "tooling_preflight": {"available": true},\n'
        '  "readiness_state": "independent_verified",\n'
        '  "indexer_lanes": [{"role": "studyforge-indexer", "lane": "source_index", "invocation_mode": "independent_subagent", "child_agent_id": "indexer-child", "raw_child_report_path": "indexer-reports/indexer-child.json", "parent_validated": true}],\n'
        '  "verifier_lanes": [{"role": "studyforge-verifier", "lane": "source_index", "invocation_mode": "independent_subagent", "child_agent_id": "verifier-child", "raw_child_report_path": "verifier-reports/source-index.json", "parent_validated": true}]\n'
        "}\n")


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


def run_self_test() -> int:
    if not all(expect_issue(case) for case in self_test_cases()):
        return 1
    audit_free_html = "<main><h1>Revision Atlas</h1><p>Source gap: unreadable note.</p></main>"
    audit_heavy_html = "<main><h2>Source Basis</h2><p>Manual QA status and raw verifier lane status.</p></main>"
    sidecar_proof: JsonObject = {"Source Basis": ["lecture slides"], "Scope Boundaries": ["revision topics"], "Verification Notes": ["checked against ledger"], "Manual QA status": "PASS", "lane_evidence": [{"lane": "learner_surface", "status": "PASS"}], "raw_report_references": ["qa-report.json"]}
    missing_sidecar: JsonObject = {"Source Basis": ["lecture slides"], "lane_evidence": []}
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
