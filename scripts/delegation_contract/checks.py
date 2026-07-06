from __future__ import annotations

from pathlib import Path
import tomllib
from collections.abc import Sequence

from .io_utils import (
    bool_json,
    normalized_json_text,
    object_json,
    object_list_json,
    read_json_object,
    read_text,
    string_list_json,
    text_json,
)
from .model import (
    COMMAND_REQUIREMENTS,
    FALLBACK_CLAIM_PHRASES,
    FALLBACK_NEGATORS,
    HOOK_AUTHORIZATION_SENTENCE,
    INDEPENDENT_INVOCATION_MODES,
    Issue,
    LEARNER_AUDIT_LABELS,
    OPT_OUT_TOKENS,
    PROMPT_TOKENS,
    READINESS_FILES,
    REQUIRED_SECTIONS,
    SHARED_TOKENS,
    SIDECAR_PROOF_FIELDS,
    JsonObject,
)


def require_tokens(text: str, relative_path: str, tokens: Sequence[str], issues: list[Issue]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(Issue(relative_path, f"missing required token: {token}"))


def table_row(text: str, first_cell: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if cells and cells[0] == first_cell:
            return stripped
    return None


def first_position(text: str, token: str) -> int | None:
    position = text.find(token)
    if position == -1:
        return None
    return position


def check_delegation(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/delegation.md"
    text = read_text(root, relative_path, issues)
    require_tokens(text, relative_path, REQUIRED_SECTIONS, issues)
    require_tokens(text, relative_path, PROMPT_TOKENS, issues)
    require_tokens(text, relative_path, SHARED_TOKENS, issues)
    require_tokens(text, relative_path, (HOOK_AUTHORIZATION_SENTENCE, *OPT_OUT_TOKENS), issues)
    matrix_row = table_row(text, "`index` or `source-index` over a PDF-heavy or multi-source folder")
    if matrix_row is None or not all(token in matrix_row for token in ("studyforge-indexer", "studyforge-verifier", "source_index")):
        issues.append(Issue(relative_path, "missing-indexer-construction: index/source-index matrix must name studyforge-indexer construction separately from studyforge-verifier source_index"))
    source_index_row = table_row(text, "`source_index`")
    if source_index_row is None:
        issues.append(Issue(relative_path, "missing source_index lane catalog row"))
        return
    lowered = source_index_row.casefold()
    if "build or refresh" in lowered or "source-pack records" in lowered.split("|")[2]:
        issues.append(Issue(relative_path, "source_index lane must not construct source-pack records; use studyforge-indexer for construction"))
    if "challenge" not in lowered:
        issues.append(Issue(relative_path, "source_index lane must describe verifier challenge behavior"))


def check_index_reference(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/index.md"
    text = read_text(root, relative_path, issues)
    indexer_at = first_position(text, "studyforge-indexer")
    verifier_at = first_position(text, "studyforge-verifier")
    source_index_at = first_position(text, "source_index")
    if indexer_at is None or verifier_at is None or source_index_at is None or not (indexer_at < verifier_at and indexer_at < source_index_at):
        issues.append(Issue(relative_path, "verifier-before-indexer: index docs must run studyforge-indexer construction before studyforge-verifier source_index checks"))
    if "file, file bundle, or page range" not in text:
        issues.append(Issue(relative_path, "missing sharding rule: indexer lanes must shard by file, file bundle, or page range"))
    topic_lines = tuple(line for line in text.casefold().splitlines() if "topic" in line and "not" in line)
    if not topic_lines:
        issues.append(Issue(relative_path, "missing topic sharding rule: topics must be outputs after extraction, not primary sharding keys"))


def check_skill_routing(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/SKILL.md"
    text = read_text(root, relative_path, issues)
    require_tokens(text, relative_path, ("references/delegation.md", "source-heavy", "second user approval", "validates worker output", HOOK_AUTHORIZATION_SENTENCE, *OPT_OUT_TOKENS), issues)


def check_command_refs(root: Path, issues: list[Issue]) -> None:
    for relative_path, tokens in COMMAND_REQUIREMENTS.items():
        text = read_text(root, relative_path, issues)
        require_tokens(text, relative_path, tokens, issues)
    check_index_reference(root, issues)


def tooling_preflight_ready(pack: JsonObject, relative_path: str, issues: list[Issue]) -> bool:
    preflight = object_json(pack, "tooling_preflight")
    if preflight is None:
        issues.append(Issue(relative_path, "tooling_preflight must be recorded for independent readiness"))
        return False
    available = bool_json(preflight, "available")
    checked = string_list_json(preflight, "checked")
    if available is not True:
        issues.append(Issue(relative_path, "tooling_preflight.available must be true for independent readiness"))
    if not checked:
        issues.append(Issue(relative_path, "tooling_preflight.checked must name the worker tooling checked"))
    return available is True and bool(checked)


def lane_has_child_proof(root: Path, pack_dir: Path, lane: JsonObject, relative_path: str) -> bool:
    if normalized_json_text(lane, "invocation_mode") not in INDEPENDENT_INVOCATION_MODES:
        return False
    has_child_identity = text_json(lane, "child_agent_id") is not None or text_json(lane, "child_thread_id") is not None
    raw_path = text_json(lane, "raw_child_report_path")
    if not has_child_identity or raw_path is None or lane.get("parent_validated") is not True:
        return False
    return (root / pack_dir / raw_path).is_file()


def add_lane_proof_issues(root: Path, pack_dir: Path, lane: JsonObject, relative_path: str, label: str, issues: list[Issue]) -> None:
    if normalized_json_text(lane, "invocation_mode") not in INDEPENDENT_INVOCATION_MODES:
        return
    if text_json(lane, "child_agent_id") is None and text_json(lane, "child_thread_id") is None:
        issues.append(Issue(relative_path, f"{label} missing child identity"))
    raw_path = text_json(lane, "raw_child_report_path")
    if raw_path is None:
        issues.append(Issue(relative_path, f"{label} missing raw_child_report_path"))
    elif not (root / pack_dir / raw_path).is_file():
        issues.append(Issue(relative_path, f"{label} raw child report path does not exist: {raw_path}"))
    if lane.get("parent_validated") is not True:
        issues.append(Issue(relative_path, f"{label} parent_validated must be true"))


def has_complete_lane(root: Path, pack_dir: Path, lanes: Sequence[JsonObject], role: str, lane_name: str | None) -> bool:
    for lane in lanes:
        role_matches = normalized_json_text(lane, "role") == role
        lane_matches = lane_name is None or normalized_json_text(lane, "lane") == lane_name
        if role_matches and lane_matches and lane_has_child_proof(root, pack_dir, lane, ".study-forge/source-pack/pack-verification.json"):
            return True
    return False


def check_source_pack_orchestration(root: Path, issues: list[Issue]) -> None:
    relative_path = ".study-forge/source-pack/pack-verification.json"
    pack_dir = Path(".study-forge/source-pack")
    pack = read_json_object(root, relative_path, issues)
    if pack is None:
        return
    readiness = normalized_json_text(pack, "readiness_state")
    invocation_mode = normalized_json_text(pack, "invocation_mode")
    indexer_lanes = object_list_json(pack, "indexer_lanes")
    verifier_lanes = object_list_json(pack, "verifier_lanes")
    for lane in (*indexer_lanes, *verifier_lanes):
        add_lane_proof_issues(root, pack_dir, lane, relative_path, normalized_json_text(lane, "role") or "lane", issues)
    has_indexer = has_complete_lane(root, pack_dir, indexer_lanes, "studyforge_indexer", None)
    has_verifier = has_complete_lane(root, pack_dir, verifier_lanes, "studyforge_verifier", "source_index")
    independent_claim = readiness == "independent_verified" or invocation_mode in INDEPENDENT_INVOCATION_MODES
    if independent_claim:
        tooling_preflight_ready(pack, relative_path, issues)
    if object_json(pack, "tooling_preflight") is not None and bool_json(object_json(pack, "tooling_preflight") or {}, "available") is True and not has_indexer:
        issues.append(Issue(relative_path, "missing indexer construction evidence: tooling was available but no studyforge-indexer child lane was recorded"))
    if readiness == "independent_verified" and not (has_indexer and has_verifier):
        issues.append(Issue(relative_path, "independent readiness requires studyforge-indexer construction and studyforge-verifier source_index child proof"))
    if invocation_mode == "fallback_local" and object_json(pack, "tooling_preflight") is not None and bool_json(object_json(pack, "tooling_preflight") or {}, "available") is True:
        issues.append(Issue(relative_path, "fallback_local cannot be conductor-complete while tooling_preflight.available is true"))


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


def check_artifact_boundary(root: Path, issues: list[Issue]) -> None:
    relative_path = "skills/references/artifact.md"
    text = read_text(root, relative_path, issues)
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.casefold()
        has_label = any(label.casefold() in lowered for label in LEARNER_AUDIT_LABELS)
        main_claim = any(token in lowered for token in ("visible", "near the top", "final html", "html render", "learner html", "main study surface"))
        sidecar_claim = any(token in lowered for token in ("sidecar", "proof file", "proof plane", "qa-report", "verifier-reports", "answer-ledger"))
        if has_label and main_claim and not sidecar_claim:
            issues.append(Issue(f"{relative_path}:{line_number}", "audit scaffold must not be required in learner HTML by default"))
    learner = read_text(root, "scripts/fixtures/delegation/audit-free-learner.html", issues)
    proof = read_json_object(root, "scripts/fixtures/delegation/artifact-sidecar-proof.json", issues)
    if learner or proof is not None:
        issues.extend(artifact_boundary_issues("audit-free-learner", learner, proof))


def line_requires_user_approval(line: str) -> bool:
    lowered = line.casefold()
    approval_phrases = ("ask user approval before", "require second user approval", "wait for a second user approval")
    if not any(phrase in lowered for phrase in approval_phrases):
        return False
    return not any(phrase in lowered for phrase in ("do not", "without", "no second"))


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
