"""
Repository for Investigation cases and analyst notes.
"""

import random
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from db.models.investigation import Investigation, InvestigationNote


class InvestigationRepository:
    """Handles Investigation cases and analyst notes persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, investigation_id: str, organization_id: str | None = None) -> Investigation | None:
        stmt = (
            select(Investigation)
            .where(Investigation.id == investigation_id)
            .options(
                selectinload(Investigation.notes).selectinload(InvestigationNote.author),
                selectinload(Investigation.finding),
                selectinload(Investigation.assigned_to),
            )
        )
        if organization_id:
            stmt = stmt.where(Investigation.organization_id == organization_id)
        return self.db.scalars(stmt).first()

    def get_by_finding_id(self, finding_id: str) -> Investigation | None:
        stmt = (
            select(Investigation)
            .where(Investigation.finding_id == finding_id)
            .options(
                selectinload(Investigation.notes),
                selectinload(Investigation.assigned_to),
            )
        )
        return self.db.scalars(stmt).first()

    def list_by_org(
        self,
        organization_id: str,
        brand_id: str | None = None,
        status: str | None = None,
    ) -> list[Investigation]:
        stmt = (
            select(Investigation)
            .where(Investigation.organization_id == organization_id)
            .options(
                selectinload(Investigation.notes),
                selectinload(Investigation.finding),
                selectinload(Investigation.assigned_to),
            )
            .order_by(Investigation.created_at.desc())
        )
        if brand_id:
            stmt = stmt.where(Investigation.brand_id == brand_id)
        if status:
            stmt = stmt.where(Investigation.status == status)
        return list(self.db.scalars(stmt).all())

    def create_case(
        self,
        organization_id: str,
        brand_id: str,
        finding_id: str,
        title: str,
        priority: str = "medium",
        summary: str | None = None,
        assigned_to_user_id: str | None = None,
    ) -> Investigation:
        # Generate case number e.g. CASE-2026-XXXX
        random_suffix = random.randint(1000, 9999)
        case_num = f"CASE-{datetime.now(timezone.utc).year}-{random_suffix}"

        investigation = Investigation(
            organization_id=organization_id,
            brand_id=brand_id,
            finding_id=finding_id,
            case_number=case_num,
            title=title.strip(),
            priority=priority.lower(),
            status="open",
            summary=summary,
            assigned_to_user_id=assigned_to_user_id,
        )
        self.db.add(investigation)
        self.db.flush()
        return investigation

    def add_note(self, investigation_id: str, author_user_id: str | None, note_text: str) -> InvestigationNote:
        note = InvestigationNote(
            investigation_id=investigation_id,
            author_user_id=author_user_id,
            note_text=note_text.strip(),
        )
        self.db.add(note)
        case = self.db.get(Investigation, investigation_id)
        if case and note not in case.notes:
            case.notes.append(note)
        self.db.flush()
        return note


    def update_case_status(
        self,
        investigation_id: str,
        status: str,
        resolution_reason: str | None = None,
    ) -> Investigation | None:
        case = self.get_by_id(investigation_id)
        if case:
            case.status = status
            if resolution_reason:
                case.resolution_reason = resolution_reason
            self.db.flush()
        return case

    def count_open_cases(self, organization_id: str) -> int:
        stmt = (
            select(func.count(Investigation.id))
            .where(
                Investigation.organization_id == organization_id,
                Investigation.status.in_(["open", "investigating", "escalated"])
            )
        )
        return self.db.scalar(stmt) or 0
