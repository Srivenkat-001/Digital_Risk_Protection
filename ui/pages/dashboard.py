"""
Executive Dashboard page.
Renders high-level KPIs, severity and triage distribution charts,
high-priority review queue, and connector integration health.
"""


from html import escape

import streamlit as st
from sqlalchemy.orm import Session

from services.dashboard_service import DashboardService
from ui.components.charts import render_severity_donut, render_status_bar
from ui.components.metric_cards import render_metric_card
from ui.components.risk_badges import render_risk_badge


def render(db: Session, organization_id: str, brand_id: str | None = None):
    service = DashboardService(db)
    metrics = service.get_dashboard_summary(organization_id, brand_id)

    st.markdown("## 📊 Threat Intelligence & Monitoring Dashboard")
    st.caption("Database-backed risk and triage overview. Included findings are synthetic demo records; live source collection is not implemented.")

    # Synthetic Demo Alert
    if metrics["is_synthetic_data_present"]:
        st.markdown(
            f"""
            <div class="bp-demo-banner">
                <span>⚠️</span>
                <div>
                    <strong>Synthetic Demo Data Active:</strong>
                    Currently viewing {metrics['synthetic_findings_count']} synthetic findings evaluated against simulated targets.
                    All records are strictly isolated and labeled.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Top KPI Metrics Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_metric_card("Registered Brands", metrics["total_brands"], "Active Profiles")
    with c2:
        render_metric_card("Candidates Seen", metrics["total_candidates"], "Social & App Records")
    with c3:
        render_metric_card("Active Findings", metrics["total_findings"], f"{metrics['new_findings']} Unreviewed")
    with c4:
        render_metric_card("Confirmed Threats", metrics["confirmed_threats"], "Verified Imposters", "Threats confirmed by analyst review")
    with c5:
        render_metric_card("False Positives", metrics["false_positives"], "Dismissed Matches", "Legitimate organizations cleared by analysts")
    with c6:
        render_metric_card("Open Cases", metrics["open_cases_count"], "Active Investigations")

    st.markdown("---")

    # Visualizations Row
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_severity_donut(metrics["severity_distribution"])
    with chart_col2:
        render_status_bar(metrics["status_distribution"])

    st.markdown("---")

    # High-Priority Review Queue & Source Health
    queue_col, health_col = st.columns([3, 2])

    with queue_col:
        st.markdown("### 🚨 High-Priority Triage Queue")
        st.caption("New findings requiring prompt analyst assessment")

        queue = metrics["high_priority_queue"]
        if not queue:
            st.success("🎉 All high-priority findings have been reviewed! No items in queue.")
        else:
            for f in queue:
                with st.container(border=True):
                    head_col1, head_col2 = st.columns([3, 1])
                    with head_col1:
                        st.markdown(f"**Finding #{f.id[:8]}** | Type: `{f.candidate_type.upper()}`")
                        st.caption(f"Brand: **{f.brand.name}** | Observed: {f.created_at.strftime('%Y-%m-%d %H:%M')}")
                    with head_col2:
                        st.markdown(render_risk_badge(f.severity, f.risk_score), unsafe_allow_html=True)

                    if f.assessment:
                        st.markdown(f.assessment.explanation.splitlines()[0])

                    if st.button("Inspect Finding", key=f"inspect_{f.id}", use_container_width=True):
                        st.session_state["current_page"] = "Findings Triage"
                        st.session_state["focus_finding_id"] = f.id
                        st.rerun()

    with health_col:
        st.markdown("### 🔌 Monitoring Source Health")
        st.caption("Status of active collectors and store connectors")

        health_list = metrics["connector_health"]
        for h in health_list:
            status_color = "#3fb950" if h["is_healthy"] else "#f85149"
            status_icon = "🟢" if h["is_healthy"] else "🔴"
            connector_name = escape(str(h["name"]))
            status = escape(str(h["status"]).upper())
            details = escape(str(h["details"]))
            with st.container(border=True):
                st.markdown(f"**{status_icon} {connector_name}**")
                st.markdown(f"<span style='color:{status_color}; font-size:0.8rem; font-weight:600;'>{status}</span> — <span style='font-size:0.8rem; color:#8b949e;'>{details}</span>", unsafe_allow_html=True)
