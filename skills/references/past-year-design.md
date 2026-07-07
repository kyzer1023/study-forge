# Past-Year HTML Design (Script)

Load this reference when rendering `artifact past-year` learner HTML.

## Canonical design system

**Path:** `design-systems/past-year-script/` (relative to this skill root)

| File | Read when |
|---|---|
| [README.md](../design-systems/past-year-script/README.md) | First: ID, ledger mapping, output layout |
| [PRODUCT.md](../design-systems/past-year-script/PRODUCT.md) | Learner purpose and anti-references |
| [DESIGN.md](../design-systems/past-year-script/DESIGN.md) | Full tokens, layout, motion, content bans |
| [reference-mock.html](../design-systems/past-year-script/reference-mock.html) | Structure, CSS, JS to copy or port |

**Rule:** Match `reference-mock.html` and `DESIGN.md`. Do not freestyle a new past-year layout.

## HTML render step (pipeline step 7)

After `answer-ledger.json` passes verifier fixes:

1. Transform ledger entries into the `Paper` / `Question` data shape in `DESIGN.md`.
2. Parse MCQ options out of `question_text` when `question_type` is objective; never leave options inside one `<pre>` blob.
3. Map `answer` to the MODEL ANSWER panel. Map `student_explanation` only to WHY / STUDY NOTE prose.
4. Emit `index.html` using Script tokens, two-column rail shell, hash router, reveal behavior, and KaTeX from the reference mock.
5. **Strip from HTML:** `source_refs`, `syllabus_fit`, verifier lane text, QA stats, build timestamps, "Answered from source" badges, Verifier Notes sections.
6. **Keep in JSON only:** all proof-plane fields above plus detailed evidence notes.

## Learner surface content per question

**Show:** question number, type, marks, topic, stem, MCQ options (objective), reveal control, panel after reveal.

**Do not show:** page references, syllabus-fit paragraphs, verifier status, pipeline metadata.

**Source gap:** small "Source gap" pill + study note panel; no correct-option highlight.

## Verifier `learner_surface` checks

When running the learner_surface lane, validate against `DESIGN.md` and `reference-mock.html`:

- HTML question count matches ledger for each paper
- No source-basis or verifier blocks in visible HTML
- One paper per hash-routed view (not one long scroll)
- MCQ reveal highlights correct option(s) in green; explanation only in panel
- Structured answers expand in MODEL ANSWER panel
- MODEL ANSWER text comes from `answer-ledger.answer`; `student_explanation` may support it but must not replace it
- Math in panels typesets via KaTeX (or plain `^` auto-convert per DESIGN.md)

Proof docs (`verifier-reports/`, `qa-report.json`) hold audit detail; the HTML is study-only.
