"""
Authentication and Role-Based Access Control (RBAC) service.
Implements PBKDF2-HMAC-SHA256 password hashing and role enforcement.
"""

import hashlib
import secrets

from sqlalchemy.orm import Session

from config.logging_config import logger
from config.settings import settings
from db.models.organization import Organization
from db.models.user import User
from db.repositories.user_repo import UserRepository

# Role hierarchy levels: admin (3) > analyst (2) > viewer (1)
ROLE_HIERARCHY = {
    settings.ROLE_ADMIN: 3,
    settings.ROLE_ANALYST: 2,
    settings.ROLE_VIEWER: 1,
}

def hash_password(password: str) -> str:
    """Hashes a password with salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salt and hash."""
    try:
        salt, stored_hash = hashed_password.split("$", 1)
        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        return secrets.compare_digest(computed_key.hex(), stored_hash)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

class AuthService:
    """Handles authentication, tenant resolution, and RBAC authorization."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticates user credentials."""
        user = self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def authenticate_demo_user(self, email: str) -> User | None:
        """Allows passwordless role selection only in the explicitly enabled local demo."""
        if not settings.DEMO_MODE_ENABLED or settings.APP_ENV.lower() == "production":
            return None
        demo_emails = {
            "admin@brandphantom.io",
            "analyst@brandphantom.io",
            "viewer@brandphantom.io",
        }
        if email not in demo_emails:
            return None
        user = self.user_repo.get_by_email(email)
        return user if user and user.is_active else None

    def get_user_role(self, user_id: str, organization_id: str) -> str | None:
        """Returns the user's role in the specified organization."""
        return self.user_repo.get_user_role_in_org(user_id, organization_id)

    @staticmethod
    def is_authorized(user_role: str, required_role: str) -> bool:
        """Checks if user_role meets or exceeds the required_role in the hierarchy."""
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        req_level = ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= req_level

    def seed_default_users_and_org(self) -> tuple[Organization, User]:
        """Seeds default tenant organization and admin/analyst/viewer accounts if not present."""
        # Find or create default Organization
        org = self.db.query(Organization).filter(Organization.slug == "novapay-org").first()
        if not org:
            org = Organization(name="NovaPay Global Security", slug="novapay-org")
            self.db.add(org)
            self.db.flush()
            logger.info("Created default organization: NovaPay Global Security")

        default_accounts = [
            ("admin@brandphantom.io", "Security Administrator", settings.ROLE_ADMIN),
            ("analyst@brandphantom.io", "Lead Threat Analyst", settings.ROLE_ANALYST),
            ("viewer@brandphantom.io", "Compliance Officer", settings.ROLE_VIEWER),
        ]

        first_user = None
        for email, full_name, role in default_accounts:
            existing = self.user_repo.get_by_email(email)
            if not existing:
                user = self.user_repo.create_user(
                    email=email,
                    hashed_password=hash_password(secrets.token_urlsafe(32)),
                    full_name=full_name,
                )
                self.user_repo.add_membership(user.id, org.id, role)
                logger.info(f"Seeded user account: {email} ({role})")
                if first_user is None:
                    first_user = user
            else:
                if first_user is None:
                    first_user = existing

        return org, first_user
