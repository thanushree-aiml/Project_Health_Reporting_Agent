from __future__ import annotations

import glob
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from rich.console import Console
from tabulate import tabulate

from config.settings import OUTPUT_FOLDER, REPORT_FOLDER

from agent.rag_scorer import score_rag
from agent.signal_extractor import extract_signals

console = Console()


def _rag_to_label(rag: str) -> str:
    return {"green": "Healthy", "amber": "Watch", "red": "At risk", "missing": "Missing"}.get(rag, rag)


def _build_plain_english(signals: Dict[str, Any], scored: Dict[str, Any]) -> Dict[str, Any]:
    per = scored["per_category"]

    def line(cat_key: str, display: str) -> str:
        r = per[cat_key]
        rag = r["rag"]
        if rag == "missing":
            return f"{display}: no usable data found (confidence: {r['confidence']})."
        return f"{display}: { _rag_to_label(rag)} ({r['threshold_note']}). Evidence: {r['evidence'] or 'N/A'}."

    reasoning = [
        line("schedule", "Schedule"),
        line("budget", "Budget burn"),
        line("milestones", "Milestone health"),
        line("blockers", "Blockers"),
        line("stakeholder_sentiment", "Stakeholder sentiment"),
    ]

    overall = scored["overall_rag"]

    if overall == "green":
        summary = "Overall status is Healthy: project indicators are within thresholds."
    elif overall == "amber":
        summary = "Overall status is Watch: some indicators are deteriorating and need attention."
    else:
        summary = "Overall status is At risk: critical indicators breach thresholds and may impact delivery."

    return {
        "summary": summary,
        "reasoning": reasoning,
        "overall_rag": overall,
        "data_sufficiency": scored.get("data_sufficiency"),
    }


def run_weekly(input_path: str, project_name: Optional[str] = None) -> None:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    signals = extract_signals(input_path=input_path, project_name_override=project_name)
    scored = score_rag(signals.as_dict())
    plain = _build_plain_english(signals.as_dict(), scored)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "input_path": input_path,
        "signals": signals.as_dict(),
        "rag": scored,
        "narrative": plain,
    }

    project_slug = signals.project_name.replace(" ", "_").lower()
    out_json = os.path.join(OUTPUT_FOLDER, f"{project_slug}_weekly.json")
    out_md = os.path.join(OUTPUT_FOLDER, f"{project_slug}_weekly.md")

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Markdown output
    md_lines = [
        f"# Weekly Project Health — {signals.project_name}",
        "",
        f"**Overall RAG:** {plain['overall_rag'].upper()} ({plain['summary']})",
        f"**Data sufficiency:** {plain.get('data_sufficiency')}",
        "",
        "## Category details",
    ]

    table_rows = []
    for k, display in [
        ("schedule", "Schedule"),
        ("budget", "Budget burn"),
        ("milestones", "Milestone health"),
        ("blockers", "Blockers"),
        ("stakeholder_sentiment", "Stakeholder sentiment"),
    ]:
        r = scored["per_category"][k]
        table_rows.append([display, r["rag"], r["threshold_note"], r.get("evidence", "")])

    md_lines.append(tabulate(table_rows, headers=["Category", "RAG", "Threshold note", "Evidence"], tablefmt="github"))
    md_lines.append("\n## Reasoning (plain English)\n")
    md_lines.extend([f"- {s}" for s in plain["reasoning"]])

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    console.print(f"Weekly report written:", style="bold")
    console.print(f"- {out_json}", style="green")
    console.print(f"- {out_md}", style="green")

