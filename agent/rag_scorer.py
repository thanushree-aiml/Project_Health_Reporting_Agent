from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from config.rag_thresholds import RAG_THRESHOLDS


@dataclass
class CategoryResult:
    rag: str  # green/amber/red/missing
    score: Optional[float]
    threshold_note: str
    confidence: str  # high/medium/low
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rag": self.rag,
            "score": self.score,
            "threshold_note": self.threshold_note,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


def _rag_from_threshold(value: Optional[float], green_t: float, amber_t: float, evidence: str) -> CategoryResult:
    if value is None:
        return CategoryResult(
            rag="missing",
            score=None,
            threshold_note="Input missing/unavailable",
            confidence="low",
            evidence=evidence,
        )

    if value <= green_t:
        return CategoryResult(
            rag="green",
            score=value,
            threshold_note=f"Value {value:.2f} <= green threshold {green_t}",
            confidence="high",
            evidence=evidence,
        )

    if value <= amber_t:
        return CategoryResult(
            rag="amber",
            score=value,
            threshold_note=f"Value {value:.2f} between green {green_t} and amber {amber_t}",
            confidence="high",
            evidence=evidence,
        )

    return CategoryResult(
        rag="red",
        score=value,
        threshold_note=f"Value {value:.2f} > amber threshold {amber_t}",
        confidence="high",
        evidence=evidence,
    )


def score_rag(signals: Dict[str, Any]) -> Dict[str, Any]:
    evidence = signals.get("evidence") or {}

    schedule = _rag_from_threshold(
        value=signals.get("schedule_slippage_days"),
        green_t=RAG_THRESHOLDS["schedule"]["green"],
        amber_t=RAG_THRESHOLDS["schedule"]["amber"],
        evidence=evidence.get("schedule_slippage_days", ""),
    )

    budget = _rag_from_threshold(
        value=signals.get("budget_burn_percent"),
        green_t=RAG_THRESHOLDS["budget"]["green"],
        amber_t=RAG_THRESHOLDS["budget"]["amber"],
        evidence=evidence.get("budget_burn_percent", ""),
    )

    milestone_val = signals.get("milestone_completion_percent")
    # For completion, higher is better. Convert thresholds accordingly.
    if milestone_val is None:
        milestone = CategoryResult(
            rag="missing",
            score=None,
            threshold_note="Input missing/unavailable",
            confidence="low",
            evidence=evidence.get("milestone_completion_percent", ""),
        )
    else:
        green_t = RAG_THRESHOLDS["milestone_completion"]["green"]
        amber_t = RAG_THRESHOLDS["milestone_completion"]["amber"]
        if milestone_val >= green_t:
            milestone = CategoryResult(
                rag="green",
                score=milestone_val,
                threshold_note=f"Completion {milestone_val:.2f}% >= green {green_t}%",
                confidence="high",
                evidence=evidence.get("milestone_completion_percent", ""),
            )
        elif milestone_val >= amber_t:
            milestone = CategoryResult(
                rag="amber",
                score=milestone_val,
                threshold_note=f"Completion {milestone_val:.2f}% between amber {amber_t}% and green {green_t}%",
                confidence="high",
                evidence=evidence.get("milestone_completion_percent", ""),
            )
        else:
            milestone = CategoryResult(
                rag="red",
                score=milestone_val,
                threshold_note=f"Completion {milestone_val:.2f}% < amber {amber_t}%",
                confidence="high",
                evidence=evidence.get("milestone_completion_percent", ""),
            )

    blockers = _rag_from_threshold(
        value=signals.get("active_blockers_count"),
        green_t=RAG_THRESHOLDS["blockers"]["green"],
        amber_t=RAG_THRESHOLDS["blockers"]["amber"],
        evidence=evidence.get("active_blockers_count", ""),
    )

    # Stakeholder sentiment: higher is better (matches RAG_METHODLOGY.md)
    sentiment_val = signals.get("stakeholder_sentiment_score")
    if sentiment_val is None:
        sentiment = CategoryResult(
            rag="missing",
            score=None,
            threshold_note="Input missing/unavailable",
            confidence="low",
            evidence=evidence.get("stakeholder_sentiment_score", ""),
        )
    else:
        green_t = RAG_THRESHOLDS["stakeholder_sentiment"]["green"]
        amber_t = RAG_THRESHOLDS["stakeholder_sentiment"]["amber"]
        if sentiment_val >= green_t:
            sentiment = CategoryResult(
                rag="green",
                score=sentiment_val,
                threshold_note=f"Sentiment {sentiment_val:.2f} >= green {green_t}",
                confidence="high",
                evidence=evidence.get("stakeholder_sentiment_score", ""),
            )
        elif sentiment_val >= amber_t:
            sentiment = CategoryResult(
                rag="amber",
                score=sentiment_val,
                threshold_note=f"Sentiment {sentiment_val:.2f} between amber {amber_t} and green {green_t}",
                confidence="high",
                evidence=evidence.get("stakeholder_sentiment_score", ""),
            )
        else:
            sentiment = CategoryResult(
                rag="red",
                score=sentiment_val,
                threshold_note=f"Sentiment {sentiment_val:.2f} < amber {amber_t}",
                confidence="high",
                evidence=evidence.get("stakeholder_sentiment_score", ""),
            )


    categories = {
        "schedule": schedule,
        "budget": budget,
        "milestones": milestone,
        "blockers": blockers,
        "stakeholder_sentiment": sentiment,
    }

    # Overall rule (based on RAG_METHODLOGY): pessimistic with missing data handling.
    critical = ["schedule", "budget", "milestones"]
    available_critical = [c for c in critical if categories[c].rag != "missing"]

    if not available_critical:
        overall = "amber"
        data_sufficiency = "insufficient critical data; at least one of schedule/budget/milestones must be provided"
    else:
        if any(categories[c].rag == "red" for c in available_critical):
            overall = "red"
        elif any(categories[c].rag == "amber" for c in available_critical):
            overall = "amber"
        else:
            overall = "green"

        data_sufficiency = "critical data available" if len(available_critical) == len(critical) else "some critical signals missing"

    return {
        "per_category": {k: v.to_dict() for k, v in categories.items()},
        "overall_rag": overall,
        "data_sufficiency": data_sufficiency,
    }

