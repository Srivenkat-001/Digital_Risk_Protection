"""
Official verified digital assets belonging to a brand.
Used by the trusted asset exclusion engine.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())

class OfficialSocialAccount(Base):
    """Verified official social media profile for exclusion."""
    __tablename__ = "official_social_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # Twitter/X, Instagram, etc.
    handle: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. @novapay
    account_url: Mapped[str] = mapped_column(String(500), nullable=False)
    platform_account_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    brand = relationship("Brand", back_populates="official_social_accounts")

class OfficialAppListing(Base):
    """Verified official mobile app listing for exclusion."""
    __tablename__ = "official_app_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    store: Mapped[str] = mapped_column(String(50), nullable=False)  # Google Play, Apple App Store
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    package_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # e.g. com.novapay.wallet
    publisher_name: Mapped[str] = mapped_column(String(255), nullable=False)
    store_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    brand = relationship("Brand", back_populates="official_app_listings")
