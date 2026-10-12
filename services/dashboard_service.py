"""
Dashboard aggregation and metrics service.
Calculates all statistics strictly from database records and integrates source health diagnostics.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from connectors.registry import connector_registry
from db.models.brand import Brand
from db.models.candidate import CandidateAppListing, CandidateProfile
from db.models.finding import Finding
from db.repositories.finding_repo import FindingRepository
from db.repositories.investigation_repo import InvestigationRepository
from db.repositories.scan_repo import ScanRepository


class DashboardService:
    """Aggregates security metrics and telemetry across tenant brands."""

    def __init__(self, db: Session):
        self.db = db
        self.finding_repo = FindingRepository(db)
        self.investigation_repo = InvestigationRepository(db)
        self.scan_repo = ScanRepository(db)

    def get_dashboard_summary(self, organization_id: str, brand_id: str | None = None) -> dict[str, Any]:
        """Gathers complete metrics payload for dashboard cards and charts."""
        # Brand count
        brand_query = select(func.count(Brand.id)).where(Brand.organization_id == organization_id)
        if brand_id:
            brand_query = brand_query.where(Brand.id == brand_id)
        total_brands = self.db.scalar(brand_query) or 0

        # Candidate counts
        social_cand_q = select(func.count(CandidateProfile.id)).where(CandidateProfile.organization_id == organization_id)
        app_cand_q = select(func.count(CandidateAppListing.id)).where(CandidateAppListing.organization_id == organization_id)
        if brand_id:
            social_cand_q = social_cand_q.where(CandidateProfile.brand_id == brand_id)
            app_cand_q = app_cand_q.where(CandidateAppListing.brand_id == brand_id)
        total_social_candidates = self.db.scalar(social_cand_q) or 0
        total_app_candidates = self.db.scalar(app_cand_q) or 0
        total_candidates = total_social_candidates + total_app_candidates

        # Finding metrics
        finding_metrics = self.finding_repo.get_metrics_summary(organization_id, brand_id)

        # High priority findings (Critical or High risk requiring review)
        high_priority_findings = self.finding_repo.list_findings(
            organization_id=organization_id,
            brand_id=brand_id,
            review_status="New",
            limit=5,
        )

        # Open investigations
        open_cases_count = self.investigation_repo.count_open_cases(organization_id)
        recent_cases = self.investigation_repo.list_by_org(organization_id, brand_id=brand_id)[:5]

        # Scan history
        recent_scans = self.scan_repo.list_by_org(organization_id, brand_id=brand_id, limit=5)

        # Connector health
        connector_health = connector_registry.get_health_report()

        # Check if dataset contains synthetic demo records
        synthetic_count = self.db.scalar(
            select(func.count(Finding.id))
            .where(Finding.organization_id == organization_id, Finding.is_synthetic == True)
        ) or 0
        is_synthetic_data_present = synthetic_count > 0

        # Recent detections
        recent_findings = self.finding_repo.list_findings(
            organization_id=organization_id,
            brand_id=brand_id,
            limit=10,
        )

        return {
            "total_brands": total_brands,
            "total_candidates": total_candidates,
            "total_findings": finding_metrics["total_findings"],
            "new_findings": finding_metrics["new_count"],
            "confirmed_threats": finding_metrics["confirmed_threats"],
            "false_positives": finding_metrics["false_positives"],
            "investigating_count": finding_metrics["investigating_count"],
            "open_cases_count": open_cases_count,
            "severity_distribution": finding_metrics["severity_counts"],
            "status_distribution": finding_metrics["status_counts"],
            "high_priority_queue": high_priority_findings,
            "recent_findings": recent_findings,
            "recent_cases": recent_cases,
            "recent_scans": recent_scans,
            "connector_health": connector_health,
            "is_synthetic_data_present": is_synthetic_data_present,
            "synthetic_findings_count": synthetic_count,
        }
