"""Unimplemented Instagram Graph API adapter placeholder."""

from typing import Any

from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand


class InstagramLiveAdapter(BaseSocialConnector):
    """Adapter for Instagram Graph API discovery."""

    @property
    def name(self) -> str:
        return "Instagram Graph API"

    @property
    def platform_or_store(self) -> str:
        return "Instagram"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        return False, "Unavailable: live collection is not implemented; no accounts are queried."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        raise NotImplementedError("Instagram live collection is not implemented.")
