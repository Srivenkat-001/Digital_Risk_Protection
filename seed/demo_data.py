"""
Deterministic demo data seed module for NovaPay.
Exercises the exact normalization, exclusion, scoring, evidence, and persistence pipelines.
"""


from sqlalchemy.orm import Session

from config.logging_config import logger
from db.models.brand import Brand
from db.models.finding import Finding
from db.models.organization import Organization
from db.models.user import User
from jobs.scan_runner import run_brand_scan
from schemas.brand import (
    BrandCreate,
    OfficialAppListingBase,
    OfficialSocialAccountBase,
)
from services.auth import AuthService
from services.brand_service import BrandService
from services.case_service import CaseService


def seed_demo_environment(db: Session) -> tuple[Organization, Brand, User]:
    """
    Seeds the standard NovaPay tenant, default accounts, official assets,
    and runs the initial demo scan.
    """
    logger.info("Starting demo environment initialization...")
    auth_service = AuthService(db)
    brand_service = BrandService(db)
    case_service = CaseService(db)

    # 1. Seed Organization & Users
    org, admin_user = auth_service.seed_default_users_and_org()

    # 2. Check if NovaPay brand already exists
    brand = brand_service.repo.get_by_name("NovaPay", org.id)
    if not brand:
        brand_data = BrandCreate(
            name="NovaPay",
            display_name="NovaPay Global Payments",
            legal_name="NovaPay Financial Technologies Inc.",
            industry="Fintech & Digital Payments",
            official_website="https://novapay.io",
            description="Global digital wallet and peer-to-peer payment platform offering instant zero-fee remittances and consumer accounts.",
            aliases=["Nova Pay", "NovaPayment", "NovaWallet"],
            approved_domains=["novapay.io", "pay.novapay.io", "checkout.novapay.io"],
            official_social_accounts=[
                OfficialSocialAccountBase(
                    platform="Twitter/X",
                    handle="NovaPayOfficial",
                    account_url="https://twitter.com/NovaPayOfficial",
                    platform_account_id="tw-novapay-official-001",
                    is_verified=True,
                    notes="Primary verified global customer communications handle.",
                )
            ],
            official_app_listings=[
                OfficialAppListingBase(
                    store="Google Play",
                    app_name="NovaPay: Digital Wallet & Pay",
                    package_id="com.novapay.wallet",
                    publisher_name="NovaPay Technologies Inc.",
                    store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
                    is_verified=True,
                    notes="Official Android consumer mobile wallet application.",
                )
            ],
        )
        brand = brand_service.create_brand(org.id, brand_data, user_id=admin_user.id)
        # Add primary brand logo with perceptual hash
        brand_service.repo.add_logo(
            brand_id=brand.id,
            image_url="https://example.com/assets/novapay_logo.png",
            perceptual_hash="a1b2c3d4e5f60000",
            is_primary=True,
        )
        logger.info("Created NovaPay brand profile with verified official assets.")

    # 3. Run the complete scan to exercise the full pipeline
    scan_job = run_brand_scan(
        db=db,
        brand_id=brand.id,
        organization_id=org.id,
        triggered_by_user_id=admin_user.id,
        source_types=["social", "app"],
    )
    logger.info(f"Initial demo scan completed with job ID {scan_job.id}")

    # 4. Create sample investigation history for realism
    # Find the fake support finding
    fake_support_finding = (
        db.query(Finding)
        .filter(Finding.brand_id == brand.id, Finding.severity.in_(["High", "Critical"]))
        .first()
    )
    if fake_support_finding:
        existing_case = case_service.repo.get_by_finding_id(fake_support_finding.id)
        if not existing_case:
            case = case_service.open_investigation_from_finding(
                organization_id=org.id,
                finding_id=fake_support_finding.id,
                title="Impersonation Attack: Malicious Support Handle @NovaPay_Help",
                priority="high",
                summary="Account actively soliciting customer credentials via direct messaging under the guise of an account recovery service.",
                assigned_to_user_id=admin_user.id,
                user_id=admin_user.id,
            )
            case_service.add_note(
                case_id=case.id,
                organization_id=org.id,
                note_text="Telemetry confirms brand logo hash match (100%) and unauthorized credential solicitation keywords.",
                author_user_id=admin_user.id,
            )
            logger.info(f"Opened sample investigation case {case.case_number}")

    logger.info("Demo environment initialization completed successfully.")
    return org, brand, admin_user
