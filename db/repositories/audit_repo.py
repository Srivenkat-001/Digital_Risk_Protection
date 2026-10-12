"""
Repository for Audit Log persistence and security review.
"""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.models.audit import AuditLog


class AuditRepository:
    """Handles persistent audit records for all security events."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        organization_id: str,
        action: str,
        target_type: str,
        target_id: str,
        user_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        details_str = json.dumps(details) if isinstance(details, dict) else (details or None)
        entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action.upper(),
            target_type=target_type.lower(),
            target_id=target_id,
            details=details_str,
            ip_address=ip_address,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_by_org(
        self,
        organization_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.organization_id == organization_id)
            .options(selectinload(AuditLog.user))
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())
