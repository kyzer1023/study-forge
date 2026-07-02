# Study Forge

Source-backed studying for students. One Codex skill that turns slides, PDFs, exam papers, examples, notebooks, code, and rubrics into simple explanations, high-yield notes, traces, drills, and exam-ready answers.

> Quick start: attach or point to your course materials, then use `$study-forge <command> <target>`. Start with `$study-forge distill lecture.pdf` or `$study-forge rescue "final tomorrow"` when time is tight.

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

## Commands

All commands run through `$study-forge`:

| Command | What it does |
|---|---|
| `$study-forge distill` | Turn slides, PDFs, or screenshots into high-yield notes and likely question types |
| `$study-forge map` | Rank a syllabus, rubric, lecture folder, or past papers into required, optional, and skip |
| `$study-forge deconstruct` | Break down examples, worked solutions, or past-paper questions step by step |
| `$study-forge trace` | Walk through algorithms, code, SQL, recursion, protocols, OS/network flows, or state changes |
| `$study-forge drill` | Generate active-recall and exam-style practice questions |
| `$study-forge mark` | Grade your answer harshly, estimate marks, and rewrite it into exam-ready wording |
| `$study-forge rescue` | Triage what to study first when time is short |
| `$study-forge sheet` | Create a condensed revision sheet from source materials |
| `$study-forge artifact` | Create a source-backed study artifact; defaults to `atlas` when no mode is given |

### Usage Examples

```text
$study-forge distill "C:\CS_USM\Y2S2\CPT212\Lecture\14a Graphs Pt.1.pdf"
$study-forge map "C:\CS_USM\Y2S2\CST235\Lecture"
$study-forge deconstruct attached past-year question
$study-forge trace "Boyer-Moore bad character shift"
$study-forge drill "network layer control plane"
$study-forge mark "my answer: ..."
$study-forge rescue "I have 2 hours and only these slides"
$study-forge sheet attached lecture screenshots
$study-forge artifact atlas "C:\CS_USM\Y2S2\CST235\Lecture"
```

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

## Design Principles

- Read the real material before making exam-priority claims.
- Treat the current brief, rubric, slide deck, or exam paper as the authority.
- Use old samples only as references or benchmarks.
- Lead with the answer, then explain.
- Teach from zero when the student is confused.
- Keep urgent answers concise, but never shallow.
- Verify rendered PDFs, screenshots, notebooks, or exported artifacts when output truth matters.
