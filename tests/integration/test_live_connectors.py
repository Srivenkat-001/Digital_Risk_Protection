"""Tests for public Bluesky and Apple App Store connector normalization."""

import json
from types import SimpleNamespace

import pytest
from sqlalchemy import select

from config.settings import settings
from connectors.apps.adapters.app_store_adapter import AppleAppStoreLiveAdapter
from connectors.http_json import MAX_RESPONSE_BYTES, SourceRequestError, get_json
from connectors.social.adapters.bluesky_adapter import BlueskyPublicAdapter
from db.models.candidate import CandidateAppListing, CandidateProfile
from jobs.scan_runner import run_brand_scan


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, headers: dict | None = None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def iter_content(self, chunk_size: int):
        yield self.body


def _response(payload: dict, status_code: int = 200, headers: dict | None = None) -> FakeResponse:
    return FakeResponse(payload, status_code, headers)


def test_bluesky_public_search_maps_and_deduplicates_profiles(
    test_brand, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)
    calls = []

    def fake_get(url, params, **kwargs):
        calls.append(params["q"])
        return _response(
            {
                "actors": [
                    {
                        "did": "did:plc:sample",
                        "handle": "novapay.example",
                        "displayName": "Nova Pay",
                        "description": "Payment services",
                        "followersCount": 12,
                    }
                ]
            }
        )

    monkeypatch.setattr("connectors.http_json.requests.get", fake_get)
    results = BlueskyPublicAdapter().collect_candidates(test_brand)

    assert len(calls) == 3
    assert len(results) == 1
    assert results[0]["platform"] == "Bluesky"
    assert results[0]["platform_account_id"] == "did:plc:sample"
    assert results[0]["profile_url"] == "https://bsky.app/profile/novapay.example"
    assert results[0]["raw_metadata"]["source"] == "Bluesky public AppView API"
    assert results[0]["is_synthetic"] is False


def test_apple_search_maps_store_metadata_and_deduplicates(
    test_brand, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)

    def fake_get(url, params, **kwargs):
        assert params["entity"] == "software"
        assert params["limit"] == 50
        return _response(
            {
                "results": [
                    {
                        "trackId": 123,
                        "bundleId": "io.example.novapay",
                        "trackName": "NovaPay",
                        "artistName": "Example Publisher",
                        "trackViewUrl": "https://apps.apple.com/us/app/id123",
                        "description": "A payment app",
                        "version": "2.1",
                        "averageUserRating": 4.5,
                        "userRatingCount": 27,
                        "primaryGenreName": "Finance",
                    }
                ]
            }
        )

    monkeypatch.setattr("connectors.http_json.requests.get", fake_get)
    results = AppleAppStoreLiveAdapter().collect_candidates(test_brand)

    assert len(results) == 1
    assert results[0]["store"] == "Apple App Store"
    assert results[0]["package_id"] == "io.example.novapay"
    assert results[0]["publisher_name"] == "Example Publisher"
    assert results[0]["raw_metadata"]["apple_track_id"] == 123
    assert results[0]["raw_metadata"]["category"] == "Finance"
    assert results[0]["raw_metadata"]["rating_count"] == 27
    assert results[0]["raw_metadata"]["storefront"] == "us"
    assert results[0]["is_synthetic"] is False


def test_apple_search_rejects_untrusted_urls_and_malformed_metadata(
    test_brand, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)

    def fake_get(url, params, **kwargs):
        return _response(
            {
                "results": [
                    {
                        "bundleId": "com.example.phishing",
                        "trackViewUrl": "https://attacker.example/app",
                        "artistName": "Untrusted URL",
                    },
                    {
                        "bundleId": "com.example.safe",
                        "trackViewUrl": "https://apps.apple.com/app/id1",
                        "trackName": {"unexpected": "object"},
                        "artistName": None,
                        "averageUserRating": "not a number",
                        "userRatingCount": -1,
                        "primaryGenreName": "F" * 200,
                        "contentAdvisoryRating": ["unexpected"],
                        "fileSizeBytes": -5,
                    },
                ]
            }
        )

    monkeypatch.setattr("connectors.http_json.requests.get", fake_get)
    results = AppleAppStoreLiveAdapter().collect_candidates(test_brand)

    assert len(results) == 1
    assert results[0]["package_id"] == "com.example.safe"
    assert results[0]["app_name"] == "com.example.safe"
    assert results[0]["publisher_name"] == "Unknown publisher"
    assert results[0]["rating"] is None
    assert results[0]["raw_metadata"]["rating_count"] is None
    assert len(results[0]["raw_metadata"]["category"]) == 100
    assert results[0]["raw_metadata"]["content_rating"] is None
    assert results[0]["raw_metadata"]["file_size_bytes"] is None


def test_apple_storefront_code_must_be_two_letters(
    test_brand, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)
    monkeypatch.setattr(settings, "APP_STORE_COUNTRY", "usa")

    with pytest.raises(ValueError, match="two-letter"):
        AppleAppStoreLiveAdapter().collect_candidates(test_brand)


@pytest.mark.parametrize("connector", [BlueskyPublicAdapter(), AppleAppStoreLiveAdapter()])
def test_live_connectors_are_opt_in(connector, test_brand, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", False)

    assert connector.health_check()[0] is False
    with pytest.raises(RuntimeError, match="disabled"):
        connector.collect_candidates(test_brand)


def test_public_json_helper_retries_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter(
        [
            _response({}, 429, {"Retry-After": "0"}),
            _response({"actors": []}),
        ]
    )
    monkeypatch.setattr("connectors.http_json.requests.get", lambda *args, **kwargs: next(responses))
    monkeypatch.setattr("connectors.http_json.time.sleep", lambda _: None)

    assert get_json("https://example.test/api", {}) == {"actors": []}


def test_public_json_helper_rejects_large_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _response({}, headers={"Content-Length": str(MAX_RESPONSE_BYTES + 1)})
    monkeypatch.setattr("connectors.http_json.requests.get", lambda *args, **kwargs: response)

    with pytest.raises(SourceRequestError, match="2 MiB"):
        get_json("https://example.test/api", {})


def test_public_connector_results_persist_through_scan(
    db_session, test_org, test_brand, test_users, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)

    def fake_get(url, params, **kwargs):
        if "bsky.app" in url:
            return _response(
                {
                    "actors": [
                        {
                            "did": "did:plc:novapaylookalike",
                            "handle": "novapay-support.example",
                            "displayName": "NovaPay Support",
                            "description": "Verify your wallet to receive a reward.",
                            "followersCount": 40,
                        }
                    ]
                }
            )
        return _response(
            {
                "results": [
                    {
                        "trackId": 321,
                        "bundleId": "com.example.novapay.copy",
                        "trackName": "NovaPay Support Rewards",
                        "artistName": "Example Apps",
                        "trackViewUrl": "https://apps.apple.com/us/app/id321",
                        "description": "Verify your wallet to claim a payment reward.",
                    }
                ]
            }
        )

    monkeypatch.setattr("connectors.http_json.requests.get", fake_get)
    job = run_brand_scan(db_session, test_brand.id, test_org.id, test_users["admin"].id)

    bluesky_candidate = db_session.scalars(
        select(CandidateProfile).where(CandidateProfile.platform_account_id == "did:plc:novapaylookalike")
    ).one()
    app_candidate = db_session.scalars(
        select(CandidateAppListing).where(CandidateAppListing.package_id == "com.example.novapay.copy")
    ).one()

    assert job.status == "completed"
    assert not bluesky_candidate.is_synthetic
    assert "Bluesky public AppView API" in bluesky_candidate.raw_metadata
    assert not app_candidate.is_synthetic
    assert "Apple iTunes Search API" in app_candidate.raw_metadata


def test_social_live_only_scan_does_not_add_synthetic_profiles(
    db_session, test_org, test_brand, test_users, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)

    def fake_get(url, params, **kwargs):
        return _response(
            {
                "actors": [
                    {
                        "did": "did:plc:liveonly",
                        "handle": "novapay-live.example",
                        "displayName": "NovaPay Live",
                        "description": "Public profile",
                        "followersCount": 4,
                    }
                ]
            }
        )

    monkeypatch.setattr("connectors.http_json.requests.get", fake_get)
    job = run_brand_scan(
        db_session,
        test_brand.id,
        test_org.id,
        test_users["admin"].id,
        source_types=["social"],
        include_demo_sources=False,
    )
    profiles = list(
        db_session.scalars(
            select(CandidateProfile).where(CandidateProfile.organization_id == test_org.id)
        ).all()
    )

    assert job.status == "completed"
    assert job.total_candidates_found == 1
    assert len(profiles) == 1
    assert profiles[0].platform == "Bluesky"
    assert profiles[0].is_synthetic is False


def test_live_app_observation_replaces_demo_source_label(
    db_session, test_org, test_brand
) -> None:
    from db.repositories.candidate_repo import CandidateRepository

    repo = CandidateRepository(db_session)
    demo_candidate, created = repo.upsert_app_candidate(
        organization_id=test_org.id,
        brand_id=test_brand.id,
        store="Apple App Store",
        app_name="Sample Wallet",
        package_id="com.example.wallet",
        publisher_name="Sample Publisher",
        store_url="https://apps.apple.com/us/app/id123",
        raw_metadata={"source": "synthetic demo"},
        is_synthetic=True,
    )
    assert created and demo_candidate.is_synthetic

    updated, created_again = repo.upsert_app_candidate(
        organization_id=test_org.id,
        brand_id=test_brand.id,
        store="Apple App Store",
        app_name="Sample Wallet",
        package_id="com.example.wallet",
        publisher_name="Sample Publisher",
        store_url="https://apps.apple.com/us/app/id123",
        raw_metadata={"source": "Apple iTunes Search API"},
        is_synthetic=False,
    )

    assert not created_again
    assert updated.id == demo_candidate.id
    assert not updated.is_synthetic
    assert "Apple iTunes Search API" in updated.raw_metadata


def test_live_social_observation_replaces_demo_source_label(
    db_session, test_org, test_brand
) -> None:
    from db.repositories.candidate_repo import CandidateRepository

    repo = CandidateRepository(db_session)
    demo_candidate, created = repo.upsert_social_candidate(
        organization_id=test_org.id,
        brand_id=test_brand.id,
        platform="Bluesky",
        profile_url="https://bsky.app/profile/acme.example",
        username="acme.example",
        display_name="Acme",
        raw_metadata={"source": "synthetic demo"},
        is_synthetic=True,
    )
    assert created and demo_candidate.is_synthetic

    updated, created_again = repo.upsert_social_candidate(
        organization_id=test_org.id,
        brand_id=test_brand.id,
        platform="Bluesky",
        profile_url="https://bsky.app/profile/acme.example",
        username="acme.example",
        display_name="Acme",
        raw_metadata={"source": "Bluesky public AppView API"},
        is_synthetic=False,
    )

    assert not created_again
    assert updated.id == demo_candidate.id
    assert not updated.is_synthetic
    assert "Bluesky public AppView API" in updated.raw_metadata


@pytest.mark.live
def test_bluesky_public_endpoint_returns_profile_results_when_reachable() -> None:
    from connectors.http_json import get_json

    payload = get_json(
        "https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors",
        {"q": "github", "limit": 1},
    )
    assert isinstance(payload.get("actors"), list)
    assert payload["actors"], "Expected the public search endpoint to return a profile for 'github'."


@pytest.mark.live
def test_apple_public_connector_returns_normalized_live_app_when_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "LIVE_CONNECTORS_ENABLED", True)
    brand = SimpleNamespace(name="github", aliases=[], logos=[])
    candidates = AppleAppStoreLiveAdapter().collect_candidates(brand)

    assert candidates, "Expected the public Apple search endpoint to return an app for 'github'."
    assert all(candidate["is_synthetic"] is False for candidate in candidates)
    assert all(candidate["raw_metadata"]["source"] == "Apple iTunes Search API" for candidate in candidates)
    assert all(candidate["store_url"].startswith("https://apps.apple.com/") for candidate in candidates)
