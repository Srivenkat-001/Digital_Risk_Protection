"""
Observed candidates from social media platforms and mobile app stores.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class CandidateProfile(Base):
    """Discovered candidate social media profile."""
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    platform_account_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    avatar_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    follower_count: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    raw_metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    is_excluded: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    exclusion_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    first_observed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_observed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    findings = relationship("Finding", primaryjoin="and_(Finding.candidate_id==CandidateProfile.id, Finding.candidate_type=='social')", foreign_keys="Finding.candidate_id", viewonly=True, overlaps="findings")

class CandidateAppListing(Base):
    """Discovered candidate mobile app listing."""
    __tablename__ = "candidate_app_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    store: Mapped[str] = mapped_column(String(50), nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    package_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    publisher_name: Mapped[str] = mapped_column(String(255), nullable=False)
    store_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    icon_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    raw_metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    is_excluded: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    exclusion_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)

    first_observed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_observed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    findings = relationship("Finding", primaryjoin="and_(Finding.candidate_id==CandidateAppListing.id, Finding.candidate_type=='app')", foreign_keys="Finding.candidate_id", viewonly=True, overlaps="findings")


class CandidateObservation(Base):
    """Audit log of each time a candidate is encountered during a scan job."""
    __tablename__ = "candidate_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    scan_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_type: Mapped[str] = mapped_column(String(20), nullable=False)  # social, app
    candidate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
