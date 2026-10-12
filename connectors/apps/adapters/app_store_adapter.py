"""Apple App Store search using Apple's public iTunes Search API."""

from typing import Any
from urllib.parse import urlparse

from config.settings import settings
from connectors.apps.base import BaseAppConnector
from connectors.http_json import collected_at, get_json
from db.models.brand import Brand

API_URL = "https://itunes.apple.com/search"
MAX_QUERIES = 3
MAX_RESULTS = 75


class AppleAppStoreLiveAdapter(BaseAppConnector):
    """Search public Apple App Store metadata; no credentials are required."""

    @property
    def name(self) -> str:
        return "Apple App Store Public Search API"

    @property
    def platform_or_store(self) -> str:
        return "Apple App Store"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        if not settings.LIVE_CONNECTORS_ENABLED:
            return False, "Disabled by configuration; enable LIVE_CONNECTORS_ENABLED to search listings."
        return True, "Enabled; public API reachability is checked when a scan runs."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        if not settings.LIVE_CONNECTORS_ENABLED:
            raise RuntimeError("Apple App Store collection is disabled. Enable LIVE_CONNECTORS_ENABLED to proceed.")

        queries = list(dict.fromkeys([brand.name, *(alias.alias for alias in brand.aliases)]))[:MAX_QUERIES]
        candidates: dict[str, dict[str, Any]] = {}
        for query in queries:
            payload = get_json(
                API_URL,
                {"term": query, "entity": "software", "country": "us", "limit": 50},
            )
            listings = payload.get("results", [])
            if not isinstance(listings, list):
                continue
            for listing in listings:
                if not isinstance(listing, dict):
                    continue
                bundle_id = listing.get("bundleId")
                listing_url = listing.get("trackViewUrl")
                if (
                    not isinstance(bundle_id, str)
                    or not bundle_id
                    or len(bundle_id) > 255
                    or not isinstance(listing_url, str)
                    or urlparse(listing_url).scheme != "https"
                    or urlparse(listing_url).hostname != "apps.apple.com"
                ):
                    continue
                app_name = listing.get("trackName")
                publisher = listing.get("artistName")
                description = listing.get("description")
                icon_url = listing.get("artworkUrl512") or listing.get("artworkUrl100")
                version = listing.get("version")
                rating = listing.get("averageUserRating")
                candidates[bundle_id.lower()] = {
                    "store": "Apple App Store",
                    "app_name": app_name[:255] if isinstance(app_name, str) else bundle_id,
                    "package_id": bundle_id,
                    "publisher_name": publisher[:255] if isinstance(publisher, str) else "Unknown publisher",
                    "store_url": listing_url[:500],
                    "description": description[:20000] if isinstance(description, str) else None,
                    "icon_url": icon_url[:500] if isinstance(icon_url, str) and icon_url.startswith("https://") else None,
                    "version": version[:50] if isinstance(version, str) else None,
                    "rating": rating if isinstance(rating, (int, float)) and 0 <= rating <= 5 else None,
                    "raw_metadata": {
                        "source": "Apple iTunes Search API",
                        "apple_track_id": listing.get("trackId"),
                        "collected_at": collected_at(),
                    },
                    "is_synthetic": False,
                }
                if len(candidates) >= MAX_RESULTS:
                    break
            if len(candidates) >= MAX_RESULTS:
                break
        return list(candidates.values())
