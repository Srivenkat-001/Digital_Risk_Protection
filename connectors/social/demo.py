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
        return "Twitter/X"

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

        # Deterministic candidates modeled on NovaPay threats
        candidates = [
            # 1. Verified official profile (Will be excluded by exclusion engine)
            {
                "platform": "Twitter/X",
                "profile_url": f"https://twitter.com/{brand_clean}Official",
                "platform_account_id": f"tw-{brand_clean.lower()}-official-001",
                "username": f"{brand_clean}Official",
                "display_name": f"{brand.name} Official",
                "bio": f"Official verified presence of {brand.name}. {brand.description or 'Secure payments and customer transactions.'}",
                "avatar_url": "https://example.com/assets/novapay_logo.png",
                "avatar_hash": logo_hash,
                "follower_count": 85400,
                "is_synthetic": True,
            },
            # 2. Fake Support Look-alike Profile (High Risk)
            {
                "platform": "Twitter/X",
                "profile_url": f"https://twitter.com/{brand_clean}_Help",
                "platform_account_id": "tw-synthetic-fake-002",
                "username": f"{brand_clean}_Help",
                "display_name": f"{brand.name} Customer Care Desk",
                "bio": f"24/7 Official Customer Support for {brand.name}. Having account issues? DM us or contact our resolution desk to unlock your wallet.",
                "avatar_url": "https://example.com/assets/fake_support.png",
                "avatar_hash": logo_hash,  # Identical logo hash
                "follower_count": 210,
                "is_synthetic": True,
            },
            # 3. Phishing / Leetspeak Profile (Critical Risk)
            {
                "platform": "Twitter/X",
                "profile_url": f"https://twitter.com/{brand_handle}",
                "platform_account_id": f"tw-synthetic-lookalike-{brand_clean.lower()}-003",
                "username": brand_handle,
                "display_name": f"{brand.name} Rewards & Bonus",
                "bio": f"Limited {brand.name} reward! Verify your account and wallet connect below to claim a free bonus.",
                "avatar_url": "https://example.com/assets/phishing_avatar.png",
                "avatar_hash": logo_hash,
                "follower_count": 1240,
                "is_synthetic": True,
            },
            # 4. Legitimate Unrelated Organization (Low Risk)
            {
                "platform": "Twitter/X",
                "profile_url": "https://twitter.com/novapayne_photo",
                "platform_account_id": "tw-synthetic-unrelated-004",
                "username": "novapayne_photo",
                "display_name": "Nova Payne Photography",
                "bio": "Professional wedding and portrait photographer based in Seattle, WA. Portfolio inquiries welcome.",
                "avatar_url": "https://example.com/assets/photo_avatar.png",
                "avatar_hash": "ffff0000aaaa5555",
                "follower_count": 3400,
                "is_synthetic": True,
            },
        ]
        return candidates
