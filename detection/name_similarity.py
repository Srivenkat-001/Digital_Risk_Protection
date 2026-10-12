"""
Name and username similarity analysis.
Combines RapidFuzz string metrics, character substitution/leetspeak detection,
and affix/brand impersonation heuristic matching.
"""

from typing import Any

from rapidfuzz import fuzz

from detection.normalization import normalize_handle, normalize_text

# Common character substitutions used in phishing/impersonation handles
LEET_MAP = {
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "@": "a",
    "$": "s",
    "5": "s",
    "7": "t",
    "8": "b",
}


# Suspicious keywords frequently appended to brand names for fake support/phishing
SUSPICIOUS_AFFIXES = [
    "support", "help", "desk", "care", "customercare", "service", "services",
    "official", "real", "verified", "auth", "security", "team", "bot",
    "login", "verify", "pay", "payment", "claims", "refund", "assist", "center"
]

def de_leet(text: str) -> str:
    """Replaces leetspeak character substitutions with their canonical alphabetical equivalents."""
    cleaned = text.lower()
    # multi-char replacements
    cleaned = cleaned.replace("rn", "m").replace("vv", "w")
    for char, replacement in LEET_MAP.items():
        cleaned = cleaned.replace(char, replacement)
    return cleaned

def compute_name_similarity(
    candidate_name: str,
    brand_name: str,
    aliases: list[str] | None = None
) -> tuple[float, dict[str, Any]]:
    """
    Computes name similarity score (0.0 to 1.0) and detailed diagnostic metrics.
    Compares against brand name and known aliases.
    """
    norm_candidate = normalize_text(candidate_name)
    norm_brand = normalize_text(brand_name)
    targets = [norm_brand] + [normalize_text(a) for a in (aliases or []) if a]

    best_score = 0.0
    best_target = norm_brand
    details = {}

    for target in targets:
        if not target:
            continue
        
        # Exact match
        if norm_candidate == target:
            return 1.0, {
                "matched_target": target,
                "ratio": 1.0,
                "partial_ratio": 1.0,
                "token_sort_ratio": 1.0,
                "de_leet_match": False,
                "exact_match": True,
            }

        # RapidFuzz metrics
        ratio = fuzz.ratio(norm_candidate, target) / 100.0
        partial = fuzz.partial_ratio(norm_candidate, target) / 100.0
        token_sort = fuzz.token_sort_ratio(norm_candidate, target) / 100.0

        # De-leeted similarity
        candidate_deleet = de_leet(norm_candidate)
        target_deleet = de_leet(target)
        deleet_ratio = fuzz.ratio(candidate_deleet, target_deleet) / 100.0
        deleet_flag = (candidate_deleet != norm_candidate) and (deleet_ratio > ratio)

        combined = max(ratio, token_sort * 0.9, deleet_ratio)
        if combined > best_score:
            best_score = combined
            best_target = target
            details = {
                "matched_target": target,
                "ratio": round(ratio, 3),
                "partial_ratio": round(partial, 3),
                "token_sort_ratio": round(token_sort, 3),
                "de_leet_match": deleet_flag,
                "de_leet_score": round(deleet_ratio, 3),
                "exact_match": False,
            }

    return round(best_score, 3), details

def compute_handle_similarity(
    candidate_handle: str,
    brand_name: str,
    official_handle: str | None = None,
    aliases: list[str] | None = None
) -> tuple[float, dict[str, Any]]:
    """
    Computes handle/username similarity, detects affixes (e.g. novapay_support),
    and identifies leetspeak impersonation (e.g. n0vapay).
    """
    c_handle = normalize_handle(candidate_handle)
    b_name = normalize_handle(brand_name)
    off_handle = normalize_handle(official_handle) if official_handle else None

    # De-leet candidate handle
    c_deleet = de_leet(c_handle)

    targets = [b_name]
    if off_handle:
        targets.append(off_handle)
    if aliases:
        targets.extend([normalize_handle(a) for a in aliases if a])

    best_similarity = 0.0
    has_suspicious_affix = False
    detected_affixes = []
    has_leetspeak = False

    # Check for suspicious affixes
    for affix in SUSPICIOUS_AFFIXES:
        if affix in c_handle or affix in c_deleet:
            # Check if brand is also in handle
            if b_name in c_handle or b_name in c_deleet:
                has_suspicious_affix = True
                detected_affixes.append(affix)

    # Check if candidate has character substitution compared to brand
    if c_handle != c_deleet and b_name in c_deleet:
        has_leetspeak = True

    for target in targets:
        if not target:
            continue
        # Standard ratio
        r = fuzz.ratio(c_handle, target) / 100.0
        # Partial ratio
        pr = fuzz.partial_ratio(c_handle, target) / 100.0
        # De-leet ratio
        dlr = fuzz.ratio(c_deleet, target) / 100.0

        score = max(r, dlr)
        if has_suspicious_affix:
            # If target brand is in the handle along with support affix, similarity is high impersonation risk
            score = max(score, 0.85)
        elif pr >= 0.9 and len(c_handle) > len(target):
            score = max(score, 0.75)

        best_similarity = max(best_similarity, score)

    details = {
        "candidate_handle": c_handle,
        "de_leeted_handle": c_deleet,
        "has_leetspeak": has_leetspeak,
        "has_suspicious_affix": has_suspicious_affix,
        "detected_affixes": detected_affixes,
        "raw_similarity": round(best_similarity, 3),
    }

    return round(min(best_similarity, 1.0), 3), details
