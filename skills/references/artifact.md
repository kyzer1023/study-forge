# Artifact

Use to create a source-backed study artifact that can be opened, checked, and reused outside the chat. Default to `atlas` when the user omits the mode.

## Source Requirement

Require source material by default. If no source is provided, pause and ask for slides, PDFs, screenshots, notebooks, code, rubrics, past-paper questions, or a local path before creating the artifact.

If the user wants a no-source exploration, do not create an artifact. Answer in chat as a clearly labeled general explanation, then ask for sources before building any artifact.

## Modes

- `atlas`: default mode; build a navigable concept atlas from the source, with topic sections, high-yield summaries, relationships, traps, and quick checks.
- `formula-lab`: build an interactive formula or calculation lab from source-backed formulas, units, assumptions, worked examples, and common mistakes.
- `trace-lab`: build a step-by-step tracing lab for algorithms, code, SQL, protocols, OS flows, state machines, or data structure operations.
- `drill-pack`: build an active-recall and exam-practice pack with revealable answers, difficulty or mark value, and weak-area repair notes.

## Preflight Declaration

Before writing the artifact, state:

- Source Basis: exact files, screenshots, pages, cells, code blocks, or user-provided scope inspected.
- Scope Boundaries: what the artifact covers and what it deliberately excludes.
- Output Path: exact file path or chosen delivery surface.
- Verification Plan: how the artifact will be opened or inspected, plus the checks that decide pass or fail.

Do not proceed until the preflight is concrete enough to verify later.

## Artifact Schema

Every artifact should include:

1. Title and mode.
2. Source Basis visible near the top.
3. Scope Boundaries visible near the top.
4. Navigation for major sections, with internal links when the surface supports them.
5. Study content shaped for the selected mode.
6. Revealable answers or explanations when the artifact contains drills or checks.
7. Verification notes naming the opened surface and any known limitations.

For HTML, prefer a static direct-open file unless the user requests another surface. Keep it self-contained enough that the user can open the file without a build step.

## Mode Notes

### Atlas

Use `distill` and `sheet` style material as the content spine. Include concept maps, high-yield rankings, lecturer examples, traps, and short checks.

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
- Test reveal behavior for answers, hints, or worked explanations.
- Check responsive layout at a narrow and wide viewport when HTML is used.
- Check print sanity with print CSS or a generated print/PDF preview when HTML is used.

## Anti-Rules

- Do not create an artifact before inspecting the required sources.
- Do not hide the source basis in a private note or final chat only.
- Do not mix old samples into the artifact unless they are labeled as comparison material.
- Do not invent formulas, examples, question likelihood, or mark weights that are not supported by the sources.
- Do not make a decorative landing page when the user asked for a study tool.
- Do not leave reveal answers, links, or print behavior unverified.
- Do not claim the artifact is ready until the declared Verification Plan has passed.
