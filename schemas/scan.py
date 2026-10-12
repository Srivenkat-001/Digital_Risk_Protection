"""
Pydantic schemas for scan jobs and execution summaries.
"""

from datetime import datetime

from pydantic import BaseModel


class ScanJobCreate(BaseModel):
    brand_id: str
    source_types: list[str] = ["social", "app"]

from pydantic import BaseModel, ConfigDict


class ScanJobResponse(BaseModel):
    id: str
    organization_id: str
    brand_id: str
    status: str
    triggered_by_user_id: str | None = None
    source_types: str
    total_candidates_found: int
    new_findings_count: int
    excluded_assets_count: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ScanSummaryResponse(BaseModel):
    scan_job_id: str
    brand_name: str
    status: str
    total_candidates: int
    excluded_official: int
    new_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    duration_seconds: float
