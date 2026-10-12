"""
Database declarative base for SQLAlchemy models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class with common attributes."""
