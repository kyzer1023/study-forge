# Deconstruct

Use for example questions, past-year questions, worked solutions, and screenshots of problem statements.

## Source Requirement

Require the question and, if available, the official or lecturer-provided solution. If the user has only a screenshot, inspect the image carefully and restate the problem before solving.

## Source-Pack Preflight

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs, slides, screenshots, or source files: pull question records, answer evidence, topic matches, source locators, confidence labels, visual notes, and gaps as the access layer.

Use fallback to original PDFs, slides, screenshots, notebooks, code, or other source files when the manifest is missing, hashes are stale, the needed record is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. Do not rebuild or reindex here; inspect original sources and recommend `$study-forge index <course-folder>` when useful. Original course files remain authority.

## Delegation Routing

Follow the shared contract in `skills/references/delegation.md`. For broad source sets, past-paper bundles, screenshot-plus-solution sets, or deconstruct output that will feed an artifact, use `source_research` to map question evidence, solution evidence, locators, confidence, and gaps before solving. Add `verifier` when the worked answer is correctness-sensitive, graded, ambiguous, or likely to be reused; use `qa_executor` when the deconstruction becomes a reusable artifact, ledger, or proof surface.

Keep one small question or one small source local. If no source exists, label the response as general; if a warranted lane cannot run, label the degraded pass `fallback_local`. This is the local-small-source fallback and must not be described as independent verification.

## Workflow

1. Identify the topic and question archetype.
2. State what the examiner is testing.
3. List the required facts, formulas, algorithms, or rules.
4. Walk through the solution step by step.
5. Explain why each step is taken, not only what the step does.
6. Extract reusable exam patterns.

## Output

1. Topic and archetype
2. What scores marks
3. Required exam machinery
4. Step-by-step walkthrough
5. Hidden traps
6. Short answer template the user can reuse
7. One quick similar practice question

For CS algorithm examples, include a trace table when useful.
