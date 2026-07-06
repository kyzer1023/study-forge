# studyforge-omo-harness-skill-shape - Work Plan

## TL;DR (For humans)
I treated this as open-ended and chose defaults from the recent Study Forge sessions. If you had a more specific final shape in mind, say so before execution continues.

**What you'll get:** Study Forge will be re-centered as a thin OmO/Codex harness skill for finals use: one course-folder prompt can index sources first, then produce verified study artifacts without the main thread doing broad extraction, QA, or verifier work itself. The current skill/orchestration work will be preserved on an archive branch before the overhaul branch changes the main-line direction.

**Why this approach:** The durable value is the study workflow contract, not another bespoke runtime. OmO already has the stronger orchestration harness; Study Forge should supply the study command semantics, worker prompts, proof schemas, fallback labels, and validators.

**What it will NOT do:** It will not mutate course artifacts under `C:\CS_USM\...` unless a later command explicitly asks for a course run. It will not claim TOML agent roles are live unless the active runtime proves them. It will not call a main-thread-only result independent verification.

**Effort:** Large
**Risk:** High - this touches git branch topology, the canonical skill docs, validator contracts, and installed skill parity.
**Decisions I made for you:** Use whole course folders by default; run `index` before artifacts; keep existing Study Forge commands but make them feed an OmO-harness flow; preserve proof details in sidecars; keep learner artifacts study-first; require explicit degraded-output acceptance for `fallback_local_reviewed`.

Your next move: execution is approved by the user's latest request. A fresh Codex implementation thread must run this plan with ULW/start-work discipline and sequential commits.

---

> TL;DR (machine): Large/high-risk architecture overhaul plan; archive current `main` at `e51e38c`, then implement an OmO-harness-centered Study Forge skill contract with validators, installed-skill sync, and sequential commits.

## Scope
### Must have
- Preserve current `main` work on a dedicated archive branch before changing implementation direction.
- Use current live git facts: current branch `main`, current HEAD `e51e38c`, upstream `origin/main`, clean status `## main...origin/main` at planning time.
- Create an implementation branch or Codex worktree branch for the overhaul before editing tracked files.
- Treat this `.omo/` plan as the handoff source, then copy it into tracked history at `docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md` before behavior/doc changes so sequential commits have a durable plan reference.
- Reframe Study Forge as a thin OmO/Codex harness skill:
  - parent thread is conductor;
  - OmO/Codex worker lanes do source research, source-pack construction, verification, QA, and final review;
  - Study Forge owns command routing, study semantics, proof contracts, artifact schemas, fallback labels, and validators.
- Keep the existing command family:
  - `index`, `source-index`;
  - `artifact atlas`, `artifact past-year`, `artifact formula-lab`, `artifact trace-lab`, `artifact drill-pack`;
  - feeders: `distill`, `map`, `deconstruct`, `trace`, `drill`, `mark`, `rescue`, `sheet`.
- Make the finals-friendly default journey explicit:
  - whole course folder input when lecture sources and past-year papers coexist;
  - `index` first;
  - artifact or drill/rescue workflow consumes the fresh source-pack;
  - originals remain authority;
  - gaps remain explicit.
- Remove or demote bespoke-runtime/hook language that makes Study Forge look like it owns subagent orchestration mechanics instead of using OmO/Codex harness conventions.
- Preserve an explicit worker authorization sentence only as a compatibility detail when the current Codex runtime gate requires it; do not make it the product architecture.
- Update validators and fixtures so regressions fail when:
  - source-heavy docs let the parent do broad dirty work;
  - source-pack construction and source_index verification are collapsed;
  - `fallback_local_reviewed` is called independent verification;
  - learner artifacts become proof dumps instead of study-first outputs;
  - installed skill copy drifts after final sync.
- Sync the installed global skill at `C:\Users\kyzer\.agents\skills\study-forge` only after repo checks pass, preserving installed-only legacy files unless explicitly obsolete.
- Use sequential Conventional Commits for traceability. Each tracked work unit gets its own commit after local verification.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not edit or regenerate course outputs under `C:\CS_USM\...`.
- Do not delete the old current-main work before the archive branch is verified.
- Do not push, force-push, run `git reset --hard`, reset published remote history, or delete branches unless the user explicitly approves that git operation in the implementation thread.
- Do not claim `main` has changed remotely unless a push actually succeeds.
- Do not install Codex TOML roles globally unless the user explicitly approves role installation.
- Do not treat source-controlled `agents/*.toml` files as proof that live Codex custom agents are available.
- Do not let source text, OCR output, screenshots, notebooks, or generated artifacts override Study Forge's authority order or prompt-injection guardrails.
- Do not hide `Source gap`, `Unreadable`, `manual_review_gap`, `fallback_local`, `fallback_local_reviewed`, `baseline_unverified`, or `usable_with_recorded_gaps`.
- Do not produce a learner artifact that is mostly links, page citations, proof notes, or navigation rather than teachable revision material.
- Do not make one omnibus commit.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD/tests-after hybrid. For validator behavior and command-contract changes, capture RED first with a failing validator fixture or targeted validator command, then GREEN after the docs/code change. For doc-only wording changes where no validator seam exists yet, capture RED with `rg`/parsed-doc checks proving the required wording/absence is not present, then add validator coverage in the same or next todo.
- Required baseline commands:
  - `python scripts/validate-delegation-contract.py --self-test`
  - `python scripts/validate-delegation-contract.py .`
  - `python scripts/validate-delegation-contract.py --hook-exercise delegated`
  - `python scripts/validate-delegation-contract.py --hook-exercise opt-out`
  - `python scripts/validate-pastyear-proof.py --self-test`
  - `python -m py_compile scripts/validate-delegation-contract.py scripts/delegation_contract/*.py scripts/validate-pastyear-proof.py scripts/pastyear_proof_*.py`
  - `git diff --check`
- Evidence root: `.omo/evidence/studyforge-omo-harness-skill-shape/`.
- Every todo must write one evidence file under that root containing:
  - RED proof command and output;
  - GREEN verification command and output;
  - manual/auxiliary QA command and output;
  - cleanup receipt;
  - commit hash and subject, or explicit no-commit reason.
- CLI/data-shaped QA is acceptable for this skill repo because the user-facing surface is docs, validators, git branch state, and installed skill files. Browser QA is not required unless the implementation creates or changes a rendered learner HTML surface.

## Execution strategy
### Parallel execution waves
- Wave 0 is serialized: git archive/branch safety must happen first.
- Wave 1 captures failing-first contract tests/checks and the exact current legacy assumptions to replace.
- Wave 2 can parallelize docs in disjoint surfaces after Wave 1:
  - top-level README/SKILL routing;
  - delegation/harness contract;
  - index/artifact source-pack and proof-plane details.
- Wave 3 updates validators/fixtures and installed skill parity after docs stabilize.
- Wave 4 runs full QA/review, global skill sync verification, and branch status reporting.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 | none | 2, 3, 4, 5, 6, 7, 8, 9 | none |
| 2 | 1 | 3, 4, 5, 6, 7, 8, 9, 10 | none |
| 3 | 2 | 4, 5, 6, 7, 8 | none |
| 4 | 3 | 7, 8, 9 | 5, 6 |
| 5 | 3 | 7, 8, 9 | 4, 6 |
| 6 | 3 | 7, 8, 9 | 4, 5 |
| 7 | 4, 5, 6 | 8, 9, 10 | none |
| 8 | 7 | 9, 10 | none |
| 9 | 8 | 10, F1, F2, F3, F4 | none |
| 10 | 9 | F1, F2, F3, F4 | none |
| F1 | 10 | completion | F2, F3, F4 |
| F2 | 10 | completion | F1, F3, F4 |
| F3 | 10 | completion | F1, F2, F4 |
| F4 | 10 | completion | F1, F2, F3 |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [x] 1. Create git archive branch and implementation branch/worktree safety checkpoint
  What to do / Must NOT do: Confirm status contains only the expected untracked tracked-plan handoff file `docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md`; create `archive/studyforge-current-skill-work-20260706` pointing at the pre-overhaul HEAD `e51e38c`; verify it resolves to the same commit; create/switch to an implementation branch such as `feat/studyforge-omo-harness-main` in the implementation worktree; do not reset, delete, or push any branch in this todo.
  Parallelization: Wave 0 | Blocked by: none | Blocks: all tracked edits
  References (executor has NO interview context - be exhaustive): `.omo/drafts/studyforge-omo-harness-skill-shape.md`; planning git evidence `main`, `origin/main`, `e51e38c`; `omo:git-master` skill; user request to archive current skill work for later.
  Acceptance criteria (agent-executable): `git show-ref --verify refs/heads/archive/studyforge-current-skill-work-20260706`; `git rev-parse archive/studyforge-current-skill-work-20260706` equals `git rev-parse e51e38c`; before Todo 2 commits the plan, `git status --short --branch` shows no dirty files except the expected untracked `docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md`; after Todo 2, status has no unexpected dirty files before behavior/doc edits.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `git log -1 --oneline archive/studyforge-current-skill-work-20260706` must print `e51e38c refactor(delegation): split validator contract checks`; failure CLI/data: `git diff --name-only archive/studyforge-current-skill-work-20260706 e51e38c` must print nothing. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-01-git-archive.txt`
  Commit: N | branch topology only; no tracked file change expected.

- [x] 2. Publish the approved plan into tracked history before behavior changes
  What to do / Must NOT do: Copy this `.omo/plans/studyforge-omo-harness-skill-shape.md` handoff plan into `docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md`. Update only path-specific references if needed; do not alter the approved scope or todos while copying. This step exists because `.omo/` is ignored and the user requested traceable sequential commits.
  Parallelization: Wave 0 | Blocked by: 1 | Blocks: all behavior/doc edits
  References (executor has NO interview context - be exhaustive): `.gitignore` entry for `.omo/`; existing tracked plan `docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md`; this plan file; user request for sequential commits.
  Acceptance criteria (agent-executable): `test -f docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md`; `git ls-files docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md` prints the tracked plan path after staging/commit; the copied plan includes `archive/studyforge-current-skill-work-20260706`, `e51e38c`, and the no-hard-reset/no-force-push guardrails.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `rg -n "archive/studyforge-current-skill-work-20260706|no-hard-reset|force-push|sequential commits" docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md` must find the safety terms; failure CLI/data: `git check-ignore -v docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md` must produce no ignore match. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-02-tracked-plan.txt`
  Commit: Y | `docs(plan): record Study Forge OmO harness overhaul`

- [x] 3. Capture failing-first contract checks for OmO-harness-first Study Forge
  What to do / Must NOT do: Add the cheapest failing validator fixture/checks that encode the new target before changing docs: Study Forge must be described as using OmO/Codex harness primitives, parent cannot do broad source extraction/indexing/verification work, fallback_local_reviewed cannot be independent verification, and worker prompt examples must be self-contained OmO/Codex assignments. Do not make production docs pass before RED is captured.
  Parallelization: Wave 1 | Blocked by: 2 | Blocks: 4, 5, 6, 7, 8
  References (executor has NO interview context - be exhaustive): `scripts/delegation_contract/model.py`; `scripts/delegation_contract/checks.py`; `scripts/delegation_contract/self_test.py`; `scripts/fixtures/delegation/*`; `skills/references/delegation.md:3`, `skills/references/delegation.md:21`, `skills/references/delegation.md:23`, `skills/references/delegation.md:93`, `skills/references/delegation.md:162`; `skills/SKILL.md:100`; `README.md:128`.
  Acceptance criteria (agent-executable): A RED evidence file shows the new fixture/check fails against the pre-change docs for the intended reason, then after adding the intended fixture/check it is committed with the failing expectation still represented in self-test coverage.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-delegation-contract.py --self-test` must pass after the fixture/check is wired; failure CLI/data: temporarily applying the fixture against an intentionally legacy sample must fail with a specific issue code/message, captured in evidence without leaving the sample active. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-03-contract-red-green.txt`
  Commit: Y | `test(harness): capture OmO-first Study Forge contract`

- [x] 4. Rewrite top-level Study Forge routing around the OmO harness and finals happy path
  What to do / Must NOT do: Update `README.md` and `skills/SKILL.md` so the first-level mental model is prompt-once finals workflow: whole course folder when applicable, index first, artifacts/drills consume the source-pack, main thread conducts, OmO/Codex workers do dirty work. Keep the command table intact. Demote bespoke hook/injection wording to compatibility detail. Do not remove anti-fabrication or source-gate rules.
  Parallelization: Wave 2 | Blocked by: 3 | Blocks: 7, 8, 9 | Can parallelize with: 5, 6
  References (executor has NO interview context - be exhaustive): `README.md:5`, `README.md:47`, `README.md:49`, `README.md:68`, `README.md:87`, `README.md:128`, `README.md:130`, `README.md:136`, `README.md:140`; `skills/SKILL.md:12`, `skills/SKILL.md:21`, `skills/SKILL.md:81`, `skills/SKILL.md:85`, `skills/SKILL.md:94`, `skills/SKILL.md:96`, `skills/SKILL.md:100`, `skills/SKILL.md:103`, `skills/SKILL.md:104`, `skills/SKILL.md:109`, `skills/SKILL.md:118`.
  Acceptance criteria (agent-executable): `rg -n "OmO|harness|course folder|index first|source-pack first|main thread.*conduct|workers do" README.md skills/SKILL.md` finds the new routing language; `rg -n "bespoke runtime|custom runtime|main thread.*broad source extraction" README.md skills/SKILL.md` finds no endorsement of bespoke runtime ownership.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-delegation-contract.py .` must pass after the docs update; failure CLI/data: `rg -n "Do not answer from memory|Source gap|fallback_local_reviewed|independent_verified" skills/SKILL.md README.md` must prove source/fallback guardrails still exist. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-04-top-level-routing.txt`
  Commit: Y | `docs(skill): center Study Forge on OmO harness`

- [x] 5. Rewrite the shared delegation reference as a portable OmO/Codex worker contract
  What to do / Must NOT do: Update `skills/references/delegation.md` so it clearly says Study Forge does not implement a runtime; it uses live OmO/Codex worker tools when available, pastes role/lane instructions into normal workers when TOMLs are not exposed, records preflight, and labels local fallback honestly. Keep the lane catalog and command trigger matrix, but ensure source-pack construction belongs to `studyforge-indexer` and `source_index` is verifier-only. Do not claim source-controlled TOMLs are live agents.
  Parallelization: Wave 2 | Blocked by: 3 | Blocks: 7, 8, 9 | Can parallelize with: 4, 6
  References (executor has NO interview context - be exhaustive): `skills/references/delegation.md:3`, `skills/references/delegation.md:5`, `skills/references/delegation.md:7`, `skills/references/delegation.md:21`, `skills/references/delegation.md:23`, `skills/references/delegation.md:25`, `skills/references/delegation.md:43`, `skills/references/delegation.md:62`, `skills/references/delegation.md:64`, `skills/references/delegation.md:68`, `skills/references/delegation.md:69`, `skills/references/delegation.md:80`, `skills/references/delegation.md:82`, `skills/references/delegation.md:95`, `skills/references/delegation.md:109`, `skills/references/delegation.md:124`, `skills/references/delegation.md:160`.
  Acceptance criteria (agent-executable): `python scripts/validate-delegation-contract.py .` passes; `rg -n "source-controlled.*not.*live|TOML.*not.*proof|fallback_local_reviewed.*Degraded|source_index.*does not construct" skills/references/delegation.md` finds explicit guardrails.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-delegation-contract.py --hook-exercise delegated` must pass; failure CLI/data: `python scripts/validate-delegation-contract.py --hook-exercise opt-out` must pass and prove opt-outs still stop delegation. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-05-delegation-contract.txt`
  Commit: Y | `docs(delegation): make OmO harness the orchestration layer`

- [x] 6. Tighten index and artifact references for source-pack-first, proof-ledger-backed study workflows
  What to do / Must NOT do: Update `skills/references/index.md` and `skills/references/artifact.md` so course-folder study flows are operationally clear: indexer lanes build, verifier lanes challenge, artifacts consume fresh packs but render from proof ledgers, and learner HTML stays study-first. Preserve `Source gap` / `Unreadable` behavior and degraded-output acceptance. Do not make source-pack the final answer authority.
  Parallelization: Wave 2 | Blocked by: 3 | Blocks: 7, 8, 9 | Can parallelize with: 4, 5
  References (executor has NO interview context - be exhaustive): `skills/references/index.md:3`, `skills/references/index.md:5`, `skills/references/index.md:7`, `skills/references/index.md:11`, `skills/references/index.md:12`, `skills/references/index.md:14`, `skills/references/index.md:18`, `skills/references/index.md:20`, `skills/references/index.md:22`, `skills/references/index.md:48`, `skills/references/index.md:58`, `skills/references/index.md:196`, `skills/references/index.md:210`; `skills/references/artifact.md:3`, `skills/references/artifact.md:7`, `skills/references/artifact.md:15`, `skills/references/artifact.md:21`, `skills/references/artifact.md:23`, `skills/references/artifact.md:25`, `skills/references/artifact.md:80`, `skills/references/artifact.md:84`, `skills/references/artifact.md:108`, `skills/references/artifact.md:110`, `skills/references/artifact.md:111`, `skills/references/artifact.md:112`, `skills/references/artifact.md:136`, `skills/references/artifact.md:176`, `skills/references/artifact.md:238`, `skills/references/artifact.md:252`.
  Acceptance criteria (agent-executable): `rg -n "index.*first|source-pack.*access layer|answer-ledger.*canonical|study-first|without opening the PDF|fallback_local_reviewed" skills/references/index.md skills/references/artifact.md` proves the intended workflow and guardrails.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-pastyear-proof.py --self-test` must pass; failure CLI/data: `rg -n "must not replace the answer ledger|must not be treated as stronger than the current source files|Source gap|Unreadable" skills/references/index.md skills/references/artifact.md` must prove no overclaim. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-06-index-artifact.txt`
  Commit: Y | `docs(artifact): route finals workflows through source packs`

- [x] 7. Update delegation validators and fixtures to enforce the new OmO-harness contract
  What to do / Must NOT do: Adjust `scripts/delegation_contract/model.py`, `scripts/delegation_contract/checks.py`, `scripts/delegation_contract/self_test.py`, and any fixtures under `scripts/fixtures/delegation/` so the new docs from todos 3-5 are machine-checked. Keep checks structural and content-based; do not overfit exact prose where a durable concept token is enough. Do not remove existing sidecar proof, audit-free learner, indexer-before-verifier, opt-out, or fallback checks.
  Parallelization: Wave 3 | Blocked by: 4, 5, 6 | Blocks: 8, 9, 10
  References (executor has NO interview context - be exhaustive): `scripts/delegation_contract/model.py:35`, `scripts/delegation_contract/model.py:47`, `scripts/delegation_contract/model.py:86`, `scripts/delegation_contract/model.py:124`; `scripts/delegation_contract/checks.py:59`, `scripts/delegation_contract/checks.py:66`, `scripts/delegation_contract/checks.py:80`, `scripts/delegation_contract/checks.py:95`, `scripts/delegation_contract/checks.py:101`; `scripts/delegation_contract/self_test.py`; `scripts/fixtures/delegation/`.
  Acceptance criteria (agent-executable): `python scripts/validate-delegation-contract.py --self-test`, `python scripts/validate-delegation-contract.py .`, delegated hook exercise, opt-out exercise, and `python -m py_compile ...` all pass.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-delegation-contract.py .` must pass with `PASS delegation contract`; failure CLI/data: introduce a temporary fixture/sample missing the OmO harness token or mislabeling `fallback_local_reviewed` as independent, run the validator to confirm it fails, then remove the temporary sample and prove `git status --short` has no temp file. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-07-validator-contract.txt`
  Commit: Y | `test(harness): enforce OmO-backed Study Forge routing`

- [x] 8. Remove stale bespoke-orchestration claims and preserve role docs as prompt templates
  What to do / Must NOT do: Audit `agents/*.toml`, `skills/references/studyforge-indexer.md`, `skills/references/studyforge-verifier.md`, and any docs that imply role files are automatically live. Keep role docs as reusable prompt templates for OmO/Codex workers. Remove, rewrite, or label stale bespoke orchestration claims. Do not delete role files unless a validator and README update prove deletion is safe.
  Parallelization: Wave 3 | Blocked by: 7 | Blocks: 9, 10
  References (executor has NO interview context - be exhaustive): `README.md:132`, `README.md:136`, `README.md:138`; `skills/references/delegation.md:5`, `skills/references/delegation.md:31`, `skills/references/delegation.md:80`; `agents/studyforge-indexer.toml`; `agents/studyforge-verifier.toml`; `skills/references/studyforge-indexer.md`; `skills/references/studyforge-verifier.md`.
  Acceptance criteria (agent-executable): `rg -n "automatically live|registered custom agent|must install.*TOML|do not install them globally unless" README.md skills agents` returns no misleading automatic-live claims and retains the explicit no-global-install guardrail.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python scripts/validate-delegation-contract.py .` passes after audit edits; failure CLI/data: `rg -n "source-controlled.*role definitions|paste the relevant lane instructions|normal Codex worker" README.md skills/references/delegation.md skills/references/index.md skills/references/artifact.md` proves fallback prompt-template wording is present. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-08-role-docs.txt`
  Commit: Y | `docs(agents): keep Study Forge roles as harness prompts`

- [x] 9. Sync installed global Study Forge skill after repo checks pass
  What to do / Must NOT do: Compare repo-owned skill files with `C:\Users\kyzer\.agents\skills\study-forge`; create a rollback backup outside discoverable skill roots such as `C:\Users\kyzer\.agents\skill-backups\study-forge-omo-harness-YYYYMMDD-HHMMSS`; copy only repo-owned Study Forge files; preserve installed-only legacy files unless explicitly obsolete; verify hash parity for all repo-owned files; write the exact restore command in evidence. Do not create `_backups` or duplicate skill metadata under `C:\Users\kyzer\.agents\skills`; do not globally install TOML roles.
  Parallelization: Wave 4 | Blocked by: 8 | Blocks: 10, F1, F2, F3, F4
  References (executor has NO interview context - be exhaustive): `README.md:108`; `README.md:136`; `skills/SKILL.md`; `C:\Users\kyzer\.agents\skills\study-forge`; memory guidance that discoverable backup folders can cause duplicate picker entries.
  Acceptance criteria (agent-executable): A manifest file under `.omo/evidence/studyforge-omo-harness-skill-shape/task-09-installed-parity.json` lists every copied repo-owned file, SHA-256 for repo and installed copy, and `match: true`; `find C:/Users/kyzer/.agents/skills/study-forge -path '*_backups*' -o -path '*backup*'` does not reveal a discoverable duplicate skill metadata folder; evidence includes a restore command from the backup path.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `python -c "from pathlib import Path; import hashlib,json,sys; root=Path('.'); installed=Path(r'C:\Users\kyzer\.agents\skills\study-forge'); rels=[Path('README.md')]+[p for base in (Path('skills'),Path('agents')) for p in sorted(base.rglob('*')) if p.is_file()]; rows=[]; ok=True; [rows.append({'path':str(r).replace('\\\\','/'),'repo_sha256':hashlib.sha256((root/r).read_bytes()).hexdigest(),'installed_sha256':hashlib.sha256((installed/r).read_bytes()).hexdigest() if (installed/r).is_file() else None,'match':(installed/r).is_file() and hashlib.sha256((root/r).read_bytes()).hexdigest()==hashlib.sha256((installed/r).read_bytes()).hexdigest()}) for r in rels]; ok=all(row['match'] for row in rows); out=Path('.omo/evidence/studyforge-omo-harness-skill-shape/task-09-installed-parity.json'); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(rows,indent=2),encoding='utf-8'); print('PASS installed parity' if ok else 'FAIL installed parity'); sys.exit(0 if ok else 1)"` must print `PASS installed parity`; failure CLI/data: `rg -n "^name: study-forge|description: Use when" C:/Users/kyzer/.agents/skills/study-forge` must show exactly the intended installed skill entry, not duplicate backup entries. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-09-installed-sync.txt`
  Commit: Y/N | Commit only repo-tracked docs/scripts if the sync requires tracked manifest/docs updates; otherwise no commit with explicit installed-copy evidence.

- [x] 10. Run full validation, commit audit, and branch status report
  What to do / Must NOT do: Run the full validator stack, inspect the full branch diff, confirm each logical unit is committed sequentially, and write a final handoff/status file under evidence root. Do not mark complete if any tracked changes remain uncommitted unintentionally or if the archive branch check fails.
  Parallelization: Wave 4 | Blocked by: 9 | Blocks: F1, F2, F3, F4
  References (executor has NO interview context - be exhaustive): this plan; `omo:git-master` skill; `scripts/validate-delegation-contract.py`; `scripts/validate-pastyear-proof.py`; `.omo/evidence/studyforge-omo-harness-skill-shape/`; current branch topology.
  Acceptance criteria (agent-executable): `git log --oneline archive/studyforge-current-skill-work-20260706..HEAD` shows sequential commits for the overhaul; `git status --short --branch` is clean except ignored `.omo` evidence; archive branch still resolves to `e51e38c`; full validator stack passes.
  QA scenarios (name the exact tool + invocation): happy CLI/data: `git log --oneline --decorate --max-count=20` plus full validator stack must be captured; failure CLI/data: `git diff --stat archive/studyforge-current-skill-work-20260706..HEAD` must show only intended tracked surfaces. Evidence `.omo/evidence/studyforge-omo-harness-skill-shape/task-10-final-status.txt`
  Commit: Y | `chore(harness): record Study Forge overhaul status` only if tracked status docs are added; otherwise no commit.

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Do not wait for more user approval to declare local completion; later push, destructive git operations, global TOML installation, or remote history rewrites still require explicit user approval.
- [x] F1. Plan compliance audit
  Scope: Read-only. Compare completed diff, evidence files, commits, and installed sync against this plan. Verify every todo has a matching commit or no-commit reason.
  Required verdict: APPROVE only if no plan item is missing or overclaimed.
  QA scenario: `python -c "from pathlib import Path; import subprocess,sys; ev=Path('.omo/evidence/studyforge-omo-harness-skill-shape'); plan=Path('docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md'); missing=[i for i in range(1,11) if not list(ev.glob(f'task-{i:02d}-*'))]; log=subprocess.check_output(['git','log','--format=%s','archive/studyforge-current-skill-work-20260706..HEAD'],text=True); required=['docs(plan): record Study Forge OmO harness overhaul','test(harness): capture OmO-first Study Forge contract','docs(skill): center Study Forge on OmO harness','docs(delegation): make OmO harness the orchestration layer','docs(artifact): route finals workflows through source packs','test(harness): enforce OmO-backed Study Forge routing','docs(agents): keep Study Forge roles as harness prompts']; absent=[s for s in required if s not in log and not any((ev/f'task-{i:02d}-no-commit.txt').exists() for i in range(1,11))]; ok=plan.is_file() and not missing and not absent; print({'tracked_plan':plan.is_file(),'missing_evidence':missing,'missing_commits':absent}); sys.exit(0 if ok else 1)"` PASS only if the tracked plan exists, every todo 1-10 has evidence, and each expected tracked commit exists or a no-commit evidence file is present.
  Evidence: `.omo/evidence/studyforge-omo-harness-skill-shape/f1-plan-compliance.md`
- [x] F2. Code quality review
  Scope: Read-only. Review Python validator changes, fixtures, docs consistency, and any installed-sync helper scripts. Reject hollow tests, overfit exact prose checks, deleted guardrails, or broad unrelated refactors.
  Required verdict: APPROVE only if the repo quality risk is clear.
  QA scenario: `git diff --stat archive/studyforge-current-skill-work-20260706..HEAD && git diff --check archive/studyforge-current-skill-work-20260706..HEAD && python -m py_compile scripts/validate-delegation-contract.py scripts/delegation_contract/*.py scripts/validate-pastyear-proof.py scripts/pastyear_proof_*.py`; PASS only if diff scope is intended, whitespace check passes, and py_compile exits 0.
  Evidence: `.omo/evidence/studyforge-omo-harness-skill-shape/f2-code-quality.md`
- [x] F3. Real manual QA
  Scope: Run the full CLI/data validation stack and installed-skill parity check from a clean shell. Capture command output and any cleanup receipt.
  Required verdict: APPROVE only if every command passes and artifacts are non-empty.
  QA scenario: `python scripts/validate-delegation-contract.py --self-test && python scripts/validate-delegation-contract.py . && python scripts/validate-delegation-contract.py --hook-exercise delegated && python scripts/validate-delegation-contract.py --hook-exercise opt-out && python scripts/validate-pastyear-proof.py --self-test`; PASS only if every command exits 0 and the installed parity manifest from Todo 9 exists with all `match: true`.
  Evidence: `.omo/evidence/studyforge-omo-harness-skill-shape/f3-manual-qa.txt`
- [x] F4. Scope fidelity
  Scope: Verify no course artifacts changed, no global TOML roles were installed, no branch was deleted/reset without evidence, and fallback/source-gap guardrails remain visible.
  Required verdict: APPROVE only if scope boundaries were honored.
  QA scenario: `git diff --name-only archive/studyforge-current-skill-work-20260706..HEAD && git status --short --branch && find C:/Users/kyzer/.codex/agents -maxdepth 1 -type f \\( -name 'studyforge-indexer.toml' -o -name 'studyforge-verifier.toml' \\) 2>/dev/null || true`; PASS only if changed tracked files are confined to repo docs/scripts/plans, no `C:\CS_USM\...` outputs changed, no new global TOML roles were installed by this work, and `rg -n "Source gap|Unreadable|fallback_local_reviewed|baseline_unverified|usable_with_recorded_gaps" README.md skills` still finds guardrails.
  Evidence: `.omo/evidence/studyforge-omo-harness-skill-shape/f4-scope-fidelity.md`

## Commit strategy
- Use `omo:git-master` before every commit.
- Commit style: Conventional Commit subjects are already present in recent history; continue that style.
- Required sequence:
  1. `docs(plan): record Study Forge OmO harness overhaul`
  2. `test(harness): capture OmO-first Study Forge contract`
  3. `docs(skill): center Study Forge on OmO harness`
  4. `docs(delegation): make OmO harness the orchestration layer`
  5. `docs(artifact): route finals workflows through source packs`
  6. `test(harness): enforce OmO-backed Study Forge routing`
  7. `docs(agents): keep Study Forge roles as harness prompts`
  8. Optional tracked status/docs commit only if a tracked status artifact is intentionally added.
- Each commit must include only its logical unit and must pass at least:
  - `python scripts/validate-delegation-contract.py --self-test`
  - `python scripts/validate-delegation-contract.py .`
  - `git diff --check`
- Final tracked commit footer when practical:
  - `Plan: .omo/plans/studyforge-omo-harness-skill-shape.md`
- Do not push by default. Report local branch state and ask before push unless the user gives explicit push approval in the implementation thread.

## Success criteria
- `archive/studyforge-current-skill-work-20260706` exists and points to `e51e38c`.
- `docs/superpowers/plans/2026-07-06-studyforge-omo-harness-main-overhaul.md` is tracked and references this approved plan.
- The implementation branch contains sequential, verified Conventional Commits for each logical work unit.
- Top-level Study Forge docs describe the OmO/Codex harness as the orchestration layer and Study Forge as the study workflow contract.
- Source-heavy commands prefer source-pack-first behavior and preserve original-source authority.
- `artifact past-year` remains proof-ledger-backed and anti-fabrication guarded.
- Validators catch the new contract and all required validation commands pass.
- Installed skill copy matches repo-owned skill files after sync, with no discoverable duplicate backup skill.
- Final git status and branch topology are explicitly reported.
