"""
Integration tests for Authentication, RBAC, and Tenant Data Isolation.
"""

from sqlalchemy.orm import Session

from db.models.organization import Organization
from services.auth import AuthService, hash_password, verify_password
from services.brand_service import BrandService


def test_password_hashing():
    pw = "SuperSecurePassword123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert "$" in hashed
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_rbac_authorization_hierarchy():
    # Admin has all privileges
    assert AuthService.is_authorized("admin", "admin") is True
    assert AuthService.is_authorized("admin", "analyst") is True
    assert AuthService.is_authorized("admin", "viewer") is True

    # Analyst has analyst and viewer privileges, not admin
    assert AuthService.is_authorized("analyst", "admin") is False
    assert AuthService.is_authorized("analyst", "analyst") is True
    assert AuthService.is_authorized("analyst", "viewer") is True

    # Viewer has only viewer privileges
    assert AuthService.is_authorized("viewer", "admin") is False
    assert AuthService.is_authorized("viewer", "analyst") is False
    assert AuthService.is_authorized("viewer", "viewer") is True

def test_tenant_data_isolation(db_session: Session, test_org, test_brand):
    # Create second organization
    org2 = Organization(name="Other Tenant Corp", slug="other-tenant")
    db_session.add(org2)
    db_session.commit()

    brand_service = BrandService(db_session)

    # List brands for Org 1
    org1_brands = brand_service.list_brands(test_org.id)
    assert len(org1_brands) == 1
    assert org1_brands[0].id == test_brand.id

    # List brands for Org 2 - MUST be empty!
    org2_brands = brand_service.list_brands(org2.id)
    assert len(org2_brands) == 0

    # Attempting to get Org 1's brand with Org 2's ID must return None
    cross_tenant_brand = brand_service.get_brand(test_brand.id, org2.id)
    assert cross_tenant_brand is None
