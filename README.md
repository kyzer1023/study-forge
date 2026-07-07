# Study Forge

Source-backed studying for students. One Codex skill that turns slides, PDFs, exam papers, examples, notebooks, code, and rubrics into simple explanations, high-yield notes, traces, drills, and exam-ready answers.

> Quick start: attach or point to your course materials, then use `$study-forge <command> <target>`. Start with `$study-forge distill lecture.pdf`, `$study-forge index "C:\...\Course"` for a full course folder, or `$study-forge rescue "final tomorrow"` when time is tight. For finals with a course folder, run `index` first, then run `artifact past-year` against the same folder so the source-pack is used first without replacing the original files as authority.

## Why Study Forge?

Most study prompts make the model sound confident before it has seen the actual class material. That is dangerous near exams: the model can over-prioritize generic textbook topics, miss the lecturer's examples, or turn a slide deck into a fluffy summary.

Study Forge is built for the way students actually revise:

- You usually have real materials: lecture slides, screenshots, exam papers, briefs, rubrics, notebooks, code, or worked examples.
- You need the easiest useful explanation first, not an academic essay.
- You need to know what scores marks, what can be skimmed, and what should be ignored.
- You need traces, drills, and answer wording, not just passive notes.
- When the exam is close, you need direct triage without losing important details.

Study Forge adds a source gate, a study command vocabulary, and exam-pressure behavior for CS-heavy coursework and revision.

## What's Included

### The Skill: `study-forge`

The skill installs as one command:

```text
$study-forge <command> <target>
```

Run it with no command to see the menu and let the agent ask what source material you have.

### Source-Backed By Default

For exam-specific work, Study Forge expects one or more sources:

- lecture slides or PDFs
- screenshots/images of slides or examples
- exam papers, past-year questions, quizzes, or worked solutions
- syllabus, assignment brief, rubric, marking scheme, or topic list
- notebooks, code, SQL, diagrams, or exported artifacts

If you ask for likely exam topics, chapter distillation, marking, a final sheet, or a study artifact without sources, the skill should ask you to attach files or provide paths first.

It can still answer general concept questions without sources, but it should label that as general explanation rather than source-backed exam prioritization.

For course folder workflows, the happy path is index first and source-pack first. `$study-forge index <course-folder>` is the feeder workflow. PDFs, slides, and screenshots stay the authority; the source-pack is fast indexed access, not a replacement for originals. The OmO/Codex harness keeps the main thread conducting while workers do source-heavy dirty work by file, file bundle, or page range, then an independent `studyforge-verifier source_index` lane checks the pack before it is called ready. Downstream commands use the pack first when it is fresh, and the pack records confidence notes and gaps in plain language so uncertain pages stay visible.

## Commands

All commands run through `$study-forge`:

| Command | What it does |
|---|---|
| `$study-forge index <course-folder>` | Build a reusable semantic source-pack for a course folder; alias: `$study-forge source-index <course-folder>` |
| `$study-forge distill` | Turn slides, PDFs, or screenshots into high-yield notes and likely question types |
| `$study-forge map` | Rank a syllabus, rubric, lecture folder, or past papers into required, optional, and skip |
| `$study-forge deconstruct` | Break down examples, worked solutions, or past-paper questions step by step |
| `$study-forge trace` | Walk through algorithms, code, SQL, recursion, protocols, OS/network flows, or state changes |
| `$study-forge drill` | Generate active-recall and exam-style practice questions |
| `$study-forge mark` | Grade your answer harshly, estimate marks, and rewrite it into exam-ready wording |
| `$study-forge rescue` | Triage what to study first when time is short |
| `$study-forge sheet` | Create a condensed revision sheet from source materials |
| `$study-forge artifact` | Create a source-backed study artifact; defaults to `atlas` when no mode is given; use `past-year` for verifier-checked lecture-grounded past-paper answer packs |

Learner HTML for `atlas` and `past-year` is study-first by default. Full Source Basis, Scope Boundaries, Verification Notes, manual QA results, lane evidence, and raw report references belong in sidecar proof files such as `qa-report.json`, `verifier-reports/`, and worker coverage reports; answer records stay in `answer-ledger.json`. The learner page shows only source gaps, unreadable notes, or limitations that affect studying.

For `artifact past-year`, use a proof-plane split: `answer-ledger.json` is canonical for answer records and HTML rendering, while worker coverage metadata, verifier reports, readiness state, raw worker-report paths, lane evidence, and manual QA stay in sidecars such as `qa-report.json`, `verifier-reports/`, and worker coverage reports. The learner HTML must render from the ledger, not from ad hoc HTML edits or worker reports.

Exam-worthy past-year output means the learner page shows mark-bearing model answers from `answer-ledger.answer`, not short hints. Worked steps, code/pseudocode, traces, tables, trees, diagrams, formulas, and objective-answer reasoning must be present when marks require them. `student_explanation` is supporting why-it-is-right prose, not a replacement model answer.

Do not call a short hint a model answer. Do not mark a visual question `Unreadable` only because text extraction failed when a rendered page image exists; inspect the visual payload or record why it is unusable. Do not call `fallback_local`, `fallback_local_reviewed`, stale verifier output, or unresolved major findings exam-ready or independently verified.

### Usage Examples

```text
$study-forge index "C:\...\Course"
$study-forge artifact past-year "C:\...\Course"
$study-forge index "C:\CS_USM\Y2S2\CST235"
$study-forge source-index "C:\CS_USM\Y2S2\CPT212"
$study-forge distill "C:\CS_USM\Y2S2\CPT212\Lecture\14a Graphs Pt.1.pdf"
$study-forge map "C:\CS_USM\Y2S2\CST235\Lecture"
$study-forge deconstruct attached past-year question
$study-forge trace "Boyer-Moore bad character shift"
$study-forge drill "network layer control plane"
$study-forge mark "my answer: ..."
$study-forge rescue "I have 2 hours and only these slides"
$study-forge sheet attached lecture screenshots
$study-forge artifact atlas "C:\CS_USM\Y2S2\CST235\Lecture"
$study-forge artifact past-year "C:\CS_USM\Y2S2\CST235"
```

Finals happy path: `index` the whole course folder first, then run `artifact past-year` against the same folder. The later `artifact past-year` command uses the source-pack first when file hashes still match, then reopens original materials for missing pages, stale records, low-confidence visual interpretation, source gaps, or spot checks. Unsupported answers stay labeled `Source gap` instead of being filled from memory.

Or use it directly with a natural request:

```text
$study-forge explain this slide like I am starting from zero, then tell me what the examiner is likely testing
```

## How Study Forge Answers

The default response shape is:

1. Direct verdict or priority
2. Source basis
3. Simple explanation
4. Study machinery: definitions, steps, traces, Big-O, comparisons, formulas if relevant
5. Common traps and likely question types
6. Immediate drill or next action

For computer science, the skill does not blindly chase formulas. It prioritizes definitions, keywords, algorithm traces, edge cases, code behavior, SQL patterns, OS/network/database flows, complexity, and examiner wording.

## Installation

Install from GitHub:

```powershell
npx skills add https://github.com/kyzer1023/study-forge --skill study-forge --agent codex --copy -y
```

The installable skill lives directly in:

```text
skills
```

For local testing before publishing, point Codex at:

```text
C:\Dev\study-forge\skills
```

### OmO/Codex Harness And Worker Lanes

Study Forge uses the portable OmO/Codex harness for source-heavy work. The main thread conducts: it scopes the command, chooses worker lanes by source scope and command shape, spawns workers when warranted, integrates their reports, and validates evidence before readiness. Workers do source-heavy dirty work such as extraction, page/image passes, source-pack construction, answer-ledger checks, verifier lanes, and learner-surface review.

The shared contract lives in `skills/references/delegation.md`. `$study-forge index` specializes it with the source-controlled indexer role in `agents/studyforge-indexer.toml` plus the workflow in `skills/references/studyforge-indexer.md`. `artifact past-year` and source-pack readiness checks specialize it with the verifier role in `agents/studyforge-verifier.toml` and the lane instructions in `skills/references/studyforge-verifier.md`.

For course folder workflows, route index first and source-pack first. The pack is the access layer; original PDFs, slides, screenshots, notebooks, and code remain authoritative and must be reopened for stale hashes, missing records, low-confidence visual interpretation, source gaps, unreadable pages, or spot checks.

For `artifact past-year`, the skill defines the output shape and proof contract while the OmO/Codex harness decides the source work needed from the materials. Source gap is a last-resort status after source-pack lookup, original-source inspection, and answer synthesis. A broad over-gapped fallback from a local answer map is degraded output, not normal delivery, unless the user gives explicit degraded acceptance.

Past-year proof requires atomic mark-bearing subpart extraction, syllabus-fit classification, and worker coverage metadata. Every answerable subpart with marks needs its own inventory and ledger identity. Old-paper topics outside the current syllabus/current lecture/source-pack authority are `Out of scope` with evidence; in-scope items that remain unsupported after source-pack lookup, original-source inspection, and answer synthesis are `Source gap` with failed lookup/inspection/synthesis evidence.

Keeping `agents/*.toml` in this repo or installing only the Study Forge skill does not register those TOMLs as live Codex agents. The tracked TOMLs are harness prompt templates and optional role definitions; normal Study Forge docs, artifact work, and verification passes should not copy files into `C:\Users\kyzer\.codex\agents` unless the user explicitly asks for that install.

Fallback when a named role is not installed or not exposed by the active worker tool: spawn a normal Codex worker for the needed lane, then paste the relevant lane instructions from `skills/references/delegation.md`, `skills/references/studyforge-indexer.md`, or `skills/references/studyforge-verifier.md`.

`index`, `artifact past-year`, and broad source-heavy commands can all use workers; do not wait for a second user approval when the active harness can spawn workers and the task shape warrants delegation. If the user says `local only`, `no subagents`, `no delegation`, or otherwise restricts tool use, keep the work local and mark any missing lane truthfully.

Verifier readiness states:

- `independent_verified`: an independent subagent or installed verifier role ran the required lanes.
- `fallback_local`: a required worker lane could not run and the main thread made a local pass. This is degraded.
- `fallback_local_reviewed`: the role was unavailable after preflight, so copied lane instructions were run as separate local passes. This is degraded.
- `baseline_unverified`: verifier preflight or required lane results are missing.

For `artifact past-year`, use copied verifier instructions only as the normal-worker fallback path, keep `fallback_local`, `fallback_local_reviewed`, and `baseline_unverified` visibly degraded, and rerun through workers if multi-agent tooling is discovered late.

A local pass is not `subagent-verified`. `fallback_local`, `fallback_local_reviewed`, `baseline_unverified`, `degraded_parent_shell`, and missing worker reports cannot be called `independent_verified`.

Fresh sidecar proof matters for readiness wording. Final gates must run after the rendered HTML and proof sidecars they certify, and they must name resolved or intentionally retained findings instead of hiding stale `BLOCKING` or `MAJOR` verifier reports behind green summary language.

## Design Principles

- Read the real material before making exam-priority claims.
- Treat the current brief, rubric, slide deck, or exam paper as the authority.
- Use old samples only as references or benchmarks.
- Lead with the answer, then explain.
- Teach from zero when the student is confused.
- Keep urgent answers concise, but never shallow.
- Verify rendered PDFs, screenshots, notebooks, or exported artifacts when output truth matters.
