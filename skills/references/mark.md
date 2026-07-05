# Mark

Use to grade the user's answers like an examiner.

## Source Requirement

Use the marking scheme, rubric, past paper, slides, or lecturer wording when available. If no marking source exists, grade as a general CS examiner and say that the score is approximate.

## Source-Pack Routing

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs: pull expected answer points, lecturer wording, marking-source locators, confidence labels, visual notes, and gaps from the pack as the source evidence/access layer.

Use fallback to source PDFs, marking schemes, rubrics, past papers, slides, or other original files when the manifest is missing, hashes are stale, the needed page/topic is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. If no fresh pack exists, inspect available marking sources directly before grading; only use general examiner judgment when no source material exists.

## Delegation Routing

Follow the shared contract in `skills/references/delegation.md`. For mark-heavy answers, multiple submissions, broad rubrics, past-paper sets, or grading that depends on several source files, use `source_research` to gather expected points, lecturer wording, marking locators, confidence, and gaps before assigning marks. Use `verifier` for correctness-sensitive grading, disputed marks, high-stakes feedback, or any answer where the score could materially change; use `qa_executor` when marks feed a reusable report, ledger, workbook, or exported artifact.

Keep one small answer against one small marking source local. If no marking source exists, label the score as general examiner judgment; if a warranted lane cannot run, label the degraded pass `fallback_local`. This is the local-small-source fallback and cannot be called independent verification.

## Workflow

1. Identify the expected answer points.
2. Compare the user's answer against them.
3. Award marks strictly.
4. Point out missing keywords, wrong assumptions, vague wording, or unsupported claims.
5. Provide corrected exam-ready wording.

## Output

Lead with:

```text
Verdict: ...
Estimated score: X/Y
```

Then give:

- marks gained
- marks lost
- corrected answer
- fastest fix
- one follow-up drill

Be direct. Do not cushion weak answers, but keep the tone useful.
