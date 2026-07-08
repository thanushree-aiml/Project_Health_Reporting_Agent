# Project Health Reporting Agent

Automated project health reporting that assigns **RAG (Red/Amber/Green)** with plain-English reasoning, plus optional monthly executive synthesis.

## Setup

1) Create a virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2) Configure environment variables:

Create a `.env` file in the repo root:

```bash
GEMINI_API_KEY=your_key_here
```

## Run weekly

```bash
python main.py weekly --input data/input/<project_plan.json> --project-name "Optional Name"
```

## Run monthly synthesis

```bash
python main.py monthly --inputs "data/output/*_weekly.json" --output monthly_executive_presentation.pptx
```

## Project structure (planned)
- `agent/`: core logic (extraction, scoring, reporting)
- `data/input/`: project plans
- `data/output/`: weekly JSON/MD outputs
- `reports/`: generated PPTX
- `logs/`: runtime logs

