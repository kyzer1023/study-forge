# Sheet

Use to produce condensed revision sheets.

## Source Requirement

Require source material for exam-specific sheets. If no source exists, produce only a general concept sheet and label it as such.

## Source-Pack Routing

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs: build the condensed sheet from high-confidence definitions, flows, formulas, comparisons, diagrams, traps, examples, self-test cues, source locators, and recorded gaps.

Use fallback to source PDFs, slides, screenshots, notebooks, code, or other original files when the manifest is missing, hashes are stale, the needed page/topic is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. If no fresh pack exists, inspect the original sources directly before compressing material into an exam-specific sheet.

## Workflow

1. Inspect the source.
2. Keep only mark-useful material.
3. Compress into definitions, steps, comparisons, traces, and traps.
4. Prefer tables and tiny examples over long prose.
5. Include a final self-test.

## Output

Use sections:

- must-know definitions
- algorithms or flows
- compare and contrast
- formulas or complexity, if relevant
- diagrams to remember, described textually if no image is needed
- common traps
- final 10-question self-test

Keep it dense, readable, and exam-facing.

## Feeds Artifact

Sheet output can feed `artifact atlas` when the user wants a navigable artifact instead of a compact chat answer. Preserve the sheet's condensed definitions, flows, comparisons, formulas, traps, and self-test while adding source basis and verification details. If the artifact is a revision website, each Required topic still needs enough teaching content to stand alone; slide/page references should only prove where the content came from.

For `artifact past-year`, the sheet's compact source basis and proof notes can feed the artifact answer ledger as learner-facing revision wording. Keep source refs as proof, not as a substitute for condensed definitions, comparisons, formulas, traps, worked examples, or the self-test.
