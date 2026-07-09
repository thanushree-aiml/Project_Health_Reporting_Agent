# Project Health Reporting Agent

An AI-assisted system that reads raw project-plan workbooks, computes an **independent RAG (Red/Amber/Green)** status for each project, explains the status in **plain English**, drafts weekly reports, generates a **monthly executive presentation that finds trends across the portfolio**, and suggests (never sends) follow-up emails for delayed tasks.

Built against the two sample workbooks provided (**Project_Plan_B.xlsx**, **S2P_Project.xlsx**) and designed to generalize to any workbook that follows the same **task-sheet / Comments / Summary** convention.

---

## 1) What it does

| Requirement | Delivered as |
|---|---|
| Read project plans from Excel | `src/excel_parser.py` (repo root: `excel_parser.py`) |
| Determine RAG status (not copied from the sheet) | `src/rag_engine.py` (repo root: `rag_engine.py`) |
| Plain-English reasoning | `src/reasoning.py` (repo root: `reasoning.py`) |
| Handle messy/incomplete data | Built into the parser + engine |
| Weekly reports | `src/report_generator.py` → `outputs/weekly/*.md` / `*.html` |
| Weekly scheduler (bonus) | `src/scheduler.py` (APScheduler, cron: every Monday 07:00) |
| Monthly executive presentation (5–7 slides, trend-focused) | `src/pptx_builder.py` → `outputs/presentation/*.pptx` (pure Python, `python-pptx`) |
| Executive Action Assistant (bonus) | `src/action_assistant.py` — drafts follow-up emails, never sends |
| Dashboard | `src/dashboard.py` (Streamlit, includes a live “Download Executive Presentation” button) |

> Note: In your current workspace, some “src/*” files may be at repo root (e.g., `excel_parser.py`) depending on how the reference port was applied.

---

## 2) Architecture

### Excel workbooks (`.xlsx`)

```text
Excel workbooks (.xlsx)
        │
        ▼
┌─────────────────┐
│ excel_parser.py │  parses: task sheet + Comments + Summary
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ rag_engine.py   │  computes 5 weighted, auditable signals → composite score → RAG
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ reasoning.py    │  deterministic narrative: executive summary, risk explanation,
└─────────────────┘  positives, concerns, recommendations
        │
        ▼
report_generator.py        action_assistant.py
weekly .md/.html           suggested email drafts (never sent)
        │                       │
        ▼                       ▼
persistence: outputs/weekly   outputs/actions/

pptx_builder.py
7-slide executive deck from portfolio_data.json (pure python-pptx)
```

---

## 3) Folder structure

Expected structure (based on the reference design):

```text
project_health_agent/
├── README.md
├── requirements.txt
├── data/                          # sample input workbooks
│   ├── Project_Plan_B.xlsx
│   └── S2P_Project.xlsx
├── docs/
│   └── RAG_Methodology.md
├── src/                           # reference layout
│   ├── excel_parser.py
│   ├── rag_engine.py
│   ├── reasoning.py
│   ├── report_generator.py
│   ├── action_assistant.py
│   ├── pptx_builder.py
│   ├── dashboard.py
│   ├── scheduler.py
│   └── main.py
└── outputs/
    ├── weekly/
    ├── actions/
    ├── presentation/
    └── portfolio_data.json
```

---

## 4) Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Node.js, npm, or other runtime is required for the executive deck: the deck is generated with **python-pptx**, so the agent runs on Python-only hosts.

---

## 5) How to run

### Run the full pipeline (Excel → weekly reports → portfolio_data.json → executive PPTX)

```bash
python src/main.py --input "data/*.xlsx" --out outputs
```

### Run the interactive dashboard

```bash
streamlit run src/dashboard.py
```

### Bonus: weekly scheduler (runs every Monday at 07:00)

```bash
python src/scheduler.py
```

Scheduler environment variables:
- `PHA_INPUT_GLOB` (default: `data/*.xlsx`)
- `PHA_OUTPUT_DIR` (default: `outputs`)

---

## 6) Example outputs (from the two provided workbooks)

The pipeline generates weekly outputs plus an executive deck; weekly reports include both:
- **Computed RAG** (independent from the sheet’s Schedule Health)
- **Plain-English disagreement explanation** when computed status differs from the sheet

---

## 7) Design decisions

### Deterministic scoring instead of an LLM for RAG
RAG status drives governance and client conversations — it must be **reproducible, explainable, auditable**. `rag_engine.py` is pure Python with auditable facts behind every score.

### Template-driven narrative
`reasoning.py` is deterministic and generated from the exact facts the scoring engine computed. This avoids contradictions between prose and score.

### “Suggest emails” (never send)
The Executive Action Assistant drafts follow-up email content for delayed/at-risk tasks, but does not send any email.

### python-pptx only for the deck
The reference version moved off a Node-based generator so that deck creation works on Python-only hosting environments.

---

## 8) Assumptions about the data
- `#UNPARSEABLE`, blank cells, and `NaN` are treated as missing.
- Task sheet auto-detected by process of elimination.
- Variance values follow the observed `-Nd / Nd` convention.
- Missing comments/milestones lower confidence rather than silently inflating risk.

---

## 9) Known limitations / future enhancements
- Template narrative can be swapped for a hosted LLM later by keeping the same interface.
- Trend analysis gets stronger as more monthly history accumulates.
- PDF export can be added by converting the print-friendly HTML.
- Action Assistant can group multiple overdue tasks per owner into a single digest email.

---

## Current workspace note
Your repo currently contains a JSON-based weekly/monthly pipeline (older implementation). The Excel-first modules and orchestration were added from the reference code, but you must ensure the end-to-end CLI wiring exists for `.xlsx` execution.

If you run into import/runtime issues, regenerate and commit the full reference files under the expected paths and update `main.py` accordingly.


---

## What it produces

**Weekly output** for each project plan:
- `<project>_weekly.json` (signals + RAG + confidence + narrative)
- `<project>_weekly.md` (human-readable summary + evidence)

**Monthly output** (across multiple weekly JSONs):
- `reports/monthly_executive_summary.json`
- `reports/monthly_executive_presentation.pptx` (best-effort; depends on `python-pptx` availability)

---

## Setup

1) Create a virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2) (Optional) Configure environment variables

Some flows may reference LLM configuration; create a `.env` file in repo root if required:

```bash
GEMINI_API_KEY=your_key_here
```

---

## Run weekly (RAG report for one project)

```bash
python main.py weekly --input data/input/<project_plan.json> --project-name "Optional Name"
```

Examples (sample inputs):

```bash
python main.py weekly --input data/input/sample_project_alpha.json --project-name "Alpha"
python main.py weekly --input data/input/sample_project_beta.json --project-name "Beta"
python main.py weekly --input data/input/sample_project_gamma.json --project-name "Gamma"
```

Outputs are written to `data/output/`.

---

## Run monthly synthesis (portfolio-level summary + PPTX)

```bash
python main.py monthly --inputs "data/output/*_weekly.json" --output monthly_executive_presentation.pptx
```

Outputs are written to `reports/`.

---

## Validate outputs (deterministic consistency checks)

This recomputes weekly results for the sample inputs and checks that the monthly summary aligns with the loaded weekly JSON outputs.

```bash
python main.py validate --inputs "data/input/sample_project_*.json"
```

---

## Project structure

- `main.py` — CLI entry point (`weekly`, `monthly`, `validate`)
- `agent/` — core logic
  - `signal_extractor.py` — parses inputs and extracts signals
  - `rag_scorer.py` — computes per-category and overall RAG
  - `weekly_reporter.py` — writes weekly JSON + Markdown reports
  - `monthly_synthesizer.py` — writes monthly summary + (optional) PPTX
  - `validator.py` — recomputation/consistency validation
- `config/`
  - `settings.py` — input/output folder configuration
  - `rag_thresholds.py` — RAG thresholds used by the scoring engine
- `data/input/` — sample project inputs (JSON)
- `data/output/` — generated weekly outputs
- `reports/` — generated monthly executive artifacts

---

## RAG methodology

The mapping from extracted signals to **Red/Amber/Green** and the overall roll-up rule are defined in:

- `RAG_METHODLOGY.md`

---

## Deterministic & auditable by design

This project computes RAG **independently** from any “self-reported” workbook status.

Key properties:
- **Reproducible:** the same input yields the same score.
- **Explainable:** each category includes threshold notes and evidence.
- **Robust to missing data:** incomplete inputs reduce category confidence rather than silently producing misleading outputs.

---

## Validation

Run consistency checks that recompute weekly scores from the sample inputs and verify the monthly roll-up:

```bash
python main.py validate --inputs "data/input/sample_project_*.json"
```

---

## Notes on generated files

`data/output/*` and `reports/*` are **generated** artifacts.
- Commit them only if you want to preserve run outputs for a specific scoring version.
- `__pycache__/*.pyc` is runtime cache and should not be committed.

---

