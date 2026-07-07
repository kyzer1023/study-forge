# Study Forge Past-Year Exam-Worthy Answer Contract Plan

Date: 2026-07-07
Repo: `C:\Dev\study-forge`
Audit source: CPT212 artifact run `019f3b21-18df-7821-8565-a6b19fbe2e59`
Course artifact audited: `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact`

> For agentic workers: implement this plan against the Study Forge repo, not the CPT212 course output folder. Treat `C:\CS_USM\Y2S2\CPT212` as read-only regression evidence unless the user explicitly asks to regenerate that course artifact.

## Goal

Make future `study-forge artifact past-year` outputs exam-worthy at the learner surface, not merely verifier-shaped in sidecars.

The audited CPT212 run used the OmO/Codex harness heavily, but the final artifact still failed the student-facing bar in two important ways:

- The learner HTML often rendered short hints from `student_explanation` while the full model answer lived only in `answer-ledger.json`.
- Some visual-dependent questions were marked `Unreadable` even when the rendered PDF page image visibly contained enough information for a human/model visual pass, for example `cpt212-2011-may-q2-a-i`.

## Current Evidence To Preserve

- Parent thread: `019f3b21-18df-7821-8565-a6b19fbe2e59`
- Parent final report: `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact\verifier-reports\final-parent-gate.json`
- Learner HTML: `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact\index.html`
- Canonical ledger: `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact\answer-ledger.json`
- Target regression page image: `C:\CS_USM\Y2S2\CPT212\.study-forge\source-pack\rendered-pages\past-year-cpt212-11-may-pdf-p0003-3.png`
- Target regression question: `cpt212-2011-may-2011-q2-a-i`, rendered anchor `cpt212-2011-may-q2-a-i`

Observed facts from the audit:

- The run spawned 21 child lanes: source preflight, four answer-production lanes, raw verifier lanes, rerun verifier lanes, and visual QA lanes.
- Final gate status was `USABLE_WITH_RECORDED_GAPS`, with 262 rendered items: 225 `Answered from source`, 5 `Source gap`, 12 `Out of scope`, and 20 `Unreadable`.
- The HTML was functionally usable, but many reveal panels were concise study notes rather than mark-bearing answers.
- The ledger was stronger than the HTML for several sampled questions, including array insertion code, quicksort trace, and heap traversal pseudocode.
- The 2011 AVL tree image for Q2(a)(i) is visible in the rendered PDF page image, but the ledger still marks the item `Unreadable` because text extraction did not recover the node structure.

## Scope

### Must Have

- Add repo-side contracts and validators so `artifact past-year` learner HTML renders exam answers from the canonical ledger, not only short explanations.
- Add question-type-specific expectations for model answers:
  - coding questions reveal code or pseudocode;
  - trace questions reveal step sequences or state tables;
  - graph/tree/heap/B-tree questions reveal the derived structure, table, traversal, or explicitly marked unresolved reason;
  - definition questions reveal mark-oriented definitions and keywords;
  - objective questions reveal selected option plus why it is correct and why distractors are wrong when the source supports it.
- Add a visual-evidence contract:
  - visual-dependent items must carry a visual locator/payload, a visual inspection result, or a blocked/unreadable reason that proves the rendered page image was inspected;
  - `Unreadable` cannot be based only on `pdftotext` failure when a rendered page image exists;
  - visual-dependent answer synthesis must use a visual worker/verifier lane before final status.
- Add regression coverage for the CPT212 2011 Q2(a)(i) failure shape without mutating the CPT212 artifact.
- Make `fallback_local` paper-answer lanes visibly degraded. A final parent gate must not upgrade fallback answer production into an exam-ready claim without independent verifier evidence.
- Make sidecar freshness stricter: final parent gates must not supersede stale raw reports unless the superseding evidence is newer than the rendered artifact and names exactly which findings are resolved or intentionally retained.
- Keep learner HTML audit-free: no source refs, verifier notes, readiness labels, local paths, worker paths, or proof metadata in the learner surface.
- Preserve existing Study Forge principles: course folder input, index first, source-pack first, original PDFs remain authority, unsupported answers become `Source gap`, outside-current-authority topics become `Out of scope`.

### Must Not Have

- Do not mutate, regenerate, or "fix" `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact` as part of this repo-side plan.
- Do not globally sync or install `C:\Users\kyzer\.agents\skills\study-forge` unless the user explicitly asks in the implementation thread.
- Do not commit, push, reset, or branch-delete unless the user explicitly asks.
- Do not weaken existing verifier or proof checks to make the current artifact pass.
- Do not hide source gaps by generating unsupported answers from general model knowledge.
- Do not remove `fallback_local`, `fallback_local_reviewed`, `baseline_unverified`, `usable_with_recorded_gaps`, `Source gap`, `Unreadable`, or `Out of scope` semantics.

## Worktree Guard

The repo is currently dirty. The implementation thread must begin by running:

```bash
git status --short
git diff --stat
```

Treat all pre-existing modified and untracked files as user/other-agent work. Work with them when they are in scope, but do not revert, overwrite, or delete them. If the current dirty design-contract work already implements part of a todo, verify it and record that as inherited work instead of redoing it.

## Verification Strategy

Evidence root:

```text
.omo/evidence/studyforge-pastyear-exam-worthy-contract/
```

Primary commands:

```bash
python -m py_compile scripts/validate-delegation-contract.py scripts/delegation_contract/*.py scripts/validate-pastyear-proof.py scripts/pastyear_proof_*.py
python scripts/validate-delegation-contract.py --self-test
python scripts/validate-delegation-contract.py .
python scripts/validate-pastyear-proof.py --self-test
git diff --check
```

Read-only CPT212 regression probes:

```bash
python scripts/validate-pastyear-proof.py "C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact"
```

If that command cannot pass against the current CPT212 artifact because the artifact predates the repo fix, record the expected failure as regression evidence. Do not patch the course artifact to make the command green.

## Todos

### Todo 1: Capture The Audit Regression As Failing Fixtures

Files likely involved:

- `scripts/fixtures/pastyear-proof/`
- `scripts/pastyear_proof_selftest.py`
- `scripts/pastyear_proof_selftest_cases.py`
- `scripts/pastyear_proof_rules.py`
- `scripts/pastyear_proof_model.py`

Implementation:

- Add a minimal fixture where `answer-ledger.json` contains a full mark-bearing `answer`, but the rendered learner payload only exposes `student_explanation`.
- Add a minimal fixture where a visual-dependent item is marked `Unreadable` solely because text extraction failed while a rendered image locator exists and no visual-inspection evidence is recorded.
- Include a fixture modeled on CPT212 2011 Q2(a)(i): visible AVL-tree prompt, text extraction missing the tree, and no visual lane result.
- Add self-test expectations for the new failures.

Acceptance:

- Self-test fails before the rule change for at least:
  - `HTML_DROPS_MODEL_ANSWER`
  - `UNREADABLE_WITH_UNCHECKED_VISUAL_PAYLOAD`
  - `FALLBACK_LOCAL_EXAM_READY_OVERCLAIM`
- The failures are captured under `.omo/evidence/studyforge-pastyear-exam-worthy-contract/todo-01-red.txt`.
- No CPT212 course files are modified.

QA:

```bash
python scripts/validate-pastyear-proof.py --self-test
git status --short
```

### Todo 2: Enforce Full Answer Rendering From The Ledger

Files likely involved:

- `skills/references/artifact.md`
- `skills/references/past-year-design.md`
- `scripts/pastyear_proof_rules.py`
- `scripts/pastyear_proof_answers.py`
- `scripts/delegation_contract/learner_surface.py`

Implementation:

- Update the contract so learner HTML renders the model answer from `answer-ledger.answer`.
- Treat `student_explanation` as a secondary "why this is right" panel, not the replacement for the model answer.
- Add validator logic that compares rendered answer text to the ledger answer for supported items.
- Add type-specific minimum structure checks, not crude length-only checks:
  - `coding`: contains code/pseudocode markers or a structured algorithm block;
  - `trace`: contains ordered steps, table rows, or state transitions;
  - `structured`: contains the final answer plus reasoning;
  - `objective`: contains selected option and explanation.
- Allow concise answers only for low-mark definitions or true/false items where the ledger answer itself is intentionally short.

Acceptance:

- A fixture where HTML only exposes `student_explanation` fails.
- A fixture where HTML exposes the full model answer passes.
- Existing proof-metadata leak checks still pass.

QA:

```bash
python scripts/validate-pastyear-proof.py --self-test
python scripts/validate-delegation-contract.py --self-test
python -m py_compile scripts/pastyear_proof_*.py scripts/delegation_contract/*.py
```

### Todo 3: Add Visual-Dependent Answer Evidence Rules

Files likely involved:

- `skills/references/artifact.md`
- `skills/references/studyforge-verifier.md`
- `scripts/pastyear_proof_inventory.py`
- `scripts/pastyear_proof_rules.py`
- `scripts/pastyear_proof_model.py`

Implementation:

- Add fields or accepted sidecar evidence for visual-dependent items:
  - `visual_locator`;
  - `rendered_page_image`;
  - `visual_payload`;
  - `visual_inspection_status`;
  - `visual_worker_report_path`.
- The exact field shape may follow existing proof model conventions, but it must be machine-checkable.
- Add a rule: if a question text includes figure/table/graph/tree/route-map/image terms, then the item must either:
  - include visual evidence sufficient to support the answer;
  - be marked `Unreadable` with evidence that the rendered visual was inspected and still not usable;
  - be marked `Source gap` or `Out of scope` for a separate, source-backed reason.
- Add a visual lane requirement for graph/tree/table/image-dependent answer synthesis.

Acceptance:

- CPT212 2011 Q2(a)(i)-style fixture fails when it has a rendered image but no visual inspection evidence.
- A fixture with visual inspection evidence and a supported AVL answer passes.
- A fixture with a rendered image inspected and explicitly too blurry/cropped/unusable passes as `Unreadable`.

QA:

```bash
python scripts/validate-pastyear-proof.py --self-test
python scripts/validate-pastyear-proof.py "C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact" > .omo/evidence/studyforge-pastyear-exam-worthy-contract/todo-03-cpt212-current.txt || true
```

### Todo 4: Tighten Harness Readiness And Fallback Semantics

Files likely involved:

- `skills/references/delegation.md`
- `skills/references/artifact.md`
- `scripts/pastyear_proof_readiness.py`
- `scripts/pastyear_proof_rules.py`
- `scripts/delegation_contract/checks.py`

Implementation:

- Require answer-production lanes for multi-paper `artifact past-year` work to be `independent_subagent` or explicitly degraded.
- If answer production remains `fallback_local`, final readiness cannot be `independent_verified` or equivalent exam-ready language.
- A parent local gate may summarize current status, but it cannot erase raw verifier `BLOCKING`/`MAJOR` findings unless a fresh report or explicit resolved-finding map exists.
- Add sidecar freshness checks:
  - report timestamps or artifact mtimes must prove the final gate happened after the rendered HTML and sidecars it verifies;
  - stale reports remain historical and cannot be counted as current pass evidence.

Acceptance:

- A fixture with fallback-local answer production and "ready" final wording fails.
- A fixture with fresh independent verifier reports and fixed findings passes.
- A fixture with stale screenshot/verifier evidence fails or remains degraded.

QA:

```bash
python scripts/validate-pastyear-proof.py --self-test
python scripts/validate-delegation-contract.py --self-test
python scripts/validate-delegation-contract.py .
```

### Todo 5: Update Study Forge Docs With Exam-Worthy Answer Rules

Files likely involved:

- `README.md`
- `skills/SKILL.md`
- `skills/references/artifact.md`
- `skills/references/studyforge-verifier.md`
- `skills/references/past-year-design.md`

Implementation:

- Define "exam-worthy" in repo docs as:
  - answers are mark-bearing;
  - worked steps are present where marks require them;
  - diagrams/tables/graphs/trees use visual evidence or are withheld;
  - learner HTML exposes the model answer, not only a study hint;
  - proof sidecars explain source refs and verifier state.
- Add anti-rules:
  - do not call a short hint a model answer;
  - do not mark visual questions unreadable without inspecting available rendered images;
  - do not call fallback-local answer synthesis independent verification.
- Keep learner HTML audit-free and study-friendly.

Acceptance:

- `rg -n "exam-worthy|model answer|student_explanation|visual|fallback_local|Unreadable" README.md skills` finds the new guidance.
- `python scripts/validate-delegation-contract.py .` passes.

QA:

```bash
python scripts/validate-delegation-contract.py .
python scripts/validate-pastyear-proof.py --self-test
git diff --check
```

### Todo 6: Real-Artifact Read-Only Regression Against CPT212

Files involved:

- No repo file edits unless a small read-only regression script is useful under `scripts/`.
- Do not modify `C:\CS_USM\Y2S2\CPT212`.

Implementation:

- Run the updated validator against `C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact`.
- Record the failures as expected evidence for the old artifact.
- Confirm the updated rules flag at least:
  - HTML answer compression where applicable;
  - visual-dependent unreadable/answered items without visual evidence;
  - fallback-local readiness overclaim if present;
  - stale or historical verifier reports if present.
- Independently inspect the CPT212 2011 rendered page image and record that the AVL tree is visible, proving the old artifact should not rely on text extraction alone.

Acceptance:

- Evidence file records current CPT212 failures without mutating course files.
- The evidence names `cpt212-2011-may-2011-q2-a-i` or its rendered anchor.
- The evidence records that this is a regression target for future artifact regeneration, not a repo test that must pass against the old artifact.

QA:

```bash
python scripts/validate-pastyear-proof.py "C:\CS_USM\Y2S2\CPT212\CPT212 Past-Year Artifact" > .omo/evidence/studyforge-pastyear-exam-worthy-contract/todo-06-cpt212-readonly.txt || true
git status --short
```

### Todo 7: Final Verification And Handoff

Implementation:

- Run the full validation stack.
- Confirm no protected course outputs changed.
- Confirm all new fixtures and docs are in repo paths only.
- Write `.omo/evidence/studyforge-pastyear-exam-worthy-contract/final-summary.md` with:
  - commands run;
  - pass/fail state;
  - known remaining limitations;
  - whether installed skill sync was intentionally skipped.

Acceptance:

- Full validator stack passes for repo fixtures.
- `git status --short` shows only intended repo changes and ignored `.omo` evidence.
- No files under `C:\CS_USM\Y2S2\CPT212` are modified.

QA:

```bash
python -m py_compile scripts/validate-delegation-contract.py scripts/delegation_contract/*.py scripts/validate-pastyear-proof.py scripts/pastyear_proof_*.py
python scripts/validate-delegation-contract.py --self-test
python scripts/validate-delegation-contract.py .
python scripts/validate-pastyear-proof.py --self-test
git diff --check
git status --short
```

## Success Criteria

- Repo docs state that past-year learner HTML must show model answers, not just hints.
- Validators fail when `answer-ledger.answer` is omitted from learner HTML for supported questions.
- Validators fail when a visual-dependent item is marked `Unreadable` without inspecting available rendered images.
- Validators fail when fallback-local answer production is called independent or exam-ready.
- CPT212 2011 Q2(a)(i) is captured as a regression shape.
- Existing source-gap, out-of-scope, unreadable, proof-sidecar, and learner-metadata-separation guarantees remain intact.
- No protected CPT212 course artifact is mutated by this repo-side implementation.
