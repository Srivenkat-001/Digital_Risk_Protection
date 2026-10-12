"""
Unit tests for explainable risk scoring engine and explanations.
"""

import pytest

from detection.explanations import generate_risk_explanation
from detection.scoring import compute_risk_score


def test_risk_scoring_high_threat():
    signals = {
        "name_similarity": {"value": 1.0, "weight": 0.25, "available": True, "rationale": "Exact match"},
        "username_similarity": {"value": 0.95, "weight": 0.25, "available": True, "rationale": "High similarity"},
        "fake_support_affix": {"value": 1.0, "weight": 0.20, "available": True, "rationale": "Support affix"},
        "logo_similarity": {"value": 1.0, "weight": 0.20, "available": True, "rationale": "Logo match"},
        "scam_intent": {"value": 0.8, "weight": 0.25, "available": True, "rationale": "Phishing keywords"},
    }
    score, severity, coverage, enriched = compute_risk_score(signals)
    assert score >= 80.0
    assert severity in ("High", "Critical")
    assert coverage == 1.0

def test_risk_scoring_missing_data_not_penalized():
    # If logo and bio are missing, coverage should reflect it, and score should normalize across available signals only
    signals = {
        "name_similarity": {"value": 0.8, "weight": 0.25, "available": True, "rationale": "Name match"},
        "username_similarity": {"value": 0.7, "weight": 0.25, "available": True, "rationale": "Username match"},
        "logo_similarity": {"value": 0.0, "weight": 0.20, "available": False, "rationale": "Image missing"},
        "bio_similarity": {"value": 0.0, "weight": 0.10, "available": False, "rationale": "Bio missing"},
    }
    score, severity, coverage, enriched = compute_risk_score(signals)
    assert coverage == 0.5
    # (0.8*0.25 + 0.7*0.25) / (0.25 + 0.25) = 0.375 / 0.5 = 0.75 -> 75.0
    assert score == 75.0

def test_explanation_generation():
    signals = {
        "name_similarity": {"value": 0.9, "weight": 0.25, "contribution": 0.225, "available": True, "rationale": "Name match"},
        "logo_similarity": {"value": 0.0, "weight": 0.20, "contribution": 0.0, "available": False, "rationale": "Logo unavailable"},
    }
    explanation = generate_risk_explanation(
        score=75.0,
        severity="High",
        coverage=0.5,
        enriched_signals=signals,
        candidate_type="social",
        brand_name="NovaPay",
    )
    assert "Risk Assessment: High" in explanation
    assert "Key Risk Drivers" in explanation
    assert "Evidence Gaps & Limitations" in explanation
    assert "Analyst Advisory" in explanation


@pytest.mark.parametrize("value", [-0.01, 1.01, float("nan"), float("inf")])
def test_risk_scoring_rejects_invalid_signal_values(value):
    with pytest.raises(ValueError, match="value must be finite"):
        compute_risk_score({"invalid": {"value": value, "weight": 1.0}})


def test_risk_scoring_rejects_negative_weights():
    with pytest.raises(ValueError, match="weight must be finite and non-negative"):
        compute_risk_score({"invalid": {"value": 0.5, "weight": -0.1}})


def test_risk_scoring_rejects_non_boolean_availability():
    with pytest.raises(TypeError, match="availability must be a boolean"):
        compute_risk_score({"invalid": {"value": 0.5, "weight": 1.0, "available": "false"}})
