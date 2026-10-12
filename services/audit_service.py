"""
Audit log query service.
"""


from sqlalchemy.orm import Session

from db.models.audit import AuditLog
from db.repositories.audit_repo import AuditRepository


class AuditService:
    """Provides security log inspection for compliance officers and administrators."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)

    def list_logs(self, organization_id: str, limit: int = 100) -> list[AuditLog]:
        return self.repo.list_by_org(organization_id, limit=limit)
