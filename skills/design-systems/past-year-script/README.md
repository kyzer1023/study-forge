# Past-Year Script Design System

**ID:** `past-year-script`
**Version:** 2
**Theme:** Script (warm paper, indigo nav, green correct, ruled exam-script layout)

Canonical design system for `study-forge artifact past-year` HTML output.

## Files

| File | Role |
|---|---|
| [DESIGN.md](DESIGN.md) | Full spec: tokens, layout, motion, content rules, data shape |
| [PRODUCT.md](PRODUCT.md) | Learner purpose, tone, anti-references |
| [reference-mock.html](reference-mock.html) | Working reference implementation with sample questions |

## When agents must load this

Load **before** rendering or regenerating any `artifact past-year` learner HTML:

1. Read `DESIGN.md` and `PRODUCT.md` in full.
2. Open `reference-mock.html` for structure, CSS tokens, JS behavior (router, reveal, KaTeX).
3. Render course output to match the reference; only question data and course title change.

Do not invent a new layout, palette, or card pattern for past-year artifacts unless the user explicitly requests a different design system.

## Output in course folders

Typical deliverable layout:

```
<Course> Past-Year Artifact/
  index.html              # learner surface (Script theme)
  answer-ledger.json      # proof plane
  question-inventory.json
  source-index.json
  source-inventory.json
  verifier-reports/
  qa-report.json
```

Optional: copy `DESIGN.md` beside `index.html` for the student's reference. The skill copy under `design-systems/past-year-script/` remains canonical.

## Ledger → HTML mapping

| Ledger field | HTML surface |
|---|---|
| `question_text` | `stem` (strip exam footers) |
| `question_type` objective + options | `kind: "mcq"`, `options[]`, `correct` index/indices |
| `question_type` structured | `kind: "structured"`, model answer from `answer` |
| `status: Source gap` | `gap: true`, study note panel, no option highlight |
| `student_explanation` | MCQ `explanation` or structured WHY / STUDY NOTE prose (panels only) |
| `source_refs`, `syllabus_fit`, verifier fields | **JSON only; never in HTML** |
