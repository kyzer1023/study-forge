# Drill

Use for practice questions, active recall, oral testing, and weak-area repair.

## Source-Pack Preflight

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs, slides, screenshots, or source files: pull examinable topics, examples, traps, source locators, confidence labels, visual notes, and gaps as the access layer.

Use fallback to original PDFs, slides, screenshots, notebooks, code, or other source files when the manifest is missing, hashes are stale, the needed record is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. Do not rebuild or reindex here; inspect original sources and recommend `$study-forge index <course-folder>` when useful. Original course files remain authority.

## Workflow

1. Use source material when available.
2. Choose the smallest useful drill set.
3. Mix recognition, explanation, trace, compare, and application questions.
4. Include mark value or difficulty.
5. Ask the user to answer before revealing full solutions when appropriate.

## Output

Provide:

- quick recall questions
- exam-style questions
- one trace or worked mini-problem if relevant
- answer key hidden under a clear heading, unless the user wants immediate marking
- weak-area diagnosis after the user replies

Avoid dumping huge question banks. Prioritize the questions most likely to expose misunderstanding.

## Feeds Artifact

Drill output can feed `artifact drill-pack` by grouping questions into a reusable practice artifact with mark value or difficulty, answer reveal behavior, and weak-area repair notes. Preserve the source basis for any exam-specific questions.
