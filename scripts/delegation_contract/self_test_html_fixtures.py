from __future__ import annotations

from typing import Final

AUDIT_FREE_LEARNER_HTML: Final = (
    "<!doctype html><html><body><main><h1>Revision Atlas</h1>"
    + "<p>Source gap: unreadable annotation.</p></main></body></html>"
)

BAD_PAST_YEAR_LEARNER_HTML: Final = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CPT212 Past-Year Artifact</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f5faf5; color: #123; }
    .metric-card { border-radius: 18px; background: #fff; padding: 16px; }
    .paper { margin: 24px 0; padding: 20px; border: 1px solid #dbe7db; }
  </style>
</head>
<body>
  <header>
    <h1>CPT212 Past-Year Artifact</h1>
    <p>Generated 2026-07-06 from C:\\CS_USM\\Y2S2\\CPT212.</p>
    <section class="metric-card">readiness_state: usable_with_recorded_gaps</section>
    <section class="metric-card">answer-ledger.json entries: 260</section>
  </header>
  <main>
    <section class="paper" id="paper-2020"><h2>Paper 2020</h2><p>Answered from source</p><p>source_refs: lecture.pdf p. 12</p></section>
    <section class="paper" id="paper-2021"><h2>Paper 2021</h2><p>Evidence: verifier-reports/learner-surface.json</p></section>
    <section class="paper" id="paper-2022"><h2>Paper 2022</h2><p>worker-report path: .study-forge/worker-report.json</p></section>
  </main>
</body>
</html>
"""

SCRIPT_PAST_YEAR_LEARNER_HTML: Final = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Past-Year Study Pack</title>
  <style>
    :root {
      --bg: oklch(96.5% 0.012 75);
      --focus: oklch(42% 0.14 275);
      --correct: oklch(48% 0.13 152);
      --font-ui: Inter, system-ui, sans-serif;
      --font-serif: "Source Serif 4", Georgia, serif;
      --font-mono: "IBM Plex Mono", ui-monospace, monospace;
    }
  </style>
</head>
<body data-design-system-id="past-year-script">
  <header class="site-header"><h1>Past-Year Study Pack</h1></header>
  <div class="desk">
    <aside class="rail-wrap">
      <nav class="rail" aria-label="Papers"><a href="#paper-2021" aria-current="true">2021</a></nav>
      <nav class="rail" id="questionRail" aria-label="Questions"><a href="#q-2021-a1" aria-current="true">A1</a></nav>
    </aside>
    <main class="main">
      <section class="view active" data-paper-view="paper-2021" id="paper-2021">
        <article class="q" id="q-2021-a1">
          <div class="qhead"><span class="qno">A1</span><span class="qmeta">mcq · 1 mark · graph traversal</span></div>
          <p class="stem">Which traversal uses a queue?</p>
          <ol class="options"><li class="opt" data-correct="true"><span class="label">A</span><span class="text">BFS</span><span class="check">✓</span></li></ol>
          <button class="reveal" type="button" aria-expanded="false" aria-controls="panel-q-2021-a1">Reveal answer</button>
          <div class="panel" id="panel-q-2021-a1" aria-live="polite"><div><b>WHY</b><p>BFS explores by levels.</p></div></div>
        </article>
      </section>
    </main>
  </div>
  <script>
    window.addEventListener("hashchange", () => {});
    document.querySelectorAll(".reveal").forEach((button) => button.addEventListener("click", () => {}));
  </script>
</body>
</html>
"""

PAST_YEAR_LEARNER_WITHOUT_SCRIPT_FONTS_HTML: Final = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Past-Year Study Pack</title>
  <style>
    :root {
      --bg: oklch(96.5% 0.012 75);
      --focus: oklch(42% 0.14 275);
      --correct: oklch(48% 0.13 152);
    }
  </style>
</head>
<body data-design-system-id="past-year-script">
  <div class="desk">
    <aside class="rail-wrap">
      <nav class="rail" aria-label="Papers"><a href="#paper-2021" aria-current="true">2021</a></nav>
      <nav class="rail" id="questionRail" aria-label="Questions"><a href="#q-2021-a1">A1</a></nav>
    </aside>
    <main class="main">
      <section class="view active" id="paper-2021">
        <article class="q" id="q-2021-a1">
          <p class="stem">Which traversal uses a queue?</p>
          <button class="reveal" type="button" aria-expanded="false">Reveal answer</button>
        </article>
      </section>
    </main>
  </div>
  <script>window.addEventListener("hashchange", () => {});</script>
</body>
</html>
"""
