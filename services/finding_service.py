"""
Finding and triage workflow service.
Handles status changes, false-positive labeling, and analyst assignment.
"""

from typing import Any

from sqlalchemy.orm import Session

from config.settings import settings
from db.models.candidate import CandidateAppListing, CandidateProfile
from db.models.finding import Finding
from db.repositories.audit_repo import AuditRepository
from db.repositories.finding_repo import FindingRepository


class FindingService:
    """Manages finding triage and risk disposition."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = FindingRepository(db)
        self.audit_repo = AuditRepository(db)

    def list_findings(
        self,
        organization_id: str,
        brand_id: str | None = None,
        severity: str | None = None,
        review_status: str | None = None,
        candidate_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Finding]:
        return self.repo.list_findings(
            organization_id=organization_id,
            brand_id=brand_id,
            severity=severity,
            review_status=review_status,
            candidate_type=candidate_type,
            limit=limit,
            offset=offset,
        )

    def get_finding(self, finding_id: str, organization_id: str) -> Finding | None:
        return self.repo.get_by_id(finding_id, organization_id)

    def get_candidate_for_finding(self, finding: Finding) -> Any | None:
        """Resolves the underlying candidate object (Profile or App)."""
        if finding.candidate_type == "social":
            return self.db.get(CandidateProfile, finding.candidate_id)
        elif finding.candidate_type == "app":
            return self.db.get(CandidateAppListing, finding.candidate_id)
        return None

    def update_status(
        self,
        finding_id: str,
        organization_id: str,
        review_status: str,
        user_id: str | None = None,
        notes: str | None = None,
    ) -> Finding:
        if review_status not in settings.ALL_STATUSES:
            raise ValueError(f"Unsupported finding review status: {review_status!r}.")
        finding = self.repo.get_by_id(finding_id, organization_id)
        if not finding:
            raise ValueError("Finding not found.")

        old_status = finding.review_status
        finding.review_status = review_status
        if user_id:
            finding.assigned_to_user_id = user_id
        self.db.flush()

        self.audit_repo.log(
            organization_id=organization_id,
            action="FINDING_STATUS_UPDATED",
            target_type="finding",
            target_id=finding.id,
            user_id=user_id,
            details={
                "old_status": old_status,
                "new_status": review_status,
                "notes": notes,
            },
        )
        return finding
