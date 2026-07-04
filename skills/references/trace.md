# Trace

Use for algorithms, code, SQL, recursion, networking, OS scheduling, memory, protocols, state machines, and data structure operations.

## Source Handling

If code, notebook, SQL, or a diagram is provided, inspect it first. If no source exists, proceed as a general concept trace and say so clearly.

## Source-Pack Preflight

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs, slides, screenshots, notebooks, code, or source files: pull trace-relevant examples, diagrams, rules, source locators, confidence labels, visual notes, and gaps as the access layer.

Use fallback to original PDFs, slides, screenshots, notebooks, code, SQL, diagrams, or other source files when the manifest is missing, hashes are stale, the needed record is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. Do not rebuild or reindex here; inspect original sources and recommend `$study-forge index <course-folder>` when useful. Original course files remain authority.

## Workflow

1. State the initial state and inputs.
2. Identify the rule that drives each step.
3. Trace one step at a time.
4. Show what changes after each step.
5. End with the invariant, result, complexity, and trap.

## Output

Use tables when they clarify:

| Step | State/Input | Rule applied | Result | Why |
|---|---|---|---|---|

Then add:

- in short
- common exam mistakes
- how to recognize this question type
- one tiny drill

Prefer concrete examples over abstract notation first. Add formal notation after the intuition.

## Feeds Artifact

Trace output can feed `artifact trace-lab` by turning the traced steps into an artifact with initial state, rule applied, state changes, invariant, result, complexity, and traps. Keep source-derived code, SQL, protocol, or diagram details visible in the artifact's source basis.
