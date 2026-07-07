from __future__ import annotations

from .model import Issue, JsonObject, LEARNER_AUDIT_LABELS, SIDECAR_PROOF_FIELDS


def artifact_boundary_issues(label: str, learner_html: str, sidecar_proof: JsonObject | None) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    lowered_html = learner_html.casefold()
    for audit_label in LEARNER_AUDIT_LABELS:
        if audit_label.casefold() in lowered_html:
            issues.append(Issue(label, f"audit scaffold in learner HTML: {audit_label}"))
    issues.extend(past_year_learner_surface_issues(label, learner_html))
    if sidecar_proof is None:
        issues.append(Issue(label, "sidecar proof missing"))
        return tuple(issues)
    for field in SIDECAR_PROOF_FIELDS:
        if field not in sidecar_proof:
            issues.append(Issue(label, f"sidecar proof missing field: {field}"))
    return tuple(issues)


def past_year_learner_surface_issues(label: str, learner_html: str) -> tuple[Issue, ...]:
    lowered = learner_html.casefold()
    if not is_past_year_learner_surface(label, lowered):
        return ()
    issues: list[Issue] = []
    proof_tokens = (
        "generated ",
        "readiness_state",
        "usable_with_recorded_gaps",
        "ledger entries",
        "answer-ledger.json entries",
        "worker-report",
        "worker report",
        "verifier-reports",
        "answered from source",
        "source_refs",
        "source refs",
        "evidence:",
        "manual qa status",
        "source basis",
        "scope boundaries",
        "verification notes",
    )
    for token in proof_tokens:
        if token in lowered:
            issues.append(Issue(label, f"proof metadata in learner HTML: {token}"))
    if "metric-card" in lowered or "metric card" in lowered:
        issues.append(Issue(label, "metric cards are not allowed in past-year learner HTML"))
    if not all(font in lowered for font in ("inter", "source serif 4", "ibm plex mono")):
        issues.append(Issue(label, "missing Script font stack: Inter, Source Serif 4, and IBM Plex Mono"))
    if "past-year-script" not in lowered or "--focus" not in lowered or "--correct" not in lowered or "oklch(" not in lowered:
        issues.append(Issue(label, "missing Script design tokens for past-year-script"))
    if "<script" not in lowered or "hashchange" not in lowered:
        issues.append(Issue(label, "missing hash router"))
    if "reveal" not in lowered or "aria-expanded" not in lowered:
        issues.append(Issue(label, "missing reveal controls"))
    if "rail-wrap" not in lowered or "questionrail" not in lowered:
        issues.append(Issue(label, "missing left rail and active-paper question rail"))
    visible_paper_sections = lowered.count('class="paper"') + lowered.count("class='paper'")
    has_hidden_papers = "aria-hidden" in lowered or "hidden" in lowered or "view active" in lowered
    if visible_paper_sections > 1 and not has_hidden_papers:
        issues.append(Issue(label, "all papers visible in one scroll instead of one paper per hash-routed view"))
    return tuple(issues)


def is_past_year_learner_surface(label: str, lowered_html: str) -> bool:
    lowered_label = label.casefold()
    return any(
        token in lowered_label or token in lowered_html
        for token in (
            "past-year",
            "past year",
            "past_year",
            "past-year-script",
            "paper-",
        )
    )
