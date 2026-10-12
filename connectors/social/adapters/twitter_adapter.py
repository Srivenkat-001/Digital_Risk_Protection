"""Live Twitter/X adapter using the official X API v2 recent-search endpoint.

Requires X API access and TWITTER_API_BEARER_TOKEN. This collects public posts
and their public authors only; it does not access private accounts or DMs.
"""
from typing import Any

import requests

from config.settings import settings
from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand


class TwitterLiveAdapter(BaseSocialConnector):
    API_URL = "https://api.x.com/2/tweets/search/recent"

    @property
    def name(self) -> str:
        return "Twitter / X API v2"

    @property
    def platform_or_store(self) -> str:
        return "Twitter/X"

    @property
    def is_demo(self) -> bool:
        return False

    def health_check(self) -> tuple[bool, str]:
        if not settings.TWITTER_API_BEARER_TOKEN:
            return False, "Not configured: set TWITTER_API_BEARER_TOKEN and ensure X API recent-search access."
        return True, "Configured; API access is checked when a scan runs."

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        token = settings.TWITTER_API_BEARER_TOKEN
        if not token:
            raise RuntimeError("Set TWITTER_API_BEARER_TOKEN to enable X API collection.")

        terms = [brand.name] + [alias.alias for alias in (brand.aliases or [])]
        terms = [term.strip().replace('"', '') for term in terms if term and term.strip()]
        if not terms:
            return []
        query = " OR ".join(f'"{term}"' for term in terms[:5]) + " -is:retweet"
        response = requests.get(
            self.API_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={
                "query": query,
                "max_results": 100,
                "expansions": "author_id",
                "user.fields": "description,public_metrics,profile_image_url,verified,username,name",
                "tweet.fields": "created_at,lang,public_metrics",
            },
            timeout=(5, 25),
        )
        response.raise_for_status()
        payload = response.json()
        users = {
            user["id"]: user
            for user in payload.get("includes", {}).get("users", [])
            if user.get("id")
        }
        results: dict[str, dict[str, Any]] = {}
        for post in payload.get("data", []):
            user = users.get(post.get("author_id"))
            if not user or not user.get("username"):
                continue
            username = user["username"]
            metrics = user.get("public_metrics") or {}
            results[user["id"]] = {
                "platform": "Twitter/X",
                "profile_url": f"https://x.com/{username}",
                "platform_account_id": str(user["id"]),
                "username": username,
                "display_name": user.get("name") or username,
                "bio": user.get("description") or "",
                "avatar_url": user.get("profile_image_url"),
                "avatar_hash": None,
                "follower_count": int(metrics.get("followers_count") or 0),
                "raw_metadata": {
                    "source": "x_api_v2_recent_search",
                    "matched_post_id": post.get("id"),
                    "matched_post_text": post.get("text", "")[:2000],
                    "post_created_at": post.get("created_at"),
                    "verified": user.get("verified"),
                },
                "is_synthetic": False,
            }
        return list(results.values())
