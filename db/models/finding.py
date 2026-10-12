"""
Finding, Detection Signal, Risk Assessment, and Evidence models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class Finding(Base):
    """An alert or risk assessment generated for an unexcluded candidate."""
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    candidate_type: Mapped[str] = mapped_column(String(20), nullable=False)  # social, app
    candidate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="Low")
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="New", index=True)
    assigned_to_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    brand = relationship("Brand", back_populates="findings")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    signals = relationship("DetectionSignal", back_populates="finding", cascade="all, delete-orphan")
    assessment = relationship("RiskAssessment", back_populates="finding", uselist=False, cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="finding", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="finding")

class DetectionSignal(Base):
    """Individual signal evaluated by the risk detection engine."""
    __tablename__ = "detection_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    finding_id: Mapped[str] = mapped_column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_name: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_value: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    signal_weight: Mapped[float] = mapped_column(Float, nullable=False)
    contribution: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    finding = relationship("Finding", back_populates="signals")

class RiskAssessment(Base):
    """Overall explainable risk assessment summary."""
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    finding_id: Mapped[str] = mapped_column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0.0")
    assessed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    finding = relationship("Finding", back_populates="assessment")

class Evidence(Base):
    """Evidence artifacts linking official brand assets to candidate attributes."""
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    finding_id: Mapped[str] = mapped_column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    official_value: Mapped[str] = mapped_column(Text, nullable=True)
    candidate_value: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    file_path_or_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    finding = relationship("Finding", back_populates="evidence_items")
