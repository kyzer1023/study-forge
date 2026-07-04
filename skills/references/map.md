# Map

Use for syllabuses, briefs, rubrics, topic lists, lecture folders, or past papers.

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
