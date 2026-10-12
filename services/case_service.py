"""
Investigation case management service.
Handles case opening, note tracking, analyst assignment, and resolution.
"""


from sqlalchemy.orm import Session

from db.models.investigation import Investigation, InvestigationNote
from db.repositories.audit_repo import AuditRepository
from db.repositories.finding_repo import FindingRepository
from db.repositories.investigation_repo import InvestigationRepository


class CaseService:
    """Business logic for security incident investigations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InvestigationRepository(db)
        self.finding_repo = FindingRepository(db)
        self.audit_repo = AuditRepository(db)

    def list_cases(
        self,
        organization_id: str,
        brand_id: str | None = None,
        status: str | None = None,
    ) -> list[Investigation]:
        return self.repo.list_by_org(organization_id, brand_id, status)

    def get_case(self, case_id: str, organization_id: str) -> Investigation | None:
        return self.repo.get_by_id(case_id, organization_id)

    def open_investigation_from_finding(
        self,
        organization_id: str,
        finding_id: str,
        title: str,
        priority: str = "medium",
        summary: str | None = None,
        assigned_to_user_id: str | None = None,
        user_id: str | None = None,
    ) -> Investigation:
        finding = self.finding_repo.get_by_id(finding_id, organization_id)
        if not finding:
            raise ValueError("Finding not found.")

        # Update finding review status to 'Investigating'
        finding.review_status = "Investigating"
        if assigned_to_user_id:
            finding.assigned_to_user_id = assigned_to_user_id

        case = self.repo.create_case(
            organization_id=organization_id,
            brand_id=finding.brand_id,
            finding_id=finding.id,
            title=title,
            priority=priority,
            summary=summary,
            assigned_to_user_id=assigned_to_user_id,
        )

        self.audit_repo.log(
            organization_id=organization_id,
            action="INVESTIGATION_OPENED",
            target_type="investigation",
            target_id=case.id,
            user_id=user_id,
            details={"finding_id": finding.id, "case_number": case.case_number, "priority": priority},
        )
        return case

    def add_note(
        self,
        case_id: str,
        organization_id: str,
        note_text: str,
        author_user_id: str | None = None,
    ) -> InvestigationNote:
        case = self.repo.get_by_id(case_id, organization_id)
        if not case:
            raise ValueError("Investigation not found.")

        note = self.repo.add_note(
            investigation_id=case.id,
            author_user_id=author_user_id,
            note_text=note_text,
        )

        self.audit_repo.log(
            organization_id=organization_id,
            action="INVESTIGATION_NOTE_ADDED",
            target_type="investigation",
            target_id=case.id,
            user_id=author_user_id,
            details={"note_preview": note_text[:80]},
        )
        return note

    def update_case_status(
        self,
        case_id: str,
        organization_id: str,
        status: str,
        resolution_reason: str | None = None,
        user_id: str | None = None,
    ) -> Investigation:
        case = self.repo.get_by_id(case_id, organization_id)
        if not case:
            raise ValueError("Investigation not found.")

        old_status = case.status
        self.repo.update_case_status(case.id, status, resolution_reason)

        # Synchronize finding status if resolving
        if status in ("resolved", "dismissed"):
            finding = self.finding_repo.get_by_id(case.finding_id)
            if finding:
                finding.review_status = "Resolved" if status == "resolved" else "Dismissed"

        self.audit_repo.log(
            organization_id=organization_id,
            action="INVESTIGATION_STATUS_UPDATED",
            target_type="investigation",
            target_id=case.id,
            user_id=user_id,
            details={
                "old_status": old_status,
                "new_status": status,
                "resolution_reason": resolution_reason,
            },
        )
        return case
