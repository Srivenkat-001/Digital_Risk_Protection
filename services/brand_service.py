"""
Brand management service.
Handles brand registration, official asset attachment, and updates.
"""


from sqlalchemy.orm import Session

from db.models.brand import Brand
from db.repositories.audit_repo import AuditRepository
from db.repositories.brand_repo import BrandRepository
from schemas.brand import (
    BrandCreate,
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
        acc = self.repo.add_official_social(
            brand_id=brand.id,
            platform=asset.platform,
            handle=asset.handle,
            account_url=asset.account_url,
            platform_account_id=asset.platform_account_id,
            notes=asset.notes,
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
        listing = self.repo.add_official_app(
            brand_id=brand.id,
            store=asset.store,
            app_name=asset.app_name,
            package_id=asset.package_id,
            publisher_name=asset.publisher_name,
            store_url=asset.store_url,
            notes=asset.notes,
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
