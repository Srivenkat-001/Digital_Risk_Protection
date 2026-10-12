"""
Repository for Scan Job records and history.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.models.scan import ScanJob


class ScanRepository:
    """Handles ScanJob persistence and status tracking."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, scan_job_id: str) -> ScanJob | None:
        stmt = (
            select(ScanJob)
            .where(ScanJob.id == scan_job_id)
            .options(
                selectinload(ScanJob.brand),
                selectinload(ScanJob.triggered_by),
            )
        )
        return self.db.scalars(stmt).first()

    def list_by_org(
        self,
        organization_id: str,
        brand_id: str | None = None,
        limit: int = 50,
    ) -> list[ScanJob]:
        stmt = (
            select(ScanJob)
            .where(ScanJob.organization_id == organization_id)
            .options(
                selectinload(ScanJob.brand),
                selectinload(ScanJob.triggered_by),
            )
            .order_by(ScanJob.started_at.desc())
        )
        if brand_id:
            stmt = stmt.where(ScanJob.brand_id == brand_id)
        stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_latest_by_brand(self, brand_id: str) -> ScanJob | None:
        stmt = (
            select(ScanJob)
            .where(ScanJob.brand_id == brand_id)
            .order_by(ScanJob.started_at.desc())
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        organization_id: str,
        brand_id: str,
        triggered_by_user_id: str | None = None,
        source_types: str = "social,app",
    ) -> ScanJob:
        job = ScanJob(
            organization_id=organization_id,
            brand_id=brand_id,
            triggered_by_user_id=triggered_by_user_id,
            source_types=source_types,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(job)
        self.db.flush()
        return job

    def complete(
        self,
        scan_job_id: str,
        status: str,
        total_candidates: int,
        new_findings: int,
        excluded_assets: int,
        error_message: str | None = None,
    ) -> ScanJob | None:
        job = self.db.get(ScanJob, scan_job_id)
        if job:
            job.status = status
            job.total_candidates_found = total_candidates
            job.new_findings_count = new_findings
            job.excluded_assets_count = excluded_assets
            job.error_message = error_message
            job.completed_at = datetime.now(timezone.utc)
            self.db.flush()
        return job
