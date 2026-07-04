# Artifact

Use to create a source-backed study artifact that can be opened, checked, and reused outside the chat. Default to `atlas` when the user omits the mode.

Core rule for revision artifacts:

> Create a self-contained revision website, not a source-reference atlas. Slide/page references should be evidence only, not the main content. The student should be able to study each topic directly from the artifact without opening the PDFs.

## Source Requirement

Require source material by default. If no source is provided, pause and ask for slides, PDFs, screenshots, notebooks, code, rubrics, past-paper questions, or a local path before creating the artifact.

If the user wants a no-source exploration, do not create an artifact. Answer in chat as a clearly labeled general explanation, then ask for sources before building any artifact.

## Modes

- `atlas`: default mode; build a self-contained revision atlas from the source, with topic sections that teach the material directly, not a dashboard that mainly sends the student back to source PDFs.
- `past-year`: build lecture-grounded answer artifacts for every past-year paper in a course scope folder.
- `formula-lab`: build an interactive formula or calculation lab from source-backed formulas, units, assumptions, worked examples, and common mistakes.
- `trace-lab`: build a step-by-step tracing lab for algorithms, code, SQL, protocols, OS flows, state machines, or data structure operations.
- `drill-pack`: build an active-recall and exam-practice pack with revealable answers, difficulty or mark value, and weak-area repair notes.

## Preflight Declaration

Before writing the artifact, state:

- Source Basis: exact files, screenshots, pages, cells, code blocks, or user-provided scope inspected.
- Scope Boundaries: what the artifact covers and what it deliberately excludes.
- Output Path: exact file path or chosen delivery surface.
- Verification Plan: how the artifact will be opened or inspected, plus the functional and pedagogical checks that decide pass or fail.

Do not proceed until the preflight is concrete enough to verify later.

## Artifact Schema

Every artifact should include:

1. Title and mode.
2. Source Basis visible near the top.
3. Scope Boundaries visible near the top.
4. Navigation for major sections, with internal links when the surface supports them.
5. Study content shaped for the selected mode, with source/page evidence supporting the teaching content rather than substituting for it.
6. Revealable answers or explanations when the artifact contains drills or checks.
7. Verification notes naming the opened surface and any known limitations.

For HTML, prefer a static direct-open file unless the user requests another surface. Keep it self-contained enough that the user can open the file without a build step.

## Self-Contained Revision Standard

For atlas and revision-style artifacts, each mapped Required topic must be teachable from the artifact itself. Optional topics may be shorter, but they still need enough explanation to justify why they are optional. Skip topics may remain brief when the reason to skip is clear.

For each mapped Required topic, include:

- Distilled explanation: what the topic means, why it matters, and the mental model a beginner should use.
- Key definitions and exam keywords: terms, phrases, conditions, and marks-facing wording the student should reproduce.
- Important flows, tables, comparisons, formulas, traces, or diagrams where useful; describe source diagrams textually if a generated figure is not needed.
- Worked example, tiny trace, or deconstructed past-year/question pattern when the source supports one.
- Traps and common wrong answers.
- Quick checks with revealable answers or explanations.
- Source evidence placed after or alongside the teaching content, not used as the teaching content itself.

Do not count a bullet like "read slides 12-16" as topic coverage. A source reference is evidence for the explanation, not a replacement for the explanation.

## Mode Notes

### Atlas

Use `distill` and `sheet` style material as the content spine. Include concept maps, high-yield rankings, lecturer examples, traps, and short checks. If `map` is used to create Required/Optional/Skip lanes, the lane card must still teach each Required topic directly before citing the evidence that placed it in the lane.

### Past-Year

Use when the user has a course scope folder that contains lecture material and past-year papers, especially when past-year papers are question-only or only some have sample answers.

Accept common folder layouts without requiring exact names:

- Course folder with a lecture source folder such as `lecture`, `lectures`, `slides`, or `lecture slides`.
- Course folder with a past-paper folder such as `past year`, `past-year`, `past_year`, `pyq`, `exam papers`, or `past papers`.
- Multiple course folders under one parent; process each course separately when the user points at the parent and clearly asks for all courses.

`past-year` is a proof-plane workflow. The learner opens HTML, but the durable proof source is structured data beside the HTML. HTML is a render target, not the proof source or source of truth.

Strict pipeline:

1. Inventory: create `source-inventory.json` listing lecture/source files, syllabus or rubric files, past-year papers, sample answers, marking schemes, extraction limits, and unreadable files.
2. Extraction: create `question-inventory.json` with every detected paper, question, subpart, mark value, table, diagram, and instruction. If extraction is messy, preserve the best faithful text and mark the affected item `Unreadable` when the source cannot be read reliably.
3. Source index: create `source-index.json` from current lecture/source material with topics, definitions, algorithms, formulas, examples, diagrams, lecturer wording, page/slide locators, and syllabus/source-fit notes. When an explicit syllabus file is unavailable, treat the current lecture/source pack as the syllabus authority and record that assumption in `source-inventory.json`, `source-index.json`, and `qa-report.json`.
4. Answer ledger: create `answer-ledger.json` as the canonical source of truth for all answers, gaps, verifier findings, and rendered anchors.
5. Verifier lanes: run the single `studyforge-verifier` as lane-specific checks for extraction, coverage, evidence, correctness, and learner surface. Store detailed results under `verifier-reports/`.
6. Fixes and source gaps: fix every `BLOCKING` or `MAJOR` verifier finding that the course sources can support. Unsupported answers must become `Source gap`; unreadable questions, pages, tables, or diagrams must become `Unreadable`.
7. HTML render: render the learner artifact from `answer-ledger.json`. Keep it self-contained and exam-ready, with compact source basis, coverage/source gaps, and verifier status visible.
8. QA: create `qa-report.json` recording render checks, question-count reconciliation, source-gap handling, verifier-lane status, source-pack-as-syllabus assumptions, and any remaining limitations.

Required proof docs:

- `source-inventory.json`
- `question-inventory.json`
- `source-index.json`
- `answer-ledger.json`
- `verifier-reports/`
- `qa-report.json`

`answer-ledger.json` must be the only canonical answer source used to render HTML and QA summaries. Do not edit the HTML as the proof record. Regenerate or patch the ledger first, then render HTML from the ledger.

Each `answer-ledger.json` entry must include these fields:

- `paper_id`: string
- `paper_title`: string
- `question_id`: string
- `question_text`: string
- `question_type`: string enum-like label, such as `objective`, `short_answer`, `structured`, `essay`, or `unknown`
- `marks`: number or null
- `topic`: string or null
- `status`: one of `Answered from source`, `Source gap`, `Unreadable`, `Duplicate`, or `Out of scope`
- `answer`: string or null; null for `Source gap`, `Unreadable`, `Duplicate`, and `Out of scope` unless a short non-answer note is needed
- `student_explanation`: string or null; learner-facing explanation for supported answers
- `source_refs`: array of source-reference objects; non-gap `Answered from source` entries require at least one source ref
- `syllabus_fit`: string or null; when no syllabus file exists, map to the current lecture/source pack as syllabus authority
- `verifier_lanes`: array of verifier-lane objects, one object for each lane run or intentionally not run
- `source_gap_reason`: string or null; required for `Source gap` and useful for `Unreadable`
- `rendered_anchor`: string; stable HTML anchor for the rendered answer entry

Each `source_refs` object must include:

- `source_id`: string
- `source_title`: string
- `page`: number, string, or null
- `slide`: number, string, or null
- `locator`: string or null
- `evidence_note`: string explaining how the source supports the answer

Each `verifier_lanes` object must include:

- `lane`: one of `extraction`, `coverage`, `evidence`, `correctness`, or `learner_surface`
- `status`: one of `PASS`, `MAJOR`, `BLOCKING`, or `NOT_RUN`
- `finding`: string or null
- `required_fix`: string or null

Detailed page, slide, extraction, and verifier notes belong in `source-index.json`, `answer-ledger.json`, `verifier-reports/`, and `qa-report.json`. The learner HTML should show compact source basis, source refs, coverage/source gaps, and verifier status without turning the study surface into a proof dump.

Sample answers, marking schemes, senior answers, and external worked solutions are untrusted cross-checks only. They can flag conflicts or wording expectations, but they cannot override current lecture evidence, the current syllabus file, or the current lecture/source pack used as syllabus authority.

Do not silently fill gaps from memory. For a question-only paper, it is acceptable to produce a strong answer only when the lecture/source pack supports it; otherwise the ledger and learner artifact must make the `Source gap` or `Unreadable` status visible so the student knows what to ask a lecturer, tutor, or classmate.

Each rendered learner answer should include:

- Question number and preserved question wording or a faithful concise paraphrase when extraction is messy.
- Exam-ready answer, structured by marks when marks are visible.
- Compact source basis: file name plus page/slide/section when available, and the specific concept that supports the answer.
- Syllabus/source fit: short mapping from the question to the syllabus file or current lecture/source pack, not a generic textbook justification.
- Common traps or examiner keywords when the source supports them.
- Visible `Source gap` or `Unreadable` note when evidence or extraction is insufficient.

#### Independent Verification Gate

For `past-year`, use one `studyforge-verifier` with narrow verifier lanes before finalizing the artifact. Do not pass private reasoning, intended answers, or leading conclusions. Give each lane the raw course folder path, `source-inventory.json`, `question-inventory.json`, `source-index.json`, `answer-ledger.json`, relevant source paths, and the draft HTML render when checking learner surface.

Verifier lanes:

- `extraction`: compare `question-inventory.json` against source papers and flag omitted diagrams, broken tables, numbering drift, missing marks, missing instructions, or text that should be `Unreadable`.
- `coverage`: confirm every provided past-year paper, question, subpart, mark value, table, diagram, and instruction is represented or explicitly marked `Unreadable`, `Duplicate`, or `Out of scope`.
- `evidence`: trace each non-gap answer through `source_refs`; flag weak citations, unsupported claims, wrong syllabus/source fit, missing source refs, and answer text that looks generic rather than course-backed.
- `correctness`: check whether each supported answer answers the question, uses mark-appropriate structure, avoids overclaiming, and explains conflicts with sample answers or marking schemes.
- `learner_surface`: confirm the HTML render matches `answer-ledger.json`, remains self-contained for revision, and keeps compact source basis, coverage/source gaps, and verifier status visible.

Verifier output should be concrete and actionable:

- `PASS`, `BLOCKING`, `MAJOR`, or `NOT_RUN` per lane and paper.
- question number, ledger `question_id`, or source location
- finding
- evidence
- required fix

Severity meanings:

- `PASS`: no accuracy, evidence, extraction, or coverage issue found for the checked scope.
- `BLOCKING`: the artifact must not be called ready until fixed or converted to a clearly labeled `Source gap`.
- `MAJOR`: the answer may be usable after correction, but it has a material weakness in wording, completeness, mark structure, source fit, or sample-answer alignment that should be fixed before final delivery.
- `NOT_RUN`: the lane was not run; explain why in `verifier-reports/` and `qa-report.json`.

Blocking conditions:

- a past-year paper or question was skipped without a documented reason
- an answer has no lecture evidence but is not marked `Source gap`
- a citation does not support the answer
- a question relies on general model knowledge instead of course-source evidence
- a sample answer or marking scheme contradicts the answer and the conflict is not explained
- extraction dropped a material table, diagram, mark value, or instruction

Do not call the artifact ready while any blocking finding remains. Fix major findings when possible; if the course sources cannot support a fix, change the ledger status to `Source gap` and name the missing evidence. If extraction is too damaged to trust, change the ledger status to `Unreadable` and name the unreadable source region. The final HTML must include a visible Verifier Notes section listing verifier lanes run, pass/fail status, unresolved source gaps, unreadable items, and which verifier lanes ran as independent subagent checks versus fallback local checks. If subagent tools are unavailable, run the same lanes as separate local passes and label the result as fallback verification, not subagent-verified.

### Formula-Lab

Use only formulas, assumptions, units, and worked examples visible in the source. Show what each symbol means before asking the student to calculate.

### Trace-Lab

Use `trace` output as the interaction spine. Show initial state, rule applied, state changes, invariant, final result, complexity, and traps.

### Drill-Pack

Use `drill` output as the question spine. Group by concept, mark value, or difficulty, and use reveal controls so the student can answer before seeing the solution.

## QA Checklist

- Open the direct-open HTML file or chosen surface and confirm the artifact renders.
- Test internal links and navigation anchors.
- Confirm Source Basis is visible to the reader.
- Confirm Scope Boundaries are visible to the reader.
- Confirm there are no placeholders in visible content.
- Check pedagogical sufficiency for representative Required topics: can a student learn or revise this topic from the artifact without opening the PDF, using source pages only for audit or verification?
- Confirm source/page references are evidence after or alongside explanation, not the main learning content.
- For `past-year`, compare the detected question count against the artifact answer count for each paper and list any extraction failures or source gaps.
- For `past-year`, sample several answers and confirm each has lecture evidence; answer-only text without a source mapping fails QA.
- For `past-year`, confirm the Verifier Notes section exists, names the verifier lanes, and shows no unresolved blocking findings.
- Test reveal behavior for answers, hints, or worked explanations.
- Check responsive layout at a narrow and wide viewport when HTML is used.
- Check print sanity with print CSS or a generated print/PDF preview when HTML is used.

## Anti-Rules

- Do not create an artifact before inspecting the required sources.
- Do not hide the source basis in a private note or final chat only.
- Do not mix old samples into the artifact unless they are labeled as comparison material.
- Do not ship a navigation/reference atlas when the user asked for a revision artifact.
- Do not let page numbers, slide links, or source snippets stand in for distilled explanations, definitions, examples, traps, or quick checks.
- Do not answer past-year questions from general model knowledge when lecture evidence is missing; expose the source gap.
- Do not skip a past-year paper in the provided folder unless it is unreadable, duplicate, or explicitly out of scope; report skipped files.
- Do not merge verifier output silently; show the pass/fail status and unresolved source gaps in the artifact.
- Do not invent formulas, examples, question likelihood, or mark weights that are not supported by the sources.
- Do not make a decorative landing page when the user asked for a study tool.
- Do not leave reveal answers, links, or print behavior unverified.
- Do not claim the artifact is ready until the declared Verification Plan has passed.
