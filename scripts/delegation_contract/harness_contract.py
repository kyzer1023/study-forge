from __future__ import annotations

from collections.abc import Sequence
import re

from .model import (
    HARNESS_LAYER_TOKENS,
    Issue,
    PARENT_SOURCE_WORK_CLAIMS,
    PARENT_SOURCE_WORK_NEGATORS,
    PARENT_THREAD_TOKENS,
    RUNTIME_NEGATORS,
    WORKER_PROMPT_ASSIGNMENT_TOKENS,
    WORKER_SOURCE_WORK_TOKENS,
)

CONTRACT_NEGATORS = (
    "not",
    "no",
    "never",
    "without",
    "cannot",
    "can't",
    "does not",
    "do not",
    "must not",
    "is not",
    "are not",
)
WORKER_OWNS_SOURCE_WORK = (
    "workers do",
    "workers own",
    "workers must own",
    "worker lanes do",
    "worker lanes own",
)
FALLBACK_REVIEWED_CONTRADICTIONS = (
    "not degraded",
    "not a degraded",
    "not locally reviewed",
)
FALLBACK_REVIEWED_PROOF = (
    "degraded",
    "not independent",
    "not independently",
    "not verified",
    "not upgradeable",
)
NEGATION_PATTERN = rf"\b({'|'.join(re.escape(token) for token in CONTRACT_NEGATORS)})(?:\s+\w+){{0,3}}\s*$"


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


def fragments(text: str) -> tuple[str, ...]:
    split_parts: list[str] = []
    for line in text.splitlines():
        split_parts.extend(part.strip() for part in re.split(r"(?<=[.;!?])\s+", line) if part.strip())
    return tuple(split_parts)


def term_is_negated(text: str, term: str) -> bool:
    lowered = text.casefold()
    folded_term = term.casefold()
    for match in re.finditer(re.escape(folded_term), lowered):
        prefix = lowered[max(0, match.start() - 40):match.start()]
        if re.search(NEGATION_PATTERN, prefix):
            return True
    return False


def contract_terms_are_negated(text: str, terms: Sequence[str]) -> bool:
    return any(term_is_negated(text, term) for term in terms)


def fragment_has_positive_tokens(text: str, required: Sequence[str], alternatives: Sequence[str]) -> bool:
    folded_required = tuple(token.casefold() for token in required)
    folded_alternatives = tuple(token.casefold() for token in alternatives)
    for fragment in fragments(text):
        lowered = fragment.casefold()
        has_required = all(token in lowered for token in folded_required)
        has_alternative = any(token in lowered for token in folded_alternatives)
        if has_required and has_alternative and not contract_terms_are_negated(fragment, (*required, *alternatives)):
            return True
    return False


def fallback_reviewed_is_degraded(text: str) -> bool:
    for line in text.splitlines():
        lowered = line.casefold()
        if "fallback_local_reviewed" not in lowered:
            continue
        if any(contradiction in lowered for contradiction in FALLBACK_REVIEWED_CONTRADICTIONS):
            return False
        if any(token in lowered for token in FALLBACK_REVIEWED_PROOF):
            return True
    return False


def parent_claims_dirty_work(line: str) -> bool:
    for fragment in fragments(line):
        lowered = fragment.casefold()
        parent_named = any(token in lowered for token in PARENT_THREAD_TOKENS)
        negated = any(negator in lowered for negator in PARENT_SOURCE_WORK_NEGATORS)
        source_work = any(claim in lowered for claim in PARENT_SOURCE_WORK_CLAIMS)
        worker_owns_source_work = any(phrase in lowered for phrase in WORKER_OWNS_SOURCE_WORK)
        if parent_named and source_work and not negated and not worker_owns_source_work:
            return True
    return False


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
        fragment_has_positive_tokens(text, ("parent thread",), ("conductor", "orchestrator"))
        or fragment_has_positive_tokens(text, ("main thread",), ("conductor", "orchestrator", "conduct"))
    )
    if not parent_is_conductor:
        issues.append(Issue(
            relative_path,
            "missing-parent-conductor: parent/main thread must be conductor or orchestrator",
        ))
    if not fragment_has_positive_tokens(text, ("worker", "source"), WORKER_SOURCE_WORK_TOKENS):
        issues.append(Issue(
            relative_path,
            "missing-worker-source-work: workers must own source-heavy dirty work",
        ))
    if not fragment_has_positive_tokens(
        text,
        WORKER_PROMPT_ASSIGNMENT_TOKENS,
        ("omo/codex", "omo harness", "codex worker", "codex assignment"),
    ):
        issues.append(Issue(
            relative_path,
            "missing-worker-prompt-assignment: prompts must be self-contained OmO/Codex assignments",
        ))
    if not fallback_reviewed_is_degraded(text):
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
