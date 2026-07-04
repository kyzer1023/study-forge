# Study Forge

Source-backed studying for students. One Codex skill that turns slides, PDFs, exam papers, examples, notebooks, code, and rubrics into simple explanations, high-yield notes, traces, drills, and exam-ready answers.

> Quick start: attach or point to your course materials, then use `$study-forge <command> <target>`. Start with `$study-forge distill lecture.pdf`, `$study-forge index "C:\...\Course"` for a full course folder, or `$study-forge rescue "final tomorrow"` when time is tight.

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

For large course folders, `$study-forge index <course-folder>` is the feeder workflow. PDFs, slides, and screenshots stay the authority; the source-pack is fast indexed access. PDF-heavy or multi-source indexing should run `studyforge-indexer` lanes by file, file bundle, or page range, then an independent `studyforge-verifier source_index` lane before the pack is called ready. Downstream commands use the pack first when it is fresh, and the pack records confidence notes and gaps in plain language so uncertain pages stay visible.

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

After the first command builds the pack, the later `artifact past-year` command reuses that pack first when file hashes still match, then reopens original materials for missing pages, stale records, low-confidence visual interpretation, source gaps, or spot checks.

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

### Verifier Agent Install

`$study-forge index` uses the source-controlled indexer role in `agents/studyforge-indexer.toml` plus the workflow in `skills/references/studyforge-indexer.md`. `artifact past-year` and source-pack readiness checks use the verifier role in `agents/studyforge-verifier.toml` and the lane instructions in `skills/references/studyforge-verifier.md`.

The optional Codex agent install paths are `C:\Users\kyzer\.codex\agents\studyforge-indexer.toml` and `C:\Users\kyzer\.codex\agents\studyforge-verifier.toml`. Do not install them globally unless the user asks for that install; normal Study Forge docs, artifact work, and verification passes should not copy files into `C:\Users\kyzer\.codex\agents`.

Fallback when a TOML is not installed: spawn a normal subagent or worker for the needed lane, then paste the relevant lane instructions from `skills/references/studyforge-indexer.md` or `skills/references/studyforge-verifier.md`. Label fallback checks as `fallback_local`; do not claim `subagent-verified` status unless an independent subagent or installed role actually ran.

## Design Principles

- Read the real material before making exam-priority claims.
- Treat the current brief, rubric, slide deck, or exam paper as the authority.
- Use old samples only as references or benchmarks.
- Lead with the answer, then explain.
- Teach from zero when the student is confused.
- Keep urgent answers concise, but never shallow.
- Verify rendered PDFs, screenshots, notebooks, or exported artifacts when output truth matters.
