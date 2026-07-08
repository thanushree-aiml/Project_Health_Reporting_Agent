# TODO - Project Health Reporting Agent

## Step 1: Dependencies
- [x] Fix `requirements.txt` (was empty)
- [ ] `pip install -r requirements.txt`
- [x] Create initial agent modules + RAG methodology + README
- [x] Implement weekly agent (signal extraction, scoring, plain-English + JSON/MD outputs)
- [x] Implement monthly synthesis (trend + PPTX + JSON summary)



## Step 2: Repo structure
- [ ] Create packages/directories: `agent/`, `scripts/`, `data/input/`, `data/output/`, `reports/`, `logs/`

## Step 3: Phase 1 - RAG methodology
- [ ] Create `RAG_METHODLOGY.md` (one-page mapping + assumptions)

## Step 4: Phase 2 - Weekly agent
- [ ] Implement `agent/signal_extractor.py` (parse project plan and extract signals)
- [ ] Implement `agent/rag_scorer.py` (map signals to RAG per category + overall)
- [ ] Implement `agent/weekly_reporter.py` (orchestrate IO + produce weekly JSON/MD)

## Step 5: Sample inputs + weekly outputs
- [ ] Add `scripts/generate_samples.py` to create sample project plans (JSON) under `data/input/`

## Step 6: Phase 3 - Monthly synthesis
- [ ] Implement `agent/monthly_synthesizer.py` (trend detection + exec insights)
- [ ] Generate PPTX via `python-pptx`

## Step 7: Documentation
- [ ] Add `README.md` with run instructions and design decisions
- [ ] Add example output files

