"""
Brand management service.
Handles brand registration, official asset attachment, and updates.
"""

from collections.abc import Callable

from sqlalchemy.orm import Session

from db.models.brand import Brand
from db.repositories.audit_repo import AuditRepository
from db.repositories.brand_repo import BrandRepository
from detection.normalization import normalize_handle, normalize_package_id, normalize_url
from schemas.brand import (
    BrandCreate,
    BrandUpdate,
    OfficialAppListingBase,
    OfficialSocialAccountBase,
)


class BrandService:
    """Business logic for brand management and verified asset configuration."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = BrandRepository(db)
        self.audit_repo = AuditRepository(db)

    def list_brands(self, organization_id: str) -> list[Brand]:
        return self.repo.list_by_org(organization_id)

    def get_brand(self, brand_id: str, organization_id: str) -> Brand | None:
        return self.repo.get_by_id(brand_id, organization_id)

    def create_brand(
        self,
        organization_id: str,
        brand_data: BrandCreate,
        user_id: str | None = None,
    ) -> Brand:
        # Check duplicate name in same org
        existing = self.repo.get_by_name(brand_data.name, organization_id)
        if existing:
            raise ValueError(f"A brand with the name '{brand_data.name}' already exists.")
        _assert_unique_assets(brand_data)

        brand = self.repo.create(
            organization_id=organization_id,
            name=brand_data.name,
            display_name=brand_data.display_name,
            official_website=brand_data.official_website,
            legal_name=brand_data.legal_name,
            description=brand_data.description,
            industry=brand_data.industry,
        )

        # Add aliases
        for alias in brand_data.aliases:
            if alias.strip():
                self.repo.add_alias(brand.id, alias.strip())

        # Add approved domains
        for domain in brand_data.approved_domains:
            if domain.strip():
                self.repo.add_domain(brand.id, domain.strip())

        # Add official social accounts
        for social in brand_data.official_social_accounts:
            self.repo.add_official_social(
                brand_id=brand.id,
                platform=social.platform,
                handle=social.handle,
                account_url=social.account_url,
                platform_account_id=social.platform_account_id,
                notes=social.notes,
                is_verified=social.is_verified,
            )

        # Add official apps
        for app in brand_data.official_app_listings:
            self.repo.add_official_app(
                brand_id=brand.id,
                store=app.store,
                app_name=app.app_name,
                package_id=app.package_id,
                publisher_name=app.publisher_name,
                store_url=app.store_url,
                notes=app.notes,
                is_verified=app.is_verified,
            )

        self.audit_repo.log(
            organization_id=organization_id,
            action="BRAND_CREATED",
            target_type="brand",
            target_id=brand.id,
            user_id=user_id,
            details={"brand_name": brand.name},
        )
        return brand

    def update_brand(
        self,
        brand_id: str,
        organization_id: str,
        brand_data: BrandUpdate,
        user_id: str | None = None,
    ) -> Brand:
        brand = self.repo.get_by_id(brand_id, organization_id)
        if not brand:
            raise ValueError("Brand not found.")

        changes = brand_data.model_dump(exclude_unset=True)
        aliases = changes.pop("aliases", None)
        domains = changes.pop("approved_domains", None)
        updated_name = changes.get("name")
        if updated_name and updated_name.strip().casefold() != brand.name.casefold():
            duplicate = self.repo.get_by_name(updated_name, organization_id)
            if duplicate and duplicate.id != brand.id:
                raise ValueError(f"A brand with the name '{updated_name}' already exists.")
        for field in ("name", "display_name", "official_website"):
            if field in changes:
                changes[field] = changes[field].strip()
        if "aliases" in brand_data.model_fields_set and aliases is not None:
            aliases = _unique_values(aliases, str.casefold)
            self.repo.replace_aliases(brand, aliases)
        if "approved_domains" in brand_data.model_fields_set and domains is not None:
            domains = _unique_values(domains, lambda value: value.strip().lower())
            self.repo.replace_domains(brand, domains)
        self.repo.update(brand, **changes)
        self.audit_repo.log(
            organization_id=organization_id,
            action="BRAND_UPDATED",
            target_type="brand",
            target_id=brand.id,
            user_id=user_id,
            details={"updated_fields": sorted(changes.keys())},
        )
        return brand

    def add_social_asset(
        self,
        brand_id: str,
        organization_id: str,
        asset: OfficialSocialAccountBase,
        user_id: str | None = None,
    ):
        brand = self.repo.get_by_id(brand_id, organization_id)
        if not brand:
            raise ValueError("Brand not found.")
        if any(
            account.platform.casefold() == asset.platform.casefold()
            and (
                (asset.platform_account_id and account.platform_account_id == asset.platform_account_id)
                or normalize_handle(account.handle) == normalize_handle(asset.handle)
                or normalize_url(account.account_url) == normalize_url(asset.account_url)
            )
            for account in brand.official_social_accounts
        ):
            raise ValueError("This social asset is already registered for the brand.")
        acc = self.repo.add_official_social(
            brand_id=brand.id,
            platform=asset.platform,
            handle=asset.handle,
            account_url=asset.account_url,
            platform_account_id=asset.platform_account_id,
            notes=asset.notes,
            is_verified=asset.is_verified,
        )
        self.audit_repo.log(
            organization_id=organization_id,
            action="OFFICIAL_SOCIAL_ASSET_ADDED",
            target_type="brand",
            target_id=brand.id,
            user_id=user_id,
            details={"platform": asset.platform, "handle": asset.handle},
        )
        return acc

    def add_app_asset(
        self,
        brand_id: str,
        organization_id: str,
        asset: OfficialAppListingBase,
        user_id: str | None = None,
    ):
        brand = self.repo.get_by_id(brand_id, organization_id)
        if not brand:
            raise ValueError("Brand not found.")
        if any(
            listing.store.casefold() == asset.store.casefold()
            and normalize_package_id(listing.package_id) == normalize_package_id(asset.package_id)
            for listing in brand.official_app_listings
        ):
            raise ValueError("This app listing is already registered for the brand.")
        listing = self.repo.add_official_app(
            brand_id=brand.id,
            store=asset.store,
            app_name=asset.app_name,
            package_id=asset.package_id,
            publisher_name=asset.publisher_name,
            store_url=asset.store_url,
            notes=asset.notes,
            is_verified=asset.is_verified,
        )
        self.audit_repo.log(
            organization_id=organization_id,
            action="OFFICIAL_APP_ASSET_ADDED",
            target_type="brand",
            target_id=brand.id,
            user_id=user_id,
            details={"store": asset.store, "package_id": asset.package_id},
        )
        return listing

    def delete_brand(self, brand_id: str, organization_id: str, user_id: str | None = None):
        brand = self.repo.get_by_id(brand_id, organization_id)
        if not brand:
            raise ValueError("Brand not found.")
        self.repo.delete(brand)
        self.audit_repo.log(
            organization_id=organization_id,
            action="BRAND_DELETED",
            target_type="brand",
            target_id=brand_id,
            user_id=user_id,
            details={"brand_name": brand.name},
        )


def _unique_values(values: list[str], normalize: Callable[[str], str]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        cleaned = value.strip()
        key = normalize(cleaned)
        if cleaned and key not in seen:
            result.append(cleaned)
            seen.add(key)
    return result


def _assert_unique_assets(brand_data: BrandCreate) -> None:
    social_seen = set()
    for asset in brand_data.official_social_accounts:
        platform = asset.platform.casefold()
        identities = [
            ("account_id", asset.platform_account_id.strip() if asset.platform_account_id else ""),
            ("handle", normalize_handle(asset.handle)),
            ("url", normalize_url(asset.account_url)),
        ]
        for identity_type, identity in identities:
            key = (platform, identity_type, identity)
            if identity and key in social_seen:
                raise ValueError("Duplicate official social assets are not allowed.")
            if identity:
                social_seen.add(key)

    app_seen = set()
    for asset in brand_data.official_app_listings:
        key = (asset.store.casefold(), normalize_package_id(asset.package_id))
        if key in app_seen:
            raise ValueError("Duplicate official app listings are not allowed.")
        app_seen.add(key)
