from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from .io_utils import write_file
from .model import (
    COMMAND_REQUIREMENTS,
    HOOK_AUTHORIZATION_SENTENCE,
    JsonObject,
    READINESS_FILES,
    REQUIRED_SECTIONS,
    PROMPT_TOKENS,
    SHARED_TOKENS,
)

AUDIT_FREE_LEARNER_HTML: Final = (
    "<!doctype html><html><body><main><h1>Revision Atlas</h1>"
    + "<p>Source gap: unreadable annotation.</p></main></body></html>"
)


def json_fixture(value: JsonObject) -> str:
    return f"{json.dumps(value, indent=2)}\n"


def independent_lane(role: str, child_id: str, report_path: str) -> JsonObject:
    return {
        "role": role,
        "lane": "source_index",
        "invocation_mode": "independent_subagent",
        "child_agent_id": child_id,
        "raw_child_report_path": report_path,
        "parent_validated": True,
    }


def valid_sidecar_proof() -> JsonObject:
    return {
        "Source Basis": ["lecture slides"],
        "Scope Boundaries": ["revision topics"],
        "Verification Notes": ["learner surface checked"],
        "Manual QA status": "PASS",
        "lane_evidence": [{"lane": "learner_surface", "status": "PASS"}],
        "raw_report_references": ["qa-report.json"],
    }


def missing_sidecar_proof() -> JsonObject:
    return {
        "Source Basis": ["lecture slides"],
        "lane_evidence": [],
    }


def valid_pack() -> JsonObject:
    return {
        "invocation_mode": "independent_subagent",
        "tooling_preflight": {
            "available": True,
            "checked": ["multi_agent_v1.spawn_agent"],
        },
        "readiness_state": "independent_verified",
        "indexer_lanes": [
            independent_lane("studyforge-indexer", "indexer-child", "indexer-reports/indexer-child.json"),
        ],
        "verifier_lanes": [
            independent_lane("studyforge-verifier", "verifier-child", "verifier-reports/source-index.json"),
        ],
    }


def fallback_pack_without_indexer() -> JsonObject:
    return {
        "invocation_mode": "fallback_local",
        "tooling_preflight": {
            "available": True,
            "checked": ["multi_agent_v1.spawn_agent"],
        },
        "readiness_state": "independent_verified",
        "verifier_lanes": [
            independent_lane("studyforge-verifier", "verifier-child", "verifier-reports/source-index.json"),
        ],
        "indexer_lanes": [],
    }


def incomplete_preflight_pack() -> JsonObject:
    return {
        "invocation_mode": "independent_subagent",
        "tooling_preflight": {"available": True},
        "readiness_state": "independent_verified",
        "indexer_lanes": [
            independent_lane("studyforge-indexer", "indexer-child", "indexer-reports/indexer-child.json"),
        ],
        "verifier_lanes": [
            independent_lane("studyforge-verifier", "verifier-child", "verifier-reports/source-index.json"),
        ],
    }


def write_valid_fixture(root: Path) -> None:
    hook_line = (
        f"{HOOK_AUTHORIZATION_SENTENCE} If the user says local only, no subagents, "
        + "no delegation, or otherwise restricts tool use, record fallback_local instead."
    )
    harness_lines = (
        "Study Forge uses the OmO/Codex harness as the orchestration layer.",
        "Study Forge does not implement a runtime or bespoke runtime; "
        + "it owns study semantics, proof contracts, artifact schemas, fallback labels, and validators.",
        "The parent thread is the conductor/orchestrator for Study Forge tasks.",
        "Workers do source-heavy dirty work: source extraction, source-pack construction, "
        + "source indexing, verification, QA, and final review.",
        "Worker prompt examples are self-contained OmO/Codex assignments.",
        "fallback_local_reviewed is degraded and not independent verification.",
    )
    delegation = "\n".join((
        *REQUIRED_SECTIONS,
        *harness_lines,
        *PROMPT_TOKENS,
        *SHARED_TOKENS,
        "second user approval",
        hook_line,
        "| `source_index` | Challenge source-pack inventory, freshness, coverage, page accounting, and consumer fallback behavior after studyforge-indexer construction. | PDF-heavy or multi-source `index`. | PASS, MAJOR, BLOCKING, or NOT_RUN findings. |",
        "| `index` or `source-index` over a PDF-heavy or multi-source folder | Run `studyforge-indexer` construction by file, file bundle, or page range first, then run `studyforge-verifier` with lane `source_index`. | `studyforge-indexer`, `source_index`, `studyforge-verifier`, `qa_executor`, `final_reviewer` |",
    ))
    write_file(root, "skills/references/delegation.md", delegation)
    skill_routing = (
        "references/delegation.md source-heavy second user approval validates worker output "
        + "OmO/Codex harness parent thread conductor workers do source-heavy dirty work "
        + f"{hook_line}"
    )
    write_file(root, "skills/SKILL.md", skill_routing)
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
    write_file(root, ".study-forge/source-pack/pack-verification.json", json_fixture(valid_pack()))


def write_artifact_fixtures(root: Path) -> None:
    write_file(root, "scripts/fixtures/delegation/audit-free-learner.html", AUDIT_FREE_LEARNER_HTML)
    write_file(
        root,
        "scripts/fixtures/delegation/artifact-sidecar-proof.json",
        json_fixture(valid_sidecar_proof()),
    )
