"""
Registry for monitoring source connectors.
Provides registration, lookup, and health inspection.
"""

from typing import Any

from connectors.apps.adapters.app_store_adapter import AppleAppStoreLiveAdapter
from connectors.apps.adapters.play_store_adapter import GooglePlayLiveAdapter
from connectors.apps.demo import DemoAppConnector
from connectors.base import BaseSourceConnector
from connectors.social.adapters.bluesky_adapter import BlueskyPublicAdapter
from connectors.social.adapters.instagram_adapter import InstagramLiveAdapter
from connectors.social.adapters.twitter_adapter import TwitterLiveAdapter
from connectors.social.demo import DemoSocialConnector


class ConnectorRegistry:
    """Manages available connectors and provides health status reporting."""

    def __init__(self):
        self._connectors: list[BaseSourceConnector] = [
            DemoSocialConnector(),
            DemoAppConnector(),
            BlueskyPublicAdapter(),
            TwitterLiveAdapter(),
            InstagramLiveAdapter(),
            GooglePlayLiveAdapter(),
            AppleAppStoreLiveAdapter(),
        ]

    def get_all(self) -> list[BaseSourceConnector]:
        return list(self._connectors)

    def get_connectors(
        self,
        source_type: str | None = None,
        only_active_or_demo: bool = True,
    ) -> list[BaseSourceConnector]:
        """Returns connectors matching criteria."""
        results = []
        for conn in self._connectors:
            if source_type and conn.source_type != source_type:
                continue
            if only_active_or_demo:
                is_healthy, _ = conn.health_check()
                if conn.is_demo or is_healthy:
                    results.append(conn)
            else:
                results.append(conn)
        return results

    def get_health_report(self) -> list[dict[str, Any]]:
        """Generates a diagnostic report of all registered connectors."""
        report = []
        for conn in self._connectors:
            is_healthy, message = conn.health_check()
            report.append({
                "name": conn.name,
                "type": conn.source_type,
                "platform": conn.platform_or_store,
                "is_demo": conn.is_demo,
                "status": (
                    "Synthetic demo"
                    if conn.is_demo
                    else "Enabled (not yet probed)"
                    if is_healthy
                    else "Disabled or unavailable"
                ),
                "is_healthy": is_healthy,
                "details": message,
            })
        return report

connector_registry = ConnectorRegistry()
