from __future__ import annotations

from pathlib import Path

from .io_utils import write_file
from .model import FixtureCase


def remove_harness_layer(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "The OmO/Codex harness routes Study Forge work through the active worker runtime.\n",
        "",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_delegation_harness_layer(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "The OmO/Codex harness routes Study Forge work through the active worker runtime.",
        "Study Forge does not use the OmO/Codex harness for orchestration.",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_readme_harness_layer(root: Path) -> None:
    write_file(
        root,
        "README.md",
        "Study Forge does not use the portable OmO/Codex harness. "
        + "The main thread acts as conductor while worker lanes own source extraction. "
        + "Course folder workflows run index first and source-pack first.",
    )


def negate_skill_harness_layer(root: Path) -> None:
    path = root / "skills/SKILL.md"
    text = path.read_text(encoding="utf-8").replace(
        "OmO/Codex harness main thread acts as conductor",
        "not OmO/Codex harness. main thread acts as conductor",
    )
    write_file(root, "skills/SKILL.md", text)


def write_parent_dirty_work(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8")
    write_file(
        root,
        "skills/references/delegation.md",
        f"{text}\nThe parent thread performs broad source extraction and source verification before assigning workers.\n",
    )


def write_parent_dirty_work_with_worker_tail(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8")
    write_file(
        root,
        "skills/references/delegation.md",
        f"{text}\nThe parent thread performs broad source extraction while workers do QA.\n",
    )


def remove_worker_assignment(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "Worker prompts are self-contained OmO/Codex assignments.\n",
        "",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_parent_conductor(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "The parent thread acts as conductor/orchestrator for Study Forge tasks.",
        "The parent thread is not the conductor/orchestrator for Study Forge tasks.",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_worker_source_work(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "Worker lanes own source-heavy work: source extraction, source-pack construction, "
        + "source indexing, verification, QA, and final review.",
        "Workers do not extract source evidence, construct source packs, index source records, "
        + "perform verification, run QA, or perform final review.",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_worker_assignment(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "Worker prompts are self-contained OmO/Codex assignments.",
        "Worker prompts are not self-contained OmO/Codex assignments.",
    )
    write_file(root, "skills/references/delegation.md", text)


def negate_fallback_reviewed_degraded(root: Path) -> None:
    path = root / "skills/references/delegation.md"
    text = path.read_text(encoding="utf-8").replace(
        "fallback_local_reviewed remains degraded local review and is not independent verification.",
        "fallback_local_reviewed is not degraded local review.",
    )
    write_file(root, "skills/references/delegation.md", text)


def production_harness_cases() -> tuple[FixtureCase, ...]:
    return (
        FixtureCase("missing-omo-harness-layer-production", remove_harness_layer, "missing-omo-harness-layer"),
        FixtureCase("negated-delegation-harness-layer-production", negate_delegation_harness_layer, "missing-omo-harness-layer"),
        FixtureCase("negated-readme-harness-layer-production", negate_readme_harness_layer, "missing-readme-harness-layer"),
        FixtureCase("negated-skill-harness-layer-production", negate_skill_harness_layer, "missing-skill-harness-layer"),
        FixtureCase("negated-parent-conductor", negate_parent_conductor, "missing-parent-conductor"),
        FixtureCase("negated-worker-source-work", negate_worker_source_work, "missing-worker-source-work"),
        FixtureCase("negated-worker-prompt-assignment", negate_worker_assignment, "missing-worker-prompt-assignment"),
        FixtureCase("negated-fallback-reviewed-degraded", negate_fallback_reviewed_degraded, "missing-fallback-reviewed-degraded"),
    )


def harness_contract_cases() -> tuple[FixtureCase, ...]:
    return (
        FixtureCase("missing-omo-harness-layer", remove_harness_layer, "missing-omo-harness-layer"),
        FixtureCase("negated-delegation-harness-layer", negate_delegation_harness_layer, "missing-omo-harness-layer"),
        FixtureCase("parent-does-source-heavy-work", write_parent_dirty_work, "parent-does-source-heavy-work"),
        FixtureCase("parent-does-source-heavy-work-worker-tail", write_parent_dirty_work_with_worker_tail, "parent-does-source-heavy-work"),
        FixtureCase("missing-worker-prompt-assignment", remove_worker_assignment, "missing-worker-prompt-assignment"),
        FixtureCase("negated-parent-conductor", negate_parent_conductor, "missing-parent-conductor"),
        FixtureCase("negated-worker-source-work", negate_worker_source_work, "missing-worker-source-work"),
        FixtureCase("negated-worker-prompt-assignment", negate_worker_assignment, "missing-worker-prompt-assignment"),
        FixtureCase("negated-fallback-reviewed-degraded", negate_fallback_reviewed_degraded, "missing-fallback-reviewed-degraded"),
    )
