from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

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
    "fallback_local_reviewed",
    "baseline_unverified",
    "installed_toml_agent",
    "parent_validated",
    "tooling_preflight",
)
HARNESS_LAYER_TOKENS: Final = ("OmO/Codex harness", "OmO harness", "Codex harness")
RUNTIME_NEGATORS: Final = (
    "does not implement",
    "does not own",
    "not implement",
    "not own",
    "not a bespoke",
    "not a custom",
    "no bespoke",
)
PARENT_THREAD_TOKENS: Final = ("parent thread", "main thread", "conductor", "orchestrator")
PARENT_SOURCE_WORK_CLAIMS: Final = (
    "broad source extraction",
    "broad source indexing",
    "broad source verification",
    "source extraction",
    "source indexing",
    "source verification",
    "source-pack construction",
    "extracts sources",
    "indexes sources",
    "verifies sources",
)
PARENT_SOURCE_WORK_NEGATORS: Final = ("does not", "do not", "must not", "cannot", "is not responsible")
WORKER_SOURCE_WORK_TOKENS: Final = ("extract", "index", "source-pack", "verification", "qa")
WORKER_PROMPT_ASSIGNMENT_TOKENS: Final = ("self-contained", "assignment")
FALLBACK_REVIEWED_DEGRADED_TOKENS: Final = ("degraded", "not independent", "not independently", "not verified")
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
