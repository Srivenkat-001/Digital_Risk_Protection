"""
Detection package exports.
"""

from detection.apps import extract_app_signals
from detection.explanations import generate_risk_explanation
from detection.logo_similarity import (
    compute_dhash,
    compute_hash_distance,
    compute_logo_similarity,
)
from detection.name_similarity import (
    compute_handle_similarity,
    compute_name_similarity,
    de_leet,
)
from detection.normalization import (
    extract_domain,
    normalize_handle,
    normalize_package_id,
    normalize_text,
    normalize_url,
)
from detection.official_asset_match import (
    check_app_official_exclusion,
    check_social_official_exclusion,
)
from detection.scoring import ENGINE_VERSION, compute_risk_score
from detection.social import extract_social_signals
from detection.text_similarity import (
    compute_text_similarity,
    detect_scam_intent,
)

__all__ = [
    "ENGINE_VERSION",
    "check_app_official_exclusion",
    "check_social_official_exclusion",
    "compute_dhash",
    "compute_handle_similarity",
    "compute_hash_distance",
    "compute_logo_similarity",
    "compute_name_similarity",
    "compute_risk_score",
    "compute_text_similarity",
    "de_leet",
    "detect_scam_intent",
    "extract_app_signals",
    "extract_domain",
    "extract_social_signals",
    "generate_risk_explanation",
    "normalize_handle",
    "normalize_package_id",
    "normalize_text",
    "normalize_url",
]
