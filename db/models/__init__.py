"""Lazy SQLAlchemy model exports and thread-safe model registration."""

from importlib import import_module
from threading import Lock

_MODEL_MODULES = (
    "db.models.organization",
    "db.models.user",
    "db.models.brand",
    "db.models.asset",
    "db.models.candidate",
    "db.models.scan",
    "db.models.finding",
    "db.models.investigation",
    "db.models.audit",
)
_EXPORTS = {
    "AuditLog": "db.models.audit",
    "Brand": "db.models.brand",
    "BrandAlias": "db.models.brand",
    "BrandDomain": "db.models.brand",
    "BrandLogo": "db.models.brand",
    "CandidateAppListing": "db.models.candidate",
    "CandidateObservation": "db.models.candidate",
    "CandidateProfile": "db.models.candidate",
    "DetectionSignal": "db.models.finding",
    "Evidence": "db.models.finding",
    "Finding": "db.models.finding",
    "Investigation": "db.models.investigation",
    "InvestigationNote": "db.models.investigation",
    "Membership": "db.models.organization",
    "OfficialAppListing": "db.models.asset",
    "OfficialSocialAccount": "db.models.asset",
    "Organization": "db.models.organization",
    "RiskAssessment": "db.models.finding",
    "ScanJob": "db.models.scan",
    "SourceConfig": "db.models.scan",
    "User": "db.models.user",
}
_model_load_lock = Lock()
__all__ = [
    "AuditLog",
    "Brand",
    "BrandAlias",
    "BrandDomain",
    "BrandLogo",
    "CandidateAppListing",
    "CandidateObservation",
    "CandidateProfile",
    "DetectionSignal",
    "Evidence",
    "Finding",
    "Investigation",
    "InvestigationNote",
    "Membership",
    "OfficialAppListing",
    "OfficialSocialAccount",
    "Organization",
    "RiskAssessment",
    "ScanJob",
    "SourceConfig",
    "User",
    "load_models",
]


def load_models() -> None:
    """Import all mapped classes before metadata inspection or table creation."""
    with _model_load_lock:
        for module_name in _MODEL_MODULES:
            import_module(module_name)


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module_name), name)
