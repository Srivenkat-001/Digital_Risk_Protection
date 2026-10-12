"""
Unit tests for text, handle, leetspeak, and phishing intent detection.
"""

from detection.name_similarity import (
    compute_handle_similarity,
    compute_name_similarity,
    de_leet,
)
from detection.text_similarity import detect_scam_intent


def test_de_leet():
    assert de_leet("n0vapay") == "novapay"
    assert de_leet("n1ght") == "nlght"
    assert de_leet("p4y") == "pay"

def test_name_similarity_exact():
    score, details = compute_name_similarity("NovaPay", "NovaPay")
    assert score == 1.0
    assert details["exact_match"] is True

def test_name_similarity_with_alias():
    score, details = compute_name_similarity("Nova Payment", "NovaPay", aliases=["Nova Payment"])
    assert score == 1.0

def test_handle_similarity_leetspeak():
    score, details = compute_handle_similarity("N0vaPay", "NovaPay")
    assert score >= 0.8
    assert details["has_leetspeak"] is True

def test_handle_similarity_suspicious_affix():
    score, details = compute_handle_similarity("NovaPay_Support", "NovaPay")
    assert score >= 0.85
    assert details["has_suspicious_affix"] is True
    assert "support" in details["detected_affixes"]

def test_unrelated_handle():
    score, details = compute_handle_similarity("SeattlePhotography", "NovaPay")
    assert score < 0.4
    assert details["has_suspicious_affix"] is False

def test_scam_intent_detection():
    text = "Having account issues? Contact customer support or dm for help to unlock account."
    score, matches = detect_scam_intent(text)
    assert score > 0.5
    assert "customer support" in matches
    assert "unlock account" in matches

def test_clean_text_no_scam_intent():
    text = "Landscape photography and wedding portraits based in Seattle."
    score, matches = detect_scam_intent(text)
    assert score == 0.0
    assert len(matches) == 0
