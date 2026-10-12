"""Unimplemented Apple App Store adapter placeholder."""

from typing import Any

from connectors.apps.base import BaseAppConnector
from db.models.brand import Brand


class AppleAppStoreLiveAdapter(BaseAppConnector):
    """Adapter for Apple App Store search."""

    @property
    def name(self) -> str:
        return "Apple App Store Live Adapter"

    @property
    def platform_or_store(self) -> str:
        return "Apple App Store"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        return False, "Unavailable: live collection is not implemented; no store listings are queried."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        raise NotImplementedError("Apple App Store live collection is not implemented.")
