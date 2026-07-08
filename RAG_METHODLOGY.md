# RAG (Red/Amber/Green) Methodology — Project Health Reporting

This document defines how the agent assigns **RAG** status for a project based on signals extracted from a project plan.

## 1) Signals and how they map to RAG

For each signal, the agent computes a category status:
- **Green (Healthy):** meets/close to target
- **Amber (Watch):** deteriorating / below target but not critical
- **Red (At risk):** meaningfully off target / likely to impact delivery

Thresholds below are configured in `config/rag_thresholds.py` and applied as described.

### A. Schedule slippage
**What we look for:** planned vs actual dates (or forecast), expressed as % or days of slippage.

- **Green:** slippage ≤ `schedule.green` (days)
- **Amber:** `schedule.green` < slippage ≤ `schedule.amber` (days)
- **Red:** slippage > `schedule.amber` (days)

### B. Budget burn
**What we look for:** budget used vs time elapsed (burn rate), or remaining budget trend.

- **Green:** budget burn % ≤ `budget.green`
- **Amber:** `budget.green` < budget burn % ≤ `budget.amber`
- **Red:** budget burn % > `budget.amber`

> If only “spent” and “total budget” are present (no time elapsed), the agent uses an *approximation*: `burn% = spent/total * 100`.

### C. Milestone health
**What we look for:** milestones completed %, milestone due dates, or milestone on-time rate.

- **Green:** completion % ≥ `milestone_completion.green`
- **Amber:** `milestone_completion.amber` ≤ completion % < `milestone_completion.green`
- **Red:** completion % < `milestone_completion.amber`

If milestone dates are present but completion % is missing, the agent estimates completion from status fields (e.g., done/in-progress/not started).

### D. Blockers
**What we look for:** number of active blockers, critical blockers, or unresolved issues.

- **Green:** active blockers ≤ `blockers.green`
- **Amber:** `blockers.green` < active blockers ≤ `blockers.amber`
- **Red:** active blockers > `blockers.amber`

> If severity labels exist (high/medium/low), the agent counts only high-severity blockers toward the threshold and reports both values in the reasoning.

### E. Stakeholder sentiment
**What we look for:** sentiment from notes (positive/negative), explicit risk ratings, or a stakeholder feedback score.

- **Green:** sentiment score ≥ `stakeholder_sentiment.green`
- **Amber:** `stakeholder_sentiment.amber` ≤ sentiment score < `stakeholder_sentiment.green`
- **Red:** sentiment score < `stakeholder_sentiment.amber`

If sentiment is not available, the agent outputs **“unknown”** sentiment and excludes it from the overall RAG calculation (details in section 3).

## 2) Overall RAG status

The agent computes per-category RAG and then derives an overall RAG.

**Default rule (pessimistic):**
- Overall is **Red** if any *critical* category is Red.
- Otherwise, Overall is the worst of the categories that are available.

**Critical categories (configurable assumption):**
- Schedule slippage = critical
- Budget burn = critical
- Milestone health = critical

**Non-critical categories:**
- Blockers and Stakeholder sentiment can override if they are Red *and* at least one critical category is Amber/Red.

This prevents a single missing/unreliable signal from forcing the overall status.

## 3) Handling incomplete or messy data

The agent is designed to be robust to missing or malformed inputs.

- If a category’s inputs are missing/unparseable, the agent marks it **“missing”** and sets its category confidence to low.
- If **all** critical categories are missing, overall RAG becomes **Amber (insufficient data)**, and reasoning lists what was not found.
- If the input contains conflicting values (e.g., multiple budgets), the agent picks the most recent timestamp or the maximum of “forecast” style fields.

## 4) Output contract (what the agent will produce)

For each project, the agent outputs:
- per-category RAG (schedule/budget/milestones/blockers/sentiment)
- overall RAG
- plain-English explanation referencing extracted evidence
- confidence per category and an overall “data sufficiency” note

