"""
Integration tests for BrandService and asset management.
"""

import pytest
from sqlalchemy.orm import Session

from schemas.brand import (
    BrandCreate,
    OfficialAppListingBase,
    OfficialSocialAccountBase,
)
from services.brand_service import BrandService


def test_brand_creation_and_retrieval(db_session: Session, test_org):
    service = BrandService(db_session)
    brand_data = BrandCreate(
        name="CryptoVault",
        display_name="CryptoVault Institutional",
        official_website="https://cryptovault.com",
        aliases=["Crypto Vault"],
        approved_domains=["cryptovault.com"],
        official_social_accounts=[
            OfficialSocialAccountBase(
                platform="Twitter/X",
                handle="CryptoVault",
                account_url="https://twitter.com/CryptoVault",
            )
        ],
        official_app_listings=[],
    )
    brand = service.create_brand(test_org.id, brand_data)
    assert brand.id is not None
    assert brand.name == "CryptoVault"

    fetched = service.get_brand(brand.id, test_org.id)
    assert fetched is not None
    assert len(fetched.aliases) == 1
    assert len(fetched.official_social_accounts) == 1

def test_prevent_duplicate_brand_name_in_same_org(db_session: Session, test_org):
    service = BrandService(db_session)
    brand_data = BrandCreate(
        name="DuplicateBrand",
        display_name="Duplicate Brand",
        official_website="https://example.com",
    )
    service.create_brand(test_org.id, brand_data)
    with pytest.raises(ValueError, match="already exists"):
        service.create_brand(test_org.id, brand_data)

def test_add_social_and_app_assets(db_session: Session, test_org, test_brand):
    service = BrandService(db_session)
    social_asset = OfficialSocialAccountBase(
        platform="Instagram",
        handle="NovaPay_Official",
        account_url="https://instagram.com/NovaPay_Official",
    )
    service.add_social_asset(test_brand.id, test_org.id, social_asset)

    app_asset = OfficialAppListingBase(
        store="Apple App Store",
        app_name="NovaPay iOS",
        package_id="com.novapay.ios",
        publisher_name="NovaPay Technologies Inc.",
        store_url="https://apps.apple.com/app/novapay",
    )
    service.add_app_asset(test_brand.id, test_org.id, app_asset)

    updated = service.get_brand(test_brand.id, test_org.id)
    assert len(updated.official_social_accounts) == 2
    assert len(updated.official_app_listings) == 2
