"""Live Google Play connector using SerpApi's Google Play search endpoint.

Google does not provide a general public Play Store search API. This adapter
uses SerpApi only when a key is configured; it does not scrape Play pages.
"""
from typing import Any

import requests

from config.settings import settings
from connectors.apps.base import BaseAppConnector
from db.models.brand import Brand


class GooglePlayLiveAdapter(BaseAppConnector):
    API_URL = "https://serpapi.com/search.json"

    @property
    def name(self) -> str:
        return "Google Play Search (SerpApi)"

    @property
    def platform_or_store(self) -> str:
        return "Google Play"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        if not settings.SERPAPI_API_KEY:
            return False, "Not configured: set SERPAPI_API_KEY to enable Google Play search."
        return True, "Configured; provider access is checked when a scan runs."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        if not settings.SERPAPI_API_KEY:
            raise RuntimeError("Set SERPAPI_API_KEY to enable Google Play collection.")
        terms = [brand.name] + [alias.alias for alias in (brand.aliases or [])]
        results: dict[str, dict[str, Any]] = {}
        for term in terms[:5]:
            if not term or not term.strip():
                continue
            response = requests.get(
                self.API_URL,
                params={
                    "engine": "google_play",
                    "store": "apps",
                    "q": term.strip(),
                    "api_key": settings.SERPAPI_API_KEY,
                },
                timeout=(5, 25),
            )
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("organic_results", []):
                package_id = item.get("product_id") or item.get("app_id")
                if not package_id:
                    link = item.get("link") or ""
                    marker = "id="
                    package_id = link.split(marker, 1)[1].split("&", 1)[0] if marker in link else None
                if not package_id:
                    continue
                results[package_id.lower()] = {
                    "store": "Google Play",
                    "app_name": item.get("title") or "",
                    "package_id": package_id,
                    "publisher_name": item.get("developer") or item.get("author") or "Unknown publisher",
                    "store_url": item.get("link") or f"https://play.google.com/store/apps/details?id={package_id}",
                    "description": (item.get("description") or "")[:10000],
                    "icon_url": item.get("thumbnail"),
                    "icon_hash": None,
                    "version": item.get("version"),
                    "rating": item.get("rating"),
                    "raw_metadata": {"source": "serpapi_google_play_search"},
                    "is_synthetic": False,
                }
        return list(results.values())
