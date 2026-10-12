"""
Pydantic schemas for brand profile management.
"""

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator


class BrandAliasBase(BaseModel):
    alias: str = Field(..., min_length=1, max_length=255)

class BrandDomainBase(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
    is_approved: bool = True

class OfficialSocialAccountBase(BaseModel):
    platform: str = Field(..., min_length=2, max_length=50)
    handle: str = Field(..., min_length=1, max_length=100)
    account_url: str = Field(..., min_length=5, max_length=500)
    platform_account_id: str | None = Field(None, max_length=100)
    is_verified: bool = True
    notes: str | None = None

    @field_validator("account_url")
    @classmethod
    def validate_account_url(cls, value: str) -> str:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Account URL must be a valid HTTP(S) URL without embedded credentials.")
        return value.strip()


class OfficialAppListingBase(BaseModel):
    store: str = Field(..., min_length=2, max_length=50)
    app_name: str = Field(..., min_length=1, max_length=255)
    package_id: str = Field(..., min_length=2, max_length=255)
    publisher_name: str = Field(..., min_length=1, max_length=255)
    store_url: str = Field(..., min_length=5, max_length=500)
    is_verified: bool = True
    notes: str | None = None

    @field_validator("store_url")
    @classmethod
    def validate_store_url(cls, value: str) -> str:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Store URL must be a valid HTTP(S) URL without embedded credentials.")
        return value.strip()


class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    legal_name: str | None = Field(None, max_length=255)
    description: str | None = None
    industry: str | None = Field(None, max_length=100)
    official_website: str = Field(..., min_length=4, max_length=500)
    is_active: bool = True

    @field_validator("official_website")
    @classmethod
    def validate_official_website(cls, value: str) -> str:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Official website must be a valid HTTP(S) URL without embedded credentials.")
        return value.strip()


class BrandCreate(BrandBase):
    aliases: list[str] = []
    approved_domains: list[str] = []
    official_social_accounts: list[OfficialSocialAccountBase] = []
    official_app_listings: list[OfficialAppListingBase] = []

class BrandUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    display_name: str | None = Field(None, min_length=1, max_length=255)
    legal_name: str | None = None
    description: str | None = None
    industry: str | None = Field(None, max_length=100)
    official_website: str | None = Field(None, min_length=4, max_length=500)
    is_active: bool | None = None
    aliases: list[str] | None = None
    approved_domains: list[str] | None = None

    @field_validator("official_website")
    @classmethod
    def validate_updated_official_website(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Official website must be a valid HTTP(S) URL without embedded credentials.")
        return value.strip()

from pydantic import BaseModel, ConfigDict, Field


class BrandResponse(BrandBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
