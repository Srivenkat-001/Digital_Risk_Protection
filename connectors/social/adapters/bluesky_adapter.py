"""Public Bluesky profile search using the official public AppView API."""

import re
from typing import Any

from config.settings import settings
from connectors.http_json import collected_at, get_json
from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand

API_URL = "https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors"
MAX_QUERIES = 3
MAX_RESULTS = 75
VALID_HANDLE = re.compile(r"^[a-z0-9.-]{1,253}$")


class BlueskyPublicAdapter(BaseSocialConnector):
    """Search public Bluesky profiles; no login or private-account access is used."""

    @property
    def name(self) -> str:
        return "Bluesky Public Profile Search"

    @property
    def platform_or_store(self) -> str:
        return "Bluesky"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        if not settings.LIVE_CONNECTORS_ENABLED:
            return False, "Disabled by configuration; enable LIVE_CONNECTORS_ENABLED to query public profiles."
        return True, "Enabled; public API reachability is checked when a scan runs."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        if not settings.LIVE_CONNECTORS_ENABLED:
            raise RuntimeError("Bluesky collection is disabled. Enable LIVE_CONNECTORS_ENABLED to proceed.")

        queries = list(dict.fromkeys([brand.name, *(alias.alias for alias in brand.aliases)]))[:MAX_QUERIES]
        candidates: dict[str, dict[str, Any]] = {}
        for query in queries:
            payload = get_json(API_URL, {"q": query, "limit": 50})
            actors = payload.get("actors", [])
            if not isinstance(actors, list):
                continue
            for actor in actors:
                if not isinstance(actor, dict):
                    continue
                did = actor.get("did")
                handle = actor.get("handle")
                if (
                    not isinstance(did, str)
                    or len(did) > 300
                    or not isinstance(handle, str)
                    or not VALID_HANDLE.fullmatch(handle.lower())
                ):
                    continue
                display_name = actor.get("displayName")
                description = actor.get("description")
                avatar = actor.get("avatar")
                followers = actor.get("followersCount")
                candidates[did] = {
                    "platform": "Bluesky",
                    "profile_url": f"https://bsky.app/profile/{handle}",
                    "platform_account_id": did,
                    "username": handle,
                    "display_name": (display_name[:255] if isinstance(display_name, str) else handle),
                    "bio": description[:20000] if isinstance(description, str) else None,
                    "avatar_url": avatar[:500] if isinstance(avatar, str) and avatar.startswith("https://") else None,
                    "follower_count": followers if isinstance(followers, int) and followers >= 0 else 0,
                    "raw_metadata": {
                        "source": "Bluesky public AppView API",
                        "collected_at": collected_at(),
                    },
                    "is_synthetic": False,
                }
                if len(candidates) >= MAX_RESULTS:
                    break
            if len(candidates) >= MAX_RESULTS:
                break
        return list(candidates.values())
