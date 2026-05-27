#!/usr/bin/env python
"""
JobRadar 🎯 — Gradio Intelligence Dashboard
Real-time job market analysis with live agent streaming.

Run with: uv run python app.py
"""
import sys
import io
import json
import queue
import threading
import time
from pathlib import Path
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)
Path("output").mkdir(exist_ok=True)
Path("memory").mkdir(exist_ok=True)

# ── Pipeline stage definitions ────────────────────────────────────────────────
STAGES = [
    ("🔍 Job Hunter",      "Searching for real job listings via Tavily"),
    ("📊 Market Analyst",  "Counting skills and extracting market patterns"),
    ("🧭 Gap Advisor",     "Comparing your CV to the market requirements"),
    ("📄 Roadmap Writer",  "Writing your personalised 90-day learning plan"),
]

# ── Example CVs for quick-start ───────────────────────────────────────────────
EXAMPLE_CVS = {
    "CS Student (Python)": (
        "Python Backend Developer",
        "Remote — Europe",
        """Skills: Python, Flask, MySQL, basic Docker, HTML/CSS, Git.
Projects: REST API for university task management (Python + Flask + MySQL).
          Personal portfolio website (HTML/CSS/JavaScript).
Experience: 6-month internship — junior web developer (PHP/MySQL).
Education: BSc Computer Science, final year.
Languages: English (fluent), Greek (native).""",
    ),
    "Frontend Student (JS/React)": (
        "Frontend React Developer",
        "Remote — Europe",
        """Skills: JavaScript (ES6+), React (basics), HTML5, CSS3, Git.
Projects: Cloned a Netflix UI in React (personal project).
          University group project — responsive website with Vanilla JS.
Experience: None professional — all academic projects.
Education: BSc Software Engineering, 3rd year.
Languages: English (intermediate).""",
    ),
    "Data Science Student": (
        "Data Analyst",
        "London, UK or Remote",
        """Skills: Python, Pandas, NumPy, Matplotlib, SQL (basic), Excel.
Projects: Analysed a Kaggle dataset (Titanic) with Python/Pandas.
          University dissertation: regression analysis on housing prices.
Experience: No professional experience.
Education: BSc Mathematics & Statistics, final year.
Languages: English (native).""",
    ),
}


# ── Stdout capture ────────────────────────────────────────────────────────────
class LineCapture(io.TextIOBase):
    """Intercepts stdout writes and feeds complete lines into a queue."""

    def __init__(self, q: queue.Queue, original):
        self._q = q
        self._original = original
        self._buf = ""

    def write(self, text: str) -> int:
        self._original.write(text)
        self._original.flush()
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                self._q.put(line)
        return len(text)

    def flush(self):
        self._original.flush()


# ── HTML helpers ──────────────────────────────────────────────────────────────
def stage_html(active: int, finished: bool = False) -> str:
    items = []
    for i, (name, desc) in enumerate(STAGES):
        if finished or i < active:
            state, icon = "done",    "✅"
        elif i == active:
            state, icon = "active",  "⏳"
        else:
            state, icon = "pending", "○"
        items.append(
            f'<div class="jr-stage {state}">'
            f'<span class="jr-icon">{icon}</span>'
            f'<div><strong>{name}</strong>'
            f'<div class="jr-desc">{desc}</div></div></div>'
        )
    return '<div class="jr-stages">' + "".join(items) + "</div>"


def readiness_html(gap_file: Path) -> str:
    """Renders the readiness score card from the gap analysis JSON."""
    if not gap_file.exists():
        return ""
    try:
        data = json.loads(gap_file.read_text(encoding="utf-8"))
        score = data.get("readiness_score", 0)
        label = data.get("readiness_label", "")
        gaps  = data.get("critical_gaps", [])
        have  = data.get("skills_you_have", [])
        now   = data.get("apply_now_jobs", [])

        if score >= 90:
            colour = "#2ea043"
        elif score >= 70:
            colour = "#388bfd"
        elif score >= 40:
            colour = "#d29922"
        else:
            colour = "#f85149"

        gaps_html = "".join(f'<span class="gap-tag">{g}</span>' for g in gaps[:6])
        have_html = "".join(f'<span class="have-tag">{s}</span>' for s in have[:8])
        now_html  = "".join(f"<li>{j}</li>" for j in now[:5])

        return f"""
        <div class="readiness-card">
          <div class="score-ring" style="--clr:{colour}">
            <span class="score-num">{score}%</span>
            <span class="score-lbl">{label}</span>
          </div>
          <div class="score-detail">
            <div class="tag-row"><strong>You have:</strong><br>{have_html or '<em style="color:#8b949e">none matched yet</em>'}</div>
            <div class="tag-row" style="margin-top:10px"><strong>Critical gaps:</strong><br>{gaps_html or '<em style="color:#8b949e">none — great!</em>'}</div>
            {'<div class="apply-now"><strong>Apply RIGHT NOW:</strong><ul>' + now_html + '</ul></div>' if now else ''}
          </div>
        </div>"""
    except Exception:
        return ""


def files_html() -> str:
    out = Path("output")
    files = sorted(out.glob("*.json")) + sorted(out.glob("*.md"))
    if not files:
        return '<p style="color:#8b949e;font-size:13px">No output files yet.</p>'
    rows = "".join(
        f'<tr><td>📄 {f.name}</td><td style="color:#8b949e">{f.stat().st_size:,} B</td></tr>'
        for f in files
    )
    return (
        '<table class="jr-files">'
        '<tr><th>File</th><th>Size</th></tr>'
        f'{rows}</table>'
    )


def get_file_choices() -> list[str]:
    out = Path("output")
    return [f.name for f in sorted(out.glob("*.json")) + sorted(out.glob("*.md"))]


def load_file_content(filename: str) -> tuple[str, str, str]:
    if not filename:
        return "", "json", ""
    path = Path("output") / filename
    if not path.exists():
        return f"File not found: {filename}", "text", ""
    text = path.read_text(encoding="utf-8")
    if filename.endswith(".json"):
        try:
            text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except Exception:
            pass
        lang = "json"
    else:
        lang = "markdown"
    size = path.stat().st_size
    info = (
        f'<div style="color:#8b949e;font-size:12px;margin-bottom:8px">'
        f'📄 <strong style="color:#e6edf3">{filename}</strong>'
        f' &nbsp;·&nbsp; {size:,} bytes'
        f' &nbsp;·&nbsp; {len(text.splitlines())} lines</div>'
    )
    return text, lang, info


# ── Core analysis generator ───────────────────────────────────────────────────
def run_analysis(job_title: str, location: str, my_cv: str):
    """
    Generator that runs the JobRadar crew and streams output to Gradio.
    Yields: (log_text, stage_html, readiness_card, report_md, files_html,
             file_picker_update, done_visible)
    """
    job_title = job_title.strip()
    location  = location.strip()
    my_cv     = my_cv.strip()

    if not job_title or not my_cv:
        yield ("⚠️  Fill in Job Title and your CV/skills.", stage_html(0),
               "", "", "", gr.update(), gr.update(visible=False))
        return

    if not location:
        location = "Remote — Europe"

    log_lines: list[str] = []
    log_q: queue.Queue   = queue.Queue()
    stage_idx = {"v": 0}
    result    = {"report": None, "error": None, "done": False}

    # ── Task completion callback ──────────────────────────────────────────
    def on_task(task_output):
        idx = stage_idx["v"]
        log_q.put(f"✅  {STAGES[idx][0]} — complete")
        log_q.put("─" * 56)
        if stage_idx["v"] < len(STAGES) - 1:
            stage_idx["v"] += 1
            nxt = STAGES[stage_idx["v"]]
            log_q.put(f"\n▶  {nxt[0]}")
            log_q.put(f"   {nxt[1]}\n")

    # ── Crew thread ───────────────────────────────────────────────────────
    def crew_thread():
        capture    = LineCapture(log_q, sys.__stdout__)
        old_stdout = sys.stdout
        sys.stdout = capture
        try:
            from ai_research_crew.crew import JobRadar
            crew = JobRadar().crew()
            crew.task_callback = on_task
            crew.kickoff(inputs={
                "job_title": job_title,
                "location":  location,
                "my_cv":     my_cv,
            })
            rp = Path("output/04_learning_roadmap.md")
            if rp.exists():
                result["report"] = rp.read_text(encoding="utf-8")
        except Exception as exc:
            result["error"] = f"❌  {type(exc).__name__}: {exc}"
        finally:
            sys.stdout = old_stdout
            result["done"] = True

    # ── Seed log ──────────────────────────────────────────────────────────
    for line in [
        "=" * 56,
        f"🎯  JobRadar — {datetime.now():%Y-%m-%d  %H:%M:%S}",
        f"    Job title : {job_title}",
        f"    Location  : {location}",
        "=" * 56,
        "",
        f"▶  {STAGES[0][0]}",
        f"   {STAGES[0][1]}",
        "",
    ]:
        log_q.put(line)

    t = threading.Thread(target=crew_thread, daemon=True)
    t.start()

    # ── Stream loop ───────────────────────────────────────────────────────
    while not result["done"] or not log_q.empty():
        time.sleep(0.2)
        changed = False
        while not log_q.empty():
            try:
                log_lines.append(log_q.get_nowait())
                changed = True
            except queue.Empty:
                break
        if changed:
            yield (
                "\n".join(log_lines[-300:]),
                stage_html(stage_idx["v"]),
                "", "", "",
                gr.update(),
                gr.update(visible=False),
            )

    # ── Final yield ───────────────────────────────────────────────────────
    log_lines += ["", "=" * 56, "Analysis complete.", "=" * 56]
    if result["error"]:
        log_lines.append(result["error"])

    report_md  = result["report"] or result["error"] or "⚠️  No report generated."
    choices    = get_file_choices()
    gap_card   = readiness_html(Path("output/03_gap_analysis.json"))

    yield (
        "\n".join(log_lines),
        stage_html(len(STAGES) - 1, finished=True),
        gap_card,
        report_md,
        files_html(),
        gr.update(choices=choices, value=choices[0] if choices else None),
        gr.update(visible=True),
    )


# CSS 
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body, .gradio-container { background:#0d1117 !important; font-family:'Inter',sans-serif !important; }
.gradio-container { max-width:1440px !important; }

/* Header */
.jr-header { background:linear-gradient(135deg,#0d1117,#161b22 55%,#1a2035);
  border:1px solid #30363d; border-radius:16px; padding:24px 36px;
  display:flex; align-items:center; gap:20px;
  box-shadow:0 4px 32px rgba(0,0,0,.5); margin-bottom:8px; }
.jr-logo  { font-size:52px; line-height:1; }
.jr-name  { color:#e6edf3; font-size:28px; font-weight:700; letter-spacing:-.5px; }
.jr-tag   { color:#8b949e; font-size:13px; margin-top:4px; }
.jr-pill  { margin-left:auto; background:linear-gradient(135deg,#1f4e8c,#388bfd);
  color:#fff; padding:6px 16px; border-radius:20px; font-size:12px; font-weight:600; }

/* Section labels */
.jr-label { color:#8b949e; font-size:11px; font-weight:600;
  text-transform:uppercase; letter-spacing:.8px;
  margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid #30363d; }

/* Inputs */
.gradio-container input,.gradio-container textarea {
  background:#0d1117 !important; border:1px solid #30363d !important;
  color:#e6edf3 !important; border-radius:8px !important;
  font-family:'Inter',sans-serif !important; }
.gradio-container input:focus,.gradio-container textarea:focus {
  border-color:#388bfd !important; box-shadow:0 0 0 3px rgba(56,139,253,.15) !important; }
label span { color:#8b949e !important; font-size:12px !important; font-weight:500 !important; }

/* Example buttons */
.ex-btn { background:#1c2128 !important; border:1px solid #30363d !important;
  color:#c9d1d9 !important; border-radius:8px !important;
  padding:8px 12px !important; font-size:12px !important;
  text-align:left !important; width:100% !important;
  margin-bottom:5px !important; transition:all .18s !important; }
.ex-btn:hover { border-color:#388bfd !important; background:#1f2d3d !important; transform:translateX(3px) !important; }

/* Run button */
.run-btn { background:linear-gradient(135deg,#1f4e8c,#388bfd) !important;
  border:none !important; color:#fff !important; font-weight:700 !important;
  font-size:15px !important; border-radius:10px !important;
  padding:14px !important; width:100% !important;
  transition:all .2s !important; margin-top:10px !important; }
.run-btn:hover { transform:translateY(-2px) !important; box-shadow:0 8px 24px rgba(56,139,253,.4) !important; }

/* Stage tracker */
.jr-stages { display:flex; flex-direction:column; gap:8px; }
.jr-stage  { display:flex; align-items:flex-start; gap:12px;
  padding:10px 14px; border-radius:8px; border:1px solid #30363d; transition:all .3s; }
.jr-stage.active  { border-color:#388bfd; background:#1f2d3d; box-shadow:0 0 12px rgba(56,139,253,.15); }
.jr-stage.done    { border-color:#2ea043; background:#0f2217; }
.jr-stage.pending { opacity:.35; }
.jr-icon { font-size:18px; flex-shrink:0; margin-top:2px; }
.jr-stage strong { color:#e6edf3; font-size:13px; }
.jr-desc { color:#8b949e; font-size:11px; margin-top:2px; }

/* Readiness card */
.readiness-card { display:flex; gap:24px; align-items:flex-start;
  background:#161b22; border:1px solid #30363d; border-radius:12px; padding:20px; }
.score-ring { display:flex; flex-direction:column; align-items:center; justify-content:center;
  width:100px; height:100px; border-radius:50%; flex-shrink:0;
  border:4px solid var(--clr,#388bfd);
  background:radial-gradient(circle, #1c2128 60%, transparent 100%); }
.score-num { color:#e6edf3; font-size:24px; font-weight:700; }
.score-lbl { color:#8b949e; font-size:10px; text-align:center; margin-top:2px; }
.score-detail { flex:1; }
.tag-row { font-size:13px; color:#c9d1d9; }
.gap-tag { background:#2d1f1f; color:#f85149; border:1px solid #5a1d1d;
  border-radius:4px; padding:2px 8px; margin:2px; font-size:11px; display:inline-block; }
.have-tag { background:#0f2217; color:#3fb950; border:1px solid #1a4028;
  border-radius:4px; padding:2px 8px; margin:2px; font-size:11px; display:inline-block; }
.apply-now { margin-top:12px; background:#1a2332; border-radius:8px;
  padding:10px 14px; border-left:3px solid #388bfd; }
.apply-now strong { color:#79c0ff; font-size:13px; }
.apply-now ul { margin:6px 0 0 16px; color:#c9d1d9; font-size:12px; }

/* Live log */
.log-box textarea { font-family:'JetBrains Mono',monospace !important;
  font-size:11.5px !important; color:#c9d1d9 !important;
  background:#0d1117 !important; line-height:1.65 !important; }

/* Files table */
.jr-files { width:100%; border-collapse:collapse; font-size:13px; color:#c9d1d9; }
.jr-files th { color:#8b949e; padding:8px 12px; text-align:left; border-bottom:1px solid #30363d; }
.jr-files td { padding:8px 12px; border-bottom:1px solid #21262d; }

/* Report */
.report-md { color:#c9d1d9 !important; }
.report-md h1 { color:#e6edf3 !important; border-bottom:1px solid #30363d; padding-bottom:8px; }
.report-md h2 { color:#79c0ff !important; margin-top:24px; }
.report-md h3 { color:#d2a8ff !important; }
.report-md strong { color:#ffa657 !important; }
.report-md table { border-collapse:collapse; width:100%; }
.report-md th { background:#1c2128; color:#e6edf3; padding:8px 12px; text-align:left; }
.report-md td { padding:8px 12px; border-bottom:1px solid #21262d; }
.report-md code { background:#1c2128; padding:2px 6px; border-radius:4px; color:#7ee787; }
.report-md li { color:#c9d1d9; margin-bottom:4px; }
.report-md blockquote { border-left:3px solid #388bfd; margin-left:0; padding-left:16px; color:#8b949e; }

/* Done banner */
.done-banner { background:linear-gradient(135deg,#0d1a2d,#1a2d4a);
  border:1px solid #388bfd; border-radius:10px; padding:16px 20px;
  color:#79c0ff; font-weight:600; font-size:14px; text-align:center; }

/* Tabs */
.tab-nav button { color:#8b949e !important; font-size:13px !important; }
.tab-nav button.selected { color:#e6edf3 !important; border-bottom:2px solid #388bfd !important; }
"""

HEADER_HTML = """
<div class="jr-header">
  <div class="jr-logo">🎯</div>
  <div>
    <div class="jr-name">JobRadar</div>
    <div class="jr-tag">AI Job Market Intelligence &amp; Career Gap Analyser — Scan the market. Find your gaps. Learn what matters.</div>
  </div>
  <div class="jr-pill">CrewAI · Tavily · GPT-4o</div>
</div>
"""


# ── Gradio Layout ─────────────────────────────────────────────────────────────
with gr.Blocks(title="JobRadar — Career Intelligence") as app:

    gr.HTML(HEADER_HTML)

    with gr.Row(equal_height=False):

        # ── LEFT: Inputs ──────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=340):

            gr.HTML('<div class="jr-label">Your Target Role</div>')
            job_title_inp = gr.Textbox(
                label="Job title you are targeting",
                placeholder="e.g. Python Backend Developer",
            )
            location_inp = gr.Textbox(
                label="Location / Remote preference",
                placeholder="e.g. Remote — Europe   or   London, UK",
                value="Remote — Europe",
            )

            gr.HTML('<div class="jr-label" style="margin-top:16px">Your CV / Skills</div>')
            cv_inp = gr.Textbox(
                label="Paste your CV or skills summary here",
                placeholder=(
                    "Skills: Python, Flask, MySQL, basic Docker...\n"
                    "Projects: built a REST API...\n"
                    "Experience: 6-month internship...\n"
                    "Education: BSc Computer Science..."
                ),
                lines=10,
            )

            gr.HTML('<div class="jr-label" style="margin-top:16px">Quick-start Examples</div>')
            ex_btns = []
            for label in EXAMPLE_CVS:
                btn = gr.Button(f"↗ {label}", elem_classes=["ex-btn"])
                ex_btns.append((btn, label))

            run_btn = gr.Button("🚀  Launch Analysis", elem_classes=["run-btn"])

            done_banner = gr.HTML(
                '<div class="done-banner">✅ Analysis complete — see Roadmap tab</div>',
                visible=False,
            )

        # ── RIGHT: Outputs ────────────────────────────────────────────────
        with gr.Column(scale=2):

            gr.HTML('<div class="jr-label">Pipeline Progress</div>')
            stage_tracker = gr.HTML(stage_html(-1))

            gr.HTML('<div style="height:10px"></div>')

            with gr.Tabs():

                with gr.Tab("📡 Live Agent Log"):
                    log_box = gr.Textbox(
                        label="",
                        lines=22,
                        max_lines=22,
                        autoscroll=True,
                        interactive=False,
                        elem_classes=["log-box"],
                        placeholder="Agent output will stream here once you launch the analysis…",
                    )

                with gr.Tab("📊 Readiness Score"):
                    readiness_card = gr.HTML(
                        '<p style="color:#8b949e;padding:20px">Your market readiness score will appear here after the Gap Advisor completes.</p>'
                    )

                with gr.Tab("📋 90-Day Roadmap"):
                    report_out = gr.Markdown(
                        value="*Your personalised learning roadmap will appear here after the analysis completes.*",
                        elem_classes=["report-md"],
                    )

                with gr.Tab("📁 Output Files"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            files_out = gr.HTML(
                                '<p style="color:#8b949e;font-size:13px">Run an analysis to generate output files.</p>'
                            )
                            file_picker = gr.Dropdown(
                                label="Select file to inspect",
                                choices=get_file_choices(),
                                value=None,
                                interactive=True,
                            )
                        with gr.Column(scale=2):
                            file_info   = gr.HTML("")
                            file_viewer = gr.Code(
                                label="",
                                language="json",
                                lines=20,
                                interactive=False,
                                value="",
                            )

    # Wire example buttons
    for btn, label in ex_btns:
        jt, loc, cv = EXAMPLE_CVS[label]
        btn.click(
            fn=lambda j=jt, l=loc, c=cv: (j, l, c),
            outputs=[job_title_inp, location_inp, cv_inp],
        )

    # Wire file picker
    def on_file_pick(filename):
        text, lang, info = load_file_content(filename)
        return gr.update(value=text, language=lang), info

    file_picker.change(
        fn=on_file_pick,
        inputs=[file_picker],
        outputs=[file_viewer, file_info],
    )

    # Wire Run button
    run_btn.click(
        fn=run_analysis,
        inputs=[job_title_inp, location_inp, cv_inp],
        outputs=[
            log_box,
            stage_tracker,
            readiness_card,
            report_out,
            files_out,
            file_picker,
            done_banner,
        ],
    )


if __name__ == "__main__":
    app.launch(inbrowser=True, show_error=True, css=CSS)
