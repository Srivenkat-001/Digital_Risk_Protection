"""
Deterministic demo social media connector for simulated risk discovery.
Supplies synthetic profiles labeled clearly as synthetic data.
"""

import re
from typing import Any

from connectors.social.base import BaseSocialConnector
from db.models.brand import Brand


class DemoSocialConnector(BaseSocialConnector):
    """Generates deterministic synthetic social media candidates for testing and demonstration."""

    @property
    def name(self) -> str:
        return "Social Media Demo Connector (Synthetic)"

    @property
    def platform_or_store(self) -> str:
        return "Multiple social platforms (synthetic)"

    @property
    def is_demo(self) -> bool:
        return True

    def health_check(self) -> tuple[bool, str]:
        return True, "Operational (Synthetic Sandbox Mode Active)"

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        brand_clean = re.sub(r"[^A-Za-z0-9]", "", brand.name)
        brand_handle = brand_clean.lower()
        for original, replacement in (("o", "0"), ("a", "4"), ("e", "3"), ("i", "1"), ("s", "5")):
            if original in brand_handle:
                brand_handle = brand_handle.replace(original, replacement, 1)
                break
        else:
            brand_handle += "1"
        logo_hash = brand.logos[0].perceptual_hash if (brand.logos and brand.logos[0].perceptual_hash) else "a1b2c3d4e5f60000"

        platforms = (
            ("Twitter/X", "twitter-x"),
            ("Instagram", "instagram"),
            ("Facebook", "facebook"),
            ("TikTok", "tiktok"),
            ("LinkedIn", "linkedin"),
            ("Telegram", "telegram"),
            ("Bluesky", "bluesky"),
        )
        candidates = []
        for platform, slug in platforms:
            examples = []
            if platform == "Twitter/X":
                examples.append(
                    {
                        "username": f"{brand_clean}Official",
                        "display_name": f"{brand.name} Official",
                        "bio": (
                            f"Official verified presence of {brand.name}. "
                            f"{brand.description or 'Secure payments and customer transactions.'}"
                        ),
                        "avatar_hash": logo_hash,
                        "follower_count": 85400,
                        "kind": "official-example",
                    }
                )

            examples.extend(
                [
                    {
                        "username": f"{brand_clean}_Help",
                        "display_name": f"{brand.name} Customer Care Desk",
                        "bio": (
                            f"24/7 Official Customer Support for {brand.name}. Having account issues? "
                            "DM us or contact our resolution desk to unlock your wallet."
                        ),
                        "avatar_hash": logo_hash,
                        "follower_count": 210,
                        "kind": "support-lookalike",
                    },
                    {
                        "username": brand_handle,
                        "display_name": f"{brand.name} Rewards & Bonus",
                        "bio": (
                            f"Limited {brand.name} reward! Verify your account and wallet connect below "
                            "to claim a free bonus."
                        ),
                        "avatar_hash": logo_hash,
                        "follower_count": 1240,
                        "kind": "lookalike",
                    },
                    {
                        "username": f"{brand_clean}_community",
                        "display_name": "Nova Payne Photography",
                        "bio": (
                            "Professional wedding and portrait photographer. "
                            "Portfolio inquiries welcome."
                        ),
                        "avatar_hash": "ffff0000aaaa5555",
                        "follower_count": 3400,
                        "kind": "unrelated",
                    },
                ]
            )

            for example in examples:
                username = example["username"]
                kind = example["kind"]
                candidates.append(
                    {
                        "platform": platform,
                        "profile_url": f"https://example.com/demo/{slug}/{username}",
                        "platform_account_id": f"demo-{slug}-{brand_clean.lower()}-{kind}",
                        "username": username,
                        "display_name": example["display_name"],
                        "bio": example["bio"],
                        "avatar_url": None,
                        "avatar_hash": example["avatar_hash"],
                        "follower_count": example["follower_count"],
                        "raw_metadata": {
                            "source": "BrandPhantom synthetic demo generator",
                            "limitation": "Example profile only; this account was not found on the platform.",
                        },
                        "is_synthetic": True,
                    }
                )
        return candidates
