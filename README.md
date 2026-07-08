# Project Health Reporting Agent

Automated project health reporting that assigns **RAG (Red/Amber/Green)** with plain-English reasoning, plus optional monthly executive synthesis.

This repo contains a Python pipeline that:
- Reads project-plan inputs (sample JSON plans in `data/input/`)
- Extracts auditable signals
- Computes an **independent** RAG status (does **not** copy it from the input)
- Generates weekly reports (`data/output/*_weekly.json`, `data/output/*_weekly.md`)
- Synthesizes a monthly executive summary and (when available) a PPTX deck (`reports/`)

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

## Optional: remove generated/unwanted artifacts before committing

To keep Git history clean, you can restore runtime/cache changes:

```bash
git restore --worktree --staged __pycache__ data/output reports
```


