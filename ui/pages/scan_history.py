"""
Scan Execution History & Job Tracker page.
Audit trail of all monitoring jobs, discovered candidate counts,
official exclusions, and execution diagnostics.
"""


from html import escape

import streamlit as st
from sqlalchemy.orm import Session

from db.repositories.scan_repo import ScanRepository
from jobs.job_status import format_job_status
from jobs.scan_runner import run_brand_scan
from services.auth import AuthService
from services.brand_service import BrandService


def render(db: Session, organization_id: str, brand_id: str | None = None):
    scan_repo = ScanRepository(db)
    brand_service = BrandService(db)
    user = st.session_state.get("user")
    user_role = st.session_state.get("role", "viewer")
    can_scan = AuthService.is_authorized(user_role, "analyst")

    st.markdown("## ⏱️ Monitoring Scan History & Job Runner")
    st.caption("Inspect past automated and on-demand discovery sweeps, execution durations, and source telemetry.")

    # Trigger New Scan section
    with st.expander("🚀 Trigger On-Demand Monitoring Scan", expanded=False):
        if not can_scan:
            st.warning("🔒 Read-Only role: Scan initiation restricted to Analysts and Administrators.")
        else:
            brands = brand_service.list_brands(organization_id)
            if not brands:
                st.info("Please register a brand first.")
            else:
                brand_map = {b.name: b.id for b in brands}
                selected_b_name = st.selectbox("Select Target Brand", options=list(brand_map.keys()))
                target_b_id = brand_map[selected_b_name]

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    scan_social = st.checkbox("Scan Social Media Sources", value=True)
                with col_s2:
                    scan_apps = st.checkbox("Scan Mobile App Stores", value=True)

                if st.button("Launch Scan Job", type="primary"):
                    selected_sources = []
                    if scan_social:
                        selected_sources.append("social")
                    if scan_apps:
                        selected_sources.append("app")

                    if not selected_sources:
                        st.error("Please select at least one source type to scan.")
                    else:
                        with st.spinner(f"Executing scan for {selected_b_name}..."):
                            job = run_brand_scan(
                                db=db,
                                brand_id=target_b_id,
                                organization_id=organization_id,
                                triggered_by_user_id=user.id if user else None,
                                source_types=selected_sources,
                            )
                            st.success(
                                f"Scan finished ({job.status.upper()})! Discovered {job.total_candidates_found} candidates, "
                                f"{job.new_findings_count} new findings, {job.excluded_assets_count} excluded official assets."
                            )
                            st.rerun()

    st.markdown("---")

    # Past Scan History Table
    scans = scan_repo.list_by_org(organization_id, brand_id=brand_id, limit=50)

    if not scans:
        st.info("No scan jobs recorded yet. Trigger a scan above to start monitoring.")
        return

    st.markdown(f"**Showing {len(scans)} scan execution records**")

    for s in scans:
        info = format_job_status(s)
        status_color = "#3fb950" if s.status == "completed" else ("#e3b341" if s.status == "partial" else "#f85149")

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown(f"**Scan ID:** `{s.id[:8]}` | Brand: **{info['brand_name']}**")
                st.caption(f"Sources: `{s.source_types}` | Started: {s.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            with c2:
                st.markdown(
                    f"<span class='bp-badge' style='background:{status_color}22; color:{status_color}; border:1px solid {status_color};'>{escape(s.status.upper())}</span>",
                    unsafe_allow_html=True,
                )
                duration_str = f"{info['duration_seconds']}s" if info['duration_seconds'] is not None else "In progress"
                st.caption(f"Duration: {duration_str}")
            with c3:
                st.metric("Candidates Found", s.total_candidates_found)
            with c4:
                st.metric("New Findings", s.new_findings_count, delta=f"-{s.excluded_assets_count} Excluded Official", delta_color="inverse")

            if s.error_message:
                st.warning(f"Diagnostics: {s.error_message}")
