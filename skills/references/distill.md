# Distill

Use for lecture slides, PDFs, screenshots, or chapter material.

## Source Requirement

Require source material. If none is provided, ask for slides, PDFs, screenshots, or a local folder path before claiming what is high-yield.

## Source-Pack Routing

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs: pull repeated terms, examples, diagrams, lecturer wording, confidence labels, visual notes, gaps, and locators from the pack as the source evidence/access layer.

Use fallback to source PDFs, slides, screenshots, or original files when the manifest is missing, hashes are stale, the needed page/topic is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. If no fresh pack exists, inspect the original sources directly before ranking or explaining the material.

## Delegation Routing

Use `skills/references/delegation.md` for worker routing. For broad folder, multi-document, or PDF-heavy distillation, delegate `source_research` to map source basis, high-yield signals, locators, confidence, and gaps before synthesizing. For correctness-sensitive, high-stakes, or conflicting source claims, add `verifier`; use `final_reviewer` when the distilled output will anchor a reusable artifact, proof note, or final study plan.

One small source can stay local as a `local-small-source` fallback. If no source exists, answer only as a clearly labeled general explanation, not an exam-specific distill. If a required delegated lane cannot run, label the result `fallback_local` and name the missing independent lane before presenting the output. When distill output feeds a generated or reusable artifact, that artifact still needs `qa_executor`.

## Workflow

1. Identify the chapter/topic and source files inspected.
2. Extract the lecturer's repeated terms, examples, diagrams, and emphasized sections.
3. Rank concepts by likely exam value: high, medium, low.
4. Explain high-yield concepts in simple language first.
5. Convert details into exam-ready phrasing and short drills.

## Output

Use this structure:

1. Verdict: what to focus on first
2. Chapter overview: what this is about and why it matters
3. Big picture: explain like the user has not learned it yet
4. High-yield ranking: highest to lowest priority
5. Exam machinery: definitions, steps, formulas if relevant, Big-O, diagrams, or flows
6. Common question types: theory, trace, compare, calculate, design, debug
7. Traps: common mistakes and wording that loses marks
8. Study strategy: what to do in 30 minutes, 1 hour, or 2 hours

Keep explanations concise, but keep mark-critical details.

## Feeds Artifact

Distill output can feed `artifact atlas` as the source-backed content spine: topic overview, high-yield ranking, exam machinery, traps, and quick checks. When feeding a revision artifact, expand terse bullets into enough distilled explanation, definitions, examples, traps, and checks for the student to revise from the artifact directly. Keep the original source basis attached as evidence so the artifact does not drift from the inspected material, but do not let citations replace the teaching content.

For `artifact past-year`, pass distilled source basis and proof notes into the artifact answer ledger or source index as support for learner-facing answers. The ledger/source refs prove where the explanation came from; they do not replace the explanation, examples, traps, or checks the student needs to study.
