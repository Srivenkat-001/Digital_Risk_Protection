"""Tenant-scoped project assistant record-search tests."""

from jobs.scan_runner import run_brand_scan
from services.project_assistant import search_project_data


def test_assistant_returns_saved_candidate_raw_data_and_finding(
    db_session, test_org, test_brand, test_users
):
    run_brand_scan(
        db_session,
        test_brand.id,
        test_org.id,
        test_users["admin"].id,
        source_types=["social"],
        include_live_sources=False,
    )

    result = search_project_data(
        db_session,
        organization_id=test_org.id,
        question="novapay help fake account raw metadata",
        brand_id=test_brand.id,
    )

    assert result["external_ai_used"] is False
    assert result["organization_record_count"] == 22
    assert result["match_count"] > 0
    match = next(
        record
        for record in result["matched_records"]
        if record["username"] == "novapay_help"
    )
    assert match["synthetic"] is True
    assert match["source_metadata"]["source"] == "BrandPhantom synthetic demo generator"
    assert match["finding"]["severity"] in {"High", "Critical"}
    assert match["finding"]["signals"]


def test_assistant_never_returns_records_from_another_organization(
    db_session, test_org, test_brand, test_users
):
    run_brand_scan(
        db_session,
        test_brand.id,
        test_org.id,
        test_users["admin"].id,
        source_types=["social"],
        include_live_sources=False,
    )

    result = search_project_data(
        db_session,
        organization_id="not-the-test-organization",
        question="novapay",
    )

    assert result["organization_record_count"] == 0
    assert result["finding_count"] == 0
    assert result["matched_records"] == []
