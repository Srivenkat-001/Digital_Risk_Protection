"""Unimplemented Twitter / X API adapter placeholder."""

from typing import Any

from config.logging_config import logger
from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand


class TwitterLiveAdapter(BaseSocialConnector):
    """Adapter for Twitter / X API v2 user search."""

    @property
    def name(self) -> str:
        return "Twitter / X Live API"

    @property
    def platform_or_store(self) -> str:
        return "Twitter/X"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        return False, "Unavailable: live collection is not implemented; no accounts are queried."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        logger.warning("Twitter live collection is not implemented.")
        raise NotImplementedError("Twitter / X live collection is not implemented.")
