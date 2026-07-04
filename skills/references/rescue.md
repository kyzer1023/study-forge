# Rescue

Use when time is short, the user is anxious, or the user asks what to do first.

## Source Handling

If sources exist, inspect them and triage from evidence. If no sources exist, give a temporary emergency plan and ask for slides, exam paper, topic list, or rubric immediately.

## Source-Pack Preflight

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs, slides, screenshots, or source files: pull topic coverage, exam signals, source locators, confidence labels, visual notes, and gaps as the access layer.

Use fallback to original PDFs, slides, screenshots, syllabuses, rubrics, past papers, notebooks, code, or other source files when the manifest is missing, hashes are stale, the needed record is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. Do not rebuild or reindex here; inspect original sources and recommend `$study-forge index <course-folder>` when useful. Original course files remain authority.

## Workflow

1. Identify time available and scope if the user provided it.
2. Separate topics into must-do, should-do, and abandon.
3. Pick mark-dense actions: definitions, traces, common questions, examples, and traps.
4. Avoid perfection work.
5. Give the next concrete action.

## Output

Use:

1. Immediate verdict
2. What to study first
3. What to ignore
4. Fast drill plan
5. If you only have 30 minutes
6. If you have 2 hours
7. Source files still needed

Do not produce a long calendar unless the user asks for one.
