# Study Forge OMO-Style Delegation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `omo:ulw-loop` plus `superpowers:subagent-driven-development` or the native Codex multi-agent tools. Implement this plan task-by-task with evidence. The parent thread is the orchestrator: it reads, plans, integrates, verifies, and commits; workers do research, indexing contract edits, QA, and verifier review.

**Goal:** Make Study Forge follow OMO's conductor-worker architecture so source-heavy commands can autonomously spawn subagents for research, indexing, QA, and verification without asking for a second user approval.

**Architecture:** Add a shared Study Forge delegation contract, route each command through that contract by task shape, and back the prose with a small validator so future edits cannot quietly remove the subagent behavior. Do not rely on source-controlled TOML files being live Codex agents; use self-contained `multi_agent_v1.spawn_agent` prompts whenever TOML-backed roles are unavailable.

**Tech Stack:** Markdown Codex skill docs, optional Codex agent TOML role definitions, Python 3.12 standard-library validators, Git Bash on Windows, Codex multi-agent tools, and OMO ULW evidence under `.omo/evidence/`.

---

## Current State To Preserve

- Current branch is `main`.
- Current uncommitted files before this plan:
  - `README.md`
  - `skills/SKILL.md`
  - `skills/references/index.md`
  - this plan file after creation
- The existing dirty edits already say that `agents/*.toml` are not live Codex custom agents by themselves and that `index` should use OMO-style delegation. Treat those edits as in-scope starting work, not unrelated dirt.
- `.omo/` is ignored by Git. Use it for runtime plans/evidence only; use this tracked plan file for commit traceability.
- Do not install or copy TOMLs to `C:\Users\kyzer\.codex\agents` unless the user explicitly asks in a later message.
- If syncing the installed skill is needed after repo verification, copy only the installable skill docs to `C:\Users\kyzer\.agents\skills\study-forge`, make a backup outside discoverable skill roots, and report that sync as a machine-state action, not a Git commit.

## Intended Architecture

### Parent Orchestrator

The main Study Forge thread:

- selects the command and reads only the needed reference files;
- decides when the source scope warrants delegation;
- spawns workers without waiting for extra user approval when subagent tooling is available;
- gives every worker a self-contained prompt beginning with `TASK:` and containing `DELIVERABLE`, `SCOPE`, and `VERIFY`;
- integrates worker outputs into source-pack, proof docs, or learner artifacts;
- verifies worker claims itself before readiness or commits;
- records fallback state when workers are unavailable, blocked, ack-only, or unusable.

### Worker Lanes

Define portable lane purposes in a shared reference rather than depending on live custom agents:

| Lane | Purpose | Typical commands |
| --- | --- | --- |
| `source_research` | Inventory sources, inspect specific files/pages, summarize source basis, detect gaps, and report exact locators. | `distill`, `map`, `sheet`, `rescue`, broad `trace`, broad `deconstruct`, artifacts |
| `source_index` / `indexer` | Build or refresh `.study-forge/source-pack/` records by file, file bundle, or page range. | `index`, course-folder artifact work |
| `verifier` | Challenge source-pack freshness, proof docs, evidence, correctness, and learner surface. | `index`, `artifact past-year`, high-stakes artifacts |
| `qa_executor` | Drive the real surface, open/check artifacts, run validators, capture evidence files. | all artifact commands, index validation, verifier readiness |
| `final_reviewer` | Review final diff, docs, evidence, and readiness claims for missed gaps. | any HEAVY command or workflow change |

### Delegation Trigger Policy

The agent decides based on task shape:

- Always delegate for PDF-heavy or multi-source `index` runs.
- Always delegate verifier lanes for `artifact past-year` before readiness.
- Delegate source research for broad course-folder or multi-document `distill`, `map`, `sheet`, `rescue`, and artifact modes.
- Delegate QA for generated artifacts, proof docs, source-packs, or any output the user will reuse outside chat.
- Keep work local for one-page concept help, tiny `trace` explanations, or emergency `rescue` with no usable sources, but label those as general or temporary.
- Never use `fallback_local` merely because the user did not explicitly ask for subagents. Use fallback only when tooling is unavailable, a spawned lane fails, or a worker returns unusable output after recovery.

## Verification Strategy

Evidence root:

```text
.omo/evidence/studyforge-omo-delegation/
```

Primary checks:

```bash
git status --short
git diff --check
uv run python -m py_compile scripts/validate-delegation-contract.py
uv run scripts/validate-delegation-contract.py --self-test
uv run scripts/validate-delegation-contract.py .
rg -n "delegation|source_research|qa_executor|final_reviewer|TASK:|DELIVERABLE|SCOPE|VERIFY|fallback_local|without a second user approval" README.md skills agents scripts
```

Manual/data-surface QA:

- Save validator RED output before production docs are complete.
- Save final validator stdout and `rg` contract output under `.omo/evidence/studyforge-omo-delegation/green/`.
- Save `git diff --check` and final `git status --short` evidence.
- If installed-skill sync is done, save repo-vs-installed hash parity for `SKILL.md` and touched `references/*.md`.

## Commit Strategy

The user requested commits. Use one sequential `feat:` commit per verified checkpoint.

Required commit rules:

- Every commit subject starts with `feat:`.
- Commit only one verified checkpoint at a time.
- Stage only files for that checkpoint.
- Run the relevant verification before each commit.
- After each commit, record `git log -1 --oneline` in evidence.
- Include this footer in the final commit:

```text
Plan: docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md
```

Recommended sequence:

1. `feat: add Study Forge delegation execution plan`
2. `feat: define Study Forge subagent delegation model`
3. `feat: route Study Forge commands through delegation lanes`
4. `feat: record Study Forge delegation evidence states`
5. `feat: validate Study Forge delegation contracts`
6. `feat: sync Study Forge installed skill docs` only if the installed copy is intentionally synced; otherwise skip and report no-sync.

## Tasks

### Task 1: Capture Baseline And Commit The Plan

**Files:**
- Create: `docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md`
- Evidence: `.omo/evidence/studyforge-omo-delegation/baseline/`

- [ ] **Step 1: Capture current state**

Run:

```bash
mkdir -p .omo/evidence/studyforge-omo-delegation/baseline
git status --short > .omo/evidence/studyforge-omo-delegation/baseline/git-status.txt
git diff -- README.md skills/SKILL.md skills/references/index.md > .omo/evidence/studyforge-omo-delegation/baseline/preexisting-delegation-diff.patch
rg -n "delegation|subagent|studyforge-indexer|studyforge-verifier|fallback_local|baseline_unverified|independent_verified" README.md skills agents > .omo/evidence/studyforge-omo-delegation/baseline/delegation-before.txt
```

Expected: `git-status.txt` names the existing dirty files; `delegation-before.txt` shows delegation is currently mostly index/past-year specific.

- [ ] **Step 2: Commit the plan only**

Run:

```bash
git add docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md
git diff --staged --check
git commit -m "feat: add Study Forge delegation execution plan"
git log -1 --oneline > .omo/evidence/studyforge-omo-delegation/baseline/commit-plan.txt
```

Expected: one commit containing only the plan file.

### Task 2: Define The Shared Delegation Model

**Files:**
- Create: `skills/references/delegation.md`
- Modify: `README.md`
- Modify: `skills/SKILL.md`

- [ ] **Step 1: Capture RED contract failure**

Run before creating `skills/references/delegation.md`:

```bash
mkdir -p .omo/evidence/studyforge-omo-delegation/red
if test -f scripts/validate-delegation-contract.py; then
  uv run scripts/validate-delegation-contract.py . > .omo/evidence/studyforge-omo-delegation/red/missing-shared-delegation.txt
else
  printf 'RED missing validator and shared delegation contract\n' > .omo/evidence/studyforge-omo-delegation/red/missing-shared-delegation.txt
fi
```

Expected: RED evidence exists and proves the shared contract was absent.

- [ ] **Step 2: Create `skills/references/delegation.md`**

The file must include these sections:

```markdown
# Delegation

## Orchestrator Contract

## Tooling Preflight

## Worker Prompt Shape

## Lane Catalog

## Command Trigger Matrix

## Fallback And Readiness States

## Parent Verification

## Evidence Metadata

## Anti-Rules
```

Required content:

- Parent orchestrator reads/plans/integrates/verifies.
- Workers do dirty work: research, indexing, QA, verifier review, artifact checks.
- Every worker prompt starts with `TASK:` and includes `DELIVERABLE`, `SCOPE`, `VERIFY`.
- Use `fork_context:false` unless full history is truly required.
- Paste role instructions into normal worker prompts when TOML roles are unavailable.
- Do not require second user approval for warranted delegation.
- Fallback states are explicit and degraded.
- Local fallback is not independent verification.
- Worker reports are claims; parent must validate outputs, schema, evidence paths, and readiness.

- [ ] **Step 3: Wire the shared model into `skills/SKILL.md`**

Add a routing bullet near the command routing section:

```markdown
- For source-heavy, PDF-heavy, multi-source, artifact, proof, or verifier-shaped work, load [references/delegation.md](references/delegation.md) along with the command reference. The main thread is the orchestrator: it decides when delegation is warranted, spawns workers without waiting for a second user approval, and validates worker output before readiness. Small one-source concept explanations may stay local.
```

Keep the existing `index` bullet, but make it a command-specific specialization of the shared model rather than the only command with delegation.

- [ ] **Step 4: Add README mental model**

Update the verifier/agent install section to say Study Forge uses portable OMO-style delegation:

- TOMLs are optional role definitions.
- Normal Codex workers are acceptable when TOML roles are not exposed.
- The parent thread chooses lanes by source scope and command shape.
- `index`, `artifact past-year`, and broad source-heavy commands can all use subagents.

- [ ] **Step 5: Verify and commit**

Run:

```bash
mkdir -p .omo/evidence/studyforge-omo-delegation/green
rg -n "Orchestrator Contract|Tooling Preflight|Worker Prompt Shape|Lane Catalog|Command Trigger Matrix|source_research|qa_executor|final_reviewer|TASK:|DELIVERABLE|SCOPE|VERIFY|second user approval|fallback_local" skills/references/delegation.md skills/SKILL.md README.md > .omo/evidence/studyforge-omo-delegation/green/shared-delegation-rg.txt
git diff --check
git add README.md skills/SKILL.md skills/references/delegation.md
git diff --staged --check
git commit -m "feat: define Study Forge subagent delegation model"
git log -1 --oneline > .omo/evidence/studyforge-omo-delegation/green/commit-shared-model.txt
```

### Task 3: Route Each Study Forge Command Through The Delegation Matrix

**Files:**
- Modify: `skills/references/index.md`
- Modify: `skills/references/artifact.md`
- Modify: `skills/references/distill.md`
- Modify: `skills/references/map.md`
- Modify: `skills/references/deconstruct.md`
- Modify: `skills/references/trace.md`
- Modify: `skills/references/drill.md`
- Modify: `skills/references/mark.md`
- Modify: `skills/references/rescue.md`
- Modify: `skills/references/sheet.md`

- [ ] **Step 1: Update `index`**

Keep the current index delegation language, but align names with the shared contract:

- `source_index` / `indexer` lanes by file, file bundle, or page range.
- independent `verifier` lane with `source_index`.
- parent-owned `pack-verification.json` fields for lane status and fallback reason.

- [ ] **Step 2: Update `artifact`**

Add a short `Delegation Routing` section:

- `atlas`, `formula-lab`, `trace-lab`, and `drill-pack`: use `source_research` workers for broad source scopes and `qa_executor` workers for generated artifact checks.
- `past-year`: keep required verifier lanes and explicitly tie them to the shared `verifier` lane.
- All artifacts: parent must open or inspect the final artifact surface and record QA evidence.

- [ ] **Step 3: Update `distill`, `map`, `sheet`, and `rescue`**

Add a compact delegation paragraph:

- broad folder or multi-document scope -> spawn `source_research` lanes;
- conflicting source basis or high-stakes exam priority -> spawn `verifier` or `final_reviewer`;
- no-source emergency paths stay local and are labeled temporary/general.

- [ ] **Step 4: Update `deconstruct`, `trace`, `drill`, and `mark`**

Add a compact delegation paragraph:

- one small source or concept -> local;
- broad source set, code/notebook trace, mark-heavy answer, or artifact feed -> use `source_research`;
- correctness-sensitive answer or grading -> use `verifier`;
- reusable output -> use `qa_executor`.

- [ ] **Step 5: Verify and commit**

Run:

```bash
rg -n "Delegation|source_research|indexer|source_index|verifier|qa_executor|final_reviewer|small.*local|broad|multi-source|PDF-heavy|fallback_local" skills/references/*.md > .omo/evidence/studyforge-omo-delegation/green/command-routing-rg.txt
git diff --check
git add skills/references/*.md
git diff --staged --check
git commit -m "feat: route Study Forge commands through delegation lanes"
git log -1 --oneline > .omo/evidence/studyforge-omo-delegation/green/commit-command-routing.txt
```

### Task 4: Standardize Evidence And Readiness Metadata

**Files:**
- Modify: `skills/references/delegation.md`
- Modify: `skills/references/studyforge-indexer.md`
- Modify: `skills/references/studyforge-verifier.md`
- Modify: `agents/studyforge-indexer.toml`
- Modify: `agents/studyforge-verifier.toml`

- [ ] **Step 1: Define parent-owned metadata fields**

In `delegation.md` and verifier docs, define durable parent metadata:

```json
{
  "invocation_mode": "independent_subagent | installed_toml_agent | fallback_local | baseline_unverified",
  "lane": "source_research | source_index | extraction | coverage | evidence | correctness | learner_surface | qa_executor | final_reviewer",
  "status": "PASS | MAJOR | BLOCKING | NOT_RUN",
  "child_agent_id": "string or null",
  "child_thread_id": "string or null",
  "raw_child_report_path": "string or null",
  "parent_validated": true,
  "tooling_preflight": {
    "available": true,
    "checked": ["multi_agent_v1.spawn_agent", "installed_toml_agent"],
    "fallback_reason": null
  }
}
```

Make clear that child workers return lane findings only; the parent fills invocation metadata.

- [ ] **Step 2: Align indexer and verifier role docs**

Ensure:

- indexer remains constructive and cannot certify readiness;
- verifier remains read-only and adversarial;
- QA executor is a lane/prompt pattern, not necessarily a TOML;
- parent validation is required before `independent_verified`.

- [ ] **Step 3: Update optional TOML text**

Keep TOMLs optional. Their instructions should say:

- do not install globally as part of normal skill operation;
- do not invent child IDs or parent metadata;
- return concise lane reports;
- preserve source-trust policy.

- [ ] **Step 4: Verify and commit**

Run:

```bash
rg -n "invocation_mode|child_agent_id|child_thread_id|raw_child_report_path|parent_validated|tooling_preflight|installed_toml_agent|fallback_local|baseline_unverified|parent.*metadata|Do not invent" skills/references/delegation.md skills/references/studyforge-indexer.md skills/references/studyforge-verifier.md agents/*.toml > .omo/evidence/studyforge-omo-delegation/green/evidence-metadata-rg.txt
uv run python - <<'PY'
from pathlib import Path
import tomllib
for path in sorted(Path("agents").glob("*.toml")):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    assert data.get("name"), path
    assert data.get("developer_instructions"), path
    print(path, data["name"])
PY
git diff --check
git add skills/references/delegation.md skills/references/studyforge-indexer.md skills/references/studyforge-verifier.md agents/*.toml
git diff --staged --check
git commit -m "feat: record Study Forge delegation evidence states"
git log -1 --oneline > .omo/evidence/studyforge-omo-delegation/green/commit-evidence-states.txt
```

### Task 5: Add A Delegation Contract Validator

**Files:**
- Create: `scripts/validate-delegation-contract.py`

- [ ] **Step 1: Create failing-first validator shape**

Before implementing the validator, capture RED from the missing validator or missing contract:

```bash
if test -f scripts/validate-delegation-contract.py; then
  uv run scripts/validate-delegation-contract.py . > .omo/evidence/studyforge-omo-delegation/red/validator-before.txt
else
  printf 'RED missing scripts/validate-delegation-contract.py\n' > .omo/evidence/studyforge-omo-delegation/red/validator-before.txt
fi
```

- [ ] **Step 2: Implement validator**

The script should:

- use only Python standard library;
- accept `<repo-root>` and `--self-test`;
- fail if `skills/references/delegation.md` is missing required sections;
- fail if `skills/SKILL.md` does not route source-heavy work through delegation;
- fail if command refs do not mention the relevant lane names;
- fail if readiness docs claim `fallback_local` is independent verification;
- fail if docs require second user approval for warranted subagents;
- parse `agents/*.toml` with `tomllib`;
- print `PASS delegation contract` on success;
- print `FAIL delegation contract` plus issue lines on failure.

- [ ] **Step 3: Add self-test**

`--self-test` should create temporary bad fixtures that prove these failures are detected:

- missing `delegation.md`;
- missing worker prompt shape;
- fallback-local claimed as independent;
- restrictive "ask user approval before spawning" phrasing.

Expected GREEN line:

```text
PASS self-test delegation contract
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
uv run python -m py_compile scripts/validate-delegation-contract.py
uv run scripts/validate-delegation-contract.py --self-test | tee .omo/evidence/studyforge-omo-delegation/green/validator-self-test.txt
uv run scripts/validate-delegation-contract.py . | tee .omo/evidence/studyforge-omo-delegation/green/validator-real-repo.txt
git diff --check
git add scripts/validate-delegation-contract.py
git diff --staged --check
git commit -m "feat: validate Study Forge delegation contracts"
git log -1 --oneline > .omo/evidence/studyforge-omo-delegation/green/commit-validator.txt
```

### Task 6: Final QA, Optional Installed-Skill Sync, And Review

**Files:**
- Repo files touched by prior tasks
- Optional machine-state sync target: `C:\Users\kyzer\.agents\skills\study-forge`

- [ ] **Step 1: Run full verification**

Run:

```bash
git status --short | tee .omo/evidence/studyforge-omo-delegation/green/final-status-before-sync.txt
git diff --check | tee .omo/evidence/studyforge-omo-delegation/green/final-diff-check.txt
uv run python -m py_compile scripts/validate-delegation-contract.py scripts/pastyear_proof_model.py scripts/pastyear_proof_rules.py scripts/pastyear_proof_validator.py
uv run scripts/validate-delegation-contract.py --self-test | tee .omo/evidence/studyforge-omo-delegation/green/final-validator-self-test.txt
uv run scripts/validate-delegation-contract.py . | tee .omo/evidence/studyforge-omo-delegation/green/final-validator-real-repo.txt
rg -n "source_research|source_index|qa_executor|final_reviewer|TASK:|DELIVERABLE|SCOPE|VERIFY|fallback_local|independent_verified|second user approval" README.md skills agents scripts | tee .omo/evidence/studyforge-omo-delegation/green/final-contract-rg.txt
```

Expected: all commands exit 0; no staged or uncommitted repo changes remain except optional installed-copy sync evidence under ignored `.omo/`.

- [ ] **Step 2: Run final reviewer subagent**

Spawn a reviewer with `fork_context:false`:

```text
TASK: Act as a rigorous final verification reviewer for Study Forge OMO-style delegation.
DELIVERABLE: APPROVE or BLOCK with concrete file/line findings.
SCOPE: Review the final diff, docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md, README.md, skills/SKILL.md, skills/references/*.md, agents/*.toml, scripts/validate-delegation-contract.py, and evidence under .omo/evidence/studyforge-omo-delegation/.
VERIFY: Confirm the parent-orchestrator model is generalized across commands, no second user approval is required for warranted delegation, fallback_local is degraded, TOMLs are not misrepresented as live agents, validator coverage is meaningful, and commits are sequential feat: checkpoints.
```

Treat anything other than unconditional approval as BLOCKING; fix and rerun affected checks.

- [ ] **Step 3: Optional installed-skill sync**

If the user expects the local installed skill to reflect repo behavior now, sync only after repo validation:

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = "C:\Users\kyzer\.agents\skill-backups\study-forge-omo-delegation-$stamp"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
Copy-Item -Recurse -Force "C:\Users\kyzer\.agents\skills\study-forge\*" $backup
Copy-Item -Recurse -Force "C:\Dev\study-forge\skills\*" "C:\Users\kyzer\.agents\skills\study-forge\"
```

Then verify hashes for every synced file:

```powershell
Get-FileHash C:\Dev\study-forge\skills\SKILL.md, C:\Users\kyzer\.agents\skills\study-forge\SKILL.md -Algorithm SHA256
```

Do not commit anything outside the repo. If syncing is skipped, record the reason.

- [ ] **Step 4: Final commit only if needed**

If Task 6 produced repo changes, commit them:

```bash
git add <only-task-6-repo-files>
git diff --staged --check
git commit -m "feat: sync Study Forge installed skill docs" -m "Plan: docs/superpowers/plans/2026-07-05-study-forge-omo-delegation.md"
```

If Task 6 only produced ignored evidence or machine-state sync, do not create a repo commit.

## Success Criteria

- Study Forge has one shared delegation contract modeled after OMO's conductor-worker pattern.
- `index` no longer owns the only delegation language; all source-heavy commands have lane-specific guidance.
- The docs explicitly say the agent may spawn workers based on task shape without waiting for a second user approval.
- TOML roles are described truthfully as optional role definitions, not automatically live Codex custom agents.
- Fallback-local and baseline-unverified states remain degraded and visible.
- A validator prevents deleting the shared delegation contract, worker prompt shape, command routing, and fallback truthfulness.
- The new thread leaves sequential `feat:` commits for each verified checkpoint.
- Final reviewer approves unconditionally or the thread reports the unresolved blocker.
