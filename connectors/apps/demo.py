"""
Deterministic demo mobile app connector for simulated app store discovery.
Supplies synthetic app listings labeled clearly as synthetic data.
"""

import re
from typing import Any

from connectors.apps.base import BaseAppConnector
from db.models.brand import Brand


class DemoAppConnector(BaseAppConnector):
    """Generates deterministic synthetic mobile app listings for testing and demonstration."""

    @property
    def name(self) -> str:
        return "Google Play & App Store Demo Connector (Synthetic)"

    @property
    def platform_or_store(self) -> str:
        return "Google Play"

    @property
    def is_demo(self) -> bool:
        return True

    def health_check(self) -> tuple[bool, str]:
        return True, "Operational (Synthetic Sandbox Mode Active)"

    def collect_candidates(self, brand: Brand) -> list[dict[str, Any]]:
        brand_clean = re.sub(r"[^a-z0-9]", "", brand.name.lower()) or "brand"
        logo_hash = brand.logos[0].perceptual_hash if (brand.logos and brand.logos[0].perceptual_hash) else "a1b2c3d4e5f60000"

        candidates = [
            # 1. Verified official application (Will be excluded by official package ID)
            {
                "store": "Google Play",
                "app_name": f"{brand.name}: Digital Wallet & Pay",
                "package_id": f"com.{brand_clean}.wallet",
                "publisher_name": f"{brand.name} Technologies Inc.",
                "store_url": f"https://play.google.com/store/apps/details?id=com.{brand_clean}.wallet",
                "description": f"Official mobile application of {brand.name}. Manage payments, bank transfers, and digital cards.",
                "icon_url": "https://example.com/assets/novapay_app_icon.png",
                "icon_hash": logo_hash,
                "version": "4.2.1",
                "rating": 4.7,
                "is_synthetic": True,
            },
            # 2. Suspicious look-alike scam application (Publisher Mismatch + predatory loan triggers)
            {
                "store": "Google Play",
                "app_name": f"{brand.name} - Instant Loan & Cash",
                "package_id": f"com.fastcash.{brand_clean}",
                "publisher_name": "Unknown Dev Corp",
                "store_url": f"https://play.google.com/store/apps/details?id=com.fastcash.{brand_clean}",
                "description": f"Get fast instant loan and cash advance with no credit check! Guaranteed instant approval directly into your {brand.name} account. Activation fee applies.",
                "icon_url": "https://example.com/assets/scam_app_icon.png",
                "icon_hash": logo_hash,  # Visual imitation
                "version": "1.0.0",
                "rating": 2.1,
                "is_synthetic": True,
            },
            # 3. Candidate with insufficient evidence (Developer SDK with missing icon hash)
            {
                "store": "Google Play",
                "app_name": f"{brand.name} Payment Gateway SDK",
                "package_id": f"org.{brand_clean}.gateway",
                "publisher_name": "Nova OpenSource Collective",
                "store_url": "https://play.google.com/store/apps/details?id=org.novasdk.gateway",
                "description": "Developer utility for sandbox testing checkout flows.",
                "icon_url": None,
                "icon_hash": None,  # Explicit missing icon test
                "version": "0.4.0",
                "rating": 3.8,
                "is_synthetic": True,
            },
            # 4. False-positive example (Legitimate unrelated enterprise payroll tool)
            {
                "store": "Google Play",
                "app_name": "Nova Payroll Manager",
                "package_id": "com.novacorp.payroll",
                "publisher_name": "Nova Corp B2B Solutions",
                "store_url": "https://play.google.com/store/apps/details?id=com.novacorp.payroll",
                "description": "Enterprise human resources time-tracking, shift rostering, and corporate payroll management software.",
                "icon_url": "https://example.com/assets/payroll_icon.png",
                "icon_hash": "ffff888800001111",
                "version": "2.8.5",
                "rating": 4.4,
                "is_synthetic": True,
            },
        ]
        return candidates
