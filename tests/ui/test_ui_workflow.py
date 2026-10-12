"""
UI and critical workflow tests.
Tests end-to-end user journeys through services and session logic.
"""

import io

import pandas as pd
from sqlalchemy.orm import Session

from jobs.scan_runner import run_brand_scan
from services.auth import AuthService
from services.case_service import CaseService
from services.dashboard_service import DashboardService
from services.finding_service import FindingService


def test_user_authentication_workflow(db_session: Session, test_org):
    auth = AuthService(db_session)
    org, admin = auth.seed_default_users_and_org()

    # The local evaluator shortcut is demo-only; seeded demo users have random, undisclosed passwords.
    user = auth.authenticate_demo_user("admin@brandphantom.io")
    assert user is not None
    assert user.email == "admin@brandphantom.io"

    assert auth.authenticate_user("admin@brandphantom.io", "not-the-random-seed-password") is None

def test_full_analyst_triage_workflow(db_session: Session, test_org, test_brand, test_users):
    # 1. Execute scan
    scan = run_brand_scan(
        db=db_session,
        brand_id=test_brand.id,
        organization_id=test_org.id,
        triggered_by_user_id=test_users["analyst"].id,
    )
    assert scan.new_findings_count > 0

    # 2. View dashboard
    dash = DashboardService(db_session)
    metrics = dash.get_dashboard_summary(test_org.id)
    assert metrics["total_findings"] > 0
    assert metrics["total_brands"] == 1

    # 3. Triage finding
    finding_svc = FindingService(db_session)
    f = finding_svc.list_findings(test_org.id)[0]
    finding_svc.update_status(f.id, test_org.id, "Investigating", user_id=test_users["analyst"].id)

    # 4. Open case and resolve
    case_svc = CaseService(db_session)
    case = case_svc.open_investigation_from_finding(
        organization_id=test_org.id,
        finding_id=f.id,
        title="Active Impersonation Case",
        priority="high",
        user_id=test_users["analyst"].id,
    )
    case_svc.add_note(case.id, test_org.id, "Evidence confirmed.", test_users["analyst"].id)
    case_svc.update_case_status(case.id, test_org.id, "resolved", "Threat eliminated.")

    # 5. Export reports
    findings = finding_svc.list_findings(test_org.id)
    rows = [{"ID": f_item.id, "Score": f_item.risk_score, "Status": f_item.review_status} for f_item in findings]
    df = pd.DataFrame(rows)
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_content = csv_buf.getvalue()
    assert "ID,Score,Status" in csv_content
    assert len(csv_content.splitlines()) == len(findings) + 1
