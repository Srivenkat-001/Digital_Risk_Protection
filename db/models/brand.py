"""
Brand models for registered organizations, domains, aliases, and logos.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class Brand(Base):
    """Registered corporate brand profile."""
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    official_website: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    organization = relationship("Organization", back_populates="brands")
    aliases = relationship("BrandAlias", back_populates="brand", cascade="all, delete-orphan")
    approved_domains = relationship("BrandDomain", back_populates="brand", cascade="all, delete-orphan")
    logos = relationship("BrandLogo", back_populates="brand", cascade="all, delete-orphan")
    official_social_accounts = relationship("OfficialSocialAccount", back_populates="brand", cascade="all, delete-orphan")
    official_app_listings = relationship("OfficialAppListing", back_populates="brand", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="brand", cascade="all, delete-orphan")
    scan_jobs = relationship("ScanJob", back_populates="brand", cascade="all, delete-orphan")

class BrandAlias(Base):
    """Alternative brand spellings, abbreviations, and trade names."""
    __tablename__ = "brand_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    brand = relationship("Brand", back_populates="aliases")

class BrandDomain(Base):
    """Approved legitimate domain names belonging to the brand."""
    __tablename__ = "brand_domains"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    brand = relationship("Brand", back_populates="approved_domains")

class BrandLogo(Base):
    """Official logo references and computed perceptual hashes."""
    __tablename__ = "brand_logos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    perceptual_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    brand = relationship("Brand", back_populates="logos")
