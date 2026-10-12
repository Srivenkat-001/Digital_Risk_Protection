"""
Trusted official asset matching and exclusion engine.
Ensures verified legitimate brand assets are excluded from impersonation findings.
"""


from db.models.asset import OfficialAppListing, OfficialSocialAccount
from detection.normalization import normalize_handle, normalize_package_id, normalize_url


def check_social_official_exclusion(
    platform: str,
    username: str,
    profile_url: str,
    platform_account_id: str | None,
    official_accounts: list[OfficialSocialAccount],
) -> tuple[bool, str | None, OfficialSocialAccount | None]:
    """
    Checks if a social media candidate matches a verified official asset.
    Returns (is_excluded, exclusion_reason, matched_account).
    Exact platform account ID, canonical URL, and verified handle matching are evaluated.
    """
    norm_platform = platform.strip().lower()
    norm_user = normalize_handle(username)
    norm_url = normalize_url(profile_url)
    norm_id = platform_account_id.strip() if platform_account_id else None

    for off in official_accounts:
        if not off.is_verified:
            continue
        if off.platform.strip().lower() != norm_platform:
            continue

        # 1. Exact platform account ID match (strongest)
        if norm_id and off.platform_account_id and norm_id == off.platform_account_id.strip():
            return (
                True,
                f"Matches verified official account ID '{off.platform_account_id}' on {off.platform}",
                off,
            )

        # 2. Canonical URL match
        if norm_url and off.account_url and norm_url == normalize_url(off.account_url):
            return (
                True,
                f"Matches verified official profile URL '{off.account_url}' on {off.platform}",
                off,
            )

        # 3. Exact handle match on the same platform
        if norm_user and off.handle and norm_user == normalize_handle(off.handle):
            return (
                True,
                f"Matches verified official handle '@{off.handle}' on {off.platform}",
                off,
            )

    return False, None, None

def check_app_official_exclusion(
    store: str,
    package_id: str,
    store_url: str,
    official_apps: list[OfficialAppListing],
) -> tuple[bool, str | None, OfficialAppListing | None]:
    """
    Checks if a mobile application candidate matches a verified official app.
    Returns (is_excluded, exclusion_reason, matched_app).
    Package ID and canonical store URL matching are evaluated.
    """
    norm_store = store.strip().lower()
    norm_pkg = normalize_package_id(package_id)
    norm_url = normalize_url(store_url)

    for off in official_apps:
        if not off.is_verified:
            continue
        if off.store.strip().lower() != norm_store:
            continue

        # 1. Exact Package/Bundle ID match (strongest identity match on app stores)
        if norm_pkg and off.package_id and norm_pkg == normalize_package_id(off.package_id):
            return (
                True,
                f"Matches verified official package ID '{off.package_id}' on {off.store}",
                off,
            )

        # 2. Canonical Store URL match
        if norm_url and off.store_url and norm_url == normalize_url(off.store_url):
            return (
                True,
                f"Matches verified official store listing URL '{off.store_url}' on {off.store}",
                off,
            )

    return False, None, None
