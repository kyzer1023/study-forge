from __future__ import annotations

from collections.abc import Sequence

from .model import (
    FALLBACK_REVIEWED_DEGRADED_TOKENS,
    HARNESS_LAYER_TOKENS,
    Issue,
    PARENT_SOURCE_WORK_CLAIMS,
    PARENT_SOURCE_WORK_NEGATORS,
    PARENT_THREAD_TOKENS,
    RUNTIME_NEGATORS,
    WORKER_PROMPT_ASSIGNMENT_TOKENS,
    WORKER_SOURCE_WORK_TOKENS,
)


def has_token(text: str, tokens: Sequence[str]) -> bool:
    lowered = text.casefold()
    return any(token.casefold() in lowered for token in tokens)


def line_has_tokens(text: str, required: Sequence[str], alternatives: Sequence[str]) -> bool:
    folded_required = tuple(token.casefold() for token in required)
    folded_alternatives = tuple(token.casefold() for token in alternatives)
    for line in text.casefold().splitlines():
        has_required = all(token in line for token in folded_required)
        has_alternative = any(token in line for token in folded_alternatives)
        if has_required and has_alternative:
            return True
    return False


def parent_claims_dirty_work(line: str) -> bool:
    lowered = line.casefold()
    parent_named = any(token in lowered for token in PARENT_THREAD_TOKENS)
    negated = any(negator in lowered for negator in PARENT_SOURCE_WORK_NEGATORS)
    source_work = any(claim in lowered for claim in PARENT_SOURCE_WORK_CLAIMS)
    return parent_named and source_work and not negated


def check_harness_contract(text: str, relative_path: str, issues: list[Issue]) -> None:
    if not has_token(text, HARNESS_LAYER_TOKENS):
        issues.append(Issue(
            relative_path,
            "missing-omo-harness-layer: docs must name OmO/Codex harness orchestration",
        ))
    if not line_has_tokens(text, ("runtime",), RUNTIME_NEGATORS):
        issues.append(Issue(
            relative_path,
            "missing-runtime-disclaimer: Study Forge must not own a bespoke runtime",
        ))
    parent_is_conductor = (
        line_has_tokens(text, ("parent thread",), ("conductor", "orchestrator"))
        or line_has_tokens(text, ("main thread",), ("conductor", "orchestrator"))
    )
    if not parent_is_conductor:
        issues.append(Issue(
            relative_path,
            "missing-parent-conductor: parent/main thread must be conductor or orchestrator",
        ))
    if not line_has_tokens(text, ("worker", "source"), WORKER_SOURCE_WORK_TOKENS):
        issues.append(Issue(
            relative_path,
            "missing-worker-source-work: workers must own source-heavy dirty work",
        ))
    if not line_has_tokens(
        text,
        WORKER_PROMPT_ASSIGNMENT_TOKENS,
        ("omo/codex", "omo harness", "codex worker", "codex assignment"),
    ):
        issues.append(Issue(
            relative_path,
            "missing-worker-prompt-assignment: prompts must be self-contained OmO/Codex assignments",
        ))
    if not line_has_tokens(text, ("fallback_local_reviewed",), FALLBACK_REVIEWED_DEGRADED_TOKENS):
        issues.append(Issue(
            relative_path,
            "missing-fallback-reviewed-degraded: fallback_local_reviewed must be degraded, not independent",
        ))
    for line_number, line in enumerate(text.splitlines(), start=1):
        if parent_claims_dirty_work(line):
            issues.append(Issue(
                f"{relative_path}:{line_number}",
                "parent-does-source-heavy-work: parent must conduct, not extract/index/verify broadly",
            ))
