"""
Integration tests for the complete monitoring scan pipeline:
connectors -> normalization -> deduplication -> trusted exclusion -> detection -> persistence.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from connectors.social.demo import DemoSocialConnector
from db.models.candidate import CandidateAppListing, CandidateProfile
from db.models.finding import Finding
from jobs.scan_runner import run_brand_scan
from services.finding_service import FindingService


def test_demo_social_connector_has_labeled_examples_for_supported_platforms(test_brand):
    candidates = DemoSocialConnector().collect_candidates(test_brand)
    platforms = {candidate["platform"] for candidate in candidates}

    assert platforms == {
        "Twitter/X",
        "Instagram",
        "Facebook",
        "TikTok",
        "LinkedIn",
        "Telegram",
        "Bluesky",
    }
    assert all(candidate["is_synthetic"] for candidate in candidates)
    assert all(candidate["profile_url"].startswith("https://example.com/demo/") for candidate in candidates)
    assert all(candidate["raw_metadata"]["source"] == "BrandPhantom synthetic demo generator" for candidate in candidates)


def test_full_scan_pipeline_execution(db_session: Session, test_org, test_brand, test_users):
    scan_job = run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
    )
    assert scan_job.status in ("completed", "partial")
    assert scan_job.total_candidates_found == 26
    assert scan_job.excluded_assets_count == 2  # 1 official social account + 1 official app listing
    assert scan_job.new_findings_count == 24

    # 1. Verify Official Twitter Asset is excluded
    stmt_soc = select(CandidateProfile).where(
        CandidateProfile.brand_id == test_brand.id,
        CandidateProfile.username == "novapayofficial"
    )
    official_soc = db_session.scalars(stmt_soc).first()
    assert official_soc is not None
    assert official_soc.is_excluded is True

    # Ensure NO finding was created for official asset
    finding_official = db_session.scalars(
        select(Finding).where(Finding.candidate_id == official_soc.id)
    ).first()
    assert finding_official is None

    # 2. Verify Official App Listing is excluded
    stmt_app = select(CandidateAppListing).where(
        CandidateAppListing.brand_id == test_brand.id,
        CandidateAppListing.package_id == "com.novapay.wallet"
    )
    official_app = db_session.scalars(stmt_app).first()
    assert official_app is not None
    assert official_app.is_excluded is True

    # Ensure NO finding was created for official app
    finding_official_app = db_session.scalars(
        select(Finding).where(Finding.candidate_id == official_app.id)
    ).first()
    assert finding_official_app is None

    # 3. Verify Findings have signals, assessment, and evidence
    fake_support_soc = db_session.scalars(
        select(CandidateProfile).where(CandidateProfile.username == "novapay_help")
    ).first()
    assert fake_support_soc is not None
    assert fake_support_soc.is_excluded is False

    finding_fake = db_session.scalars(
        select(Finding).where(Finding.candidate_id == fake_support_soc.id)
    ).first()
    assert finding_fake is not None
    assert finding_fake.severity in ("High", "Critical")
    assert len(finding_fake.signals) > 0
    assert finding_fake.assessment is not None
    assert len(finding_fake.evidence_items) > 0


def test_demo_only_scan_creates_examples_without_live_sources(
    db_session: Session, test_org, test_brand, test_users
):
    scan_job = run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
        source_types=["social"],
        include_live_sources=False,
    )
    profiles = db_session.scalars(
        select(CandidateProfile).where(CandidateProfile.brand_id == test_brand.id)
    ).all()

    assert scan_job.status == "completed"
    assert scan_job.total_candidates_found == 22
    assert len(profiles) == 22
    assert all(profile.is_synthetic for profile in profiles)


def test_scan_deduplication(db_session: Session, test_org, test_brand, test_users):
    # Run scan twice
    run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
    )
    second_job = run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
    )

    # Second scan should observe existing candidates, but create 0 new findings
    assert second_job.new_findings_count == 0

    # The demo produces 22 synthetic social examples across seven platforms.
    total_profiles = db_session.query(CandidateProfile).count()
    assert total_profiles == 22


def test_finding_status_rejects_unknown_values(db_session: Session, test_org, test_brand, test_users):
    run_brand_scan(db_session, test_brand.id, test_org.id, test_users["admin"].id)
    finding = FindingService(db_session).list_findings(test_org.id)[0]

    with pytest.raises(ValueError, match="Unsupported finding review status"):
        FindingService(db_session).update_status(finding.id, test_org.id, "arbitrary status")


def test_rescan_refreshes_finding_evidence_and_score(db_session: Session, test_org, test_brand, test_users, monkeypatch):
    run_brand_scan(db_session, test_brand.id, test_org.id, test_users["admin"].id)
    candidate = db_session.scalars(
        select(CandidateProfile).where(CandidateProfile.username == "novapay_help")
    ).first()
    finding = FindingService(db_session).repo.get_by_candidate("social", candidate.id)
    assert any(item.evidence_type == "scam_intent_keywords" for item in finding.evidence_items)

    original_collect = DemoSocialConnector.collect_candidates

    def collect_without_scam_text(connector, brand):
        candidates = original_collect(connector, brand)
        candidates[1] = {
            **candidates[1],
            "bio": "A community profile sharing financial product release notes.",
        }
        return candidates

    monkeypatch.setattr(DemoSocialConnector, "collect_candidates", collect_without_scam_text)
    second_scan = run_brand_scan(db_session, test_brand.id, test_org.id, test_users["admin"].id)
    refreshed = FindingService(db_session).get_finding(finding.id, test_org.id)

    scam_signal = next(signal for signal in refreshed.signals if signal.signal_name == "scam_intent")
    assert second_scan.new_findings_count == 0
    assert refreshed.scan_job_id == second_scan.id
    assert scam_signal.signal_value == 0.0
    assert not any(item.evidence_type == "scam_intent_keywords" for item in refreshed.evidence_items)
    assert refreshed.assessment.score == refreshed.risk_score
