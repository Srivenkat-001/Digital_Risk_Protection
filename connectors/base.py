"""
Base interface for social media and mobile application source connectors.
"""

from abc import ABC, abstractmethod
from typing import Any

from db.models.brand import Brand


class BaseSourceConnector(ABC):
    """Abstract base class for all monitoring source connectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the connector (e.g. 'Twitter Demo Connector')."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Type of source: 'social' or 'app'."""

    @property
    @abstractmethod
    def platform_or_store(self) -> str:
        """Specific platform or store name (e.g. 'Twitter/X', 'Google Play')."""

    @property
    @abstractmethod
    def is_demo(self) -> bool:
        """Whether this connector supplies deterministic synthetic data."""

    @abstractmethod
    def health_check(self) -> tuple[bool, str]:
        """
        Verifies connector status and connectivity.
        Returns (is_healthy, status_message).
        """

    @abstractmethod
    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        """
        Discovers candidate profiles or app listings for the given target brand.
        Returns a list of raw candidate dictionaries.
        """
