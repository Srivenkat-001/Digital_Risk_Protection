"""
Integration tests for BrandService and asset management.
"""

import pytest
from sqlalchemy.orm import Session

from detection.official_asset_match import check_app_official_exclusion, check_social_official_exclusion
from schemas.brand import (
    BrandCreate,
    BrandUpdate,
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
    assert fetched.official_social_accounts[0].is_verified is True

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


def test_brand_profile_update_persists_fields_aliases_domains_and_audit(
    db_session, test_org, test_brand, test_users
):
    service = BrandService(db_session)

    updated = service.update_brand(
        test_brand.id,
        test_org.id,
        BrandUpdate(
            name="NovaPay Plus",
            display_name="NovaPay Plus Payments",
            legal_name="NovaPay Plus Inc.",
            official_website="https://novapayplus.example",
            description="Updated payment services.",
            aliases=["NovaPay+", "NP"],
            approved_domains=["novapayplus.example", "pay.novapayplus.example"],
            is_active=False,
        ),
        user_id=test_users["admin"].id,
    )

    assert updated.name == "NovaPay Plus"
    assert updated.display_name == "NovaPay Plus Payments"
    assert updated.official_website == "https://novapayplus.example"
    assert updated.description == "Updated payment services."
    assert updated.is_active is False
    assert {alias.alias for alias in updated.aliases} == {"NovaPay+", "NP"}
    assert {domain.domain for domain in updated.approved_domains} == {
        "novapayplus.example",
        "pay.novapayplus.example",
    }
    assert any(log.action == "BRAND_UPDATED" for log in service.audit_repo.list_by_org(test_org.id, limit=10))


def test_brand_profile_update_rejects_duplicate_name(db_session, test_org, test_brand):
    service = BrandService(db_session)
    other = service.create_brand(
        test_org.id,
        BrandCreate(name="Other", display_name="Other", official_website="https://other.example"),
    )

    with pytest.raises(ValueError, match="already exists"):
        service.update_brand(other.id, test_org.id, BrandUpdate(name=test_brand.name))


def test_unverified_assets_are_saved_but_not_marked_verified(db_session, test_org, test_brand):
    service = BrandService(db_session)
    social = service.add_social_asset(
        test_brand.id,
        test_org.id,
        OfficialSocialAccountBase(
            platform="Bluesky",
            handle="novapay-test.example",
            account_url="https://bsky.app/profile/novapay-test.example",
            is_verified=False,
        ),
    )
    app = service.add_app_asset(
        test_brand.id,
        test_org.id,
        OfficialAppListingBase(
            store="Apple App Store",
            app_name="NovaPay Test",
            package_id="com.novapay.test",
            publisher_name="Test Publisher",
            store_url="https://apps.apple.com/app/id456",
            is_verified=False,
        ),
    )

    assert not social.is_verified
    assert not app.is_verified
    assert not check_social_official_exclusion(
        social.platform,
        social.handle,
        social.account_url,
        social.platform_account_id,
        [social],
    )[0]
    assert not check_app_official_exclusion(
        app.store,
        app.package_id,
        app.store_url,
        [app],
    )[0]


def test_duplicate_official_assets_are_rejected(db_session, test_org, test_brand):
    service = BrandService(db_session)
    duplicate_social = OfficialSocialAccountBase(
        platform="Twitter/X",
        handle="NovaPayOfficial",
        account_url="https://twitter.com/NovaPayOfficial",
    )
    duplicate_app = OfficialAppListingBase(
        store="Google Play",
        app_name="NovaPay",
        package_id="COM.NOVAPAY.WALLET",
        publisher_name="NovaPay Inc.",
        store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
    )

    with pytest.raises(ValueError, match="social asset is already registered"):
        service.add_social_asset(test_brand.id, test_org.id, duplicate_social)
    with pytest.raises(ValueError, match="app listing is already registered"):
        service.add_app_asset(test_brand.id, test_org.id, duplicate_app)


def test_brand_and_asset_urls_reject_unsafe_schemes_and_credentials():
    with pytest.raises(ValueError, match="HTTP"):
        BrandCreate(name="Bad", display_name="Bad", official_website="javascript:alert(1)")
    with pytest.raises(ValueError, match="credentials"):
        OfficialSocialAccountBase(
            platform="Bluesky",
            handle="brand.example",
            account_url="https://user:secret@bsky.app/profile/brand.example",
        )
