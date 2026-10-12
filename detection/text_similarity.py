"""
Description, bio, and scam intent text analysis.
"""

from rapidfuzz import fuzz

from detection.normalization import normalize_text

PHISHING_INTENT_PATTERNS = [
    # Support impersonation patterns
    "customer support", "customer care", "help desk", "helpline", "toll free",
    "tollfree", "whatsapp support", "contact support", "dm for help", "dm us",
    "complaint resolution", "support team", "support agent",
    # Phishing / credential theft triggers
    "verify your account", "kyc verification", "account suspended", "unlock account",
    "restore access", "send seed phrase", "wallet connect", "reset password",
    "claim bonus", "free reward", "giveaway", "airdrop", "refund claims",
    # Loan & financial scam triggers
    "instant loan", "fast cash", "no credit check", "guaranteed approval",
    "send payment to", "transfer money", "activation fee"
]

def compute_text_similarity(candidate_text: str, brand_description: str) -> float:
    """Computes semantic overlap between candidate text and official brand description."""
    if not candidate_text or not brand_description:
        return 0.0
    c_norm = normalize_text(candidate_text)
    b_norm = normalize_text(brand_description)
    if not c_norm or not b_norm:
        return 0.0
    token_set = fuzz.token_set_ratio(c_norm, b_norm) / 100.0
    return round(token_set, 3)

def detect_scam_intent(text: str) -> tuple[float, list[str]]:
    """
    Scans text for known social engineering, fake support, and scam keywords.
    Returns (intent_score: 0.0 to 1.0, matched_keywords: list).
    """
    if not text:
        return 0.0, []
    norm = normalize_text(text)
    matches = []
    for pattern in PHISHING_INTENT_PATTERNS:
        if pattern in norm:
            matches.append(pattern)

    if not matches:
        return 0.0, []

    # Score escalates with multiple suspicious triggers
    score = min(1.0, 0.4 + (len(matches) * 0.2))
    return round(score, 3), matches
