"""
Pytest fixtures for BrandPhantom unit and integration tests.
Provides isolated test database session and baseline test records.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.base import Base
from db.models.brand import Brand
from db.models.organization import Membership, Organization
from db.models.user import User
from schemas.brand import BrandCreate, OfficialAppListingBase, OfficialSocialAccountBase
from services.auth import hash_password
from services.brand_service import BrandService

# In-memory test SQLite engine
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session() -> Session:
    """Yields a fresh in-memory SQLite database session for each test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_org(db_session: Session) -> Organization:
    """Creates a test organization."""
    org = Organization(name="Test Security Corp", slug="test-security-corp")
    db_session.add(org)
    db_session.commit()
    return org

@pytest.fixture
def test_users(db_session: Session, test_org: Organization) -> dict:
    """Creates test Admin, Analyst, and Viewer users."""
    admin = User(
        email="admin@test.com",
        hashed_password=hash_password("Pass123!"),
        full_name="Test Admin",
        is_active=True,
    )
    analyst = User(
        email="analyst@test.com",
        hashed_password=hash_password("Pass123!"),
        full_name="Test Analyst",
        is_active=True,
    )
    viewer = User(
        email="viewer@test.com",
        hashed_password=hash_password("Pass123!"),
        full_name="Test Viewer",
        is_active=True,
    )
    db_session.add_all([admin, analyst, viewer])
    db_session.flush()

    m_admin = Membership(user_id=admin.id, organization_id=test_org.id, role="admin")
    m_analyst = Membership(user_id=analyst.id, organization_id=test_org.id, role="analyst")
    m_viewer = Membership(user_id=viewer.id, organization_id=test_org.id, role="viewer")
    db_session.add_all([m_admin, m_analyst, m_viewer])
    db_session.commit()

    return {"admin": admin, "analyst": analyst, "viewer": viewer}

@pytest.fixture
def test_brand(db_session: Session, test_org: Organization, test_users: dict) -> Brand:
    """Creates a registered test brand with official assets."""
    service = BrandService(db_session)
    brand_data = BrandCreate(
        name="NovaPay",
        display_name="NovaPay Global Payments",
        official_website="https://novapay.io",
        legal_name="NovaPay Inc.",
        description="Official payment gateway and consumer digital wallet.",
        aliases=["Nova Pay", "NovaPayment"],
        approved_domains=["novapay.io", "pay.novapay.io"],
        official_social_accounts=[
            OfficialSocialAccountBase(
                platform="Twitter/X",
                handle="NovaPayOfficial",
                account_url="https://twitter.com/NovaPayOfficial",
                platform_account_id="tw-novapay-official-001",
                is_verified=True,
            )
        ],
        official_app_listings=[
            OfficialAppListingBase(
                store="Google Play",
                app_name="NovaPay: Digital Wallet",
                package_id="com.novapay.wallet",
                publisher_name="NovaPay Technologies Inc.",
                store_url="https://play.google.com/store/apps/details?id=com.novapay.wallet",
                is_verified=True,
            )
        ],
    )
    brand = service.create_brand(test_org.id, brand_data, user_id=test_users["admin"].id)
    service.repo.add_logo(
        brand_id=brand.id,
        perceptual_hash="a1b2c3d4e5f60000",
        is_primary=True,
    )
    db_session.commit()
    return brand
