"""
Reports & Data Export page.
Generates executive risk summaries, threat-to-false-positive distributions,
and authorized tenant-isolated CSV export downloads.
"""

import io

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from services.auth import AuthService
from services.dashboard_service import DashboardService
from services.finding_service import FindingService


def safe_csv_cell(value):
    """Prevent spreadsheet applications from evaluating exported text as a formula."""
    if isinstance(value, str) and value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def render(db: Session, organization_id: str, brand_id: str | None = None):
    finding_service = FindingService(db)
    dashboard_service = DashboardService(db)
    user_role = st.session_state.get("role", "viewer")
    can_export = AuthService.is_authorized(user_role, "viewer")  # Viewers can download filtered reports

    st.markdown("## 📑 Security Reports & Data Export")
    st.caption("Generate executive-ready audit reports and export tenant-isolated monitoring records.")

    # High-level summary metrics
    summary = dashboard_service.get_dashboard_summary(organization_id, brand_id)

    st.markdown("### Executive Risk Posture Summary")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Total Findings", summary["total_findings"])
    with r2:
        st.metric("Confirmed Threats", summary["confirmed_threats"])
    with r3:
        st.metric("False Positives Cleared", summary["false_positives"])
    with r4:
        st.metric("Active Investigations", summary["open_cases_count"])

    st.markdown("---")

    # Findings Table for Export
    st.markdown("### Findings Export Dataset")
    findings = finding_service.list_findings(organization_id, brand_id=brand_id, limit=500)

    if not findings:
        st.info("No findings available to generate reports.")
        return

    # Build export dataframe
    rows = []
    for f in findings:
        cand = finding_service.get_candidate_for_finding(f)
        target_name = ""
        target_identifier = ""
        if f.candidate_type == "social" and cand:
            target_name = cand.display_name
            target_identifier = f"@{cand.username}"
        elif f.candidate_type == "app" and cand:
            target_name = cand.app_name
            target_identifier = cand.package_id

        rows.append({
            "Finding ID": f.id,
            "Brand Name": safe_csv_cell(f.brand.name),
            "Candidate Type": safe_csv_cell(f.candidate_type),
            "Target Name": safe_csv_cell(target_name),
            "Target Identifier": safe_csv_cell(target_identifier),
            "Risk Score": f.risk_score,
            "Severity": safe_csv_cell(f.severity),
            "Review Status": safe_csv_cell(f.review_status),
            "Is Synthetic Demo": f.is_synthetic,
            "Observed Timestamp": f.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    # CSV Download Button
    if can_export:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        st.download_button(
            label="📥 Download Findings Report (CSV)",
            data=csv_bytes,
            file_name=f"brandphantom_findings_report_{organization_id[:8]}.csv",
            mime="text/csv",
            type="primary",
        )
    else:
        st.warning("🔒 Export restricted by organization access control policy.")
