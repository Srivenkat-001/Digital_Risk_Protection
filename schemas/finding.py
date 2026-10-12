"""
Pydantic schemas for detection signals, risk assessments, and findings.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from schemas.evidence import EvidenceItemSchema


class DetectionSignalSchema(BaseModel):
    signal_name: str
    signal_value: float  # 0.0 to 1.0
    signal_weight: float
    contribution: float
    rationale: str

class RiskAssessmentSchema(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0)
    severity: str = Field(..., description="Low, Medium, High, Critical")
    explanation: str
    model_version: str = "v1.2.0"
    assessed_at: datetime

class FindingStatusUpdate(BaseModel):
    review_status: str
    notes: str | None = None
    assigned_to_user_id: str | None = None

from pydantic import BaseModel, ConfigDict, Field


class FindingResponse(BaseModel):
    id: str
    organization_id: str
    brand_id: str
    scan_job_id: str | None = None
    candidate_type: str  # social, app
    candidate_id: str
    risk_score: float
    severity: str
    review_status: str
    assigned_to_user_id: str | None = None
    is_synthetic: bool
    created_at: datetime
    updated_at: datetime
    signals: list[DetectionSignalSchema] = []
    assessment: RiskAssessmentSchema | None = None
    evidence_items: list[EvidenceItemSchema] = []

    model_config = ConfigDict(from_attributes=True)

