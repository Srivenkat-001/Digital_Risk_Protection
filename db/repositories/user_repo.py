"""
Repository for User and Organization Membership queries.
"""


from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.organization import Membership, Organization
from db.models.user import User


class UserRepository:
    """Handles User and Membership persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self.db.scalars(stmt).first()

    def get_by_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def create_user(self, email: str, hashed_password: str, full_name: str) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_user_role_in_org(self, user_id: str, organization_id: str) -> str | None:
        stmt = select(Membership.role).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id
        )
        return self.db.scalars(stmt).first()

    def get_user_organizations(self, user_id: str) -> list[tuple[Organization, str]]:
        stmt = (
            select(Organization, Membership.role)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user_id)
        )
        return list(self.db.execute(stmt).all())

    def add_membership(self, user_id: str, organization_id: str, role: str) -> Membership:
        membership = Membership(
            user_id=user_id,
            organization_id=organization_id,
            role=role
        )
        self.db.add(membership)
        self.db.flush()
        return membership
