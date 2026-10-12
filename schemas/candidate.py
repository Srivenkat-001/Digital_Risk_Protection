"""
Pydantic schemas for candidate profiles and candidate app listings.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CandidateSocialCreate(BaseModel):
    brand_id: str
    platform: str
    profile_url: str
    username: str
    display_name: str
    bio: str | None = None
    platform_account_id: str | None = None
    avatar_url: str | None = None
    avatar_hash: str | None = None
    follower_count: int | None = 0
    raw_metadata: dict[str, Any] | None = None
    is_synthetic: bool = False

class CandidateSocialResponse(BaseModel):
    id: str
    organization_id: str
    brand_id: str
    platform: str
    profile_url: str
    username: str
    display_name: str
    bio: str | None = None
    platform_account_id: str | None = None
    avatar_url: str | None = None
    avatar_hash: str | None = None
    follower_count: int
    is_excluded: bool
    exclusion_reason: str | None = None
    is_synthetic: bool
    first_observed_at: datetime
    last_observed_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateAppCreate(BaseModel):
    brand_id: str
    store: str
    app_name: str
    package_id: str
    publisher_name: str
    store_url: str
    description: str | None = None
    icon_url: str | None = None
    icon_hash: str | None = None
    version: str | None = None
    rating: float | None = None
    raw_metadata: dict[str, Any] | None = None
    is_synthetic: bool = False

class CandidateAppResponse(BaseModel):
    id: str
    organization_id: str
    brand_id: str
    store: str
    app_name: str
    package_id: str
    publisher_name: str
    store_url: str
    description: str | None = None
    icon_url: str | None = None
    icon_hash: str | None = None
    version: str | None = None
    rating: float | None = None
    is_excluded: bool
    exclusion_reason: str | None = None
    is_synthetic: bool
    first_observed_at: datetime
    last_observed_at: datetime

    model_config = ConfigDict(from_attributes=True)

