"""
Social media connector base.
"""

from connectors.base import BaseSourceConnector


class BaseSocialConnector(BaseSourceConnector):
    """Base connector for social media monitoring sources."""

    @property
    def source_type(self) -> str:
        return "social"
