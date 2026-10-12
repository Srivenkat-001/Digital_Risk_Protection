"""
Pydantic schemas for evidence generation and representation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class EvidenceItemSchema(BaseModel):
    evidence_type: str = Field(..., description="e.g. name_similarity, handle_mismatch, icon_hash, publisher_mismatch")
    title: str
    description: str
    official_value: str | None = None
    candidate_value: str | None = None
    confidence: float = 1.0
    file_path_or_url: str | None = None

from pydantic import BaseModel, ConfigDict, Field


class EvidenceResponse(EvidenceItemSchema):
    id: str
    finding_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

