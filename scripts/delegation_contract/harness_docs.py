from __future__ import annotations

from pathlib import Path

from .harness_contract import check_harness_contract, fragment_has_positive_tokens, has_positive_token
from .io_utils import read_text
from .model import Issue, WORKER_SOURCE_WORK_TOKENS

HARNESS_LAYER_TOKENS = ("OmO/Codex harness", "OmO harness", "Codex harness")


def add_missing(path: str, detail: str, issues: list[Issue]) -> None:
    issues.append(Issue(path, detail))


def has_index_first(text: str) -> bool:
    return fragment_has_positive_tokens(text, ("index",), ("first", "before"))


def has_source_pack_first(text: str) -> bool:
    return fragment_has_positive_tokens(text, ("source-pack",), ("first", "before"))


def has_conductor(text: str) -> bool:
    return (
        fragment_has_positive_tokens(text, ("main thread",), ("conduct", "conductor", "orchestrator"))
        or fragment_has_positive_tokens(text, ("parent thread",), ("conduct", "conductor", "orchestrator"))
    )


def has_worker_source_work(text: str) -> bool:
    return fragment_has_positive_tokens(text, ("worker", "source"), WORKER_SOURCE_WORK_TOKENS)


def check_readme_harness_routing(text: str, path: str, issues: list[Issue]) -> None:
    if not has_positive_token(text, HARNESS_LAYER_TOKENS):
        add_missing(path, "missing-readme-harness-layer: README must name OmO/Codex harness routing", issues)
    if not has_conductor(text):
        add_missing(path, "missing-readme-conductor: README must make the main thread the conductor", issues)
    if not has_worker_source_work(text):
        add_missing(path, "missing-readme-worker-source-work: README must assign source-heavy work to workers", issues)
    if not has_index_first(text):
        add_missing(path, "missing-readme-index-first: README must route course folders through index first", issues)
    if not has_source_pack_first(text):
        add_missing(path, "missing-readme-source-pack-first: README must use source-pack first when fresh", issues)


def check_skill_harness_routing(text: str, path: str, issues: list[Issue]) -> None:
    if not has_positive_token(text, HARNESS_LAYER_TOKENS):
        add_missing(path, "missing-skill-harness-layer: skill must name OmO/Codex harness routing", issues)
    if not has_conductor(text):
        add_missing(path, "missing-skill-conductor: skill must make the main thread the conductor", issues)
    if not has_worker_source_work(text):
        add_missing(path, "missing-skill-worker-source-work: skill must assign source-heavy work to workers", issues)
    if not has_index_first(text) or not has_source_pack_first(text):
        add_missing(path, "missing-skill-course-folder-route: skill must route course folders index/source-pack first", issues)
    if "Source gap" not in text:
        add_missing(path, "missing-skill-source-gap: skill must preserve Source gap handling", issues)


def check_harness_docs(root: Path, issues: list[Issue]) -> None:
    readme_path = "README.md"
    readme_text = read_text(root, readme_path, issues)
    check_readme_harness_routing(readme_text, readme_path, issues)
    delegation_path = "skills/references/delegation.md"
    delegation_text = read_text(root, delegation_path, issues)
    check_harness_contract(delegation_text, delegation_path, issues)
