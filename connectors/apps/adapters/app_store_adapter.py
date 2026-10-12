"""Live Apple App Store connector using Apple's public iTunes Search API."""
from typing import Any

import requests

from connectors.apps.base import BaseAppConnector
from db.models.brand import Brand


class AppleAppStoreLiveAdapter(BaseAppConnector):
    API_URL = "https://itunes.apple.com/search"

    @property
    def name(self) -> str:
        return "Apple App Store Search API"

    @property
    def platform_or_store(self) -> str:
        return "Apple App Store"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        return True, "Available: Apple's public search API; network access is checked during a scan."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        terms = [brand.name] + [alias.alias for alias in (brand.aliases or [])]
        results: dict[str, dict[str, Any]] = {}
        for term in terms[:5]:
            if not term or not term.strip():
                continue
            response = requests.get(
                self.API_URL,
                params={
                    "term": term.strip(),
                    "entity": "software",
                    "country": "us",
                    "limit": 50,
                },
                timeout=(5, 20),
            )
            response.raise_for_status()
            for item in response.json().get("results", []):
                bundle_id = item.get("bundleId")
                track_id = item.get("trackId")
                identifier = bundle_id or (str(track_id) if track_id else None)
                if not identifier:
                    continue
                results[identifier.lower()] = {
                    "store": "Apple App Store",
                    "app_name": item.get("trackName") or "",
                    "package_id": identifier,
                    "publisher_name": item.get("sellerName") or item.get("artistName") or "Unknown publisher",
                    "store_url": item.get("trackViewUrl") or "",
                    "description": (item.get("description") or "")[:10000],
                    "icon_url": item.get("artworkUrl512") or item.get("artworkUrl100"),
                    "icon_hash": None,
                    "version": item.get("version"),
                    "rating": item.get("averageUserRating"),
                    "raw_metadata": {
                        "source": "apple_itunes_search_api",
                        "track_id": track_id,
                        "seller_url": item.get("sellerUrl"),
                        "bundle_id": bundle_id,
                        "country": "us",
                    },
                    "is_synthetic": False,
                }
        return list(results.values())
