# Project Health Reporting Agent — Run Commands

This file contains copy-paste commands to run your project end-to-end.

## 0) One-time setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 1) (Optional) Set Gemini API key

If your flow uses `GEMINI_API_KEY`, set it in a repo-root `.env` file:

```bash
echo 'GEMINI_API_KEY=YOUR_KEY_HERE' > .env
```

## 2) Generate weekly report for a single project (JSON input)

```bash
python main.py weekly --input data/input/sample_project_alpha.json --project-name "Alpha"
```

Other samples:

```bash
python main.py weekly --input data/input/sample_project_beta.json --project-name "Beta"
python main.py weekly --input data/input/sample_project_gamma.json --project-name "Gamma"
```

Outputs:
- `data/output/*_weekly.json`
- `data/output/*_weekly.md`

## 3) Monthly synthesis (portfolio executive summary + PPTX)

```bash
python main.py monthly --inputs "data/output/*_weekly.json" --output monthly_executive_presentation.pptx
```

Outputs:
- `reports/monthly_executive_summary.json`
- `reports/monthly_executive_presentation.pptx` (best-effort)

## 4) Validate correctness (recompute weekly + check monthly)

```bash
python main.py validate --inputs "data/input/sample_project_*.json"
```

Expected result:
- `Validation passed`

## 5) Convenience: run everything (weekly for all samples -> monthly -> validate)

```bash
python main.py weekly --input data/input/sample_project_alpha.json --project-name "Alpha"
python main.py weekly --input data/input/sample_project_beta.json --project-name "Beta"
python main.py weekly --input data/input/sample_project_gamma.json --project-name "Gamma"
python main.py monthly --inputs "data/output/*_weekly.json" --output monthly_executive_presentation.pptx
python main.py validate --inputs "data/input/sample_project_*.json"
```

