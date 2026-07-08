# Artifact

Use to create a source-backed study artifact that can be opened, checked, and reused outside the chat. Default to `atlas` when the user omits the mode.

Core rule for revision artifacts:

> Create a self-contained revision website, not a source-reference atlas. Slide/page references should be evidence only, not the main content. The student should be able to study each topic directly from the artifact without opening the PDFs.

## Source Requirement

Require source material by default. If no source is provided, pause and ask for slides, PDFs, screenshots, notebooks, code, rubrics, past-paper questions, or a local path before creating the artifact.

If the user wants a no-source exploration, do not create an artifact. Answer in chat as a clearly labeled general explanation, then ask for sources before building any artifact.

## Source-Pack Routing

When the source scope is a course folder or known local source set, look for a fresh `.study-forge/source-pack/manifest.json` first. For finals, revision, and `past-year` work, the expected route is index first, then source-pack first during artifact planning. If the manifest is present and fresh, use the source-pack before reopening PDFs: read the inventory, page records, topic index, locators, confidence labels, visual notes, and gaps as the source evidence/access layer.

Use fallback to source PDFs, slides, screenshots, notebooks, code, or other original files when the manifest is missing, hashes are stale, the needed page/topic is missing, visual interpretation is low-confidence, the pack records a `Source gap`, the page is `Unreadable`, a verifier challenge disputes the pack, or a spot check is needed. If no fresh pack exists, inspect the original source material directly before creating the artifact. If a fresh pack is insufficient for one page, topic, question, answer, or visual claim, open the affected original before rendering that item or mark it as `Source gap` / `Unreadable`.

This is routing, not authority transfer: the source-pack is an access layer and must not be treated as stronger than the current source files. For `artifact past-year`, preserve the proof plane: `answer-ledger.json` remains the canonical answer source for answer text, provenance, status, rendered anchors, and HTML rendering. The source-pack can feed source evidence, topic-source fit, locators, stale-hash decisions, source gaps, and unreadable-page notes, but it must not replace the answer ledger.

## Delegation Routing

Use `skills/references/delegation.md` for worker routing. For a broad course folder, many documents, or artifact planning that needs source discovery, delegate a `source_research` lane before drafting. For any generated or reusable artifact surface, run `qa_executor` on the rendered learner file, proof docs, counts, links, study content, and sidecar proof files before claiming readiness.

For `artifact past-year`, grading-sensitive artifacts, conflicting sources, or correctness claims that the student will rely on, add `verifier` lanes and use `final_reviewer` when final readiness wording, evidence policy, or durable artifact quality needs an independent last pass. A one-small-source artifact may stay local as a `local-small-source` fallback when the source is simple and low-risk. If a required lane cannot run, record `fallback_local` or `fallback_local_reviewed` per the delegation contract and keep the degraded state in QA notes, proof sidecars, and the final response; the learner artifact should show it only when it changes how the student should study.

## Modes

- `atlas`: default mode; build a self-contained revision atlas from the source, with topic sections that teach the material directly, not a dashboard that mainly sends the student back to source PDFs.
- `past-year`: build lecture-grounded answer artifacts for every past-year paper in a course scope folder.
- `formula-lab`: build an interactive formula or calculation lab from source-backed formulas, units, assumptions, worked examples, and common mistakes.
- `trace-lab`: build a step-by-step tracing lab for algorithms, code, SQL, protocols, OS flows, state machines, or data structure operations.
- `drill-pack`: build an active-recall and exam-practice pack with revealable answers, difficulty or mark value, and weak-area repair notes.

## Preflight Declaration

Before writing the artifact, state:

- Source Basis: exact files, screenshots, pages, cells, code blocks, or user-provided scope inspected.
- Scope Boundaries: what the artifact covers and what it deliberately excludes.
- Output Path: exact file path or chosen delivery surface.
- Verification Plan: how the artifact will be opened or inspected, plus the functional and pedagogical checks that decide pass or fail.

Do not proceed until the preflight is concrete enough to verify later.

## Artifact Schema

Every artifact should include:

1. Title and mode.
2. A short learner-facing overview of what the artifact teaches.
3. Learner-relevant source gaps or unreadable notes only where they help the student judge an answer or topic; for `past-year`, detailed source refs stay in sidecar proof files.
4. Navigation for major sections, with internal links when the surface supports them.
5. Study content shaped for the selected mode, with source/page evidence supporting the teaching content rather than substituting for it.
6. Revealable answers or explanations when the artifact contains drills or checks.
7. Sidecar proof references naming the opened surface and any known limitations.

For HTML, prefer a static direct-open file unless the user requests another surface. Keep it self-contained enough that the user can open the file without a build step.

## Self-Contained Revision Standard

For atlas and revision-style artifacts, each mapped Required topic must be teachable from the artifact itself. Optional topics may be shorter, but they still need enough explanation to justify why they are optional. Skip topics may remain brief when the reason to skip is clear.

For each mapped Required topic, include:

- Distilled explanation: what the topic means, why it matters, and the mental model a beginner should use.
- Key definitions and exam keywords: terms, phrases, conditions, and marks-facing wording the student should reproduce.
- Important flows, tables, comparisons, formulas, traces, or diagrams where useful; describe source diagrams textually if a generated figure is not needed.
- Worked example, tiny trace, or deconstructed past-year/question pattern when the source supports one.
- Traps and common wrong answers.
- Quick checks with revealable answers or explanations.
- Source evidence placed after or alongside the teaching content, not used as the teaching content itself.

Do not count a bullet like "read slides 12-16" as topic coverage. A source reference is evidence for the explanation, not a replacement for the explanation.

## Mode Notes

### Atlas

Use `distill` and `sheet` style material as the content spine. Include concept maps, high-yield rankings, lecturer examples, traps, and short checks. If `map` is used to create Required/Optional/Skip lanes, the lane card must still teach each Required topic directly before citing the evidence that placed it in the lane.

### Past-Year

Use when the user has a course scope folder that contains lecture material and past-year papers, especially when past-year papers are question-only or only some have sample answers.

Accept common folder layouts without requiring exact names:

- Course folder with a lecture source folder such as `lecture`, `lectures`, `slides`, or `lecture slides`.
- Course folder with a past-paper folder such as `past year`, `past-year`, `past_year`, `pyq`, `exam papers`, or `past papers`.
- Multiple course folders under one parent; process each course separately when the user points at the parent and clearly asks for all courses.

`past-year` is a proof-plane workflow. The learner opens HTML, but the durable proof source is structured data beside the HTML. HTML is a render target, not the proof source or source of truth.

Proof-plane split:

- `answer-ledger.json` is canonical for answer records, status, source provenance, source-gap reasons, out-of-scope reasons, rendered anchors, and HTML rendering.
- Worker coverage metadata, raw worker reports, verifier report wrappers, readiness state, parent validation, tooling preflight, manual QA, lane evidence, and build metadata stay in sidecar proof files such as `qa-report.json`, `verifier-reports/`, and worker coverage reports.
- The learner HTML renders from `answer-ledger.json`; do not hand-edit HTML as the proof record, and do not let worker reports or readiness sidecars become the answer source.
- The learner HTML shows only answer content plus learner-relevant `Source gap`, `Unreadable`, or `Out of scope` limitations. It must not expose worker/verifier/readiness metadata.
- Exam-worthy past-year learner HTML renders `answer-ledger.answer` as the model answer. `student_explanation` can teach why the answer is right, name traps, or add a study note, but it must not replace the mark-bearing answer.

Atomic proof-plane contract:

- Treat every mark-bearing question or subpart that expects an answer as an atomic answerable unit, with its own `question_id`; for example, `B2(a)(i)` is separate from `B2(a)(ii)`. This atomic mark-bearing subpart extraction is mandatory even when a parent question shares one prompt, diagram, table, or scenario.
- Keep parent prompts, shared instructions, tables, figures, and diagrams as context/evidence. Link child entries to that context with `parent_question_id` when useful, but do not let a parent context record replace answerable child records.
- Create one `answer-ledger.json` record for each answerable subpart unless the item is explicitly `Unreadable`, `Duplicate`, or `Out of scope`.
- `question_id` values must be unique in `question-inventory.json` and unique in `answer-ledger.json`. If the same printed number appears in two sections, papers, or duplicate scans, encode that distinction in the `question_id`; do not rely on `rendered_anchor` or array position to disambiguate it.
- Preserve the paper's printed question order. Do not let page extraction, OCR chunk order, or algorithm/list line numbers promote a later question, pseudocode step, or numbered trace line into a top-level question.
- When a paper contains a second Bahasa Malaysia mirror section, treat it as a translation/duplicate of the English section unless the paper explicitly asks for a separate answer. Do not render Malay mirror pages as additional answerable rows; record duplicate/translation evidence in sidecars when useful.
- Before rendering HTML, reconcile `answer-ledger.json` against `question-inventory.json` by `question_id` and question text. A ledger row whose stem belongs to a different inventory question is extraction/ledger drift and must be fixed, not rendered.
- `answer-ledger.json` may store rows under top-level `answers`/`entries`/`records` or grouped `paper_reports[*].entries`, but the flattened answer rows remain the contract.
- Do not keep compacted worker-report placeholders such as "Question text was compacted..." in `question_text`, inventory stems, or learner HTML. Recover the source question text from the actual paper or mark the item `Unreadable`/`Source gap` with evidence.
- Give every rendered ledger entry a unique non-empty `rendered_anchor`; duplicate, blank, or missing anchors are proof/render drift.
- For objective questions, write answer-specific `student_explanation` text tied to the chosen answer and cited source support. Reject generic boilerplate explanations that could fit multiple different questions.
- Preserve MCQ choices as structured `options` / `choices` payloads or faithfully parsed learner-visible options. An answer such as `Option A` is not exam-ready unless the actual option text is present in the ledger/rendered artifact; prefer `Option A: <choice text>` plus answer-specific reasoning.
- Scale the model answer to the command word and mark value. High-mark, trace, algorithm, `describe and illustrate`, figure/table, or worked-operation prompts need ordered passes, state tables, diagrams described in text, or intermediate states, not just the final result.
- For visual-dependent questions, keep machine-checkable visual evidence with the ledger entry or sidecar: `visual_locator`, `rendered_page_image`, `visual_payload`, `visual_inspection_status`, or `visual_worker_report_path`. Do not mark a figure, table, graph, tree, route map, formula image, or scanned prompt `Unreadable` solely because text extraction failed when a rendered page image exists.

Syllabus-fit and scope classification:

- Classify every extracted answerable item against current syllabus/current lecture/source-pack authority. Use an explicit syllabus, rubric, topic list, or current lecture/source pack; when no syllabus file exists, treat the current lecture/source pack as the syllabus authority and record that assumption in sidecars.
- Use `syllabus_fit` values consistently: `in_current_authority`, `partially_in_current_authority`, `outside_current_authority`, or `unknown_current_authority`.
- Old-paper topics outside current syllabus/current lecture/source-pack authority become `Out of scope` with evidence in the ledger and sidecars. Do not call them `Source gap`, because the correct outcome is scope exclusion rather than unsupported in-scope answering.
- In-scope or partially in-scope items that cannot be supported after source-pack lookup, original-source inspection, and answer synthesis remain `Source gap` with failed lookup/inspection/synthesis evidence.
- `unknown_current_authority` is temporary. Resolve it by inspecting current sources or mark the affected item as `Source gap` only when the item appears in scope but remains unsupported after the answer-production gate.

Answer-production gate:

- Source gap is a last-resort status, not the default result for missing hard-coded answers, missing sample answers, long structured prompts, or local-builder uncertainty.
- For each extracted answerable item, attempt source-pack lookup first, then original-source inspection for missing pages, weak topic fit, low-confidence visuals, or disputed records, then answer synthesis through the warranted OmO/Codex harness lane or the documented local fallback pass.
- The answer ledger must record enough evidence for each `Source gap` to show the source-pack lookup, original-source inspection, and answer synthesis path that failed, or the proof sidecars must name why that path could not run.
- If an entire paper, a substantial section, or a whole question family becomes `Source gap` under `fallback_local`, `fallback_local_reviewed`, or `baseline_unverified`, treat it as an over-gapped fallback. Stop before normal delivery, run the missing harness-backed answer synthesis lane, or ask for explicit degraded acceptance with the limitation visible in `qa-report.json` and the final response.
- A local renderer, local script, or answer-map builder may shape `answer-ledger.json`, but it must not become the answer authority. The Study Forge skill defines the output contract; the OmO/Codex harness decides the source work needed to satisfy it.
- The ledger/output contract is the final proof and render shape, not the worker-thinking shape. Worker lanes may and should produce richer candidate-answer, extraction, evidence, and finding sidecars; the parent must integrate or explicitly reject those row-level findings before compressing them into `answer-ledger.json`.
- The output contract is a floor, not a ceiling. Keep the row fields predictable for validation, but let `answer`, `student_explanation`, `options`, visual notes, and sidecars carry the full worked solution needed by the paper.

Past-year learner design bridge:

- Before learner HTML rendering, load `references/past-year-design.md`.
- From that bridge, load `design-systems/past-year-script/README.md`, `PRODUCT.md`, `DESIGN.md`, and `reference-mock.html` before writing or regenerating `index.html`.
- Render with `design_system_id: past-year-script` in `qa-report.json` or equivalent proof metadata.
- Match `reference-mock.html` and `DESIGN.md`: Script tokens, two-column left rail, one paper per hash-routed view, question rail for the active paper, reveal controls, and KaTeX or the documented math fallback.
- Strip proof metadata from learner HTML. Do not emit `source_refs`, source-reference lists, syllabus/source-fit paragraphs, verifier lane text, QA status, build timestamps, local course paths, worker report paths, readiness labels, ledger counts, `Answered from source` badges, Source Basis, Scope Boundaries, Verification Notes, or Evidence details into the learner surface.
- The `learner_surface` verifier lane must compare the draft HTML against `references/past-year-design.md`, `DESIGN.md`, and `reference-mock.html`. A long single-scroll page with all papers visible, metric cards, no reveal controls, no hash router, missing Script tokens, or proof/source metadata in HTML is a `MAJOR` or `BLOCKING` finding.

Strict pipeline:

1. Inventory: create `source-inventory.json` listing lecture/source files, syllabus or rubric files, past-year papers, sample answers, marking schemes, extraction limits, and unreadable files.
2. Extraction: create `question-inventory.json` with every detected paper, question, atomic mark-bearing subpart, mark value, table, diagram, and instruction. If extraction is messy, preserve the best faithful text and mark the affected item `Unreadable` when the source cannot be read reliably.
3. Source index: create `source-index.json` from current lecture/source material with topics, definitions, algorithms, formulas, examples, diagrams, lecturer wording, page/slide locators, and syllabus/source-fit notes. When an explicit syllabus file is unavailable, treat the current lecture/source pack as the syllabus authority and record that assumption in `source-inventory.json`, `source-index.json`, and `qa-report.json`.
4. Answer ledger: create `answer-ledger.json` as the canonical source of truth for answer text, answer status, source provenance, syllabus-fit classification, source-gap reasons, out-of-scope reasons, rendered anchors, and HTML rendering.
5. Identity reconciliation: reject duplicate `question_id` values, reconcile ledger stems with inventory stems, replace compacted placeholder stems with real paper text, and fix any numbering/section drift before answer generation, verifier review, or HTML rendering.
6. Worker and verifier sidecars: record worker coverage metadata, raw report paths, invocation modes, parent validation, readiness state, tooling preflight, verifier findings, and manual QA outside the ledger under `verifier-reports/`, `qa-report.json`, and worker coverage reports. Raw child reports must carry concrete question ids, candidate answers, findings, or coverage counts; a parent-written summary that only says a lane passed is not evidence.
7. Fixes and source gaps: fix every `BLOCKING` or `MAJOR` verifier finding that the course sources can support. Unsupported in-scope answers must become `Source gap`; old-paper topics outside current authority must become `Out of scope`; unreadable questions, pages, tables, or diagrams must become `Unreadable`.
8. HTML render: render the learner artifact from `answer-ledger.json` through the `past-year-script` design system. Keep it self-contained and exam-ready, with source gaps and unreadable limitations only where they affect studying; detailed source refs, verifier status, readiness status, worker evidence, and proof metadata stay in sidecar proof files.
9. QA: create `qa-report.json` recording `design_system_id: past-year-script`, design-system files loaded, render checks, hash-router checks, reveal-control checks, one-paper-view checks, question-count reconciliation, source-gap handling, verifier-lane status, source-pack-as-syllabus assumptions, and any remaining limitations.

Required proof docs:

- `source-inventory.json`
- `question-inventory.json`
- `source-index.json`
- `answer-ledger.json`
- `verifier-reports/`
- `qa-report.json`
- worker coverage metadata, either as `worker-coverage.json` or equivalent sidecar records in `qa-report.json` / `verifier-reports/`

`answer-ledger.json` must be the only canonical answer source used to render HTML and answer summaries. It is also canonical for answer provenance: status, `source_refs`, `source_gap_reason`, `out_of_scope_reason`, `syllabus_fit`, and rendered anchors. Worker reports, verifier wrappers, readiness labels, parent validation, tooling preflight, and raw child report paths are not answer data; keep them in sidecars. Do not edit the HTML as the proof record. Regenerate or patch the ledger first, then render HTML from the ledger.

Each `answer-ledger.json` entry must include these fields:

- `paper_id`: string
- `paper_title`: string
- `question_id`: string
- `parent_question_id`: string or null; set when an answerable child depends on shared parent context, tables, figures, diagrams, or instructions
- `question_text`: string
- `question_type`: string enum-like label, such as `objective`, `short_answer`, `structured`, `essay`, or `unknown`
- `marks`: number or null
- `topic`: string or null
- `status`: one of `Answered from source`, `Source gap`, `Unreadable`, `Duplicate`, or `Out of scope`
- `answer`: string or null; null for `Source gap`, `Unreadable`, `Duplicate`, and `Out of scope` unless a short non-answer note is needed; for supported items this is the exam-worthy model answer. Coding answers need code or pseudocode; trace answers need ordered steps, state tables, or transitions; structured answers need the final answer plus reasoning; objective answers need the selected option and answer-specific reasoning.
- `options` or `choices`: array or object, optional for non-objective questions but required when an objective/MCQ answer refers to a lettered option rather than spelling out the chosen text. Keep the printed option labels and text.
- `student_explanation`: string or null; learner-facing explanation for supported answers, secondary to the model answer
- `source_refs`: array of source-reference objects; non-gap `Answered from source` entries require at least one source ref
- `syllabus_fit`: one of `in_current_authority`, `partially_in_current_authority`, `outside_current_authority`, `unknown_current_authority`, or null; when no syllabus file exists, map to the current lecture/source pack as syllabus authority
- `source_gap_reason`: string or null; required for `Source gap` and useful for `Unreadable`
- `out_of_scope_reason`: string or null; required for `Out of scope`, with evidence that the old-paper topic is outside current syllabus/current lecture/source-pack authority
- `rendered_anchor`: string; stable HTML anchor for the rendered answer entry

Each `source_refs` object must include:

- `source_id`: string
- `source_title`: string
- `page`: number, string, or null
- `slide`: number, string, or null
- `locator`: string or null
- `evidence_note`: string explaining how the source supports the answer

Each worker coverage metadata sidecar record must include:

- `lane`: one of `source_research`, `extraction`, `coverage`, `evidence`, `correctness`, `learner_surface`, `qa_executor`, or `final_reviewer`
- `invocation_mode`: `independent_subagent`, `installed_toml_agent`, `fallback_local`, or `baseline_unverified`
- `status`: one of `PASS`, `MAJOR`, `BLOCKING`, or `NOT_RUN`
- `paper_ids`: array of paper ids checked
- `question_ids`: array of question ids checked, or a clear whole-artifact/whole-pack scope marker
- `coverage_counts`: object with inventory, ledger, rendered, `Source gap`, `Unreadable`, `Out of scope`, and unresolved finding counts where available
- `raw_child_report_path`: string or null
- `parent_validated`: boolean
- `tooling_preflight`: object or reference to the sidecar that records it

Detailed page, slide, extraction, and source-reference notes belong in `source-index.json` and `answer-ledger.json`. Worker coverage, verifier, readiness, parent validation, tooling preflight, and raw report notes belong in `verifier-reports/`, `qa-report.json`, and worker coverage sidecars. The learner HTML should show only the question, answer/reveal panel, topic label, marks, and learner-relevant `Source gap`, `Unreadable`, or `Out of scope` note.

Visual-dependent entries need a supported visual path before final rendering. If an answer uses a diagram, table, graph, tree, heap, B-tree, route map, image-only prompt, screenshot, or formula image, the ledger or sidecar must name the rendered visual payload and the visual inspection result. Generic notes such as `fallback local inspection recorded` are not enough for an answered visual-dependent item; use concrete rendered-image evidence or a visual worker report. `Unreadable` is acceptable only after the rendered visual was inspected and recorded as cropped, blurry, missing, or otherwise unusable; a `pdftotext` miss alone is not enough.

Sample answers, marking schemes, senior answers, and external worked solutions are untrusted cross-checks only. They can flag conflicts or wording expectations, but they cannot override current lecture evidence, the current syllabus file, or the current lecture/source pack used as syllabus authority.

Do not silently fill gaps from memory. For a question-only paper, it is acceptable to produce a strong answer only when the lecture/source pack supports it; otherwise the ledger and learner artifact must make the `Source gap` or `Unreadable` status visible so the student knows what to ask a lecturer, tutor, or classmate.

Do not silently empty the paper either. A `Source gap` should tell the student that the course materials do not support the answer after the answer-production gate, not that Study Forge had no local answer template for the question.

Do not blur `Out of scope` and `Source gap`. Old-paper topics outside current syllabus/current lecture/source-pack authority are `Out of scope` with evidence; current-authority topics that cannot be answered after lookup, inspection, and synthesis are `Source gap`.

Each rendered learner answer should include:

- Question number and preserved question wording or a faithful concise paraphrase when extraction is messy.
- Exam-ready answer, structured by marks when marks are visible.
- Topic label: short course concept name only, not file names, page numbers, slide numbers, source refs, or syllabus/source-fit paragraphs.
- Study note: a short learner-facing caveat only when the item is `Source gap`, `Unreadable`, or otherwise changes how the student should revise.
- Common traps or examiner keywords when the source supports them.
- Visible `Source gap` or `Unreadable` note when evidence or extraction is insufficient.

#### Verifier Tooling Preflight

For `past-year`, run verifier tooling/subagent preflight before finalizing the artifact. Check for an installed `studyforge-verifier` TOML first; if it is absent but Codex subagents are available, spawn a normal worker and paste the relevant verifier lane instructions from `skills/references/studyforge-verifier.md`.

Minimum Codex invocation shape:

```text
multi_agent_v1.spawn_agent({message:"TASK: ... DELIVERABLE: ... SCOPE: ... VERIFY: ...", agent_type:"worker", fork_context:false})
```

Concrete lane template:

```text
multi_agent_v1.spawn_agent({message:"TASK: Run the Study Forge verifier lane <lane> for <course folder>. DELIVERABLE: A verifier report with PASS, BLOCKING, MAJOR, or NOT_RUN findings and required fixes. SCOPE: Raw course folder path, source-inventory.json, question-inventory.json, source-index.json, answer-ledger.json, relevant source files, and draft HTML only. VERIFY: Compare the lane evidence against source material and answer-ledger.json without private reasoning, intended answers, or leading conclusions.", agent_type:"worker", fork_context:false})
```

Record exactly one readiness state in `qa-report.json`, sidecar proof files, and the final response:

- `independent_verified`: all required verifier lanes ran through independent verifier subagents or the installed verifier role, parent validation checked the worker coverage metadata and raw reports, and every `BLOCKING` finding was fixed or converted to `Source gap` / `Unreadable` / `Out of scope`.
- `fallback_local_reviewed`: verifier tooling/subagent preflight was attempted, independent lanes could not run, and the same lanes were checked as separate local passes. This is degraded local review, not independent verification.
- `baseline_unverified`: verifier preflight was not run, proof docs are incomplete, or verifier lane results are missing.
- `degraded_parent_shell`: the parent produced a ledger, HTML shell, or local review without required worker reports or sidecar coverage metadata. This is degraded and cannot be called `independent_verified`.

Only `independent_verified` can support a normal readiness claim after blocking findings are resolved. `fallback_local`, `fallback_local_reviewed`, `baseline_unverified`, `degraded_parent_shell`, and missing worker reports must not be promoted to independent verification and still require explicit degraded-state wording. The other states must remain visible in proof sidecars and the final response, with unresolved limitations named; learner HTML shows only limitations that affect studying.

late discovery rule: if multi-agent tooling or the verifier role becomes available after local review began, rerun the affected verifier lanes through that tooling or escalate as blocked. Do not silently finish from local passes.

Freshness rule: a final parent gate or QA report can supersede raw verifier findings only when its timestamp or artifact mtime is newer than the rendered HTML and proof sidecars it certifies, and when it names which `BLOCKING` or `MAJOR` findings were resolved, converted to `Source gap` / `Unreadable` / `Out of scope`, intentionally retained as degraded, or accepted by the user. Stale reports remain historical evidence, not current pass evidence.

#### Independent Verification Gate

For `past-year`, use one `studyforge-verifier` with narrow verifier lanes before finalizing the artifact. Do not pass private reasoning, intended answers, or leading conclusions. Give each lane the raw course folder path, `source-inventory.json`, `question-inventory.json`, `source-index.json`, `answer-ledger.json`, relevant source paths, and the draft HTML render when checking learner surface.

Verifier lanes:

- `extraction`: compare `question-inventory.json` against source papers and flag omitted diagrams, broken tables, numbering drift, missing marks, missing instructions, or text that should be `Unreadable`.
- `coverage`: confirm every provided past-year paper, question, subpart, mark value, table, diagram, and instruction is represented or explicitly marked `Unreadable`, `Duplicate`, or `Out of scope`.
- `evidence`: trace each non-gap answer through `source_refs`; flag weak citations, unsupported claims, wrong syllabus/source fit, missing source refs, and answer text that looks generic rather than course-backed.
- `correctness`: check whether each supported answer answers the question, uses mark-appropriate structure, avoids overclaiming, and explains conflicts with sample answers or marking schemes.
- `learner_surface`: confirm the HTML render matches `answer-ledger.json`, renders the ledger model answer rather than only `student_explanation`, remains self-contained for revision, uses the `past-year-script` design system, and keeps proof metadata, source refs, verifier status, readiness status, worker paths, and build metadata out of the learner surface.

Verifier output should be concrete and actionable:

- `PASS`, `BLOCKING`, `MAJOR`, or `NOT_RUN` per lane and paper.
- question number, ledger `question_id`, or source location
- finding
- evidence
- required fix

Severity meanings:

- `PASS`: no accuracy, evidence, extraction, or coverage issue found for the checked scope.
- `BLOCKING`: the artifact must not be called ready until fixed, converted to a clearly labeled `Source gap`, converted to `Unreadable`, or converted to `Out of scope`.
- `MAJOR`: the answer may be usable after correction, but it has a material weakness in wording, completeness, mark structure, source fit, or sample-answer alignment that should be fixed before final delivery.
- `NOT_RUN`: the lane was not run; explain why in `verifier-reports/` and `qa-report.json`.

Blocking conditions:

- a past-year paper or question was skipped without a documented reason
- an answer has no lecture evidence but is not marked `Source gap`
- a citation does not support the answer
- a question relies on general model knowledge instead of course-source evidence
- a sample answer or marking scheme contradicts the answer and the conflict is not explained
- extraction dropped a material table, diagram, mark value, or instruction

Do not call the artifact ready while any blocking finding remains. Fix major findings when possible; if the course sources cannot support a fix, change the ledger status to `Source gap` and name the missing evidence. If extraction is too damaged to trust, change the ledger status to `Unreadable` and name the unreadable source region. Sidecar proof files must list verifier lanes run, pass/fail status, unresolved source gaps, unreadable items, the readiness state, raw report references, and which verifier lanes ran as independent subagent checks versus local review. The final learner HTML stays study-first and shows only learner-relevant gaps or limitations. After preflight, if independent tools remain unavailable, run the same lanes as separate local passes and label the readiness state as `fallback_local_reviewed`, not subagent-verified. The output is degraded and requires explicit user acceptance before delivery.

### Formula-Lab

Use only formulas, assumptions, units, and worked examples visible in the source. Show what each symbol means before asking the student to calculate.

### Trace-Lab

Use `trace` output as the interaction spine. Show initial state, rule applied, state changes, invariant, final result, complexity, and traps.

### Drill-Pack

Use `drill` output as the question spine. Group by concept, mark value, or difficulty, and use reveal controls so the student can answer before seeing the solution.

## QA Checklist

- Open the direct-open HTML file or chosen surface and confirm the artifact renders.
- Test internal links and navigation anchors.
- Confirm sidecar proof records the Source Basis and Scope Boundaries.
- Confirm the learner artifact avoids audit scaffold labels while preserving learner-relevant source gaps and limitations.
- Confirm there are no placeholders in visible content.
- Check pedagogical sufficiency for representative Required topics: can a student learn or revise this topic from the artifact without opening the PDF, using source pages only for audit or verification?
- Confirm source/page references are evidence after or alongside explanation, not the main learning content.
- For `past-year`, compare the detected question count against the artifact answer count for each paper and list any extraction failures or source gaps.
- For `past-year`, run the proof validator or equivalent checks before delivery; duplicate ledger IDs, duplicate inventory IDs, compacted placeholder stems, and ledger/inventory question-text drift are blocking proof defects.
- For `past-year`, sample several answers and confirm each has lecture evidence; answer-only text without a source mapping fails QA.
- For `past-year`, confirm sidecar verifier/proof files name the verifier lanes and show no unresolved blocking findings.
- Test reveal behavior for answers, hints, or worked explanations.
- Check responsive layout at a narrow and wide viewport when HTML is used.
- Check print sanity with print CSS or a generated print/PDF preview when HTML is used.

## Anti-Rules

- Do not create an artifact before inspecting the required sources.
- Do not hide the source basis in a private note or final chat only; record it in sidecar proof files when the selected learner design keeps source refs out of HTML.
- Do not mix old samples into the artifact unless they are labeled as comparison material.
- Do not ship a navigation/reference atlas when the user asked for a revision artifact.
- Do not let page numbers, slide links, or source snippets stand in for distilled explanations, definitions, examples, traps, or quick checks.
- Do not answer past-year questions from general model knowledge when lecture evidence is missing; expose the source gap.
- Do not ship an over-gapped fallback where a whole paper or large structured section becomes `Source gap` because local answer synthesis was skipped, blocked, or not implemented.
- Do not skip a past-year paper in the provided folder unless it is unreadable, duplicate, or explicitly out of scope; report skipped files.
- Do not merge verifier output silently; show the pass/fail status and unresolved source gaps in the artifact.
- Do not invent formulas, examples, question likelihood, or mark weights that are not supported by the sources.
- Do not make a decorative landing page when the user asked for a study tool.
- Do not leave reveal answers, links, or print behavior unverified.
- Do not claim the artifact is ready until the declared Verification Plan has passed.
