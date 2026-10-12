"""
Repository for Brand profile and official asset management.
"""


from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.models.asset import OfficialAppListing, OfficialSocialAccount
from db.models.brand import Brand, BrandAlias, BrandDomain, BrandLogo


class BrandRepository:
    """Handles Brand and associated official asset persistence with tenant isolation."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_org(self, organization_id: str) -> list[Brand]:
        stmt = (
            select(Brand)
            .where(Brand.organization_id == organization_id)
            .options(
                selectinload(Brand.aliases),
                selectinload(Brand.approved_domains),
                selectinload(Brand.logos),
                selectinload(Brand.official_social_accounts),
                selectinload(Brand.official_app_listings),
            )
            .order_by(Brand.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, brand_id: str, organization_id: str) -> Brand | None:
        stmt = (
            select(Brand)
            .where(Brand.id == brand_id, Brand.organization_id == organization_id)
            .options(
                selectinload(Brand.aliases),
                selectinload(Brand.approved_domains),
                selectinload(Brand.logos),
                selectinload(Brand.official_social_accounts),
                selectinload(Brand.official_app_listings),
            )
        )
        return self.db.scalars(stmt).first()

    def get_by_name(self, name: str, organization_id: str) -> Brand | None:
        stmt = (
            select(Brand)
            .where(Brand.name.ilike(name.strip()), Brand.organization_id == organization_id)
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        organization_id: str,
        name: str,
        display_name: str,
        official_website: str,
        legal_name: str | None = None,
        description: str | None = None,
        industry: str | None = None,
    ) -> Brand:
        brand = Brand(
            organization_id=organization_id,
            name=name.strip(),
            display_name=display_name.strip(),
            official_website=official_website.strip(),
            legal_name=legal_name.strip() if legal_name else None,
            description=description,
            industry=industry,
            is_active=True,
        )
        self.db.add(brand)
        self.db.flush()
        return brand

    def update(self, brand: Brand, **kwargs) -> Brand:
        for key, value in kwargs.items():
            if hasattr(brand, key):
                setattr(brand, key, value)
        self.db.flush()
        return brand

    def replace_aliases(self, brand: Brand, aliases: list[str]) -> None:
        brand.aliases = [BrandAlias(brand_id=brand.id, alias=alias) for alias in aliases]
        self.db.flush()

    def replace_domains(self, brand: Brand, domains: list[str]) -> None:
        brand.approved_domains = [
            BrandDomain(brand_id=brand.id, domain=domain.strip().lower(), is_approved=True)
            for domain in domains
        ]
        self.db.flush()

    def add_alias(self, brand_id: str, alias: str) -> BrandAlias:
        brand_alias = BrandAlias(brand_id=brand_id, alias=alias.strip())
        self.db.add(brand_alias)
        self.db.flush()
        return brand_alias

    def add_domain(self, brand_id: str, domain: str, is_approved: bool = True) -> BrandDomain:
        brand_domain = BrandDomain(brand_id=brand_id, domain=domain.strip().lower(), is_approved=is_approved)
        self.db.add(brand_domain)
        self.db.flush()
        return brand_domain

    def add_logo(
        self,
        brand_id: str,
        image_url: str | None = None,
        file_path: str | None = None,
        perceptual_hash: str | None = None,
        is_primary: bool = False,
    ) -> BrandLogo:
        logo = BrandLogo(
            brand_id=brand_id,
            image_url=image_url,
            file_path=file_path,
            perceptual_hash=perceptual_hash,
            is_primary=is_primary,
        )
        self.db.add(logo)
        self.db.flush()
        return logo

    def add_official_social(
        self,
        brand_id: str,
        platform: str,
        handle: str,
        account_url: str,
        platform_account_id: str | None = None,
        notes: str | None = None,
        is_verified: bool = True,
    ) -> OfficialSocialAccount:
        account = OfficialSocialAccount(
            brand_id=brand_id,
            platform=platform.strip(),
            handle=handle.strip().lstrip("@"),
            account_url=account_url.strip(),
            platform_account_id=platform_account_id.strip() if platform_account_id else None,
            is_verified=is_verified,
            notes=notes,
        )
        self.db.add(account)
        brand = self.db.get(Brand, brand_id)
        if brand and account not in brand.official_social_accounts:
            brand.official_social_accounts.append(account)
        self.db.flush()
        return account

    def add_official_app(
        self,
        brand_id: str,
        store: str,
        app_name: str,
        package_id: str,
        publisher_name: str,
        store_url: str,
        notes: str | None = None,
        is_verified: bool = True,
    ) -> OfficialAppListing:
        app_listing = OfficialAppListing(
            brand_id=brand_id,
            store=store.strip(),
            app_name=app_name.strip(),
            package_id=package_id.strip(),
            publisher_name=publisher_name.strip(),
            store_url=store_url.strip(),
            is_verified=is_verified,
            notes=notes,
        )
        self.db.add(app_listing)
        brand = self.db.get(Brand, brand_id)
        if brand and app_listing not in brand.official_app_listings:
            brand.official_app_listings.append(app_listing)
        self.db.flush()
        return app_listing


    def delete(self, brand: Brand) -> None:
        self.db.delete(brand)
        self.db.flush()
