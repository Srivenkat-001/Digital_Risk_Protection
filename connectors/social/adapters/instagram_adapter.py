"""Instagram Graph API Business Discovery adapter.

Meta's API does not provide unrestricted search across all Instagram accounts.
This adapter checks plausible brand/look-alike usernames through Business
Discovery and therefore requires an eligible Instagram professional account.
"""
from typing import Any

import requests

from config.settings import settings
from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand


class InstagramLiveAdapter(BaseSocialConnector):
    @property
    def name(self) -> str:
        return "Instagram Graph API Business Discovery"

    @property
    def platform_or_store(self) -> str:
        return "Instagram"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            return False, "Not configured: set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID for an eligible professional account."
        return True, "Configured; Meta API access is checked when a scan runs."

    @staticmethod
    def _username_variants(brand: Brand) -> list[str]:
        bases = [brand.name] + [alias.alias for alias in (brand.aliases or [])]
        suffixes = ("", "official", "help", "support", "care", "customer", "secure", "verify")
        variants: list[str] = []
        for base in bases:
            cleaned = "".join(ch.lower() for ch in base if ch.isalnum())
            if cleaned:
                for suffix in suffixes:
                    candidate = cleaned + suffix
                    if candidate not in variants:
                        variants.append(candidate)
        for account in (brand.official_social_accounts or []):
            if (account.platform or "").lower() == "instagram" and account.handle:
                handle = account.handle.lstrip("@").lower()
                if handle not in variants:
                    variants.insert(0, handle)
        return variants[:30]

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            raise RuntimeError("Configure INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID.")
        version = settings.META_GRAPH_API_VERSION
        base_url = f"https://graph.facebook.com/{version}/{settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}"
        found: dict[str, dict[str, Any]] = {}
        for username in self._username_variants(brand):
            response = requests.get(
                base_url,
                params={
                    "fields": f"business_discovery.username({username}){{username,name,biography,followers_count,profile_picture_url,id}}",
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                },
                timeout=(5, 20),
            )
            # A missing username or a profile outside API eligibility is not a scan failure.
            if response.status_code in (400, 404):
                continue
            response.raise_for_status()
            profile = response.json().get("business_discovery")
            if not profile or not profile.get("username"):
                continue
            handle = profile["username"]
            found[handle.lower()] = {
                "platform": "Instagram",
                "profile_url": f"https://www.instagram.com/{handle}/",
                "platform_account_id": str(profile.get("id") or handle),
                "username": handle,
                "display_name": profile.get("name") or handle,
                "bio": profile.get("biography") or "",
                "avatar_url": profile.get("profile_picture_url"),
                "avatar_hash": None,
                "follower_count": int(profile.get("followers_count") or 0),
                "raw_metadata": {"source": "instagram_graph_business_discovery"},
                "is_synthetic": False,
            }
        return list(found.values())
