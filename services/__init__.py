"""Lazy service exports to avoid importing the entire application on package load."""

from importlib import import_module

_EXPORTS = {
    "AuditService": "services.audit_service",
    "AuthService": "services.auth",
    "BrandService": "services.brand_service",
    "CaseService": "services.case_service",
    "DashboardService": "services.dashboard_service",
    "FindingService": "services.finding_service",
    "hash_password": "services.auth",
    "verify_password": "services.auth",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module_name), name)
