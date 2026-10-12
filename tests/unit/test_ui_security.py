from types import SimpleNamespace

import pytest

from connectors.apps.adapters.app_store_adapter import AppleAppStoreLiveAdapter
from connectors.apps.adapters.play_store_adapter import GooglePlayLiveAdapter
from connectors.apps.demo import DemoAppConnector
from connectors.social.adapters.instagram_adapter import InstagramLiveAdapter
from connectors.social.adapters.twitter_adapter import TwitterLiveAdapter
from connectors.social.demo import DemoSocialConnector
from ui.components.risk_badges import render_risk_badge, render_status_badge
from ui.pages.reports import safe_csv_cell


def test_badge_text_is_escaped():
    assert "<script>" not in render_status_badge("<script>alert(1)</script>")
    assert "<img" not in render_risk_badge('High"><img src=x onerror=alert(1)>')


def test_csv_text_cannot_start_a_spreadsheet_formula():
    assert safe_csv_cell('=HYPERLINK("https://example.invalid")') == "'=HYPERLINK(\"https://example.invalid\")"
    assert safe_csv_cell("  @SUM(A1:A2)") == "'  @SUM(A1:A2)"
    assert safe_csv_cell(-5.0) == -5.0


def test_demo_candidates_follow_configured_brand():
    brand = SimpleNamespace(name="Acme", description="Payments", logos=[])

    social_candidates = DemoSocialConnector().collect_candidates(brand)
    app_candidates = DemoAppConnector().collect_candidates(brand)

    assert all(candidate["is_synthetic"] for candidate in social_candidates + app_candidates)
    assert social_candidates[2]["username"] != "N0vaPay"
    assert "Acme" in social_candidates[2]["bio"]
    assert app_candidates[2]["app_name"] == "Acme Payment Gateway SDK"
    assert app_candidates[2]["package_id"] == "org.acme.gateway"


def test_unimplemented_live_adapters_are_reported_unavailable():
    brand = SimpleNamespace(name="Acme", description="Payments", logos=[])
    for adapter in (
        TwitterLiveAdapter(),
        InstagramLiveAdapter(),
        GooglePlayLiveAdapter(),
    ):
        healthy, message = adapter.health_check()
        assert not healthy
        assert "not implemented" in message
        with pytest.raises(NotImplementedError, match="not implemented"):
            adapter.collect_candidates(brand)


def test_apple_public_adapter_is_disabled_by_default(test_brand):
    adapter = AppleAppStoreLiveAdapter()
    healthy, message = adapter.health_check()

    assert not healthy
    assert "Disabled by configuration" in message
    with pytest.raises(RuntimeError, match="disabled"):
        adapter.collect_candidates(test_brand)
