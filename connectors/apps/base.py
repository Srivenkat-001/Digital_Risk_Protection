"""
Mobile application store connector base.
"""

from connectors.base import BaseSourceConnector


class BaseAppConnector(BaseSourceConnector):
    """Base connector for mobile application store monitoring."""

    @property
    def source_type(self) -> str:
        return "app"
