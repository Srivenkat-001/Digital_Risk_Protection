"""
Scan jobs and source configuration models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class ScanJob(Base):
    """Execution record of an automated or manual monitoring scan."""
    __tablename__ = "scan_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    triggered_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source_types: Mapped[str] = mapped_column(String(100), nullable=False, default="social,app")
    total_candidates_found: Mapped[int] = mapped_column(Integer, default=0)
    new_findings_count: Mapped[int] = mapped_column(Integer, default=0)
    excluded_assets_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="scan_jobs")
    triggered_by = relationship("User")
    observations = relationship("CandidateObservation", backref="scan_job", cascade="all, delete-orphan")

class SourceConfig(Base):
    """Configuration for monitoring sources and connectors."""
    __tablename__ = "source_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # social, app
    platform_or_store: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    api_key_name: Mapped[str] = mapped_column(String(100), nullable=True)
    extra_config: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
