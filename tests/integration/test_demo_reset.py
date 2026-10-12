"""
Integration tests for Demo Environment Seeding and Safe Reset.
"""

from sqlalchemy.orm import Session

from db.models.brand import Brand
from db.models.finding import Finding
from seed.demo_data import ensure_platform_reference_brands, seed_demo_environment
from seed.reset_demo import reset_demo_data


def test_demo_seed_and_reset(db_session: Session):
    # 1. Seed demo environment
    org, brand, admin_user = seed_demo_environment(db_session)
    assert org is not None
    assert brand is not None
    assert admin_user is not None
    reference_brands = db_session.query(Brand).filter(
        Brand.organization_id == org.id,
        Brand.name.in_(["Instagram", "Snapchat"]),
    ).all()
    assert {brand.name for brand in reference_brands} == {"Instagram", "Snapchat"}
    assert all(not brand.official_social_accounts for brand in reference_brands)
    ensure_platform_reference_brands(db_session, org.id, admin_user.id)
    assert (
        db_session.query(Brand)
        .filter(Brand.organization_id == org.id, Brand.name.in_(["Instagram", "Snapchat"]))
        .count()
        == 2
    )

    # Check findings
    findings = db_session.query(Finding).filter(Finding.organization_id == org.id).all()
    assert len(findings) == 24

    # 2. Reset demo data safely
    success = reset_demo_data(db_session, org.id)
    assert success is True

    # Re-verify that records exist and are consistent after reset
    reset_findings = db_session.query(Finding).filter(Finding.organization_id == org.id).all()
    assert len(reset_findings) == 24
