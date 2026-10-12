"""
Integration tests for Finding triage, Investigations, and audit logging.
"""

from sqlalchemy.orm import Session

from db.models.audit import AuditLog
from jobs.scan_runner import run_brand_scan
from services.case_service import CaseService
from services.finding_service import FindingService


def test_finding_triage_and_investigation_lifecycle(db_session: Session, test_org, test_brand, test_users):
    run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
    )

    finding_service = FindingService(db_session)
    case_service = CaseService(db_session)

    findings = finding_service.list_findings(test_org.id)
    assert len(findings) > 0

    target_finding = findings[0]
    assert target_finding.review_status == "New"

    # 1. Update finding status to 'Investigating'
    finding_service.update_status(
        finding_id=target_finding.id,
        organization_id=test_org.id,
        review_status="Investigating",
        user_id=test_users["analyst"].id,
        notes="Opening investigation case.",
    )
    assert target_finding.review_status == "Investigating"

    # 2. Open formal investigation case
    case = case_service.open_investigation_from_finding(
        organization_id=test_org.id,
        finding_id=target_finding.id,
        title="Impersonation Telemetry Inquiry",
        priority="high",
        summary="Suspicious profile imitating official brand handles.",
        assigned_to_user_id=test_users["analyst"].id,
        user_id=test_users["analyst"].id,
    )
    assert case.id is not None
    assert case.case_number.startswith("CASE-")
    assert case.status == "open"

    # 3. Add analyst note
    note = case_service.add_note(
        case_id=case.id,
        organization_id=test_org.id,
        note_text="Identified matching logo hash and high token similarity.",
        author_user_id=test_users["analyst"].id,
    )
    assert note.id is not None
    assert len(case.notes) == 1

    # 4. Resolve case
    case_service.update_case_status(
        case_id=case.id,
        organization_id=test_org.id,
        status="resolved",
        resolution_reason="Confirmed fraudulent account reported to provider.",
        user_id=test_users["analyst"].id,
    )
    assert case.status == "resolved"
    assert target_finding.review_status == "Resolved"

    # 5. Check audit logs
    audit_count = db_session.query(AuditLog).filter(AuditLog.organization_id == test_org.id).count()
    assert audit_count >= 3

def test_false_positive_marking(db_session: Session, test_org, test_brand, test_users):
    run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["admin"].id,
    )

    finding_service = FindingService(db_session)
    findings = finding_service.list_findings(test_org.id)

    # Mark second finding as False Positive
    f2 = findings[1]
    finding_service.update_status(
        finding_id=f2.id,
        organization_id=test_org.id,
        review_status="False Positive",
        user_id=test_users["analyst"].id,
        notes="Legitimate unrelated entity verified by registry check.",
    )
    assert f2.review_status == "False Positive"
