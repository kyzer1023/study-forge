# Past-Year Study Pack — Design System v2 (Script)

**Design system ID:** `past-year-script`
**Reference implementation:** `reference-mock.html` (this folder).
Used by `study-forge artifact past-year`. Supersedes sage-green card layouts for all past-year HTML.

---

## Scene (theme forcing sentence)

A student at a bedroom desk around 10pm, one warm desk lamp, laptop screen slightly amber from the room light, flipping question by question through a past paper the night before the exam. They want the screen to feel like marked exam pages, not another productivity app.

**Theme decision:** warm light mode. Paper-toned surfaces, ink-dark text, green for "correct," indigo for navigation focus.

---

## Color strategy

**Committed warm paper.** The page background and question surfaces carry most of the identity (warm neutrals ~40% of perceived color). Accent colors appear only for navigation selection, primary actions, correct reveal, and gap warnings.

All colors in OKLCH. No pure `#000` or `#fff`. Neutrals tinted toward warm hue **75** (parchment).

### Core tokens

| Token | OKLCH | Role |
|---|---|---|
| `--bg` | `oklch(96.5% 0.012 75)` | page; warm parchment |
| `--bg-raised` | `oklch(98.8% 0.008 75)` | sidebar rail, jump strip |
| `--surface` | `oklch(99.4% 0.006 80)` | question block surface |
| `--ink` | `oklch(22% 0.02 265)` | primary text; cool ink, not warm brown |
| `--ink-soft` | `oklch(48% 0.018 265)` | metadata, dimmed options |
| `--line` | `oklch(88% 0.014 75)` | rules, borders |
| `--line-strong` | `oklch(78% 0.02 75)` | section dividers |

### Accent (navigation + actions)

| Token | OKLCH | Role |
|---|---|---|
| `--focus` | `oklch(42% 0.14 275)` | active paper, focus rings, primary buttons |
| `--focus-soft` | `oklch(94% 0.03 275)` | selected nav item fill |
| `--focus-ink` | `oklch(36% 0.12 275)` | text on focus-soft |

### Semantic

| Token | OKLCH | Role |
|---|---|---|
| `--correct` | `oklch(48% 0.13 152)` | revealed correct option text |
| `--correct-soft` | `oklch(94% 0.035 152)` | correct option fill |
| `--correct-ink` | `oklch(38% 0.11 155)` | "Why" panel label |
| `--gap` | `oklch(44% 0.1 25)` | source-gap tag text |
| `--gap-soft` | `oklch(95% 0.025 35)` | source-gap tag fill |

### Reflex check

- Not sage-green study app (retired)
- Not dark terminal or neon
- Not navy/gold academic
- Not healthcare teal on white
- Green correct + indigo nav is the pairing; domain should not predict it

---

## Typography

**Pairing:** UI chrome in **Inter**; question stems in **Source Serif 4** (exam-script voice). Labels and indices in **IBM Plex Mono**.

| Role | Family | Size | Weight | Notes |
|---|---|---|---|---|
| Page title | Inter | 1.75rem | 700 | letter-spacing -0.02em |
| Paper title | Inter | 1.25rem | 600 | |
| Question stem | Source Serif 4 | 1.0625rem | 600 | full main column width; justify |
| Body / explanation | Inter | 1rem | 400 | full main column width; line-height 1.6; justify |
| Metadata | Inter | 0.8125rem | 500 | topic, marks, type |
| Q number / option label | IBM Plex Mono | 0.8125rem | 600 | A, B, C; jump chips |
| Panel label | Inter | 0.6875rem | 700 | uppercase, tracking 0.08em |

Scale ratio ~1.2 between heading steps. Load fonts via `<link>` (Google Fonts) or self-host; fallbacks: `Georgia` for serif, `system-ui` for sans, `ui-monospace` for mono.

---

## Layout architecture

### Shell: two-column study desk (not card stack)

```
┌─────────────────────────────────────────────────────────┐
│  Header: title + one-line instruction (no stat grid)    │
├──────────────┬──────────────────────────────────────────┤
│  Rail (~200) │  Main column (fluid, max ~1000px)      │
│              │                                          │
│  Paper list  │  Paper title only (questions in rail)   │
│  (vertical)  │  Question blocks (ruled, not cards)      │
│  Question    │  ...                                     │
│  list        │                                          │
└──────────────┴──────────────────────────────────────────┘
```

- **Left rail:** two stacked panels in one sticky column.
  - **Papers:** year switcher with question count suffix.
  - **Questions:** vertical list for the active paper only; updates when the paper changes. Same item styling as papers (indigo active, green when revealed).
- **Main column:** current paper only. No other paper's questions in the DOM while inactive (or `hidden` + `aria-hidden`).
- **Question blocks:** flat ruled sections separated by `--line-strong` hairlines, not floating cards. Padding 28px vertical. First question has no top rule.
- **No stat grid** in header. Revealed questions tint green in the sidebar question list.

### Spacing rhythm

- Section gaps vary: 8px inside question metadata, 20px stem-to-options, 32px between questions, 48px below jump strip.
- Avoid uniform 16px padding everywhere.

---

## Components

### Paper rail item

- Default: ink-soft text, transparent background
- Active: `--focus-soft` background, `--focus-ink` text, 2px inset `--focus` left edge (full-height inset bar, not a side-stripe on content cards; this is nav chrome only)
- Hover (inactive): `--bg-raised`

### Question sidebar (`.qnav-item`)

- Renders in `#questionRail` below the paper list; repopulated on paper switch.
- Mono labels (A1, B1(a)(i), …); same hover/active inset bar as paper items.
- **Done (revealed):** `--correct-soft` fill, `--correct-ink` text.
- **Current (hash deep link):** `--focus-soft` active state.
- Desktop: vertical scroll within sticky sidebar if the list is long.
- Mobile: second horizontal scroll row under papers.

### Question block

**Header row:** `[QNO mono]` · `[type · marks · topic]` · optional `[Source gap]` pill

**Stem:** serif, pre-wrap for multi-line stems

**MCQ options:** vertical list, each row:
```
[mono label]  [option text ........................]  [check slot]
```
- Rows are plain (no boxes) until reveal
- On reveal: correct row gets `--correct-soft` background, text `--correct`, check SVG fades in; wrong rows fade to `--ink-soft` at 70% opacity
- Multi-answer: all correct indices highlighted; wrong unchanged opacity

**Reveal control:** text button styled as underline link in `--focus-ink`, not a filled pill. On reveal becomes "Hide answer". `aria-expanded` required.

**Panel (below button):** grid-rows `0fr → 1fr` expand. Inner panel has top rule `--line-strong`, padding-top 20px.
- MCQ label: **WHY** (not "Explanation")
- Structured label: **MODEL ANSWER**
- Gap label: **STUDY NOTE**
- Body in Inter, not serif

### Source gap

- Small pill: `--gap-soft` / `--gap` text
- No option highlights on reveal (none are correct)
- Panel explains what to study instead

---

## Navigation & routing

Unchanged from v1 content contract:

- Hash router: `#paper-<slug>` shows one paper
- Deep link `#<question-id>` opens owning paper + scrolls to question
- `aria-current="true"` on active rail item only (remove attribute when inactive)
- Never one long multi-paper scroll

**Paper switch motion:** main column opacity 0 → 1 over 220ms; `translateX(8px → 0)` (horizontal, not vertical; different from retired mock). Rail selection updates instantly. No card stagger on paper switch (ruled blocks load as one column).

---

## Motion contract

Easing: `--ease-out: cubic-bezier(0.16, 1, 0.3, 1)`
Check only: `--ease-pop: cubic-bezier(0.34, 1.2, 0.64, 1)` (subtle; no bounce)

| Interaction | Behavior | Duration |
|---|---|---|
| Panel expand | `grid-template-rows 0fr → 1fr` | 480ms ease-out |
| Panel content | opacity + translateY(4px → 0), 50ms delay | 320ms |
| Correct option | color + background | 520ms ease-out |
| Check mark | scale 0.5 → 1, opacity 0 → 1, 160ms delay | 380ms ease-pop |
| Wrong options | opacity → 0.7 | 400ms |
| Jump chip done | background + color | 200ms |
| Question sidebar switch | list repopulate (instant) | 0ms |
| Paper switch | main column fade + slideX | 220ms |

`prefers-reduced-motion: reduce`: all ≤ 1ms.

**Bans:** no height/margin animation, no page-load orchestration, no decorative motion, no elastic/bounce on layout.

---

## Hard content rules (unchanged)

Generators must NOT emit into the learner surface:

- Source-basis page references
- Syllabus/source fit paragraphs
- Verifier notes, QA status, build metadata, pipeline badges

Generators MUST emit per question:

- `id`, `no`, `kind` (`mcq` | `structured`), `marks`, `topic`, `stem`
- MCQ: `options[]`, `correct` (index or index[]), `explanation`
- Structured: `answer`
- Optional: `gap: true`

Strip exam noise from stems (SULIT footers, page markers).

## Math notation

Answers and explanations may contain exponents, subnet formulas, and BER values.
Render them with **KaTeX** (inline `$...$` delimiters), not raw `^` text.

**Generator options (pick one):**

1. **Emit LaTeX directly** in answer text: `$2^{32-27} = 32$`, `$10^{-5}$`
2. **Emit plain shorthand** and let the HTML layer auto-convert:
   - `2^(32-27)` → `$2^{32-27}$`
   - `10^-5` → `$10^{-5}$`

Auto-convert runs at render time on panel prose only (stems stay plain unless
you add the same pass). Typeset when a panel is first revealed to avoid work
on hidden content.

For offline use, bundle KaTeX CSS/JS locally instead of the jsDelivr CDN.

---

## Reveal behavior (unchanged logic, new visuals)

- **Objective:** correct option(s) turn green (`--correct`). Explanation only in panel. No "Answer: X." line.
- **Structured:** model answer panel only.
- **Gap:** study note panel; no option highlight.

---

## Responsive

| Breakpoint | Behavior |
|---|---|
| ≥768px | Rail + main two-column |
| <768px | Rail becomes two horizontal scroll rows (papers, then questions); main full width |
| <480px | Reduce horizontal padding; option label column 22px |

Touch targets ≥ 44px for reveal control and sidebar nav items.

---

## Accessibility

- Focus visible: 2px `--focus` outline, 2px offset
- Reveal button: `aria-expanded`, panel `aria-live="polite"` on first open only
- Rail: `<nav aria-label="Papers">`, list of links/buttons
- Color is not sole indicator: check mark on correct options
- Contrast: ink on surface ≥ 7:1; correct text on correct-soft ≥ 4.5:1

---

## Bans (shared + product)

- Side-stripe accents on question content (nav inset bar excepted)
- Gradient text, glassmorphism, hero-metric grids, icon-card grids, modals
- Sage-green card-stack study apps (mint floating cards from v1 mock)
- Em dashes in copy
- Reviewer metadata in HTML

---

## Data shape (generator contract)

```ts
type Paper = {
  slug: string;       // "paper-2021"
  label: string;      // "2021"
  title: string;      // "CST_PSY_2021"
  questions: Question[];
};

type Question = {
  id: string;
  no: string;
  kind: "mcq" | "structured";
  marks: number;
  topic: string;
  stem: string;
  gap?: boolean;
  // mcq only:
  options?: string[];
  correct?: number | number[] | null;
  explanation?: string;
  // structured only:
  answer?: string;
};
```

---

## Implementation checklist (for next build)

- [ ] Self-contained HTML or generator outputs Script tokens, not v1 green tokens
- [ ] Two-column shell with paper rail
- [ ] Ruled question blocks (no card borders)
- [ ] Inter + Source Serif 4 + IBM Plex Mono
- [ ] Green correct / indigo nav palette
- [ ] Hash router, one paper per view
- [ ] Panel expand via grid-rows
- [ ] Strip all reviewer fields at generation time
