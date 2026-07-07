# Study Forge Past-Year Design Contract ULW Notepad

Date: 2026-07-06
Repo: `C:\Dev\study-forge`
ULW session: `.omo/ulw-loop/pastyear-design-contract-20260706`

## Brief

Fix Study Forge repo-side prompt, contract, and validation so future `artifact past-year` runs load and enforce the installed `past-year-script` learner-surface design system before rendering learner HTML.

Scope guard:

- Repo-side changes first.
- Do not redefine or patch the OmO/Codex harness.
- Do not mutate installed global skill paths under `C:\Users\kyzer\.agents\skills\study-forge` unless an explicit sync step is requested.
- Do not commit unless explicitly asked.

## Skills

- `omo:ulw-loop`: active because the delegated task explicitly requires ULW mode, RED/GREEN evidence, and a durable notepad.
- `omo:programming`: active because this task edits Python validator and self-test files.
- `omo:ulw-plan`: surveyed but not used as planner-only mode, because this thread was delegated to implement rather than to wait for plan approval.

## Tier

LIGHT: narrow hardening inside existing Study Forge prompt docs and existing delegation-contract validators. No new renderer, no new domain layer, no DB/auth/external integration, and no cross-boundary refactor.

If a new validator module, renderer, or cross-domain refactor becomes necessary, upgrade to HEAVY and run the reviewer loop.

## Success Criteria

1. Prompt contract: `artifact past-year` routing requires loading `references/past-year-design.md` and design system files before learner HTML rendering, with `design_system_id: past-year-script` recorded in proof metadata.
   - RED: `python scripts/validate-delegation-contract.py --self-test` fails after adding a failing-first fixture that removes the design bridge.
   - GREEN: same command passes after updating docs and required tokens.

2. Learner-surface validator: an audited CPT212-style bad learner HTML fixture fails for proof metadata, metric-card/dashboard language, source refs, all-papers-visible long scroll, missing reveal buttons, missing hash router, and missing Script tokens.
   - RED: `python scripts/validate-delegation-contract.py --self-test` fails after adding a failing-first learner-surface fixture because existing `artifact_boundary_issues` is too weak.
   - GREEN: same command passes after tightening `artifact_boundary_issues`.

3. Existing contract checks still pass for the repo.
   - GREEN: `python scripts/validate-delegation-contract.py .`
   - GREEN: `python scripts/validate-pastyear-proof.py --self-test`
   - GREEN: `python -m py_compile scripts/validate-delegation-contract.py scripts/delegation_contract/*.py scripts/validate-pastyear-proof.py scripts/pastyear_proof_*.py`

## Real-Surface / Auxiliary QA

Surface is CLI/data-shaped prompt contract and validator behavior.

Scenario A, bad learner surface:

```bash
python scripts/validate-delegation-contract.py --self-test
```

Binary observable: self-test prints RED cases for the bad learner fixture and exits 0 only after the tightened validator rejects the fixture for learner-surface violations.

Scenario B, repo contract:

```bash
python scripts/validate-delegation-contract.py .
```

Binary observable: exits 0 only when current repo docs contain required routing/design tokens and valid learner fixtures remain clean.

Evidence directory:

`.omo/evidence/studyforge-pastyear-design-contract/`

## Findings

- Current installed global bridge exists at `C:\Users\kyzer\.agents\skills\study-forge\references\past-year-design.md`.
- Current repo `skills/SKILL.md` and `skills/references/artifact.md` mention audit-free learner HTML, verifier lanes, sidecars, and readiness states, but do not currently route `artifact past-year` to `references/past-year-design.md` or the `past-year-script` design system.
- Current validator only checks a short list of audit labels and sidecar proof fields. It does not enforce hash routing, reveal controls, one-paper views, Script design tokens, or proof/source metadata bans strongly enough for the audited CPT212 failure.

## Reviewer Rejection Follow-Up

First review rejected the initial completion for:

- Artifact contract contradictions that still told learner HTML to show compact source refs/source basis/syllabus fit.
- Python files over the 250 pure-LOC ceiling.
- Bad learner fixture self-test only locking `missing hash router`.
- Missing manual QA matrix and scoped programming/slop report.

Fixes applied:

- Reworded `skills/references/artifact.md` so source refs, source basis, syllabus/source fit, verifier status, readiness status, worker paths, and build metadata stay in proof sidecars, while learner HTML shows only question, reveal/answer panel, topic, marks, and learner-relevant `Source gap`/`Unreadable` notes.
- Split validator helpers into `scripts/delegation_contract/answer_production.py` and `scripts/delegation_contract/learner_surface.py`.
- Split self-test support into `scripts/delegation_contract/self_test_expectations.py` and `scripts/delegation_contract/self_test_html_fixtures.py`.
- Strengthened the audited bad HTML self-test to require proof metadata, worker path, source refs, metric cards, missing Script font stack/tokens, missing hash router, missing reveal controls, missing left rail, and all-papers-visible failures.
- Added `.omo/evidence/studyforge-pastyear-design-contract/manual-qa-matrix.md`.
- Added `.omo/evidence/studyforge-pastyear-design-contract/programming-slop-self-review.md`.
