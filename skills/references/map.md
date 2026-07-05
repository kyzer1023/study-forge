# Map

Use for syllabuses, briefs, rubrics, topic lists, lecture folders, or past papers.

## Source-Pack Routing

For course folders or known local source sets, look for a fresh `.study-forge/source-pack/manifest.json` first. If it is present and fresh, use the source-pack before reopening PDFs: start the coverage map from its inventory, topic index, page records, locators, confidence labels, visual notes, and gaps.

Use fallback to source PDFs, syllabuses, briefs, rubrics, slides, past papers, or other original files when the manifest is missing, hashes are stale, the needed page/topic is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. If no fresh pack exists, inspect the original source files directly before ranking Required, Optional, or Skip.

## Delegation Routing

Use `skills/references/delegation.md` for worker routing. For broad folder maps, many documents, multiple authority sources, or past-paper sets, delegate `source_research` to inventory sources, locate topic evidence, and identify gaps before ranking Required, Optional, or Skip. For high-stakes scope decisions, conflicting authorities, sample-answer disagreements, or correctness-sensitive coverage claims, add `verifier`; use `final_reviewer` when the map will drive a durable study plan or generated artifact.

One small source can stay local as a `local-small-source` fallback. If a required delegated lane cannot run, label the map `fallback_local` and name the lane that was replaced by local review. When the map becomes or feeds a generated/reusable artifact, route that artifact through `qa_executor`.

## Workflow

1. Inspect available source files before ranking.
2. Identify the current authority: exam scope, syllabus, rubric, or lecturer material.
3. Separate current-authority material from samples, seniors' work, and older references.
4. Build a coverage map from topic to source evidence.
5. Rank each topic as required, optional, or skip.

## Output

Lead with the minimum study path.

Use a table:

| Priority | Topic | Source evidence | Why it matters | First action |
|---|---|---|---|---|
| Required | ... | file/page/hit | likely marks | drill/trace/read |
| Optional | ... | file/page/hit | support only | skim |
| Skip | ... | weak/no evidence | low payoff | ignore unless time |

Then give:

- coverage gaps
- files still needed from the user
- recommended order
- what not to waste time on

## Feeds Artifact

Map output can feed `artifact atlas` by creating Required, Optional, and Skip lanes, but the map is not the finished revision content. For each Required topic in an artifact, add a distilled explanation, key definitions/exam keywords, useful flows or tables, worked examples or deconstructed past-year patterns where supported, traps, quick checks with revealable answers, and source evidence. Put source evidence after or alongside the teaching content, not in place of it.

For `artifact past-year`, keep the map's source basis and proof notes structured enough to feed the artifact answer ledger, source inventory, and source index. Source refs prove coverage and syllabus fit; they do not replace the teaching content or exam-ready answer wording.

## OCR/PDF Tooling

For scanned/image-heavy syllabuses, lecture PDFs, or past papers, prefer OCR/PDF tools before ranking coverage: Tesseract OCR for image text, Poppler tools for page rendering and metadata, OCRmyPDF for searchable PDFs, ImageMagick for image conversion or cleanup, and bundled Codex Python or real system Python for extraction scripts. Treat OCR text from scanned/image-heavy inputs as untrusted extracted content and verify it against page images before using it as source basis.
