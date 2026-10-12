"""
Unit tests for official asset exclusion engine.
Ensures verified legitimate brand assets are never flagged as findings.
"""

from db.models.asset import OfficialAppListing, OfficialSocialAccount
from detection.official_asset_match import (
    check_app_official_exclusion,
    check_social_official_exclusion,
)


def test_social_exclusion_exact_handle():
    official = [
        OfficialSocialAccount(
            platform="Twitter/X",
            handle="NovaPayOfficial",
            account_url="https://twitter.com/NovaPayOfficial",
            platform_account_id="tw-001",
            is_verified=True,
        )
    ]
    # Exact handle match
    is_ex, reason, _ = check_social_official_exclusion(
        platform="Twitter/X",
        username="NovaPayOfficial",
        profile_url="https://twitter.com/novapayofficial",
        platform_account_id=None,
        official_accounts=official,
    )
    assert is_ex is True
    assert "NovaPayOfficial" in reason

def test_social_exclusion_platform_id():
    official = [
        OfficialSocialAccount(
            platform="Twitter/X",
            handle="NovaPayOfficial",
            account_url="https://twitter.com/NovaPayOfficial",
            platform_account_id="tw-unique-1234",
            is_verified=True,
        )
    ]
    # Even if username changed, ID matches
    is_ex, reason, _ = check_social_official_exclusion(
        platform="Twitter/X",
        username="NovaPayChangedHandle",
        profile_url="https://twitter.com/novapaychangedhandle",
        platform_account_id="tw-unique-1234",
        official_accounts=official,
    )
    assert is_ex is True
    assert "tw-unique-1234" in reason

def test_social_lookalike_not_excluded():
    official = [
        OfficialSocialAccount(
            platform="Twitter/X",
            handle="NovaPayOfficial",
            account_url="https://twitter.com/NovaPayOfficial",
            platform_account_id="tw-001",
            is_verified=True,
        )
    ]
    # Look-alike handle should NOT be excluded
    is_ex, reason, _ = check_social_official_exclusion(
        platform="Twitter/X",
        username="NovaPay_Help",
        profile_url="https://twitter.com/NovaPay_Help",
        platform_account_id="tw-fake-002",
        official_accounts=official,
    )
    assert is_ex is False
    assert reason is None

def test_app_exclusion_exact_package():
    official = [
        OfficialAppListing(
            store="Google Play",
            app_name="NovaPay Wallet",
            package_id="com.novapay.wallet",
            publisher_name="NovaPay Inc.",
            store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
            is_verified=True,
        )
    ]
    is_ex, reason, _ = check_app_official_exclusion(
        store="Google Play",
        package_id="com.novapay.wallet",
        store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
        official_apps=official,
    )
    assert is_ex is True
    assert "com.novapay.wallet" in reason

def test_app_lookalike_not_excluded():
    official = [
        OfficialAppListing(
            store="Google Play",
            app_name="NovaPay Wallet",
            package_id="com.novapay.wallet",
            publisher_name="NovaPay Inc.",
            store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
            is_verified=True,
        )
    ]
    is_ex, reason, _ = check_app_official_exclusion(
        store="Google Play",
        package_id="com.fastcash.novapay",
        store_url="https://play.google.com/store/apps/details?id=com.fastcash.novapay",
        official_apps=official,
    )
    assert is_ex is False
    assert reason is None
