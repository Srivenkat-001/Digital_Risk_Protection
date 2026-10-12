"""
Explainable risk scoring engine.
Combines extracted signals with heuristic weighting, explicitly handles missing signals,
and maps normalized scores into severity categories.
"""

import math
from typing import Any

from config.settings import settings

ENGINE_VERSION = "v1.2.0"

def compute_risk_score(
    signals: dict[str, dict[str, Any]]
) -> tuple[float, str, float, dict[str, dict[str, Any]]]:
    """
    Computes a normalized risk score (0.0 to 100.0) from extracted detection signals.
    
    Returns:
        (risk_score, severity, signal_coverage, enriched_signals)
    
    Explicitly handles missing data:
    Signals where available == False are NOT counted as evidence of malice;
    instead, available weights are dynamically normalized to sum to 1.0.
    """
    total_available_weight = 0.0
    weighted_sum = 0.0
    total_signals = len(signals)
    available_signals = 0

    enriched = {}

    for name, data in signals.items():
        is_available = data.get("available", True)
        try:
            raw_val = float(data.get("value", 0.0))
            base_weight = float(data.get("weight", 0.1))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Signal '{name}' must have numeric value and weight.") from exc
        if not math.isfinite(raw_val) or not 0.0 <= raw_val <= 1.0:
            raise ValueError(f"Signal '{name}' value must be finite and between 0 and 1.")
        if not math.isfinite(base_weight) or base_weight < 0.0:
            raise ValueError(f"Signal '{name}' weight must be finite and non-negative.")
        if not isinstance(is_available, bool):
            raise TypeError(f"Signal '{name}' availability must be a boolean.")

        if is_available:
            available_signals += 1
            total_available_weight += base_weight
            contribution = raw_val * base_weight
            weighted_sum += contribution
        else:
            contribution = 0.0

        enriched[name] = {
            "value": raw_val,
            "weight": base_weight,
            "contribution": round(contribution, 4),
            "available": is_available,
            "rationale": data.get("rationale", ""),
        }

    # Signal coverage fraction
    coverage = (available_signals / total_signals) if total_signals > 0 else 0.0

    # Normalize by total available weight so missing signals don't artificially deflate risk
    if total_available_weight > 0.0:
        normalized_ratio = weighted_sum / total_available_weight
    else:
        normalized_ratio = 0.0

    # Final score scaled from 0.0 to 100.0
    risk_score = round(normalized_ratio * 100.0, 1)

    # Classify severity
    if risk_score >= settings.RISK_THRESHOLD_HIGH:
        # If score is >= 80, distinguish Critical vs High
        if risk_score >= 85.0 or (signals.get("scam_intent", {}).get("value", 0) >= 0.8 and risk_score >= 75.0):
            severity = settings.SEVERITY_CRITICAL
        else:
            severity = settings.SEVERITY_HIGH
    elif risk_score >= settings.RISK_THRESHOLD_MEDIUM:
        severity = settings.SEVERITY_HIGH if risk_score >= 70.0 else settings.SEVERITY_MEDIUM
    elif risk_score >= settings.RISK_THRESHOLD_LOW:
        severity = settings.SEVERITY_MEDIUM if risk_score >= 45.0 else settings.SEVERITY_LOW
    else:
        severity = settings.SEVERITY_LOW

    return risk_score, severity, round(coverage, 2), enriched
