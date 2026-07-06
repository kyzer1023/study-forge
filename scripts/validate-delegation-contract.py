#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# noqa: SIZE_OK - single-file standard-library contract validator; splitting it would broaden this scoped hook check.
# --- How to run ---
# python scripts/validate-delegation-contract.py --self-test
# python scripts/validate-delegation-contract.py --hook-exercise delegated
# python scripts/validate-delegation-contract.py --hook-exercise opt-out
# python scripts/validate-delegation-contract.py .

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import tempfile
import tomllib
from typing import Final, TypeAlias, assert_never


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
HOOK_AUTHORIZATION_SENTENCE: Final = (
    "The user explicitly authorizes Study Forge to use OMO-style subagent delegation lanes for this source-heavy command "
    "without second approval."
)
OPT_OUT_TOKENS: Final = ("local only", "no subagents", "no delegation", "restricts tool use")
HOOK_OPT_OUT_PHRASES: Final = (
    "local only",
    "stay local",
    "no subagents",
    "no delegation",
    "no delegate",
    "no agents",
    "no workers",
    "do not use subagents",
    "do not use agents",
    "do not use workers",
    "do not delegate",
    "do not spawn",
    "don't use subagents",
    "don't use agents",
    "don't use workers",
    "don't delegate",
    "without subagents",
    "without agents",
    "without workers",
    "without delegation",
)
INHERENTLY_SOURCE_HEAVY_COMMAND_PATTERNS: Final = (
    "$study-forge index",
    "$study-forge source-index",
    "$study-forge artifact",
)
SOURCE_SCOPED_STUDY_COMMAND_PATTERNS: Final = (
    "$study-forge distill",
    "$study-forge map",
    "$study-forge sheet",
    "$study-forge deconstruct",
    "$study-forge trace",
    "$study-forge drill",
    "$study-forge mark",
    "$study-forge rescue",
)
SOURCE_SCOPE_HINTS: Final = (
    ":\\\\",
    ":/",
    "\\\\",
    "://",
    ".study-forge",
    ".pdf",
    ".ppt",
    ".pptx",
    ".docx",
    ".ipynb",
    ".py",
    ".java",
    "course",
    "folder",
    "source",
    "sources",
    "lecture",
    "lectures",
    "slides",
    "past-year",
    "past year",
)
DELEGATED_EXERCISE_COMMANDS: Final = (
    '$study-forge index "C:\\\\Course"',
    '$study-forge source-index "C:\\\\Course"',
    '$study-forge artifact past-year "C:\\\\Course"',
    '$study-forge distill "C:\\\\Course\\\\Lecture"',
    '$study-forge map "C:\\\\Course"',
    '$study-forge sheet "C:\\\\Course"',
    '$study-forge deconstruct "C:\\\\Course"',
    '$study-forge trace "C:\\\\Course"',
    '$study-forge drill "C:\\\\Course"',
    '$study-forge mark "C:\\\\Course"',
    '$study-forge rescue "C:\\\\Course"',
)
OPT_OUT_EXERCISE_COMMANDS: Final = (
    '$study-forge distill lecture.pdf; user says "local only"',
    '$study-forge artifact past-year "C:\\\\Course"; user says "no subagents"',
    '$study-forge index "C:\\\\Course"; user says "no delegation"',
    '$study-forge map "C:\\\\Course"; user says "do not use subagents"',
    '$study-forge trace "C:\\\\Course"; user says "do not delegate"',
    '$study-forge drill slides.pdf; user says "don\'t use subagents"',
    '$study-forge mark answers.pdf; user says "without subagents"',
)
LOCAL_EXERCISE_COMMANDS: Final = (
    "$study-forge explain one term",
    '$study-forge trace "what is BFS?"',
    '$study-forge rescue "I have 2 hours"',
    '$study-forge trace "what is TCP/IP?"',
    '$study-forge rescue "I have 2/3 hours"',
    '$study-forge trace "BFS/DFS difference"',
)
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
INDEPENDENT_INVOCATION_MODES: Final = frozenset(("independent_subagent", "installed_toml_agent"))
LEARNER_AUDIT_LABELS: Final = (
    "Source Basis",
    "Scope Boundaries",
    "Verification Notes",
    "Manual QA status",
    "raw verifier",
    "verifier lane status",
    "raw worker-lane status",
)
SIDECAR_PROOF_FIELDS: Final = (
    "Source Basis",
    "Scope Boundaries",
    "Verification Notes",
    "Manual QA status",
    "lane_evidence",
    "raw_report_references",
)


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


@dataclass(frozen=True, slots=True)
class HookDecision:
    command: str
    delegate: bool
    authorization: str | None
    reason: str


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


def lines_with_all(text: str, tokens: Sequence[str]) -> tuple[str, ...]:
    return tuple(line for line in text.splitlines() if all(token in line for token in tokens))


def first_position(text: str, token: str) -> int | None:
    position = text.find(token)
    if position == -1:
        return None
    return position


def to_json_value(value: JsonValue) -> JsonValue:
    match value:
        case str() | int() | float() | bool() | None:
            return value
        case list():
            return [to_json_value(item) for item in value]
        case dict():
            return {str(key): to_json_value(item) for key, item in value.items()}
        case _ as unreachable:
            assert_never(unreachable)


def read_json_object(root: Path, relative_path: str, issues: list[Issue]) -> JsonObject | None:
    path = root / relative_path
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as error:
        issues.append(Issue(relative_path, f"cannot read UTF-8 JSON: {error}"))
        return None
    except json.JSONDecodeError as error:
        issues.append(Issue(relative_path, f"cannot parse JSON: {error}"))
        return None
    data = to_json_value(loaded)
    if isinstance(data, dict):
        return data
    issues.append(Issue(relative_path, "JSON root must be an object"))
    return None


def text_json(container: JsonObject, key: str) -> str | None:
    value = container.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def bool_json(container: JsonObject, key: str) -> bool | None:
    value = container.get(key)
    if isinstance(value, bool):
        return value
    return None


def object_json(container: JsonObject, key: str) -> JsonObject | None:
    value = container.get(key)
    if isinstance(value, dict):
        return value
    return None


def object_list_json(container: JsonObject, key: str) -> tuple[JsonObject, ...]:
    value = container.get(key)
    if isinstance(value, list):
        return tuple(item for item in value if isinstance(item, dict))
    return ()


def normalized_json_text(container: JsonObject, key: str) -> str:
    value = text_json(container, key)
    if value is None:
        return ""
    return "_".join(value.casefold().replace("-", " ").split())


def lane_has_child_proof(lane: JsonObject) -> bool:
    mode = normalized_json_text(lane, "invocation_mode")
    if mode not in INDEPENDENT_INVOCATION_MODES:
        return False
    has_child_identity = text_json(lane, "child_agent_id") is not None or text_json(lane, "child_thread_id") is not None
    return has_child_identity and text_json(lane, "raw_child_report_path") is not None and lane.get("parent_validated") is True


def has_indexer_construction_lane(lanes: Sequence[JsonObject]) -> bool:
    for lane in lanes:
        role = normalized_json_text(lane, "role")
        if role == "studyforge_indexer" and lane_has_child_proof(lane):
            return True
    return False


def has_source_index_verifier_lane(lanes: Sequence[JsonObject]) -> bool:
    for lane in lanes:
        role = normalized_json_text(lane, "role")
        lane_name = normalized_json_text(lane, "lane")
        if role == "studyforge_verifier" and lane_name == "source_index" and lane_has_child_proof(lane):
            return True
    return False


def artifact_boundary_issues(label: str, learner_html: str, sidecar_proof: JsonObject | None) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    for audit_label in LEARNER_AUDIT_LABELS:
        if audit_label in learner_html:
            issues.append(Issue(label, f"audit scaffold in learner HTML: {audit_label}"))
    if sidecar_proof is None:
        issues.append(Issue(label, "sidecar proof missing"))
        return tuple(issues)
    for field in SIDECAR_PROOF_FIELDS:
        if field not in sidecar_proof:
            issues.append(Issue(label, f"sidecar proof missing field: {field}"))
    return tuple(issues)


def check_delegation(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/delegation.md"
    text = read_text(root, relative_path, issues)
    require_tokens(text, relative_path, REQUIRED_SECTIONS, issues)
    require_tokens(text, relative_path, PROMPT_TOKENS, issues)
    require_tokens(text, relative_path, SHARED_TOKENS, issues)
    require_tokens(text, relative_path, (HOOK_AUTHORIZATION_SENTENCE, *OPT_OUT_TOKENS), issues)
    index_rows = lines_with_all(text, ("index", "source-index"))
    has_constructive_indexer = any(
        "studyforge-indexer" in row and "studyforge-verifier" in row and "source_index" in row for row in index_rows
    )
    if not has_constructive_indexer:
        issues.append(
            Issue(
                relative_path,
                "missing-indexer-construction: index/source-index matrix must name studyforge-indexer construction separately from studyforge-verifier source_index",
            )
        )


def check_index_reference(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/index.md"
    text = read_text(root, relative_path, issues)
    indexer_at = first_position(text, "studyforge-indexer")
    verifier_at = first_position(text, "studyforge-verifier")
    source_index_at = first_position(text, "source_index")
    if indexer_at is None or verifier_at is None or source_index_at is None or not (indexer_at < verifier_at and indexer_at < source_index_at):
        issues.append(
            Issue(
                relative_path,
                "verifier-before-indexer: index docs must run studyforge-indexer construction before studyforge-verifier source_index checks",
            )
        )
    if "file, file bundle, or page range" not in text:
        issues.append(Issue(relative_path, "missing sharding rule: indexer lanes must shard by file, file bundle, or page range"))
    topic_rule_lines = lines_with_all(text.casefold(), ("topic", "not"))
    if not topic_rule_lines:
        issues.append(Issue(relative_path, "missing topic sharding rule: topics must be outputs after extraction, not primary sharding keys"))


def check_skill_routing(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/SKILL.md"
    text = read_text(root, relative_path, issues)
    require_tokens(
        text,
        relative_path,
        (
            "references/delegation.md",
            "source-heavy",
            "second user approval",
            "validates worker output",
            HOOK_AUTHORIZATION_SENTENCE,
            *OPT_OUT_TOKENS,
        ),
        issues,
    )


def check_command_refs(root: Path, issues: list[Issue]) -> None:
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        text = read_text(root, relative_path, issues)
        require_tokens(text, relative_path, tokens, issues)
    check_index_reference(root, issues)


def check_source_pack_orchestration(root: Path, issues: list[Issue]) -> None:
    relative_path = ".study-forge/source-pack/pack-verification.json"
    pack = read_json_object(root, relative_path, issues)
    if pack is None:
        return
    preflight = object_json(pack, "tooling_preflight")
    tooling_available = bool_json(preflight, "available") if preflight is not None else None
    invocation_mode = normalized_json_text(pack, "invocation_mode")
    readiness = normalized_json_text(pack, "readiness_state")
    indexer_lanes = object_list_json(pack, "indexer_lanes")
    verifier_lanes = object_list_json(pack, "verifier_lanes")
    has_indexer = has_indexer_construction_lane(indexer_lanes)
    has_verifier = has_source_index_verifier_lane(verifier_lanes)
    if tooling_available is True and not has_indexer:
        issues.append(Issue(relative_path, "missing indexer construction evidence: tooling was available but no studyforge-indexer child lane was recorded"))
    if readiness == "independent_verified" and not (has_indexer and has_verifier):
        issues.append(Issue(relative_path, "independent readiness requires studyforge-indexer construction and studyforge-verifier source_index child proof"))
    if invocation_mode == "fallback_local" and tooling_available is True:
        issues.append(Issue(relative_path, "fallback_local cannot be conductor-complete while tooling_preflight.available is true"))


def check_artifact_boundary(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/artifact.md"
    text = read_text(root, relative_path, issues)
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.casefold()
        has_audit_label = any(label.casefold() in lowered for label in LEARNER_AUDIT_LABELS)
        main_surface_claim = any(token in lowered for token in ("visible", "near the top", "final html", "html render", "learner html", "main study surface"))
        sidecar_claim = any(token in lowered for token in ("sidecar", "proof file", "proof plane", "qa-report", "verifier-reports", "answer-ledger"))
        if has_audit_label and main_surface_claim and not sidecar_claim:
            issues.append(Issue(f"{relative_path}:{line_number}", "audit scaffold must not be required in learner HTML by default"))
    learner_path = "scripts/fixtures/delegation/audit-free-learner.html"
    proof_path = "scripts/fixtures/delegation/artifact-sidecar-proof.json"
    learner = read_text(root, learner_path, issues)
    proof = read_json_object(root, proof_path, issues)
    if learner or proof is not None:
        issues.extend(artifact_boundary_issues("audit-free-learner", learner, proof))


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
    check_source_pack_orchestration(root, issues)
    check_artifact_boundary(root, issues)
    check_truthfulness(root, issues)
    check_toml_roles(root, issues)
    return tuple(issues)


def decide_hook(command: str) -> HookDecision:
    lowered = command.casefold()
    if any(phrase in lowered for phrase in HOOK_OPT_OUT_PHRASES):
        return HookDecision(command, False, None, "user restricts tool use")
    if any(pattern in lowered for pattern in INHERENTLY_SOURCE_HEAVY_COMMAND_PATTERNS):
        return HookDecision(command, True, HOOK_AUTHORIZATION_SENTENCE, "source-heavy Study Forge command")
    if any(pattern in lowered for pattern in SOURCE_SCOPED_STUDY_COMMAND_PATTERNS) and any(hint in lowered for hint in SOURCE_SCOPE_HINTS):
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


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")


def write_valid_fixture(root: Path) -> None:
    hook_line = (
        f"{HOOK_AUTHORIZATION_SENTENCE} If the user says local only, no subagents, no delegation, "
        "or otherwise restricts tool use, record fallback_local instead."
    )
    delegation = "\n".join(
        (
            *REQUIRED_SECTIONS,
            *PROMPT_TOKENS,
            *SHARED_TOKENS,
            "second user approval",
            hook_line,
            "| `index` or `source-index` over a PDF-heavy or multi-source folder | Run `studyforge-indexer` construction by file, file bundle, or page range first, then run `studyforge-verifier` with lane `source_index`. | `studyforge-indexer`, `source_index`, `studyforge-verifier`, `qa_executor`, `final_reviewer` |",
        )
    )
    write_file(root, "skills/references/delegation.md", delegation)
    write_file(root, "skills/SKILL.md", f"references/delegation.md source-heavy second user approval validates worker output {hook_line}")
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        if relative_path == "skills/references/index.md":
            write_file(
                root,
                relative_path,
                "Run studyforge-indexer construction by file, file bundle, or page range first. "
                "Topics are outputs after extraction, not primary sharding keys. "
                "Then run studyforge-verifier with lane source_index. "
                + " ".join(tokens)
                + "\n",
            )
        elif relative_path == "skills/references/artifact.md":
            write_file(
                root,
                relative_path,
                " ".join(tokens)
                + "\nLearner HTML is self-contained and audit-free by default. "
                "Source Basis, Scope Boundaries, Verification Notes, Manual QA status, raw verifier lane status, lane_evidence, and raw_report references stay in sidecar proof files, qa-report.json, verifier-reports, and answer-ledger.json.\n",
            )
        else:
            write_file(root, relative_path, " ".join(tokens))
    write_file(
        root,
        ".study-forge/source-pack/pack-verification.json",
        "{\n"
        '  "invocation_mode": "independent_subagent",\n'
        '  "tooling_preflight": {"available": true},\n'
        '  "readiness_state": "independent_verified",\n'
        '  "indexer_lanes": [\n'
        "    {\n"
        '      "role": "studyforge-indexer",\n'
        '      "lane": "source_index",\n'
        '      "invocation_mode": "independent_subagent",\n'
        '      "child_agent_id": "indexer-child",\n'
        '      "raw_child_report_path": "indexer-reports/indexer-child.json",\n'
        '      "parent_validated": true\n'
        "    }\n"
        "  ],\n"
        '  "verifier_lanes": [\n'
        "    {\n"
        '      "role": "studyforge-verifier",\n'
        '      "lane": "source_index",\n'
        '      "invocation_mode": "independent_subagent",\n'
        '      "child_agent_id": "verifier-child",\n'
        '      "raw_child_report_path": "verifier-reports/source-index.json",\n'
        '      "parent_validated": true\n'
        "    }\n"
        "  ]\n"
        "}\n",
    )
    write_file(
        root,
        "scripts/fixtures/delegation/audit-free-learner.html",
        "<!doctype html><html><body><main><h1>Revision Atlas</h1><p>Source gap: unreadable annotation.</p></main></body></html>",
    )
    write_file(
        root,
        "scripts/fixtures/delegation/artifact-sidecar-proof.json",
        "{\n"
        '  "Source Basis": ["lecture slides"],\n'
        '  "Scope Boundaries": ["revision topics"],\n'
        '  "Verification Notes": ["learner surface checked"],\n'
        '  "Manual QA status": "PASS",\n'
        '  "lane_evidence": [{"lane": "learner_surface", "status": "PASS"}],\n'
        '  "raw_report_references": ["qa-report.json"]\n'
        "}\n",
    )
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


def remove_hook_authorization(root: Path) -> None:
    write_file(
        root,
        "skills/SKILL.md",
        "references/delegation.md source-heavy second user approval validates worker output local only no subagents no delegation user restricts tool use fallback_local",
    )


def remove_opt_out(root: Path) -> None:
    write_file(root, "skills/SKILL.md", f"references/delegation.md source-heavy second user approval validates worker output {HOOK_AUTHORIZATION_SENTENCE}")


def write_missing_indexer_construction(root: Path) -> None:
    hook_line = (
        f"{HOOK_AUTHORIZATION_SENTENCE} If the user says local only, no subagents, no delegation, "
        "or otherwise restricts tool use, record fallback_local instead."
    )
    delegation = "\n".join(
        (
            *REQUIRED_SECTIONS,
            *PROMPT_TOKENS,
            *SHARED_TOKENS,
            hook_line,
            "fallback_local is not independent verification; do not wait for a second user approval.",
            "| `index` or `source-index` over a PDF-heavy or multi-source folder | Delegate source-pack construction by file, file bundle, or page range; then run a separate source-pack challenge before readiness. | `source_index`, `qa_executor`, `final_reviewer` |",
        )
    )
    write_file(root, "skills/references/delegation.md", delegation)


def write_verifier_before_indexer(root: Path) -> None:
    text = (
        "source_index indexer verifier qa_executor final_reviewer fallback_local\n"
        "Run an independent studyforge-verifier invocation with lane source_index before construction.\n"
        "Then run studyforge-indexer lanes by file, file bundle, or page range.\n"
        "Topics are outputs after extraction, not primary sharding keys.\n"
    )
    write_file(root, "skills/references/index.md", text)


def write_fallback_local_pack_without_indexer(root: Path) -> None:
    write_file(
        root,
        ".study-forge/source-pack/pack-verification.json",
        "{\n"
        '  "invocation_mode": "fallback_local",\n'
        '  "tooling_preflight": {"available": true},\n'
        '  "readiness_state": "independent_verified",\n'
        '  "verifier_lanes": [\n'
        "    {\n"
        '      "role": "studyforge-verifier",\n'
        '      "lane": "source_index",\n'
        '      "invocation_mode": "independent_subagent",\n'
        '      "child_agent_id": "019f33ca-a9d2-7600-9c5f-95cf40fd9a77",\n'
        '      "raw_child_report_path": "verifier-reports/source-index.json",\n'
        '      "parent_validated": true\n'
        "    }\n"
        "  ],\n"
        '  "indexer_lanes": []\n'
        "}\n",
    )


def require_audit_heavy_learner_html(root: Path) -> None:
    write_file(
        root,
        "skills/references/artifact.md",
        "source_research verifier qa_executor final_reviewer fallback_local Source Basis visible Scope Boundaries visible Verification Notes section Manual QA status",
    )


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


def run_self_test() -> int:
    cases = (
        FixtureCase("missing-delegation", remove_delegation, "missing required file"),
        FixtureCase("missing-worker-prompt-shape", remove_prompt_shape, "missing required token: TASK:"),
        FixtureCase("fallback-local-claimed-independent", claim_fallback_independent, "fallback_local claimed"),
        FixtureCase("approval-before-spawn", require_approval, "requires second user approval"),
        FixtureCase("missing-hook-authorization", remove_hook_authorization, f"missing required token: {HOOK_AUTHORIZATION_SENTENCE}"),
        FixtureCase("missing-opt-out-coverage", remove_opt_out, "missing required token: local only"),
        FixtureCase("missing-indexer-construction", write_missing_indexer_construction, "missing-indexer-construction"),
        FixtureCase("verifier-before-indexer", write_verifier_before_indexer, "verifier-before-indexer"),
        FixtureCase("cpt212-fallback-local-pack", write_fallback_local_pack_without_indexer, "missing indexer construction evidence"),
        FixtureCase("artifact-audit-heavy-contract", require_audit_heavy_learner_html, "audit scaffold"),
    )
    if not all(expect_issue(case) for case in cases):
        return 1
    audit_free_html = "<main><h1>Revision Atlas</h1><p>Source gap: unreadable note.</p></main>"
    audit_heavy_html = "<main><h2>Source Basis</h2><p>Manual QA status and raw verifier lane status.</p></main>"
    sidecar_proof: JsonObject = {
        "Source Basis": ["lecture slides"],
        "Scope Boundaries": ["revision topics"],
        "Verification Notes": ["checked against ledger"],
        "Manual QA status": "PASS",
        "lane_evidence": [{"lane": "learner_surface", "status": "PASS"}],
        "raw_report_references": ["qa-report.json"],
    }
    missing_sidecar: JsonObject = {"Source Basis": ["lecture slides"], "lane_evidence": []}
    if not expect_artifact_boundary_issue("audit-heavy-learner", audit_heavy_html, sidecar_proof, "audit scaffold"):
        return 1
    if not expect_artifact_boundary_issue("artifact-sidecar-missing-proof", audit_free_html, missing_sidecar, "sidecar proof missing field"):
        return 1
    if not expect_artifact_boundary_clean("audit-free-learner", audit_free_html, sidecar_proof):
        return 1
    hook_ok = True
    for command in DELEGATED_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, True) and hook_ok
    for command in OPT_OUT_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, False) and hook_ok
    for command in LOCAL_EXERCISE_COMMANDS:
        hook_ok = expect_hook_decision(command, False) and hook_ok
    if not hook_ok:
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
        return run_self_test()
    if args.repo_root is None:
        print(usage())
        return 2
    issues = validate(args.repo_root)
    print_result(issues)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
