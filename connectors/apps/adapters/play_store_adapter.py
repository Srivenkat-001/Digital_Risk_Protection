"""Unimplemented Google Play Store adapter placeholder."""

from typing import Any

from connectors.apps.base import BaseAppConnector
from db.models.brand import Brand


class GooglePlayLiveAdapter(BaseAppConnector):
    """Adapter for Google Play Store search."""

    @property
    def name(self) -> str:
        return "Google Play Live Store Adapter"

    @property
    def platform_or_store(self) -> str:
        return "Google Play"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        return False, "Unavailable: live collection is not implemented; no store listings are queried."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        raise NotImplementedError("Google Play live collection is not implemented.")
