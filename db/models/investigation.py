"""
Investigation case management and notes models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class Investigation(Base):
    """Case investigation opened for one or more suspicious findings."""
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id: Mapped[str] = mapped_column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    assigned_to_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    resolution_reason: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    finding = relationship("Finding", back_populates="investigations")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    notes = relationship("InvestigationNote", back_populates="investigation", cascade="all, delete-orphan")

class InvestigationNote(Base):
    """Analyst comment or update attached to an investigation case."""
    __tablename__ = "investigation_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    investigation_id: Mapped[str] = mapped_column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    author_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="notes")
    author = relationship("User", foreign_keys=[author_user_id])
