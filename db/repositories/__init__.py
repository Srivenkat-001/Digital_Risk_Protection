"""Lazy repository exports to keep package imports side-effect free."""

from importlib import import_module

_EXPORTS = {
    "AuditRepository": "db.repositories.audit_repo",
    "BrandRepository": "db.repositories.brand_repo",
    "CandidateRepository": "db.repositories.candidate_repo",
    "FindingRepository": "db.repositories.finding_repo",
    "InvestigationRepository": "db.repositories.investigation_repo",
    "ScanRepository": "db.repositories.scan_repo",
    "UserRepository": "db.repositories.user_repo",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module_name), name)
