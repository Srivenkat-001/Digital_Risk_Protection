"""Lazy public exports for BrandPhantom's detection utilities."""

from importlib import import_module

_EXPORTS = {
    "ENGINE_VERSION": "detection.scoring",
    "check_app_official_exclusion": "detection.official_asset_match",
    "check_social_official_exclusion": "detection.official_asset_match",
    "compute_dhash": "detection.logo_similarity",
    "compute_handle_similarity": "detection.name_similarity",
    "compute_hash_distance": "detection.logo_similarity",
    "compute_logo_similarity": "detection.logo_similarity",
    "compute_name_similarity": "detection.name_similarity",
    "compute_risk_score": "detection.scoring",
    "compute_text_similarity": "detection.text_similarity",
    "de_leet": "detection.name_similarity",
    "detect_scam_intent": "detection.text_similarity",
    "extract_app_signals": "detection.apps",
    "extract_domain": "detection.normalization",
    "extract_social_signals": "detection.social",
    "generate_risk_explanation": "detection.explanations",
    "normalize_handle": "detection.normalization",
    "normalize_package_id": "detection.normalization",
    "normalize_text": "detection.normalization",
    "normalize_url": "detection.normalization",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module_name), name)
