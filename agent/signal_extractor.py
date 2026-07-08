from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class ExtractedSignals:
    project_name: str
    schedule_slippage_days: Optional[float] = None
    budget_burn_percent: Optional[float] = None
    milestone_completion_percent: Optional[float] = None
    active_blockers_count: Optional[int] = None
    stakeholder_sentiment_score: Optional[float] = None

    # Evidence for reasoning
    evidence: Dict[str, str] = None
    raw: Dict[str, Any] = None

    def as_dict(self) -> Dict[str, Any]:
        d = {
            "project_name": self.project_name,
            "schedule_slippage_days": self.schedule_slippage_days,
            "budget_burn_percent": self.budget_burn_percent,
            "milestone_completion_percent": self.milestone_completion_percent,
            "active_blockers_count": self.active_blockers_count,
            "stakeholder_sentiment_score": self.stakeholder_sentiment_score,
            "evidence": self.evidence or {},
            "raw": self.raw or {},
        }
        return d


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None


def _detect_project_name(payload: Dict[str, Any], fallback: str) -> str:
    for k in ["project_name", "name", "project"]:
        if k in payload and isinstance(payload[k], str) and payload[k].strip():
            return payload[k].strip()
    return fallback


def extract_signals(input_path: str, project_name_override: Optional[str] = None) -> ExtractedSignals:
    """Extracts health signals from a project plan file.

    Supported formats (Phase 2 MVP):
    - JSON with keys like: schedule_slippage_days, budget_burn_percent, milestone_completion_percent,
      active_blockers_count, stakeholder_sentiment_score
    - JSON with nested structures (best-effort heuristics)
    - Plain text: uses regex heuristics for numbers + keywords

    If a field can't be found, it will be None.
    """

    ext = os.path.splitext(input_path)[1].lower()
    base_name = os.path.basename(input_path)

    evidence: Dict[str, str] = {}

    if ext == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        pname = project_name_override or _detect_project_name(payload, base_name)

        def pick(d: Dict[str, Any], candidates: Tuple[str, ...]) -> Any:
            for c in candidates:
                if c in d:
                    return d[c]
            return None

        # Try direct keys
        schedule = pick(payload, ("schedule_slippage_days", "slippage_days", "schedule_slippage"))
        budget = pick(payload, ("budget_burn_percent", "burn_percent", "budget_burn"))
        milestone = pick(payload, ("milestone_completion_percent", "milestone_completion", "completion_percent"))
        blockers = pick(payload, ("active_blockers_count", "blockers", "active_blockers"))
        sentiment = pick(payload, ("stakeholder_sentiment_score", "sentiment_score", "stakeholder_sentiment"))

        # Nested heuristics
        if schedule is None and isinstance(payload.get("schedule"), dict):
            schedule = payload["schedule"].get("slippage_days") or payload["schedule"].get("slippage")
        if budget is None and isinstance(payload.get("budget"), dict):
            budget = payload["budget"].get("burn_percent") or payload["budget"].get("burn")
        if milestone is None and isinstance(payload.get("milestones"), dict):
            milestone = payload["milestones"].get("completion_percent")
        if blockers is None and isinstance(payload.get("blockers"), dict):
            blockers = payload["blockers"].get("active") or payload["blockers"].get("count")
        if sentiment is None and isinstance(payload.get("sentiment"), dict):
            sentiment = payload["sentiment"].get("score")

        sch_f = _safe_float(schedule)
        bud_f = _safe_float(budget)
        mil_f = _safe_float(milestone)
        blk_i = _safe_int(blockers)
        sen_f = _safe_float(sentiment)

        if schedule is not None:
            evidence["schedule_slippage_days"] = str(schedule)
        if budget is not None:
            evidence["budget_burn_percent"] = str(budget)
        if milestone is not None:
            evidence["milestone_completion_percent"] = str(milestone)
        if blockers is not None:
            evidence["active_blockers_count"] = str(blockers)
        if sentiment is not None:
            evidence["stakeholder_sentiment_score"] = str(sentiment)

        return ExtractedSignals(
            project_name=pname,
            schedule_slippage_days=sch_f,
            budget_burn_percent=bud_f,
            milestone_completion_percent=mil_f,
            active_blockers_count=blk_i,
            stakeholder_sentiment_score=sen_f,
            evidence=evidence,
            raw=payload,
        )

    # fallback: plain text
    if ext in (".txt", ".md"):
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        pname = project_name_override or os.path.splitext(base_name)[0]

        # Heuristic patterns
        # e.g. "Schedule slippage: 12 days"
        def find_number(pattern: str) -> Optional[float]:
            m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if not m:
                return None
            return _safe_float(m.group(1))

        schedule = find_number(r"schedule\s+slippage\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:days|day)?")
        if schedule is not None:
            evidence["schedule_slippage_days"] = str(schedule)

        budget = find_number(r"budget\s+burn\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*%?")
        if budget is not None:
            evidence["budget_burn_percent"] = str(budget)

        milestone = find_number(r"milestone\s+completion\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*%?")
        if milestone is not None:
            evidence["milestone_completion_percent"] = str(milestone)

        blockers_f = find_number(r"blockers\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)")
        blockers_i = None if blockers_f is None else int(blockers_f)
        if blockers_i is not None:
            evidence["active_blockers_count"] = str(blockers_i)

        sentiment = find_number(r"sentiment\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)")
        if sentiment is not None:
            evidence["stakeholder_sentiment_score"] = str(sentiment)

        return ExtractedSignals(
            project_name=pname,
            schedule_slippage_days=schedule,
            budget_burn_percent=budget,
            milestone_completion_percent=milestone,
            active_blockers_count=blockers_i,
            stakeholder_sentiment_score=sentiment,
            evidence=evidence,
            raw={"text_source": input_path},
        )

    raise ValueError(f"Unsupported input format for {input_path}. Use .json or .txt/.md")

